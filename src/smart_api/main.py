"""FastAPI application and route definitions."""

from __future__ import annotations

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from smart_api import __version__
from smart_api.config import OLLAMA_MODEL, OLLAMA_URL, OLLAMA_TIMEOUT
from smart_api.models import (
    ClassifyRequest, ClassifyResponse,
    SummariseRequest, SummariseResponse,
    ExtractRequest, ExtractResponse,
    HealthResponse, ErrorResponse,
)
from smart_api.ollama import OllamaError
from smart_api.services import classify_text, summarise_text, extract_entities

app = FastAPI(
    title="smart-api",
    description=(
        "AI-powered REST API for text classification, summarisation, and entity extraction. "
        "Powered by Ollama — fully local, no API keys required."
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ---------------------------------------------------------------------------
# Error handler
# ---------------------------------------------------------------------------

@app.exception_handler(OllamaError)
async def ollama_error_handler(request, exc: OllamaError):
    return JSONResponse(
        status_code=503,
        content={"error": "AI service unavailable", "detail": str(exc)},
    )


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    tags=["system"],
)
async def health():
    """Check service health and Ollama connectivity."""
    ollama_ok = False
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            ollama_ok = resp.status_code == 200
    except Exception:
        pass

    return HealthResponse(
        status="ok" if ollama_ok else "degraded",
        ollama_reachable=ollama_ok,
        model=OLLAMA_MODEL,
        version=__version__,
    )


# ---------------------------------------------------------------------------
# Classify
# ---------------------------------------------------------------------------

@app.post(
    "/classify",
    response_model=ClassifyResponse,
    summary="Classify text",
    tags=["ai"],
    responses={503: {"model": ErrorResponse}},
)
async def classify(req: ClassifyRequest):
    """Classify text into a category.

    Uses Ollama to assign the input text to one of the configured categories,
    returning the category, confidence level, and reasoning.
    """
    try:
        return await classify_text(req)
    except OllamaError as e:
        raise HTTPException(status_code=503, detail=str(e))


# ---------------------------------------------------------------------------
# Summarise
# ---------------------------------------------------------------------------

@app.post(
    "/summarise",
    response_model=SummariseResponse,
    summary="Summarise text",
    tags=["ai"],
    responses={503: {"model": ErrorResponse}},
)
async def summarise(req: SummariseRequest):
    """Summarise text into a brief summary and key points.

    Returns a 1-2 sentence summary and up to `max_points` key points
    extracted from the input text.
    """
    try:
        return await summarise_text(req)
    except OllamaError as e:
        raise HTTPException(status_code=503, detail=str(e))


# ---------------------------------------------------------------------------
# Extract
# ---------------------------------------------------------------------------

@app.post(
    "/extract",
    response_model=ExtractResponse,
    summary="Extract entities",
    tags=["ai"],
    responses={503: {"model": ErrorResponse}},
)
async def extract(req: ExtractRequest):
    """Extract named entities from text.

    Identifies and extracts named entities such as people, organisations,
    dates, amounts, invoice numbers, emails, and more.
    Optionally filter by specific entity types.
    """
    try:
        return await extract_entities(req)
    except OllamaError as e:
        raise HTTPException(status_code=503, detail=str(e))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run():
    """Run the API server."""
    uvicorn.run(
        "smart_api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    run()
