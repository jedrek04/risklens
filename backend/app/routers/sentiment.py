import logging
from functools import cache

from fastapi import APIRouter, Depends, HTTPException

from backend.app.schemas import PortfolioInput
from backend.app.services.sentiment.finbert import FinBERTScorer
from backend.app.services.sentiment.gnews import GNewsClient
from backend.app.services.sentiment.service import SentimentService
from backend.app.services.sentiment.store import BigQueryStore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/risk", tags=["sentiment"])


@cache
def get_sentiment_service() -> SentimentService:
    return SentimentService(GNewsClient(), BigQueryStore(), FinBERTScorer())


@router.post("/sentiment")
def run_sentiment(request: PortfolioInput, service: SentimentService = Depends(get_sentiment_service)):
    try:
        return service.analyze([a.ticker for a in request.portfolio])

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        logger.exception("sentiment request failed")
        raise HTTPException(status_code=500, detail="Internal server error")
