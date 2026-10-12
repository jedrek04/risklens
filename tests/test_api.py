import pandas as pd
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.risk import portfolio
from tests.conftest import make_prices

client = TestClient(app)

PAYLOAD = {
    "portfolio": [{"ticker": "AAA", "weight": 0.6}, {"ticker": "BBB", "weight": 0.4}],
    "days": 365,
    "horizon": 5,
    "n_sim": 2000,
}


@pytest.fixture(autouse=True)
def fake_bigquery(monkeypatch):
    def fake_load(tickers, days):
        if "NOPE" in tickers:
            raise ValueError("No data for ticker(s): NOPE")
        return pd.concat(
            [make_prices(seed=sum(map(ord, t)), ticker=t) for t in tickers], ignore_index=True
        )

    monkeypatch.setattr(portfolio, "load_prices", fake_load)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_portfolio_ok():
    r = client.post("/risk/portfolio", json=PAYLOAD)

    assert r.status_code == 200
    body = r.json()
    assert [a["ticker"] for a in body["assets"]] == ["AAA", "BBB"]
    assert body["portfolio"]["cvar"] > body["portfolio"]["var"] > 0
    assert len(body["portfolio"]["fan_chart"]["day"]) == 5
    assert len(body["assets"][0]["volatility"]["forecast"]) == 5
    assert body["correlation"]["tickers"] == ["AAA", "BBB"]
    assert body["meta"]["confidence"] == 0.95


def test_single_asset_portfolio():
    payload = {**PAYLOAD, "portfolio": [{"ticker": "AAA", "weight": 1.0}]}

    assert client.post("/risk/portfolio", json=payload).status_code == 200


def test_unknown_ticker_is_400():
    payload = {**PAYLOAD, "portfolio": [{"ticker": "NOPE", "weight": 1.0}]}

    r = client.post("/risk/portfolio", json=payload)

    assert r.status_code == 400
    assert "NOPE" in r.json()["detail"]


def test_too_little_overlap_is_400(monkeypatch):
    monkeypatch.setattr(
        portfolio, "load_prices", lambda tickers, days: make_prices(n=60, ticker=tickers[0])
    )
    payload = {**PAYLOAD, "portfolio": [{"ticker": "AAA", "weight": 1.0}]}

    r = client.post("/risk/portfolio", json=payload)

    assert r.status_code == 400
    assert "common trading days" in r.json()["detail"]


@pytest.mark.parametrize(
    "bad",
    [
        {"portfolio": [{"ticker": "AAA", "weight": 0.5}]},
        {"portfolio": []},
        {"portfolio": [{"ticker": "AAA", "weight": 0.5}, {"ticker": "AAA", "weight": 0.5}]},
        {"portfolio": [{"ticker": "AAA", "weight": 1.0}], "horizon": 0},
        {"portfolio": [{"ticker": "AAA", "weight": 1.0}], "days": 10},
        {"portfolio": [{"ticker": "AAA", "weight": 1.0}], "n_sim": 5},
    ],
)
def test_invalid_requests_are_422(bad):
    assert client.post("/risk/portfolio", json=bad).status_code == 422


def test_anomalies_ok(monkeypatch):
    from backend.app.services.risk import anomalies

    monkeypatch.setattr(
        anomalies, "load_prices",
        lambda tickers, days: pd.concat(
            [make_prices(n=1000, seed=sum(map(ord, t)), ticker=t) for t in tickers], ignore_index=True
        ),
    )
    payload = {"portfolio": [{"ticker": "AAA", "weight": 0.6}, {"ticker": "BBB", "weight": 0.4}], "days": 200}

    r = client.post("/risk/anomalies", json=payload)

    assert r.status_code == 200
    body = r.json()
    assert [a["name"] for a in body["assets"]] == ["AAA", "BBB"]
    assert body["portfolio"]["name"] == "portfolio"
    assert body["portfolio"]["summary"]["scored_days"] > 100


def test_anomalies_short_history_is_400(monkeypatch):
    from backend.app.services.risk import anomalies

    monkeypatch.setattr(
        anomalies, "load_prices", lambda tickers, days: make_prices(n=150, ticker=tickers[0])
    )
    payload = {"portfolio": [{"ticker": "AAA", "weight": 1.0}]}

    r = client.post("/risk/anomalies", json=payload)

    assert r.status_code == 400
    assert "Not enough price history" in r.json()["detail"]
