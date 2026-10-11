---
title: SDG8 Career Guide
emoji: 🧭
colorFrom: teal
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# SDG 8 Career Guidance & Skill-Gap Platform

```
sdg8-career-platform/
├── backend/
│   ├── main.py            FastAPI app + endpoints
│   ├── resume_parser.py   Module 1: regex + LLM extraction
│   ├── matcher.py         Module 2: MiniLM embeddings, cosine match, skill gaps
│   ├── roadmap.py         Module 3: 3-step prompt chain
│   ├── llm_client.py      Failure-tolerant Anthropic wrapper
│   ├── schemas.py / config.py
├── frontend/app.py        Streamlit UI
├── data/                  skills_taxonomy.py, generate_jobs.py -> jobs.json (555 listings)
└── models/                embedding cache (auto-created)
```

## Run
```bash
pip install -r requirements.txt
cp .env.example .env && export $(grep -v '^#' .env | xargs)   # optional: set ANTHROPIC_API_KEY
python -m data.generate_jobs                                  # optional, auto-runs if missing
uvicorn backend.main:app --reload                             # terminal 1 (http://localhost:8000/docs)
streamlit run frontend/app.py                                 # terminal 2
```
First start downloads all-MiniLM-L6-v2 (~90 MB). Without an API key the app runs fully in
regex/template mode; with a key, extraction and roadmaps use the LLM chain.

## Production hardening (next steps)
Replace simulated jobs with a real feed (ESCO/O*NET + scraped/licensed listings), add OCR for scanned PDFs,
auth + rate limiting, PII redaction before LLM calls, a vector DB (pgvector/FAISS) beyond ~50k listings,
and evaluation sets for extraction accuracy and match quality.

## Deploy (Hugging Face Spaces, Docker)
1. Create a Space → SDK **Docker** → blank template.
2. Upload/push this folder (Dockerfile, start.sh and README.md must be at the repo root).
3. Settings → Variables and secrets → add secret `ANTHROPIC_API_KEY` (optional).
4. Wait for the build (~5-10 min). The app opens at `https://<user>-<space>.hf.space`.

Local Docker test: `docker build -t sdg8 . && docker run -p 7860:7860 -e ANTHROPIC_API_KEY=... sdg8`

## Deploy on Render (FREE plan, from GitHub)
This build uses `fastembed` (ONNX) instead of PyTorch so it fits in 512 MB RAM.
1. Push the repo to GitHub (never commit `.env`).
2. Render -> New -> Web Service -> connect repo -> Runtime **Docker** -> Instance type **Free**.
   (Or use New -> Blueprint; `render.yaml` is included.)
3. Environment: add `ANTHROPIC_API_KEY` (optional). Health Check Path: `/_stcore/health`.
4. Free services sleep after ~15 min idle; the first request afterwards takes ~30-60 s.
