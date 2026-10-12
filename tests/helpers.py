from datetime import datetime, timedelta, timezone

from backend.app.services.sentiment.gnews import Page
from backend.app.services.sentiment.store import MemoryStore

NOW = datetime(2026, 10, 12, 12, 0, tzinfo=timezone.utc)


def article(title, description="", url=None, source="Reuters", days_ago=1.0):
    return {
        "title": title,
        "description": description,
        "url": url or f"https://example.com/{abs(hash(title))}",
        "source": source,
        "published_at": NOW - timedelta(days=days_ago),
    }


class FakeNews:
    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def search(self, query, since, page=1):
        self.calls.append((query, page))
        articles = self.pages[page - 1] if page <= len(self.pages) else []
        total = sum(len(p) for p in self.pages)
        return Page(total, articles)


class FakeScorer:
    def __init__(self):
        self.scored = []

    def score(self, texts):
        self.scored.extend(texts)
        out = []
        for t in texts:
            if "rises" in t:
                out.append({"positive": 0.8, "negative": 0.1, "neutral": 0.1})
            elif "falls" in t:
                out.append({"positive": 0.1, "negative": 0.8, "neutral": 0.1})
            else:
                out.append({"positive": 0.1, "negative": 0.1, "neutral": 0.8})
        return out


def apple_articles(n, prefix="rises"):
    return [
        article(f"Apple stock {prefix} {i}", url=f"https://example.com/aapl/{prefix}/{i}")
        for i in range(n)
    ]


def new_store():
    return MemoryStore()
