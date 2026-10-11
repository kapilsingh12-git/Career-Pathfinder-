"""FastAPI application.   Run from project root:  uvicorn backend.main:app --reload

Endpoints
  GET  /health            liveness + LLM availability
  GET  /roles             industries and roles known to the matcher
  POST /parse-resume      multipart PDF/TXT  -> ParsedResume JSON
  POST /predict-match     skills JSON        -> top-3 roles + skill gap
  POST /generate-roadmap  missing skills     -> 4-week roadmap
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.config import MAX_UPLOAD_MB
from backend.llm_client import llm
from backend.matcher import JobMatcher
from backend.resume_parser import ResumeParseError, parse_resume
from backend.roadmap import generate_roadmap
from backend.schemas import MatchRequest, MatchResponse, ParsedResume, RoadmapRequest, RoadmapResponse
from data.skills_taxonomy import INDUSTRIES

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("api")
state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["matcher"] = JobMatcher()          # load model + embeddings once at startup
    log.info("Matcher ready (%d listings). LLM available: %s", len(state["matcher"].jobs), llm.available)
    yield
    state.clear()


app = FastAPI(title="SDG 8 Career Guidance API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:8501"],   # tighten for production
                   allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health():
    return {"status": "ok", "llm_enabled": llm.available, "jobs": len(state["matcher"].jobs)}


@app.get("/roles")
def roles():
    return {"industries": INDUSTRIES, "roles": state["matcher"].roles}


@app.post("/parse-resume", response_model=ParsedResume)
async def parse_resume_endpoint(file: UploadFile = File(...)):
    content = await file.read(MAX_UPLOAD_MB * 1024 * 1024 + 1)
    if not content:
        raise HTTPException(400, "Uploaded file is empty.")
    if len(content) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {MAX_UPLOAD_MB} MB limit.")
    try:
        return parse_resume(file.filename or "", content)
    except ResumeParseError as exc:
        raise HTTPException(422, str(exc))
    except Exception:
        log.exception("Unexpected parse failure")
        raise HTTPException(500, "Internal error while parsing the resume.")


@app.post("/predict-match", response_model=MatchResponse)
def predict_match(req: MatchRequest):
    try:
        return state["matcher"].match(req.skills, req.industry, req.target_role)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    except Exception:
        log.exception("Unexpected match failure")
        raise HTTPException(500, "Internal error while computing matches.")


@app.post("/generate-roadmap", response_model=RoadmapResponse)
def roadmap(req: RoadmapRequest):
    try:
        return generate_roadmap(req.target_role, req.missing_skills, req.current_skills, req.weekly_hours)
    except Exception:
        log.exception("Roadmap generation failed")
        raise HTTPException(500, "Internal error while generating the roadmap.")
