"""Ollama HTTP client."""

from __future__ import annotations

import json

import httpx

from smart_api.config import OLLAMA_MODEL, OLLAMA_TIMEOUT, OLLAMA_URL


class OllamaError(Exception):
    """Raised when Ollama returns an error or unreachable."""


async def chat(
    prompt: str,
    system: str,
    json_mode: bool = True,
    model: str = OLLAMA_MODEL,
) -> str:
    """Send a chat request to Ollama and return the response text.

    Parameters
    ----------
    prompt:
        The user message.
    system:
        The system prompt.
    json_mode:
        If True, instructs Ollama to return valid JSON only.
    model:
        The Ollama model to use.

    Returns
    -------
    str
        The model's response text.

    Raises
    ------
    OllamaError
        If Ollama is unreachable or returns an error.
    """
    payload: dict = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }

    if json_mode:
        payload["format"] = "json"

    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
    except httpx.ConnectError:
        raise OllamaError(
            f"Cannot connect to Ollama at {OLLAMA_URL}. "
            "Is `ollama serve` running?"
        )
    except httpx.TimeoutException:
        raise OllamaError(
            f"Ollama request timed out after {OLLAMA_TIMEOUT}s."
        )
    except httpx.HTTPStatusError as e:
        raise OllamaError(f"Ollama returned HTTP {e.response.status_code}: {e.response.text}")
    except (KeyError, json.JSONDecodeError) as e:
        raise OllamaError(f"Unexpected Ollama response format: {e}")


def parse_json_response(text: str) -> dict:
    """Parse a JSON response from Ollama, stripping markdown fences if present."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise OllamaError(f"Model returned invalid JSON: {e}\nResponse: {text[:200]}")
