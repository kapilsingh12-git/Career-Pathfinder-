"""Module 3 - Automated 4-week upskilling roadmap (3-step prompt chain).

  Step 1  PRIORITISE : cluster missing skills into 4 themed weeks (ordered by dependency)
  Step 2  DETAIL     : goals + free learning resources per week (uses step-1 output)
  Step 3  PROJECTS   : weekly mini-project + capstone (uses step-1 + step-2 output)

Each step has a deterministic fallback, so output is always complete. Resource
URLs are NEVER taken from the LLM (hallucination risk): the LLM only names a
platform + topic, and we build the link from a whitelist of search URL templates.
"""
import logging
import math
from urllib.parse import quote_plus

from backend.llm_client import llm
from backend.schemas import Resource, RoadmapResponse, WeekPlan

log = logging.getLogger("roadmap")

PLATFORMS = {   # whitelist of free platforms -> URL template
    "YouTube": "https://www.youtube.com/results?search_query={q}",
    "freeCodeCamp": "https://www.freecodecamp.org/news/search/?query={q}",
    "Kaggle Learn": "https://www.kaggle.com/learn",
    "Microsoft Learn": "https://learn.microsoft.com/en-us/search/?terms={q}",
    "Google Cloud Skills Boost": "https://www.cloudskillsboost.google/catalog?keywords={q}",
    "AWS Skill Builder": "https://skillbuilder.aws/search?searchText={q}",
    "Coursera (audit for free)": "https://www.coursera.org/search?query={q}",
    "edX (audit for free)": "https://www.edx.org/search?q={q}",
    "MIT OpenCourseWare": "https://ocw.mit.edu/search/?q={q}",
    "roadmap.sh": "https://roadmap.sh/",
}
_CATEGORY = [   # keyword -> best-fit free platforms for the skill
    ({"python", "sql", "pandas", "numpy", "machine learning", "deep learning", "nlp", "pytorch", "tensorflow",
      "scikit-learn", "statistics", "mlops", "etl", "apache spark", "airflow"}, ["Kaggle Learn", "freeCodeCamp"]),
    ({"aws"}, ["AWS Skill Builder"]), ({"gcp"}, ["Google Cloud Skills Boost"]),
    ({"azure", "power bi", "excel"}, ["Microsoft Learn"]),
    ({"react", "javascript", "typescript", "node.js", "html/css", "docker", "kubernetes", "git", "linux",
      "ci/cd", "rest apis", "fastapi", "django", "flask", "java"}, ["freeCodeCamp", "roadmap.sh"]),
]
_DEFAULT = ["Coursera (audit for free)", "edX (audit for free)"]


def _resource(platform: str, topic: str, title: str | None = None) -> Resource:
    if platform not in PLATFORMS:
        platform = "YouTube"
    return Resource(title=title or f"{topic}: free tutorials & courses", platform=platform,
                    url=PLATFORMS[platform].format(q=quote_plus(topic + " tutorial")))


def _fallback_resources(skill: str) -> list[Resource]:
    plats = ["YouTube"]
    for keys, p in _CATEGORY:
        if skill.lower() in keys:
            plats += p
            break
    else:
        plats += _DEFAULT
    return [_resource(p, skill) for p in plats[:3]]


# ----------------------------------------------------------------- step 1
def _fallback_weeks(skills: list[str], role: str) -> list[dict]:
    size = max(1, math.ceil(len(skills) / 4))
    chunks = [skills[i:i + size] for i in range(0, len(skills), size)][:4]
    weeks = [{"theme": f"Foundations: {', '.join(c)}", "skills": c} for c in chunks]
    extras = ["Integrate & build a portfolio piece", "Polish, publish & interview prep"]
    while len(weeks) < 4:
        weeks.append({"theme": extras[len(weeks) % 2], "skills": []})
    return weeks


def _step1(role: str, missing: list[str], current: list[str]) -> tuple[list[dict], bool]:
    prompt = (f"Target role: {role}\nCandidate's current skills: {', '.join(current[:25])}\n"
              f"Missing skills (highest priority first): {', '.join(missing)}\n\n"
              "Group ALL missing skills into exactly 4 consecutive weeks, ordered so prerequisites come first. "
              'Return {"weeks":[{"theme":str,"skills":[str]} x4]}. Only use the listed skills.')
    data = llm.complete_json("You are a career coach designing a realistic 4-week upskilling plan.", prompt, 900)
    try:
        weeks = data["weeks"]
        if len(weeks) == 4 and all(isinstance(w["theme"], str) and isinstance(w["skills"], list) for w in weeks):
            allowed = set(missing)
            return [{"theme": w["theme"], "skills": [s for s in w["skills"] if s in allowed]} for w in weeks], True
    except (TypeError, KeyError):
        pass
    return _fallback_weeks(missing, role), False


