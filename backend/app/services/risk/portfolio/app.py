from fastapi import FastAPI, HTTPException, Header
from backend.app.services.risk.portfolio.schemas import PortfolioRequest
from backend.app.services.risk.portfolio.service import PortfolioService

app = FastAPI(title="RiskLens Portfolio API")

service = PortfolioService()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/risk/portfolio")
def run_portfolio(request: PortfolioRequest):
    try:
        return service.run(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))