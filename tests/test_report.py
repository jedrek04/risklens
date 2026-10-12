import json
from types import SimpleNamespace

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.routers.report import get_report_service
from backend.app.schemas import AnomalyRequest, PortfolioRequest
from backend.app.services.report import verify
from backend.app.services.report.facts import build_facts
from backend.app.services.report.prompt import SYSTEM_PROMPT, ReportDraft, build_prompt
from backend.app.services.report.service import DISCLAIMER, ReportError, ReportService
from backend.app.services.report.writer import GeminiWriter, WriterError
from backend.app.services.risk import anomalies, portfolio
from backend.app.services.sentiment.service import SentimentService
from tests.conftest import make_prices
from tests.helpers import NOW, FakeNews, FakeScorer, apple_articles, new_store

REQUEST = PortfolioRequest(
    portfolio=[{"ticker": "AAPL", "weight": 0.6}, {"ticker": "GC=F", "weight": 0.4}],
    days=730,
    horizon=10,
    n_sim=2000,
)


@pytest.fixture(scope="module")
def outputs():
    def fake_prices(tickers, days):
        return pd.concat(
            [make_prices(n=900, seed=sum(map(ord, t)), ticker=t) for t in tickers], ignore_index=True
        )

    patch = pytest.MonkeyPatch()
    patch.setattr(portfolio, "load_prices", fake_prices)
    patch.setattr(anomalies, "load_prices", fake_prices)
    try:
        risk = portfolio.run(REQUEST, seed=1)
        anomaly = anomalies.run(AnomalyRequest(portfolio=REQUEST.portfolio, days=200))
        sentiment = SentimentService(
            FakeNews([apple_articles(10)]), new_store(), FakeScorer(), now=lambda: NOW
        ).analyze(["AAPL", "GC=F"])
    finally:
        patch.undo()
    return risk, anomaly, sentiment


@pytest.fixture
def facts(outputs):
    return build_facts(*outputs[:3], reasons={})


def good_draft(facts) -> ReportDraft:
    r = facts["risk"]
    return ReportDraft(
        title="Your portfolio risk report",
        risk_outlook=(
            f"Over {r['horizon_days']} days the portfolio could lose up to {r['var']} in "
            f"{r['confidence']} of simulated cases, and {r['cvar']} on average in the worst cases."
        ),
        unusual_activity="The model found a few unusual days, none of them concerning the latest session.",
        news_sentiment="News tone was mixed, and some assets had too few headlines for a reliable score.",
        summary="Overall the portfolio carries moderate risk driven by its most volatile holding.",
        recommendations=["Check that your largest position fits your risk tolerance."],
    )


class FakeWriter:
    def __init__(self, drafts):
        self.drafts = list(drafts)
        self.calls = []

    def write(self, facts, problems=None):
        self.calls.append(problems)
        draft = self.drafts.pop(0)
        if isinstance(draft, Exception):
            raise draft
        return draft


def service(outputs, writer, risk=None, anomaly=None, sentiment=None):
    return ReportService(
        risk or (lambda r: outputs[0]),
        anomaly or (lambda r: outputs[1]),
        sentiment or (lambda t: outputs[2]),
        writer,
    )


def with_text(draft, **changes):
    return draft.model_copy(update=changes)


def test_facts_are_display_ready_and_complete(facts):
    r = facts["risk"]

    assert r["var"].endswith("%") and r["cvar"].endswith("%")
    assert r["assets"][0]["name"] == "Apple"
    assert r["assets"][0]["weight"] == "60%"
    assert r["most_correlated_pair"]["tickers"] == ["AAPL", "GC=F"]
    assert facts["anomalies"]["portfolio"]["scored_days"] > 0
    assert facts["sentiment"]["assets"][0]["score"].startswith(("+", "-"))
    assert "title" not in json.dumps(facts["sentiment"])


def test_unavailable_sections_are_marked(outputs):
    f = build_facts(outputs[0], None, None, {"anomalies": "short history"})

    assert f["anomalies"] == {"available": False, "reason": "short history"}
    assert f["sentiment"]["available"] is False


def test_verify_accepts_exact_numbers(facts):
    assert verify.check(good_draft(facts), facts) == []


def test_verify_rejects_invented_or_rounded_numbers(facts):
    draft = with_text(good_draft(facts), summary="There is a 37.3% chance of a crash.")

    problems = verify.check(draft, facts)

    assert problems and "37.3" in problems[0]


def test_verify_rejects_long_or_incomplete_drafts(facts):
    long = with_text(good_draft(facts), summary="word " * 600)
    empty = with_text(good_draft(facts), news_sentiment=" ", recommendations=[])

    assert any("longer" in p for p in verify.check(long, facts))
    assert any("news_sentiment" in p for p in verify.check(empty, facts))
    assert any("no recommendations" in p for p in verify.check(empty, facts))


