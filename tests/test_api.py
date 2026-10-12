import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.routers import risk
from tests.conftest import make_prices

client = TestClient(app)

PAYLOAD = {
    "portfolio": [{"ticker": "AAA", "weight": 0.6}, {"ticker": "BBB", "weight": 0.4}],
    "days": 365,
    "horizon": 5,
}


@pytest.fixture(autouse=True)
def fake_bigquery(monkeypatch):
    def fake_load(ticker, days):
        if ticker == "NOPE":
            raise ValueError("No data for ticker=NOPE")
        return make_prices(seed=sum(map(ord, ticker)))

    monkeypatch.setattr(risk, "load_price_data", fake_load)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_garch_ok():
    r = client.post("/risk/garch", json=PAYLOAD)
    assert r.status_code == 200
    body = r.json()["portfolio"]
    assert [a["ticker"] for a in body] == ["AAA", "BBB"]
    assert [a["weight"] for a in body] == [0.6, 0.4]
    assert len(body[0]["volatility"]["forecast"]) == 5


def test_unknown_ticker_is_400():
    payload = {**PAYLOAD, "portfolio": [{"ticker": "NOPE", "weight": 1.0}]}
    r = client.post("/risk/garch", json=payload)
    assert r.status_code == 400
    assert "NOPE" in r.json()["detail"]


@pytest.mark.parametrize(
    "bad",
    [
        {"portfolio": [{"ticker": "AAA", "weight": 0.5}]},
        {"portfolio": []},
        {"portfolio": [{"ticker": "AAA", "weight": 1.0}], "horizon": 0},
        {"portfolio": [{"ticker": "AAA", "weight": 1.0}], "days": 10},
    ],
)
def test_invalid_requests_are_422(bad):
    assert client.post("/risk/garch", json=bad).status_code == 422
