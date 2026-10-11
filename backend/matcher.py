"""Module 2 - ML job matcher & skill-gap predictor.

Method
------
1. Embed every job listing ("title + required skills") and the candidate's skill
   string with MiniLM (all-MiniLM-L6-v2, run through fastembed/ONNX). Cosine similarity of the
   L2-normalised vectors = semantic fit.
2. Skill coverage = share of a listing's required skills the candidate has. A
   skill counts as covered on exact match OR embedding similarity >= 0.80, so
   "PyTorch" can partially satisfy near-synonyms without a hand-made ontology.
3. listing score = 0.4 * scaled_cosine + 0.6 * coverage  (embeddings alone are
   noisy on short skill lists; coverage keeps the score explainable).
4. Role score = mean of the 5 best listings for that role. Top-3 roles returned.
5. Skill gap for the target role = skills demanded by >=40% of its listings that
   the candidate lacks, ranked by market demand.
"""
import hashlib
import json
import logging
from collections import Counter, defaultdict
from typing import Optional

import numpy as np

from backend.config import EMBED_CACHE_DIR, EMBED_MODEL, JOBS_PATH, MODELS_DIR
from backend.schemas import MatchResponse, MissingSkill, RoleMatch, SkillGap

log = logging.getLogger("matcher")

W_EMB, W_COV = 0.4, 0.6
FUZZY_SKILL_THRESHOLD = 0.80
DEMAND_CUTOFF = 0.40          # skill must appear in >=40% of a role's listings
COSINE_CEILING = 0.70         # cosine at/above this is treated as a perfect semantic fit


class JobMatcher:
    def __init__(self) -> None:
        from fastembed import TextEmbedding   # ONNX runtime: no PyTorch, ~5x less RAM

        self.jobs = self._load_jobs()
        log.info("Loading embedding model %s ...", EMBED_MODEL)
        self.model = TextEmbedding(model_name=EMBED_MODEL, cache_dir=EMBED_CACHE_DIR, threads=1)

        texts = [f"{j['title']}. Skills: {', '.join(j['required_skills'])}" for j in self.jobs]
        self.job_emb = self._cached_embeddings(texts)

        self.skill_vocab = sorted({s for j in self.jobs for s in j["required_skills"]})
        self.skill_emb = self._encode(self.skill_vocab)

        self.role_idx: dict[str, list[int]] = defaultdict(list)
        self.role_industry: dict[str, str] = {}
        for i, j in enumerate(self.jobs):
            self.role_idx[j["role"]].append(i)
            self.role_industry[j["role"]] = j["industry"]

    # ------------------------------------------------------------ setup helpers
    @staticmethod
    def _load_jobs() -> list[dict]:
        if not JOBS_PATH.exists():
            from data.generate_jobs import save
            log.info("jobs.json missing - generating simulated market data")
            return save()
        return json.loads(JOBS_PATH.read_text(encoding="utf-8"))

    def _encode(self, texts: list[str]) -> np.ndarray:
        vecs = np.array(list(self.model.embed(texts, batch_size=32)), dtype=np.float32)
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)     # L2-normalise -> dot product = cosine
        return vecs / np.clip(norms, 1e-12, None)

    def _cached_embeddings(self, texts: list[str]) -> np.ndarray:
        """Cache job embeddings on disk, keyed by content+model hash."""
        key = hashlib.md5((EMBED_MODEL + "|".join(texts)).encode()).hexdigest()[:12]
        path = MODELS_DIR / f"job_embeddings_{key}.npy"
        try:
            if path.exists():
                return np.load(path)
        except Exception:
            log.warning("Corrupt embedding cache, recomputing")
        emb = self._encode(texts)
        try:
            MODELS_DIR.mkdir(exist_ok=True)
            np.save(path, emb)
        except OSError as exc:
            log.warning("Could not write cache: %s", exc)
        return emb

    # ------------------------------------------------------------ public helpers
    @property
    def roles(self) -> dict[str, str]:
        return dict(sorted(self.role_industry.items()))

    def _covered(self, skills: list[str]) -> set[str]:
        have = {s.lower() for s in skills}
        best = (self.skill_emb @ self._encode(skills).T).max(axis=1)
        return {v for v, b in zip(self.skill_vocab, best) if v.lower() in have or b >= FUZZY_SKILL_THRESHOLD}

    def _demand(self, role: str) -> dict[str, float]:
        idxs = self.role_idx[role]
        c = Counter(s for i in idxs for s in self.jobs[i]["required_skills"])
        return {s: n / len(idxs) for s, n in c.most_common()}

    # ------------------------------------------------------------ main entry
    def match(self, skills: list[str], industry: str = "Any",
              target_role: Optional[str] = None, top_k: int = 3) -> MatchResponse:
        skills = list(dict.fromkeys(s.strip() for s in skills if s and s.strip()))
        if not skills:
            raise ValueError("At least one skill is required.")
        if target_role and target_role not in self.role_idx:
            raise ValueError(f"Unknown target role '{target_role}'.")

        cand = self._encode(["Skills: " + ", ".join(skills)])[0]
        cos = self.job_emb @ cand
        covered = self._covered(skills)
        cov = np.array([sum(s in covered for s in j["required_skills"]) / len(j["required_skills"])
                        for j in self.jobs])
        score = W_EMB * np.clip(cos / COSINE_CEILING, 0, 1) + W_COV * cov

        ranked: list[tuple[str, float, np.ndarray]] = []
        for role, idxs in self.role_idx.items():
            if industry != "Any" and self.role_industry[role] != industry:
                continue
            top = np.array(idxs)[np.argsort(score[idxs])[-5:]]   # best 5 listings
            ranked.append((role, float(score[top].mean()), top))
        if not ranked:
            raise ValueError(f"No roles found for industry '{industry}'.")
        ranked.sort(key=lambda r: r[1], reverse=True)

        matches = []
        for role, sc, top in ranked[:top_k]:
            demand = self._demand(role)
            req = [s for s, f in demand.items() if f >= DEMAND_CUTOFF]
            matches.append(RoleMatch(
                role=role, industry=self.role_industry[role],
                confidence_pct=round(sc * 100, 1),
                embedding_similarity=round(float(cos[top].mean()), 3),
                skill_coverage_pct=round(float(cov[top].mean()) * 100, 1),
                matched_skills=[s for s in req if s in covered],
                missing_skills=[s for s in req if s not in covered],
            ))

        # Skill gap vs. dream role (user-chosen, else best match)
        gap_role = target_role or matches[0].role
        demand = self._demand(gap_role)
        req = {s: f for s, f in demand.items() if f >= DEMAND_CUTOFF}
        missing = [MissingSkill(
            skill=s, demand_pct=round(f * 100, 1),
            priority="Critical" if f >= 0.75 else "Important" if f >= 0.55 else "Nice-to-have",
        ) for s, f in req.items() if s not in covered]
        readiness = sum(f for s, f in req.items() if s in covered) / sum(req.values()) * 100

        return MatchResponse(
            top_matches=matches,
            skill_gap=SkillGap(target_role=gap_role, readiness_pct=round(readiness, 1),
                               matched_skills=[s for s in req if s in covered], missing_skills=missing),
            jobs_searched=len(self.jobs),
        )
