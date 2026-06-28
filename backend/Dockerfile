FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependências de sistema mínimas (psycopg, build).
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Instala as dependências primeiro (melhor cache).
COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install -e .

# Copia o restante do código.
COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
    CMD curl -fsS http://localhost:8000/saude || exit 1

CMD ["uvicorn", "app.principal:app", "--host", "0.0.0.0", "--port", "8000"]
