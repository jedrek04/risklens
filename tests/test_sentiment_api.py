import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.routers.sentiment import get_sentiment_service
from backend.app.services.sentiment.service import SentimentService
from tests.helpers import NOW, FakeNews, FakeScorer, apple_articles, new_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def fake_service():
    service = SentimentService(FakeNews([apple_articles(10)]), new_store(), FakeScorer(), now=lambda: NOW)
    app.dependency_overrides[get_sentiment_service] = lambda: service
    yield
    app.dependency_overrides.clear()


def test_sentiment_ok():
    r = client.post("/risk/sentiment", json={"portfolio": [{"ticker": "AAPL", "weight": 1.0}]})

    assert r.status_code == 200
    body = r.json()
    assert body["meta"]["window_days"] == 7 and body["meta"]["model"] == "ProsusAI/finbert"
    assert body["assets"][0]["ticker"] == "AAPL" and body["assets"][0]["status"] == "ok"


def test_unknown_ticker_is_400():
    r = client.post("/risk/sentiment", json={"portfolio": [{"ticker": "NOPE123", "weight": 1.0}]})

    assert r.status_code == 400


def test_bad_weights_are_422():
    r = client.post("/risk/sentiment", json={"portfolio": [{"ticker": "AAPL", "weight": 0.5}]})

    assert r.status_code == 422
