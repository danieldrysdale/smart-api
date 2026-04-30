"""Configuration for smart-api."""

from __future__ import annotations

import os

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "120"))

# Classification categories
CLASSIFICATION_CATEGORIES = [
    "complaint",
    "enquiry",
    "compliment",
    "refund_request",
    "technical_support",
    "other",
]
