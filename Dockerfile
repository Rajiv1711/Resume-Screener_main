# syntax=docker/dockerfile:1

# Production-grade container for FastAPI backend
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install only what's needed to build and run, then purge build tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       ca-certificates \
       curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    # purge build toolchain to shrink image
    && apt-get purge -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Pre-fetch NLTK data used at runtime to avoid downloads in prod
RUN python - <<'PY'
import nltk
for pkg, locator in {
    'punkt': 'tokenizers/punkt',
    'punkt_tab': 'tokenizers/punkt_tab',
    'stopwords': 'corpora/stopwords',
    'wordnet': 'corpora/wordnet',
}.items():
    try:
        nltk.data.find(locator)
    except LookupError:
        nltk.download(pkg)
PY

# Application code (only backend pieces)
COPY app ./app
COPY ml ./ml

# Create non-root user for security
RUN useradd -m -u 10001 appuser
USER appuser

EXPOSE 8000

# Healthcheck against root endpoint
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -fsS http://127.0.0.1:8000/ || exit 1

# Run via gunicorn with uvicorn workers (production)
# Adjust workers/threads via image rebuilds if needed
CMD [
  "gunicorn",
  "-k", "uvicorn.workers.UvicornWorker",
  "-w", "2",
  "--threads", "8",
  "--timeout", "60",
  "--keep-alive", "10",
  "--bind", "0.0.0.0:8000",
  "app.main:app",
  "--access-logfile", "-",
  "--error-logfile", "-"
]
