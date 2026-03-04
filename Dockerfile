FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for pandas/numpy builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-mcp.txt pyproject.toml ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-mcp.txt && \
    pip install --no-cache-dir fastapi uvicorn python-dotenv

COPY . .

ENV TRADINGAGENTS_DATA_DIR=/app/tradingagents/data \
    TRADINGAGENTS_RESULTS_DIR=/app/tradingagents/results \
    TRADINGAGENTS_DATA_CACHE_DIR=/app/tradingagents/dataflows/data_cache \
    TRADINGAGENTS_PYTHON=python

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
