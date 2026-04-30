"""Shared pytest fixtures."""

from __future__ import annotations

import json
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

from smart_api.main import app


@pytest.fixture
async def client():
    """Async test client for the FastAPI app."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


def mock_ollama(response: dict):
    """Patch smart_api.ollama.chat to return a canned JSON response."""
    return patch(
        "smart_api.services.chat",
        new=AsyncMock(return_value=json.dumps(response)),
    )
