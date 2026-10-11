"""Simulated job-market generator -> data/jobs.json (520+ listings, seeded).

Run:  python -m data.generate_jobs
"""
import json
import math
import random
from pathlib import Path

from data.skills_taxonomy import ROLES, SKILLS

OUT = Path(__file__).parent / "jobs.json"
COMPANIES = ["Aurora Labs", "GreenGrid", "NovaHealth", "Pinnacle Bank", "BrightPath", "Helix Systems",
             "Meridian Corp", "Orbit Analytics", "TerraWorks", "Zenith Retail", "CivicTech", "BlueRiver Energy",
             "Summit Logistics", "Lumen Education", "Atlas Consulting", "Kestrel Software"]
LOCATIONS = ["Remote", "Bengaluru", "Pune", "Hyderabad", "Delhi NCR", "Mumbai", "London", "Berlin", "Toronto", "Singapore"]
LEVELS = [("Junior", 0, 2), ("Mid-level", 2, 5), ("Senior", 5, 10)]


def build_jobs(total: int = 520, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    per_role = math.ceil(total / len(ROLES))
    jobs: list[dict] = []
    for role, (industry, core, optional) in ROLES.items():
        for i in range(per_role):
            level, lo, hi = rng.choice(LEVELS)
            req = list(core)
            if len(req) > 3 and rng.random() < 0.15:          # listings differ slightly
                req.remove(rng.choice(req))
            req += rng.sample(optional, k=min(len(optional), rng.randint(2, 3)))
            assert all(s in SKILLS for s in req), f"Unknown skill in {role}"
            company, loc = rng.choice(COMPANIES), rng.choice(LOCATIONS)
            jobs.append({
                "id": f"JOB-{len(jobs) + 1:04d}", "role": role, "title": f"{level} {role}",
                "industry": industry, "company": company, "location": loc,
                "min_years": lo, "max_years": hi, "required_skills": req,
                "description": f"{company} ({loc}) is hiring a {level} {role}. Key skills: {', '.join(req)}.",
            })
    return jobs


def save(path: Path = OUT) -> list[dict]:
    jobs = build_jobs()
    path.write_text(json.dumps(jobs, indent=1), encoding="utf-8")
    return jobs


if __name__ == "__main__":
    print(f"Wrote {len(save())} listings to {OUT}")
