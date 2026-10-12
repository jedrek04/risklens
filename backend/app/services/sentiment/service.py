from datetime import datetime, timedelta, timezone

from backend.app.services.sentiment.assets import build_asset
from backend.app.services.sentiment.filters import dedupe, is_relevant
from backend.app.services.sentiment.gnews import PAGE_SIZE, NewsUnavailable
from backend.app.services.sentiment.finbert import MODEL

WINDOW_DAYS = 7
MIN_HEADLINES = 10
CACHE_TTL = timedelta(hours=6)
MAX_PAGES = 2
LABEL_THRESHOLD = 0.1
TOP_N = 3


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _label(score: float) -> str:
    if score > LABEL_THRESHOLD:
        return "positive"
    if score < -LABEL_THRESHOLD:
        return "negative"
    return "neutral"


def _headline(row: dict) -> dict:
    return {
        "title": row["title"],
        "source": row["source"],
        "url": row["url"],
        "published_at": row["published_at"].isoformat(),
        "score": row["positive"] - row["negative"],
    }


def summarize(ticker: str, name: str, rows: list[dict], note: str | None = None) -> dict:
    if not rows:
        return {
            "ticker": ticker,
            "name": name,
            "status": "unavailable",
            "score": None,
            "label": None,
            "headlines": 0,
            "message": note or "No relevant news found for this asset in the last 7 days",
        }

    scored = sorted((_headline(r) for r in rows), key=lambda h: h["score"])
    score = sum(h["score"] for h in scored) / len(scored)
    counts = {"positive": 0, "neutral": 0, "negative": 0}
    for r in rows:
        counts[max(("positive", "negative", "neutral"), key=lambda k: r[k])] += 1

    low = len(rows) < MIN_HEADLINES
    message = (
        f"Only {len(rows)} relevant {'headline' if len(rows) == 1 else 'headlines'}, "
        f"below the {MIN_HEADLINES} needed for a reliable score"
        if low else None
    )

    return {
        "ticker": ticker,
        "name": name,
        "status": "low_confidence" if low else "ok",
        "score": score,
        "label": _label(score),
        "headlines": len(rows),
        "share": {k: v / len(rows) for k, v in counts.items()},
        "top_positive": [h for h in reversed(scored[-TOP_N:]) if h["score"] > 0],
        "top_negative": [h for h in scored[:TOP_N] if h["score"] < 0],
        "message": note or message,
    }


class SentimentService:
    def __init__(self, news, store, scorer, now=utc_now):
        self.news = news
        self.store = store
        self.scorer = scorer
        self.now = now

    def analyze(self, tickers: list[str]) -> dict:
        now = self.now()
        since = now - timedelta(days=WINDOW_DAYS)
        assets = [build_asset(t) for t in tickers]
        last_fetches = self.store.last_fetches(tickers)
        cached = self.store.headlines_for(tickers, since)
        results = []

        for asset in assets:
            rows = list(cached.get(asset.ticker, []))
            note = None
            try:
                rows += self._refresh(asset, now, since, last_fetches.get(asset.ticker), rows)
            except NewsUnavailable as e:
                note = str(e)

            results.append(summarize(asset.ticker, asset.name, rows, note))

        return {
            "meta": {
                "window_days": WINDOW_DAYS,
                "min_headlines": MIN_HEADLINES,
                "model": MODEL,
                "news_source": "gnews.io",
                "generated_at": now.isoformat(),
            },
            "assets": results,
        }

    def _refresh(self, asset, now: datetime, since: datetime, last, cached_rows: list[dict]) -> list[dict]:
        if last is not None and now - last < CACHE_TTL:
            return []

        kept, raw = [], 0
        for page in range(1, MAX_PAGES + 1):
            result = self.news.search(asset.query, since, page)
            raw += len(result.articles)
            kept = dedupe(kept + [a for a in result.articles if is_relevant(a, asset)])
            exhausted = len(result.articles) < PAGE_SIZE or page * PAGE_SIZE >= result.total
            if len(kept) >= MIN_HEADLINES or exhausted:
                break

        known = {r["url"] for r in cached_rows}
        new = [a for a in kept if a["url"] not in known and a["published_at"] >= since]
        scores = self.scorer.score([a["title"] for a in new])

        rows = [
            {
                "ticker": asset.ticker,
                "url": a["url"],
                "title": a["title"],
                "source": a["source"],
                "published_at": a["published_at"],
                "positive": s["positive"],
                "negative": s["negative"],
                "neutral": s["neutral"],
                "fetched_at": now,
            }
            for a, s in zip(new, scores)
        ]
        self.store.save_headlines(rows)
        self.store.save_fetch(asset.ticker, now, raw, len(kept))
        return rows
