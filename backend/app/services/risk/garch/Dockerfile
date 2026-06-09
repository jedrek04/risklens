FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend backend

ENV PYTHONPATH=/app

CMD ["uvicorn", "backend.app.services.risk.garch.app:app", "--host", "0.0.0.0", "--port", "8080"]