# RiskLens

Portfolio risk platform: market data pipeline + risk API on GCP.

Project `risklens-498721`, region `europe-west1`. Run everything from the repo root with the venv active
(`pip install -r requirements.txt -r requirements-pipeline.txt pytest`). `GNEWS_API_KEY` goes in `.env` locally and in Secret Manager (`gnews-api-key`) in the cloud.

## Layout

- `backend/app/main.py` – FastAPI app (`/health`, `/risk/portfolio`, `/risk/anomalies`, `/risk/sentiment`, `/risk/report`); routes live in `routers/`, models in `services/`
- `backend/app/services/market_data/` – ticker universe (`tickers.py`) and yfinance fetcher
- `backend/app/services/risk/` – price loading, return alignment, GARCH volatility, Monte Carlo VaR/CVaR, Isolation Forest anomalies
- `backend/app/services/sentiment/` – GNews client, relevance filters, FinBERT scoring, BigQuery cache (`news_headlines`, `news_fetches`)
- `backend/app/services/report/` – fact sheet, Gemini (Vertex AI) writer, number verification, request validation. `/risk/report` takes the portfolio plus the results the page already has (risk, anomalies, sentiment)
- `backend/app/pipeline/` – Cloud Run Job `market-data-load`: fetch -> BigQuery staging -> MERGE into
  `market_data.market_prices_raw`. Runs nightly at 01:00 (Cloud Scheduler, `--days 730`)
- `tests/` – pytest, no GCP needed
- `frontend/` – React app (Build screen done, see `frontend/README.md`)

## Commands

    pytest                                         # unit + API tests (fast, no cloud)
    pytest -m slow                                 # also runs the real FinBERT model
    uvicorn backend.app.main:app --reload          # run API locally (uses your gcloud credentials)
    python -m backend.app.pipeline.quality         # data-quality report on the BigQuery table
    python deploy.py api                           # build + deploy Cloud Run service risklens-api
    python deploy.py pipeline                      # build + update Cloud Run Job market-data-load

Manual backfill: `gcloud run jobs execute market-data-load --region europe-west1 --args="--days,3700"`

## Try the API

    curl -X POST "$API_URL/risk/portfolio" \
      -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
      -H "Content-Type: application/json" \
      -d '{"portfolio": [{"ticker": "SPY", "weight": 0.6}, {"ticker": "BTC-USD", "weight": 0.4}], "days": 365, "horizon": 10, "n_sim": 10000}'
