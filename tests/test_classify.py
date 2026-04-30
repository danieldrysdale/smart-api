"""Tests for the /classify endpoint."""

import pytest
from tests.conftest import mock_ollama


class TestClassify:
    async def test_classifies_complaint(self, client):
        with mock_ollama({"category": "complaint", "confidence": "high", "reasoning": "Expresses dissatisfaction."}):
            resp = await client.post("/classify", json={"text": "I've been waiting 3 weeks and no delivery!"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["category"] == "complaint"
        assert data["confidence"] == "high"
        assert "reasoning" in data
        assert data["input_length"] > 0

    async def test_classifies_enquiry(self, client):
        with mock_ollama({"category": "enquiry", "confidence": "high", "reasoning": "Asking a question."}):
            resp = await client.post("/classify", json={"text": "What are your opening hours?"})
        assert resp.status_code == 200
        assert resp.json()["category"] == "enquiry"

    async def test_custom_categories(self, client):
        with mock_ollama({"category": "urgent", "confidence": "high", "reasoning": "Time sensitive."}):
            resp = await client.post("/classify", json={
                "text": "Need help NOW",
                "categories": ["urgent", "normal", "low_priority"],
            })
        assert resp.status_code == 200
        assert resp.json()["category"] == "urgent"

    async def test_invalid_category_falls_back_to_other(self, client):
        with mock_ollama({"category": "made_up_category", "confidence": "high", "reasoning": "Something."}):
            resp = await client.post("/classify", json={"text": "Some text here"})
        assert resp.status_code == 200
        assert resp.json()["category"] == "other"

    async def test_empty_text_rejected(self, client):
        resp = await client.post("/classify", json={"text": ""})
        assert resp.status_code == 422

    async def test_confidence_medium_default_on_invalid(self, client):
        with mock_ollama({"category": "complaint", "confidence": "very_sure", "reasoning": "Test."}):
            resp = await client.post("/classify", json={"text": "I am unhappy with my order."})
        assert resp.status_code == 200
        assert resp.json()["confidence"] == "medium"
