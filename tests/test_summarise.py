"""Tests for the /summarise endpoint."""

import pytest
from tests.conftest import mock_ollama

LONG_TEXT = "word " * 60  # 60 words, satisfies min_length=50


class TestSummarise:
    async def test_summarises_text(self, client):
        with mock_ollama({
            "summary": "A brief summary of the content.",
            "key_points": ["Point one", "Point two", "Point three"],
        }):
            resp = await client.post("/summarise", json={"text": LONG_TEXT})
        assert resp.status_code == 200
        data = resp.json()
        assert data["summary"] == "A brief summary of the content."
        assert len(data["key_points"]) == 3
        assert data["word_count_in"] == 60
        assert data["word_count_out"] > 0

    async def test_respects_max_points(self, client):
        with mock_ollama({
            "summary": "Summary.",
            "key_points": ["P1", "P2", "P3", "P4", "P5"],
        }):
            resp = await client.post("/summarise", json={"text": LONG_TEXT, "max_points": 3})
        assert resp.status_code == 200
        assert len(resp.json()["key_points"]) == 3

    async def test_text_too_short_rejected(self, client):
        resp = await client.post("/summarise", json={"text": "Too short."})
        assert resp.status_code == 422

    async def test_max_points_out_of_range_rejected(self, client):
        resp = await client.post("/summarise", json={"text": LONG_TEXT, "max_points": 11})
        assert resp.status_code == 422

    async def test_empty_key_points_handled(self, client):
        with mock_ollama({"summary": "Nothing here.", "key_points": []}):
            resp = await client.post("/summarise", json={"text": LONG_TEXT})
        assert resp.status_code == 200
        assert resp.json()["key_points"] == []
