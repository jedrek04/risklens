# RiskLens

Portfolio risk platform: market data pipeline + risk API on GCP.

Project `risklens-498721`, region `europe-west1`. Run everything from the repo root with the venv active
(`pip install -r requirements-dev.txt`).

## Layout

- `backend/app/main.py` – FastAPI app (`/health`, `/risk/garch`); routes live in `routers/`, models in `services/`
- `backend/app/services/market_data/` – ticker universe (`tickers.py`) and yfinance fetcher
- `backend/app/services/risk/` – BigQuery price reader and GARCH volatility
- `backend/app/pipeline/` – Cloud Run Job `market-data-load`: fetch -> BigQuery staging -> MERGE into
  `market_data.market_prices_raw`. Runs nightly at 01:00 (Cloud Scheduler, `--days 730`)
- `tests/` – pytest, no GCP needed
- `frontend/` – not started

## Commands

    pytest                                         # unit + API tests
    uvicorn backend.app.main:app --reload          # run API locally (uses your gcloud credentials)
    python -m backend.app.pipeline.quality         # data-quality report on the BigQuery table
    python deploy.py api                           # build + deploy Cloud Run service risklens-api
    python deploy.py pipeline                      # build + update Cloud Run Job market-data-load

Manual backfill: `gcloud run jobs execute market-data-load --region europe-west1 --args="--days,3700"`

## Try the API

    curl -X POST "$API_URL/risk/garch" \
      -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
      -H "Content-Type: application/json" \
      -d '{"portfolio": [{"ticker": "SPY", "weight": 0.6}, {"ticker": "BTC-USD", "weight": 0.4}], "days": 365, "horizon": 10}'
