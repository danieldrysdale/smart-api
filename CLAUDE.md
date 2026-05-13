# smart-api — Project Context

## What this is
An AI-powered REST API for text classification, summarisation, and entity extraction. Fully local — powered by Ollama, no external API keys required.

## Stack
- Python 3.12
- FastAPI + uvicorn
- Ollama — local LLM backend
- httpx for Ollama communication
- src layout with pyproject.toml

## Project structure
```
smart-api/
├── pyproject.toml
└── src/smart_api/
    ├── main.py       — FastAPI app and route definitions
    ├── services.py   — Business logic (classify, summarise, extract)
    ├── ollama.py     — Ollama HTTP client
    ├── models.py     — Pydantic request/response models
    └── config.py     — Configuration
```

## API endpoints
- `POST /classify`  — classify text into a category
- `POST /summarise` — summarise text
- `POST /extract`   — extract named entities
- `GET /health`     — health check, confirms Ollama reachability

## Running locally
```bash
source venv/bin/activate
ollama serve  # required
uvicorn smart_api.main:app --reload --port 8002
pip install -e ".[dev]"
pytest tests/ -v
```

## Docker notes
- Ollama runs on the HOST, not in the container
- Use `OLLAMA_URL=http://host.docker.internal:11434` when running in Docker
- Image: `ghcr.io/danieldrysdale/smart-api:latest`

## CI/CD
- Uses shared reusable workflow from `danieldrysdale/.github`
- Multi-platform Docker image (amd64 + arm64) to GHCR

## Environment variables
- `OLLAMA_URL` — default: `http://localhost:11434`
- `OLLAMA_MODEL` — default: `llama3.2`
- `OLLAMA_TIMEOUT` — default: 30

## Conventions
- Conventional Commits
- Models in models.py, business logic in services.py, HTTP in ollama.py
