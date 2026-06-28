# =============================================================================
# production-grade-devops-platform — Production Dockerfile
# GitHub  : https://github.com/shivam535353/production-grade-devops-platform
# Author  : Shivam Gadilkar
#
# Multi-stage build:
#   Stage 1 (builder) — installs all Python dependencies
#   Stage 2 (runtime) — minimal image with non-root user
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1 — Builder
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2 — Runtime
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

LABEL maintainer="Shivam Gadilkar" \
      org.opencontainers.image.title="production-grade-devops-platform" \
      org.opencontainers.image.description="Multi-Environment CI/CD Platform" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.source="https://github.com/shivam535353/production-grade-devops-platform"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    PORT=5000

# Non-root user for security
RUN groupadd --gid 1001 appgroup \
    && useradd --uid 1001 --gid appgroup --shell /bin/bash --no-create-home appuser

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" \
    || exit 1

CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--threads", "4", \
     "--worker-class", "gthread", \
     "--timeout", "60", \
     "--keep-alive", "5", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "app:create_app()"]
