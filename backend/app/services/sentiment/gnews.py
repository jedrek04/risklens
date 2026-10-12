import time
from dataclasses import dataclass
from datetime import datetime, timezone

import httpx

from backend.app.config import GNEWS_API_KEY

URL = "https://gnews.io/api/v4/search"
PAGE_SIZE = 10
MIN_INTERVAL = 1.3
RETRIES = 3


class NewsUnavailable(Exception):
    pass


@dataclass
class Page:
    total: int
    articles: list[dict]


def _parse(raw: dict) -> dict:
    return {
        "title": raw["title"],
        "description": raw.get("description") or "",
        "url": raw["url"],
        "source": raw["source"]["name"],
        "published_at": datetime.fromisoformat(raw["publishedAt"].replace("Z", "+00:00")),
    }


class GNewsClient:
    def __init__(self, api_key=GNEWS_API_KEY, http=None, sleep=time.sleep, clock=time.monotonic):
        self.api_key = api_key
        self.http = http or httpx.Client(timeout=30)
        self.sleep = sleep
        self.clock = clock
        self._last_call = None

    def _wait(self):
        if self._last_call is not None:
            remaining = MIN_INTERVAL - (self.clock() - self._last_call)
            if remaining > 0:
                self.sleep(remaining)
        self._last_call = self.clock()

    def search(self, query: str, since: datetime, page: int = 1) -> Page:
        if not self.api_key:
            raise NewsUnavailable("GNEWS_API_KEY is not configured")

        params = {
            "q": query,
            "lang": "en",
            "max": PAGE_SIZE,
            "page": page,
            "sortby": "publishedAt",
            "from": since.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "apikey": self.api_key,
        }

        for attempt in range(RETRIES):
            self._wait()
            response = self.http.get(URL, params=params)

            if response.status_code == 429 and attempt < RETRIES - 1:
                self.sleep(3 * (attempt + 1))
                continue

            if response.status_code in (401, 403, 429):
                raise NewsUnavailable(f"news provider refused the request (HTTP {response.status_code}), daily quota may be used up")

            response.raise_for_status()
            data = response.json()
            return Page(data.get("totalArticles", 0), [_parse(a) for a in data.get("articles", [])])

        raise NewsUnavailable("news provider rate limit")
