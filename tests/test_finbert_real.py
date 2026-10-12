import pytest

from backend.app.services.sentiment.finbert import FinBERTScorer

pytestmark = pytest.mark.slow


def test_real_model_polarity_and_label_order():
    out = FinBERTScorer().score([
        "Company reports record quarterly profit and raises full-year guidance",
        "Shares plunge after regulators open fraud investigation",
        "The central bank left interest rates unchanged on Wednesday",
    ])

    assert out[0]["positive"] > 0.8
    assert out[1]["negative"] > 0.8
    assert out[2]["neutral"] > 0.5
    assert all(abs(sum(r.values()) - 1) < 1e-4 for r in out)