# ----------------------------------------------------------------- step 2
def _step2(role: str, weeks: list[dict], hours: int) -> tuple[list[dict], bool]:
    prompt = (f"Role: {role}. The learner has {hours} hours/week. Weekly plan:\n"
              + "\n".join(f"Week {i+1}: {w['theme']} (skills: {', '.join(w['skills']) or 'none'})" for i, w in enumerate(weeks))
              + "\n\nFor each week return 3 concrete, measurable learning goals and 2-3 FREE resources. "
              f"Each resource: {{\"title\": str, \"platform\": one of {list(PLATFORMS)}, \"topic\": short search phrase}}. "
              'Return {"weeks":[{"goals":[str],"resources":[...]} x4]}.')
    data = llm.complete_json("You are a career coach who recommends only free learning resources.", prompt, 1800)
    out, ok = [], False
    try:
        for w, d in zip(weeks, data["weeks"]):
            res = [_resource(r["platform"], r.get("topic") or w["theme"], r.get("title")) for r in d["resources"][:3]]
            out.append({**w, "goals": [str(g) for g in d["goals"][:4]], "resources": res})
        ok = len(out) == 4 and all(o["goals"] and o["resources"] for o in out)
    except (TypeError, KeyError):
        ok = False
    if ok:
        return out, True
    out = []
    for w in weeks:
        sk = w["skills"]
        res = [r for s in sk[:2] for r in _fallback_resources(s)][:4] or [_resource("freeCodeCamp", role + " portfolio")]
        goals = ([f"Learn the core concepts of {s} and complete one hands-on tutorial" for s in sk[:3]]
                 or [f"Consolidate this month's learning for the {role} role"])
        out.append({**w, "goals": goals + ["Write short notes summarising what you learned"], "resources": res})
    return out, False


# ----------------------------------------------------------------- step 3
def _step3(role: str, weeks: list[dict]) -> tuple[list[str], str, bool]:
    prompt = (f"Role: {role}. Weekly themes and goals:\n"
              + "\n".join(f"Week {i+1}: {w['theme']} | {'; '.join(w['goals'][:2])}" for i, w in enumerate(weeks))
              + '\n\nSuggest one small, portfolio-worthy mini-project per week (1 sentence each) and one capstone '
              'that combines everything and can be published on GitHub. '
              'Return {"projects":[str x4],"capstone":str}.')
    data = llm.complete_json("You are a mentor who designs practical portfolio projects.", prompt, 800)
    try:
        if len(data["projects"]) == 4 and data["capstone"]:
            return [str(p) for p in data["projects"]], str(data["capstone"]), True
    except (TypeError, KeyError):
        pass
    projects = [f"Build a small demo applying {', '.join(w['skills']) or 'your new skills'} and document it in a README." for w in weeks]
    allsk = ", ".join(s for w in weeks for s in w["skills"]) or "your new skills"
    return projects, f"Capstone: an end-to-end {role} portfolio project combining {allsk}; publish on GitHub with a write-up.", False


# ----------------------------------------------------------------- public API
def generate_roadmap(target_role: str, missing_skills: list[str], current_skills: list[str],
                     weekly_hours: int = 8) -> RoadmapResponse:
    missing = list(dict.fromkeys(missing_skills))[:12]          # cap scope: 4 weeks is short
    # No gaps -> skip step 1 and run a portfolio/interview-prep sprint instead
    weeks, ok1 = _step1(target_role, missing, current_skills) if missing else (_fallback_weeks([], target_role), False)
    weeks, ok2 = _step2(target_role, weeks, weekly_hours)
    projects, capstone, ok3 = _step3(target_role, weeks)

    plan = [WeekPlan(week=i + 1, theme=w["theme"], skills=w["skills"], goals=w["goals"],
                     resources=w["resources"], project=projects[i]) for i, w in enumerate(weeks)]
    flags = [ok1, ok2, ok3]
    mode = "llm-chain" if all(flags) else "mixed" if any(flags) else "template-fallback"
    return RoadmapResponse(target_role=target_role, weekly_hours=weekly_hours, weeks=plan,
                           capstone_project=capstone, generated_by=mode)
