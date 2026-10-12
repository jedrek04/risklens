import numpy as np
import pandas as pd

from backend.app.services.risk import returns
from tests.conftest import make_prices


def test_aligns_on_common_dates_only():
    stock = make_prices(n=100, ticker="STK")
    days = pd.date_range("2024-01-01", periods=140, freq="D")
    crypto = pd.DataFrame({"ticker": "CRY", "date": days, "close": np.linspace(100, 200, 140)})

    rets = returns.aligned_log_returns(pd.concat([stock, crypto]))

    assert set(rets.columns) == {"STK", "CRY"}
    assert all(d.weekday() < 5 for d in rets.index)
    assert rets.notna().all().all()


def test_weekend_move_is_compounded_into_monday():
    days = pd.date_range("2024-01-05", periods=5, freq="D")
    closes = [100, 110, 121, 133.1, 146.41]
    crypto = pd.DataFrame({"ticker": "CRY", "date": days, "close": closes})
    stock = pd.DataFrame({"ticker": "STK", "date": days[[0, 3, 4]], "close": [1.0, 1.0, 1.0]})

    rets = returns.aligned_log_returns(pd.concat([crypto, stock]))

    assert np.isclose(rets["CRY"].iloc[0], np.log(133.1 / 100))


def test_non_positive_prices_are_dropped():
    df = make_prices(n=50, ticker="OIL")
    df.loc[10, "close"] = -5.0

    rets = returns.aligned_log_returns(df)

    assert len(rets) == 48
    assert np.isfinite(rets.to_numpy()).all()


def test_correlation_matrix():
    a = make_prices(n=200, seed=1, ticker="A")
    b = a.assign(ticker="B")
    c = make_prices(n=200, seed=2, ticker="C")

    corr = returns.correlation(returns.aligned_log_returns(pd.concat([a, b, c])))

    assert corr.shape == (3, 3)
    assert np.isclose(corr[0, 1], 1.0)
    assert abs(corr[0, 2]) < 0.3
