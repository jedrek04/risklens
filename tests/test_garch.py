import numpy as np
import pytest

from backend.app.services.risk import garch
from tests.conftest import make_prices


def test_log_returns_sorted_and_length(prices):
    shuffled = prices.sample(frac=1, random_state=1)
    r = garch.log_returns(shuffled)
    assert len(r) == len(prices) - 1
    np.testing.assert_allclose(r, garch.log_returns(prices))


def test_analyze_shape_and_sanity(prices):
    out = garch.analyze(prices, "TEST", horizon=5)

    assert out["ticker"] == "TEST"
    assert len(out["volatility"]["forecast"]) == 5
    assert out["volatility"]["current"] == out["volatility"]["forecast"][0]
    assert all(0 < v < 0.2 for v in out["volatility"]["forecast"])
    assert 0 < out["returns_stats"]["annualized_vol"] < 2


def test_analyze_rejects_short_history():
    with pytest.raises(ValueError, match="Not enough price history"):
        garch.analyze(make_prices(n=50), "TEST", horizon=5)
