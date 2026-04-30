# smart-api

An AI-powered REST API for text classification, summarisation, and entity extraction. Powered by Ollama — fully local, no API keys, no cloud.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health and Ollama connectivity |
| `POST` | `/classify` | Classify text into a category |
| `POST` | `/summarise` | Summarise text into key points |
| `POST` | `/extract` | Extract named entities from text |

Interactive docs available at `http://localhost:8000/docs` when running.

## Examples

### Classify

```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "I have been waiting 3 weeks and still no delivery!"}'
```

```json
{
  "category": "complaint",
  "confidence": "high",
  "reasoning": "The message expresses clear dissatisfaction about a delayed delivery.",
  "input_length": 54
}
```

### Summarise

```bash
curl -X POST http://localhost:8000/summarise \
  -H "Content-Type: application/json" \
  -d '{"text": "your long document here...", "max_points": 3}'
```

```json
{
  "summary": "A concise overview of the document.",
  "key_points": ["First key point", "Second key point", "Third key point"],
  "word_count_in": 450,
  "word_count_out": 8
}
```

### Extract entities

```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Invoice #1234 from Acme Corp, due 15 May 2026, total $4,500. Contact: billing@acme.com"}'
```

```json
{
  "entities": [
    {"type": "invoice_number", "value": "1234", "context": "Invoice #1234"},
    {"type": "organisation", "value": "Acme Corp", "context": null},
    {"type": "date", "value": "15 May 2026", "context": "due 15 May 2026"},
    {"type": "amount", "value": "$4,500", "context": "total $4,500"},
    {"type": "email", "value": "billing@acme.com", "context": null}
  ],
  "entity_count": 5
}
```

## Project structure

```
smart-api/
├── src/smart_api/
│   ├── __init__.py
│   ├── main.py       # FastAPI app and route definitions
│   ├── models.py     # Pydantic request/response models
│   ├── services.py   # AI service logic (prompt engineering + parsing)
│   ├── ollama.py     # Ollama HTTP client with JSON mode support
│   └── config.py     # Configuration
├── tests/
│   ├── conftest.py
│   ├── test_classify.py
│   ├── test_summarise.py
│   └── test_extract.py
└── pyproject.toml
```

## Prerequisites

Install [Ollama](https://ollama.com) and pull a model:

```bash
brew install ollama
ollama pull llama3.2
ollama serve
```

## Installation

```bash
git clone https://github.com/danieldrysdale/smart-api
cd smart-api
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running

```bash
smart-api
```

Or directly:

```bash
uvicorn smart_api.main:app --reload
```

The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/docs` for the interactive Swagger UI.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama service URL |
| `OLLAMA_MODEL` | `llama3.2` | Model to use |
| `OLLAMA_TIMEOUT` | `120` | Request timeout in seconds |

```bash
export OLLAMA_MODEL=mistral
smart-api
```

## Custom classification categories

Pass a `categories` array to override the defaults:

```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Fix this bug immediately",
    "categories": ["bug", "feature_request", "question", "urgent"]
  }'
```

## Running tests

Tests mock Ollama — no running service required:

```bash
pytest -v
```
