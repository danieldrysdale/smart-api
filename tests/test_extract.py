"""Tests for the /extract endpoint."""

import pytest
from tests.conftest import mock_ollama


class TestExtract:
    async def test_extracts_entities(self, client):
        with mock_ollama({"entities": [
            {"type": "invoice_number", "value": "1234", "context": "Invoice #1234"},
            {"type": "organisation", "value": "Acme Corp", "context": None},
            {"type": "amount", "value": "$4,500", "context": "total $4,500"},
            {"type": "date", "value": "15 May 2026", "context": "due 15 May 2026"},
        ]}):
            resp = await client.post("/extract", json={
                "text": "Invoice #1234 from Acme Corp, due 15 May 2026, total $4,500"
            })
        assert resp.status_code == 200
        data = resp.json()
        assert data["entity_count"] == 4
        types = {e["type"] for e in data["entities"]}
        assert "invoice_number" in types
        assert "organisation" in types

    async def test_filtered_entity_types(self, client):
        with mock_ollama({"entities": [
            {"type": "email", "value": "billing@acme.com", "context": None},
        ]}):
            resp = await client.post("/extract", json={
                "text": "Contact billing@acme.com for invoices",
                "entity_types": ["email"],
            })
        assert resp.status_code == 200
        assert resp.json()["entity_count"] == 1
        assert resp.json()["entities"][0]["type"] == "email"

    async def test_no_entities_found(self, client):
        with mock_ollama({"entities": []}):
            resp = await client.post("/extract", json={"text": "Nothing to extract here."})
        assert resp.status_code == 200
        assert resp.json()["entity_count"] == 0
        assert resp.json()["entities"] == []

    async def test_malformed_entity_skipped(self, client):
        with mock_ollama({"entities": [
            {"type": "person", "value": "Dan"},
            {"bad_key": "no type or value"},
        ]}):
            resp = await client.post("/extract", json={"text": "Dan sent an email."})
        assert resp.status_code == 200
        assert resp.json()["entity_count"] == 1

    async def test_empty_text_rejected(self, client):
        resp = await client.post("/extract", json={"text": ""})
        assert resp.status_code == 422


class TestHealth:
    async def test_health_returns_200(self, client):
        from unittest.mock import AsyncMock, patch, MagicMock
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        with patch("smart_api.main.httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client.return_value)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value.get = AsyncMock(return_value=mock_resp)
            resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert "ollama_reachable" in data
        assert "model" in data

    async def test_health_degraded_when_ollama_down(self, client):
        import httpx
        from unittest.mock import AsyncMock, patch
        with patch("smart_api.main.httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client.return_value)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value.get = AsyncMock(side_effect=httpx.ConnectError("down"))
            resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["ollama_reachable"] is False
        assert data["status"] == "degraded"
