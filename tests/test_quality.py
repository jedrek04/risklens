import numpy as np
import pandas as pd

from backend.app.pipeline.quality import check_prices

TODAY = pd.Timestamp("2026-01-31")


def frame(ticker, dates, close=None, ret=None, category="x"):
    n = len(dates)
    return pd.DataFrame({
        "date": dates,
        "ticker": ticker,
        "close": close if close is not None else np.full(n, 10.0),
        "daily_return": ret if ret is not None else np.full(n, 0.001),
        "category": category,
    })


def good(ticker="OK"):
    return frame(ticker, pd.bdate_range(end=TODAY, periods=300))


def test_clean_data_has_no_problems():
    problems = check_prices(good(), today=TODAY)
    assert all(len(p) == 0 for p in problems.values())


def test_detects_each_problem():
    dup = pd.concat([good("DUP"), good("DUP").iloc[[0]]])
    bad_close = good("BAD")
    bad_close.loc[bad_close.index[5], "close"] = np.nan
    spike = good("SPIKE")
    spike.loc[spike.index[10], "daily_return"] = 1.09
    stale = frame("STALE", pd.bdate_range(end=TODAY - pd.Timedelta(days=30), periods=300))
    short = frame("SHORT", pd.bdate_range(end=TODAY, periods=40))
    holes = good("HOLE").drop(index=range(100, 120))

    p = check_prices(pd.concat([good(), dup, bad_close, spike, stale, short, holes]), today=TODAY)

    assert set(p["duplicates"]["ticker"]) == {"DUP"}
    assert set(p["bad_close"]["ticker"]) == {"BAD"}
    assert set(p["extreme_returns"]["ticker"]) == {"SPIKE"}
    assert set(p["stale"]["ticker"]) == {"STALE"}
    assert set(p["short_history"]["ticker"]) == {"SHORT"}
    assert set(p["gaps"]["ticker"]) == {"HOLE"}
