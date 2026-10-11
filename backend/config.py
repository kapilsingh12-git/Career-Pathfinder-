"""Central configuration (env-driven)."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"          # embedding cache lives here
JOBS_PATH = DATA_DIR / "jobs.json"

EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBED_CACHE_DIR = os.getenv("EMBED_CACHE_DIR", str(MODELS_DIR / "fastembed"))  # ONNX model files
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-5-5")
MAX_UPLOAD_MB = 5
