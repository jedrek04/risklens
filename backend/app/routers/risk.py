import logging

from fastapi import APIRouter, HTTPException

from backend.app.schemas import PortfolioRequest
from backend.app.services.risk import garch
from backend.app.services.risk.data_provider import load_price_data

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/risk", tags=["risk"])


@router.post("/garch")
def run_garch(request: PortfolioRequest):
    try:
        results = []

        for asset in request.portfolio:
            df = load_price_data(ticker=asset.ticker, days=request.days)
            result = garch.analyze(df, ticker=asset.ticker, horizon=request.horizon)
            result["weight"] = asset.weight
            results.append(result)

        return {"portfolio": results}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        logger.exception("GARCH request failed")
        raise HTTPException(status_code=500, detail="Internal server error")
