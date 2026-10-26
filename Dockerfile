# ---------- Etapa 1: instala dependencias con uv ----------
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

# psycopg2 (sin -binary) se compila desde el código fuente: necesita gcc y libpq-dev.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Primero solo las dependencias, para aprovechar la caché de Docker.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# ---------- Etapa 2: imagen final ----------
FROM python:3.14-slim-bookworm

# libpq5 es la librería de PostgreSQL que psycopg2 usa en tiempo de ejecución.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY . .

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# Aplica las migraciones y luego levanta la API.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
