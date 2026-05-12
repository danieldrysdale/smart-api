FROM python:3.12-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY pyproject.toml .
RUN pip install --no-cache-dir ".[dev]" || pip install --no-cache-dir .

# Copy source
COPY src/ src/

EXPOSE 8002

CMD ["uvicorn", "smart_api.main:app", "--host", "0.0.0.0", "--port", "8002"]
