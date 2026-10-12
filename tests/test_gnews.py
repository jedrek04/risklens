from datetime import datetime, timezone

import httpx
import pytest

from backend.app.services.sentiment.gnews import GNewsClient, NewsUnavailable

SINCE = datetime(2026, 10, 5, tzinfo=timezone.utc)
BODY = {
    "totalArticles": 1,
    "articles": [{
        "title": "Apple stock rises",
        "description": None,
        "url": "https://x.com/a",
        "publishedAt": "2026-10-11T05:33:39Z",
        "source": {"name": "Reuters"},
    }],
}


class Clock:
    def __init__(self):
        self.t = 0.0
        self.sleeps = []

    def now(self):
        return self.t

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += s


def client(handler, key="k"):
    clock = Clock()
    http = httpx.Client(transport=httpx.MockTransport(handler))
    return GNewsClient(api_key=key, http=http, sleep=clock.sleep, clock=clock.now), clock


def test_parses_articles_and_sends_params():
    seen = {}

    def handler(request):
        seen.update(dict(request.url.params))
        return httpx.Response(200, json=BODY)

    c, _ = client(handler)
    page = c.search("Apple", SINCE, page=2)

    assert page.total == 1
    assert page.articles[0]["description"] == ""
    assert page.articles[0]["published_at"].tzinfo is not None
    assert seen["page"] == "2" and seen["lang"] == "en" and seen["from"] == "2026-10-05T00:00:00Z"


def test_retries_after_rate_limit():
    responses = [httpx.Response(429), httpx.Response(200, json=BODY)]
    c, clock = client(lambda r: responses.pop(0))

    assert len(c.search("Apple", SINCE).articles) == 1
    assert 3 in clock.sleeps


def test_gives_up_after_repeated_rate_limit():
    c, _ = client(lambda r: httpx.Response(429))

    with pytest.raises(NewsUnavailable):
        c.search("Apple", SINCE)


def test_forbidden_means_unavailable():
    c, _ = client(lambda r: httpx.Response(403))

    with pytest.raises(NewsUnavailable, match="quota"):
        c.search("Apple", SINCE)


def test_missing_key():
    c, _ = client(lambda r: httpx.Response(200, json=BODY), key=None)

    with pytest.raises(NewsUnavailable, match="not configured"):
        c.search("Apple", SINCE)


def test_calls_are_spaced_out():
    c, clock = client(lambda r: httpx.Response(200, json=BODY))

    c.search("a", SINCE)
    c.search("b", SINCE)

    assert clock.sleeps and clock.sleeps[0] > 1.0
