from fastapi import FastAPI

from backend.app.routers import risk

app = FastAPI(title="RiskLens API")
app.include_router(risk.router)


@app.get("/health")
def health():
    return {"status": "ok"}
