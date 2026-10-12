import logging

from fastapi import APIRouter, HTTPException

from backend.app.schemas import AnomalyRequest, PortfolioRequest
from backend.app.services.risk import anomalies, portfolio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/risk", tags=["risk"])


@router.post("/portfolio")
def run_portfolio(request: PortfolioRequest):
    try:
        return portfolio.run(request)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        logger.exception("portfolio risk request failed")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/anomalies")
def run_anomalies(request: AnomalyRequest):
    try:
        return anomalies.run(request)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        logger.exception("anomaly request failed")
        raise HTTPException(status_code=500, detail="Internal server error")
