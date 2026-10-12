import logging
from functools import cache

from fastapi import APIRouter, Depends, HTTPException

from backend.app.services.report.payload import ReportRequest
from backend.app.services.report.service import ReportError, ReportService
from backend.app.services.report.writer import GeminiWriter

logger = logging.getLogger(__name__)

router = APIRouter(tags=["report"])


@cache
def get_report_service() -> ReportService:
    return ReportService(GeminiWriter())


@router.post("/risk/report")
def create_report(request: ReportRequest, service: ReportService = Depends(get_report_service)):
    try:
        return service.generate(request)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except ReportError as e:
        logger.error("report could not be generated: %s", e)
        raise HTTPException(status_code=502, detail="The report could not be generated right now. Please try again.")

    except Exception:
        logger.exception("report request failed")
        raise HTTPException(status_code=500, detail="Internal server error")
