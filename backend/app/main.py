from fastapi import FastAPI

from backend.app.routers import report, risk, sentiment

app = FastAPI(title="RiskLens API")
app.include_router(risk.router)
app.include_router(sentiment.router)
app.include_router(report.router)


@app.get("/health")
def health():
    return {"status": "ok"}
