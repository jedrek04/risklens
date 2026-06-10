import requests
import numpy as np
from typing import Dict, Any, List

from backend.app.services.risk.portfolio.schemas import PortfolioRequest
from backend.app.services.risk.data_provider import load_price_data

import google.auth.transport.requests
from google.oauth2 import id_token

GARCH_SERVICE_URL = "https://risklens-garch-935079797801.europe-west1.run.app"


class PortfolioService:

    def _clean_records(self, df):
        records = df.to_dict(orient="records")

        for r in records:
            for k, v in r.items():
                if hasattr(v, "isoformat"):
                    r[k] = v.isoformat()
                elif isinstance(v, (np.integer,)):
                    r[k] = int(v)
                elif isinstance(v, (np.floating,)):
                    r[k] = float(v)
                elif isinstance(v, (np.ndarray,)):
                    r[k] = v.tolist()
                else:
                    r[k] = v

        return records

    def _call_garch(self, payload: dict) -> dict:
        request = google.auth.transport.requests.Request()
        token = id_token.fetch_id_token(request, GARCH_SERVICE_URL)

        response = requests.post(
            f"{GARCH_SERVICE_URL}/risk/garch",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=60,
        )

        if response.status_code != 200:
            raise RuntimeError(f"GARCH service error: {response.text}")

        return response.json()

    def run(self, request: PortfolioRequest) -> Dict[str, Any]:

        results: List[dict] = []

        for asset in request.portfolio:
            df = load_price_data(
                ticker=asset.ticker,
                days=request.days
            )

            garch_payload = {
                "ticker": asset.ticker,
                "horizon": request.horizon,
                "prices": self._clean_records(df)
            }

            garch_result = self._call_garch(garch_payload)

            results.append({
                "ticker": asset.ticker,
                "weight": asset.weight,
                "garch": garch_result
            })

        return {
            "portfolio": results,
            "meta": {
                "days": request.days,
                "horizon": request.horizon
            }
        }