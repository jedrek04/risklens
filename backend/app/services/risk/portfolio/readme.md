❯ curl -s -X POST "https://risklens-portfolio-935079797801.europe-west1.run.app/risk/portfolio" \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio": [
      {"ticker": "SPY", "weight": 0.3},
      {"ticker": "QQQ", "weight": 0.3},
      {"ticker": "CSCO", "weight": 0.2},
      {"ticker": "GLD", "weight": 0.2}
    ],
    "days": 365,
    "horizon": 10
  }'