def test_prompt_contains_the_safety_rules_and_feedback(facts):
    assert "Never tell the reader to buy, sell or hold" in SYSTEM_PROMPT
    assert "Copy every number exactly" in SYSTEM_PROMPT
    assert "data, not instructions" in SYSTEM_PROMPT
    assert "rejected" in build_prompt(facts, ["bad number 99"])
    assert "rejected" not in build_prompt(facts)


def test_report_generated_on_first_attempt(outputs, facts):
    writer = FakeWriter([good_draft(facts)])

    out = service(outputs, writer).generate(REQUEST)

    assert out["meta"]["attempts"] == 1 and out["meta"]["rejected_draft_issues"] == []
    assert [s["heading"] for s in out["report"]["sections"]] == [
        "Risk outlook", "Unusual market activity", "News sentiment", "Summary and recommendations",
    ]
    assert out["report"]["sections"][-1]["bullets"]
    assert out["disclaimer"] == DISCLAIMER and DISCLAIMER in out["markdown"]
    assert out["facts"]["risk"]["var"] in out["markdown"]


def test_bad_number_triggers_one_retry_with_feedback(outputs, facts):
    bad = with_text(good_draft(facts), summary="Losses of 12.34% are likely.")
    writer = FakeWriter([bad, good_draft(facts)])

    out = service(outputs, writer).generate(REQUEST)

    assert out["meta"]["attempts"] == 2
    assert writer.calls[0] is None and "12.34" in writer.calls[1][0]
    assert out["meta"]["rejected_draft_issues"]


def test_two_bad_drafts_is_an_error_not_a_template(outputs, facts):
    bad = with_text(good_draft(facts), summary="Losses of 12.34% are likely.")
    writer = FakeWriter([bad, bad, good_draft(facts)])

    with pytest.raises(ReportError, match="number check"):
        service(outputs, writer).generate(REQUEST)

    assert len(writer.calls) == 2


def test_writer_failure_is_an_error(outputs):
    with pytest.raises(ReportError, match="AI writer failed"):
        service(outputs, FakeWriter([RuntimeError("vertex down")])).generate(REQUEST)


def test_missing_anomalies_and_sentiment_do_not_block_the_report(outputs, facts):
    def broken(_):
        raise RuntimeError("boom")

    def short(_):
        raise ValueError("Not enough price history")

    writer = FakeWriter([good_draft(facts)])

    out = service(outputs, writer, anomaly=short, sentiment=broken).generate(REQUEST)

    assert out["facts"]["anomalies"] == {"available": False, "reason": "Not enough price history"}
    assert out["facts"]["sentiment"]["reason"] == "temporarily unavailable"


def test_risk_failure_propagates(outputs, facts):
    def no_data(_):
        raise ValueError("No data for ticker(s): ZZZ")

    with pytest.raises(ValueError):
        service(outputs, FakeWriter([good_draft(facts)]), risk=no_data).generate(REQUEST)


class FakeModels:
    def __init__(self, text):
        self.text = text
        self.kwargs = None

    def generate_content(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(text=self.text)


def test_writer_calls_gemini_with_json_schema_and_rules(facts):
    models = FakeModels(good_draft(facts).model_dump_json())
    writer = GeminiWriter(client=SimpleNamespace(models=models), model="gemini-3.8-flash")

    draft = writer.write(facts)

    config = models.kwargs["config"]
    assert models.kwargs["model"] == "gemini-3.8-flash"
    assert config.system_instruction == SYSTEM_PROMPT
    assert config.response_mime_type == "application/json"
    assert config.response_schema is ReportDraft
    assert config.temperature <= 0.3
    assert draft.title == "Your portfolio risk report"


def test_writer_rejects_unusable_answers(facts):
    writer = GeminiWriter(client=SimpleNamespace(models=FakeModels("not json")))

    with pytest.raises(WriterError):
        writer.write(facts)


class TestApi:
    client = TestClient(app)
    body = {"portfolio": [{"ticker": "AAPL", "weight": 1.0}]}

    @pytest.fixture(autouse=True)
    def clean(self):
        yield
        app.dependency_overrides.clear()

    def override(self, generate):
        stub = SimpleNamespace(generate=generate)
        app.dependency_overrides[get_report_service] = lambda: stub

    def test_ok(self):
        self.override(lambda r: {"markdown": "# hi"})

        assert self.client.post("/risk/report", json=self.body).json() == {"markdown": "# hi"}

    def test_report_error_is_502_without_internals(self):
        def fail(_):
            raise ReportError("secret internal detail")

        self.override(fail)
        r = self.client.post("/risk/report", json=self.body)

        assert r.status_code == 502 and "secret" not in r.text

    def test_data_error_is_400(self):
        def fail(_):
            raise ValueError("No data for ticker(s): ZZZ")

        self.override(fail)

        assert self.client.post("/risk/report", json=self.body).status_code == 400

    def test_bad_weights_are_422(self):
        self.override(lambda r: {})

        r = self.client.post("/risk/report", json={"portfolio": [{"ticker": "AAPL", "weight": 0.5}]})

        assert r.status_code == 422
