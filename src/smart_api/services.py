"""AI service functions — one per endpoint."""

from __future__ import annotations

import json

from smart_api.config import CLASSIFICATION_CATEGORIES
from smart_api.models import (
    ClassifyRequest, ClassifyResponse, Confidence,
    SummariseRequest, SummariseResponse,
    ExtractRequest, ExtractResponse, Entity,
)
from smart_api.ollama import chat, parse_json_response, OllamaError


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

async def classify_text(req: ClassifyRequest) -> ClassifyResponse:
    """Classify text into one of the configured categories."""
    categories = req.categories or CLASSIFICATION_CATEGORIES
    categories_str = ", ".join(f'"{c}"' for c in categories)

    system = f"""You are a text classification engine. Classify the user's text into exactly one of these categories: {categories_str}.

Respond with a JSON object containing exactly these fields:
- "category": one of the allowed categories (string)
- "confidence": one of "high", "medium", or "low" (string)
- "reasoning": a single sentence explaining the classification (string)

Respond with JSON only. No other text."""

    prompt = f"Classify this text:\n\n{req.text}"

    raw = await chat(prompt, system, json_mode=True)
    data = parse_json_response(raw)

    # Validate category is in the allowed list
    category = data.get("category", "other")
    if category not in categories:
        category = "other"

    confidence_raw = data.get("confidence", "medium").lower()
    try:
        confidence = Confidence(confidence_raw)
    except ValueError:
        confidence = Confidence.medium

    return ClassifyResponse(
        category=category,
        confidence=confidence,
        reasoning=data.get("reasoning", ""),
        input_length=len(req.text),
    )


# ---------------------------------------------------------------------------
# Summarisation
# ---------------------------------------------------------------------------

async def summarise_text(req: SummariseRequest) -> SummariseResponse:
    """Summarise text into a short summary and key points."""
    system = f"""You are a precise text summarisation engine.

Respond with a JSON object containing exactly these fields:
- "summary": a concise 1-2 sentence summary of the entire text (string)
- "key_points": a list of up to {req.max_points} key points as short strings (array of strings)

Respond with JSON only. No other text."""

    prompt = f"Summarise this text:\n\n{req.text}"

    raw = await chat(prompt, system, json_mode=True)
    data = parse_json_response(raw)

    summary = data.get("summary", "")
    key_points = data.get("key_points", [])

    # Enforce max_points
    key_points = key_points[: req.max_points]

    return SummariseResponse(
        summary=summary,
        key_points=key_points,
        word_count_in=len(req.text.split()),
        word_count_out=len(summary.split()),
    )


# ---------------------------------------------------------------------------
# Entity extraction
# ---------------------------------------------------------------------------

async def extract_entities(req: ExtractRequest) -> ExtractResponse:
    """Extract named entities from text."""
    if req.entity_types:
        types_str = ", ".join(f'"{t}"' for t in req.entity_types)
        types_instruction = f"Extract only these entity types: {types_str}."
    else:
        types_instruction = (
            'Extract all named entities. Common types include: '
            '"person", "organisation", "location", "date", "amount", '
            '"invoice_number", "email", "phone", "url".'
        )

    system = f"""You are a named entity extraction engine.

{types_instruction}

Respond with a JSON object containing exactly this field:
- "entities": an array of objects, each with:
  - "type": the entity type as a lowercase string
  - "value": the extracted value as it appears in the text
  - "context": a short snippet of surrounding text (optional, can be null)

If no entities are found, return an empty array.
Respond with JSON only. No other text."""

    prompt = f"Extract entities from this text:\n\n{req.text}"

    raw = await chat(prompt, system, json_mode=True)
    data = parse_json_response(raw)

    raw_entities = data.get("entities", [])
    entities = []
    for e in raw_entities:
        if isinstance(e, dict) and "type" in e and "value" in e:
            entities.append(Entity(
                type=e["type"],
                value=e["value"],
                context=e.get("context"),
            ))

    return ExtractResponse(
        entities=entities,
        entity_count=len(entities),
    )
