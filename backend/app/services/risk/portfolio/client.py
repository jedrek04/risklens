import os
import httpx


class GARCHClient:
    def __init__(self):
        self.base_url = os.getenv(
            "GARCH_URL",
            "https://risklens-garch-935079797801.europe-west1.run.app"
        )

        self.timeout = 30.0

    def run_garch(self, ticker: str, weight: float, days: int, horizon: int, token: str):
        url = f"{self.base_url}/risk/garch"

        payload = {
            "portfolio": [
                {
                    "ticker": ticker,
                    "weight": 1.0
                }
            ],
            "days": days,
            "horizon": horizon
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        with httpx.Client(timeout=self.timeout) as client:
            r = client.post(url, json=payload, headers=headers)

        r.raise_for_status()
        data = r.json()

        data["weight"] = weight

        return data