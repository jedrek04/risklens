from fastapi import FastAPI, HTTPException

from backend.app.services.risk.data_provider import load_price_data
from backend.app.services.risk.garch.schemas import GARCHRequest
from backend.app.services.risk.garch.service import GARCHService


app = FastAPI(
    title="RiskLens GARCH API"
)


@app.get("/health")
def health():

    return {
        "status": "ok"
    }


@app.post("/risk/garch")
def run_garch(request: GARCHRequest):

    try:

        service = GARCHService()

        results = []

        for asset in request.portfolio:

            df = load_price_data(
                ticker=asset.ticker,
                days=request.days
            )

            result = service.run(
                df=df,
                ticker=asset.ticker,
                horizon=request.horizon
            )

            result["weight"] = asset.weight

            results.append(result)

        return {
            "portfolio": results
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )