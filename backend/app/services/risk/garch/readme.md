curl -X POST "https://risklens-garch-935079797801.europe-west1.run.app/risk/garch" \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio": [
      {"ticker": "SPY", "weight": 0.25},
      {"ticker": "QQQ", "weight": 0.25},
      {"ticker": "CSCO", "weight": 0.25},
      {"ticker": "GLD", "weight": 0.15},
      {"ticker": "BTC-USD", "weight": 0.10}
    ],
    "days": 365,
    "horizon": 10
  }'