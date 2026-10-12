FROM python:3.12-slim

WORKDIR /app

ENV PYTHONPATH=/app \
    HF_HOME=/app/.hf \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt requirements-api.txt ./

RUN pip install $(grep '^torch==' requirements-api.txt) --index-url https://download.pytorch.org/whl/cpu
RUN pip install -r requirements.txt -r requirements-api.txt

RUN python -c "from transformers import AutoModelForSequenceClassification as M, AutoTokenizer as T; T.from_pretrained('ProsusAI/finbert'); M.from_pretrained('ProsusAI/finbert')"

COPY backend backend

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
