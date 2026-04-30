"""Pydantic request and response models for all endpoints."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------

class Confidence(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


# ---------------------------------------------------------------------------
# /classify
# ---------------------------------------------------------------------------

class ClassifyRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000, description="Text to classify")
    categories: Optional[list[str]] = Field(
        None,
        description="Custom categories. If omitted, uses the default set.",
    )

    model_config = {"json_schema_extra": {
        "example": {
            "text": "I've been waiting 3 weeks and still no delivery!",
        }
    }}


class ClassifyResponse(BaseModel):
    category: str = Field(..., description="The assigned category")
    confidence: Confidence = Field(..., description="Model's confidence in the classification")
    reasoning: str = Field(..., description="Brief explanation of the classification")
    input_length: int = Field(..., description="Number of characters in the input text")


# ---------------------------------------------------------------------------
# /summarise
# ---------------------------------------------------------------------------

class SummariseRequest(BaseModel):
    text: str = Field(..., min_length=50, max_length=50000, description="Text to summarise")
    max_points: int = Field(5, ge=1, le=10, description="Maximum number of key points")

    model_config = {"json_schema_extra": {
        "example": {
            "text": "Your long document goes here...",
            "max_points": 3,
        }
    }}


class SummariseResponse(BaseModel):
    summary: str = Field(..., description="One or two sentence summary")
    key_points: list[str] = Field(..., description="Bullet-point key points")
    word_count_in: int = Field(..., description="Word count of the input")
    word_count_out: int = Field(..., description="Word count of the summary")


# ---------------------------------------------------------------------------
# /extract
# ---------------------------------------------------------------------------

class EntityType(str, Enum):
    person = "person"
    organisation = "organisation"
    location = "location"
    date = "date"
    amount = "amount"
    invoice_number = "invoice_number"
    email = "email"
    phone = "phone"
    url = "url"
    other = "other"


class Entity(BaseModel):
    type: str = Field(..., description="Entity type")
    value: str = Field(..., description="Extracted value")
    context: Optional[str] = Field(None, description="Surrounding context snippet")


class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000, description="Text to extract entities from")
    entity_types: Optional[list[str]] = Field(
        None,
        description="Entity types to extract. If omitted, extracts all.",
    )

    model_config = {"json_schema_extra": {
        "example": {
            "text": "Invoice #1234 from Acme Corp, due 15 May 2026, total $4,500. Contact: billing@acme.com",
        }
    }}


class ExtractResponse(BaseModel):
    entities: list[Entity] = Field(..., description="List of extracted entities")
    entity_count: int = Field(..., description="Total number of entities found")


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    ollama_reachable: bool
    model: str
    version: str


# ---------------------------------------------------------------------------
# Error
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
