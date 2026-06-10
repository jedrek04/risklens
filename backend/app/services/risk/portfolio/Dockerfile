FROM python:3.12-slim

WORKDIR /app

COPY backend /app/backend
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

CMD ["uvicorn", "backend.app.services.risk.portfolio.app:app", "--host", "0.0.0.0", "--port", "8080"]