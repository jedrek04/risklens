from datetime import timedelta

import pytest

from backend.app.services.sentiment.gnews import NewsUnavailable
from backend.app.services.sentiment.service import SentimentService
from tests.helpers import NOW, FakeNews, FakeScorer, apple_articles, article, new_store


def service(pages, store=None, scorer=None, now=NOW):
    store = store or new_store()
    scorer = scorer or FakeScorer()
    news = FakeNews(pages)
    return SentimentService(news, store, scorer, now=lambda: now), news, store, scorer


def test_scores_and_aggregates():
    s, _, _, _ = service([apple_articles(7, "rises") + apple_articles(3, "falls")])

    out = s.analyze(["AAPL"])["assets"][0]

    assert out["headlines"] == 10
    assert out["status"] == "ok"
    assert out["score"] == pytest.approx(0.7 * 0.7 + 0.3 * -0.7)
    assert out["label"] == "positive"
    assert out["share"]["positive"] == pytest.approx(0.7)
    assert len(out["top_positive"]) == 3 and len(out["top_negative"]) == 3


def test_low_confidence_below_minimum():
    s, _, _, _ = service([apple_articles(4)])

    out = s.analyze(["AAPL"])["assets"][0]

    assert out["status"] == "low_confidence"
    assert out["score"] is not None
    assert "below the 10" in out["message"]


def test_irrelevant_articles_are_filtered_before_scoring():
    pages = [[article("Apple pie recipe for autumn"), article("Apple stock rises on strong sales")]]
    s, _, _, scorer = service(pages)

    out = s.analyze(["AAPL"])["assets"][0]

    assert out["headlines"] == 1
    assert scorer.scored == ["Apple stock rises on strong sales"]


def test_second_call_uses_cache():
    s, news, _, scorer = service([apple_articles(10)])

    s.analyze(["AAPL"])
    calls, scored = len(news.calls), len(scorer.scored)
    s.analyze(["AAPL"])

    assert len(news.calls) == calls and len(scorer.scored) == scored


def test_stale_cache_refetches_without_rescoring_known_headlines():
    store = new_store()
    s1, _, _, _ = service([apple_articles(10)], store=store)
    s1.analyze(["AAPL"])

    later = NOW + timedelta(hours=7)
    scorer = FakeScorer()
    s2, news2, _, _ = service([apple_articles(10) + apple_articles(2, "falls")], store=store, scorer=scorer, now=later)
    s2.analyze(["AAPL"])

    assert news2.calls
    assert len(scorer.scored) == 2


def test_second_page_only_when_needed():
    full = [apple_articles(10, "rises"), apple_articles(10, "falls")]
    s, news, _, _ = service([full[0]] + [full[1]])
    s.analyze(["AAPL"])
    assert [c[1] for c in news.calls] == [1]

    sparse = [apple_articles(10, "x")[:5] + [article("Unrelated pasta news")] * 5, apple_articles(10, "y")]
    s, news, _, _ = service(sparse)
    s.analyze(["AAPL"])
    assert [c[1] for c in news.calls] == [1, 2]


def test_stops_when_provider_has_no_more_articles():
    s, news, _, _ = service([apple_articles(3)])

    s.analyze(["AAPL"])

    assert [c[1] for c in news.calls] == [1]


def test_window_ignores_old_headlines():
    old = [article("Apple stock rises long ago", url="old", days_ago=20)]
    s, _, _, _ = service([old + apple_articles(2)])

    assert s.analyze(["AAPL"])["assets"][0]["headlines"] == 2


def test_unavailable_without_cache():
    s, news, _, _ = service([[]])
    news.search = lambda *a, **k: (_ for _ in ()).throw(NewsUnavailable("quota used up"))

    out = s.analyze(["AAPL"])["assets"][0]

    assert out["status"] == "unavailable" and out["score"] is None
    assert "quota used up" in out["message"]


def test_provider_failure_still_serves_cached_headlines():
    store = new_store()
    s1, _, _, _ = service([apple_articles(10)], store=store)
    s1.analyze(["AAPL"])

    later = NOW + timedelta(hours=7)
    s2, news2, _, _ = service([[]], store=store, now=later)
    news2.search = lambda *a, **k: (_ for _ in ()).throw(NewsUnavailable("quota used up"))
    out = s2.analyze(["AAPL"])["assets"][0]

    assert out["headlines"] == 10 and out["status"] == "ok"
    assert "quota" in out["message"]


def test_no_relevant_news_message():
    s, _, _, _ = service([[article("Pasta news")]])

    out = s.analyze(["AAPL"])["assets"][0]

    assert out["status"] == "unavailable"
    assert "No relevant news" in out["message"]


def test_unknown_ticker():
    s, _, _, _ = service([[]])

    with pytest.raises(ValueError):
        s.analyze(["NOPE123"])


def test_store_is_queried_once_per_request_not_per_asset():
    store = new_store()
    calls = {"last": 0, "rows": 0}
    original_last, original_rows = store.last_fetches, store.headlines_for
    store.last_fetches = lambda t: (calls.__setitem__("last", calls["last"] + 1), original_last(t))[1]
    store.headlines_for = lambda t, s: (calls.__setitem__("rows", calls["rows"] + 1), original_rows(t, s))[1]
    s, _, _, _ = service([apple_articles(10)], store=store)

    s.analyze(["AAPL", "GC=F", "BTC-USD"])

    assert calls == {"last": 1, "rows": 1}


def test_message_uses_singular_for_one_headline():
    s, _, _, _ = service([apple_articles(1)])

    assert "Only 1 relevant headline," in s.analyze(["AAPL"])["assets"][0]["message"]
