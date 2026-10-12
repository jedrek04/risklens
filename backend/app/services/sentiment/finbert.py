import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODEL = "ProsusAI/finbert"
BATCH_SIZE = 32
MAX_LENGTH = 64


class FinBERTScorer:
    def __init__(self):
        self._tokenizer = None
        self._model = None

    def _load(self):
        if self._model is None:
            self._tokenizer = AutoTokenizer.from_pretrained(MODEL)
            self._model = AutoModelForSequenceClassification.from_pretrained(MODEL).eval()

    def score(self, texts: list[str]) -> list[dict]:
        if not texts:
            return []

        self._load()
        labels = {i: l.lower() for i, l in self._model.config.id2label.items()}
        out = []

        for start in range(0, len(texts), BATCH_SIZE):
            batch = texts[start:start + BATCH_SIZE]
            encoded = self._tokenizer(
                batch, padding=True, truncation=True, max_length=MAX_LENGTH, return_tensors="pt"
            )
            with torch.no_grad():
                probs = torch.softmax(self._model(**encoded).logits, dim=-1)

            for row in probs:
                out.append({labels[i]: float(p) for i, p in enumerate(row)})

        return out
