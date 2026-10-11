# Low-RAM image for Render FREE plan (512 MB): ONNX embeddings, no PyTorch.
FROM python:3.11-slim

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=1 \
    EMBED_CACHE_DIR=/home/user/fastembed_cache \
    BACKEND_URL=http://127.0.0.1:8000
WORKDIR $HOME/app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bake the ONNX model into the image (no download at runtime)
RUN python -c "from fastembed import TextEmbedding; TextEmbedding('sentence-transformers/all-MiniLM-L6-v2', cache_dir='/home/user/fastembed_cache')"

COPY --chown=user . .
# Bake job data + job-embedding cache so cold starts are fast
RUN python -m data.generate_jobs && python -c "from backend.matcher import JobMatcher; JobMatcher()"

EXPOSE 7860
CMD ["bash", "start.sh"]
