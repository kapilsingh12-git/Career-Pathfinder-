#!/usr/bin/env bash
# Runs the API (internal :8000) and the Streamlit UI (public $PORT, default 7860).
set -e
uvicorn backend.main:app --host 127.0.0.1 --port 8000 &

# Wait until the API is healthy so the UI never loads before the model
python - <<'PY'
import time, urllib.request
for _ in range(120):
    try:
        urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2); break
    except Exception:
        time.sleep(1)
PY

# CORS/XSRF off: required for file upload behind HF's iframe/proxy
exec streamlit run frontend/app.py \
  --server.port "${PORT:-7860}" --server.address 0.0.0.0 --server.headless true \
  --server.enableCORS false --server.enableXsrfProtection false
