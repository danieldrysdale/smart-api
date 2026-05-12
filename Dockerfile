FROM python:3.12-slim

WORKDIR /app

# Copy everything needed to build the package
COPY pyproject.toml .
COPY src/ src/

# Install the package and dependencies
RUN pip install --no-cache-dir ".[dev]" || pip install --no-cache-dir .

EXPOSE 8002

CMD ["uvicorn", "smart_api.main:app", "--host", "0.0.0.0", "--port", "8002"]
