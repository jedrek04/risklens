import numpy as np
import pandas as pd
import pytest


def make_prices(n: int = 400, seed: int = 0, start_price: float = 100.0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    vol = np.empty(n)
    vol[0] = 0.01
    ret = np.empty(n)
    for t in range(n):
        if t:
            vol[t] = np.sqrt(1e-6 + 0.1 * ret[t - 1] ** 2 + 0.85 * vol[t - 1] ** 2)
        ret[t] = vol[t] * rng.standard_normal()
    close = start_price * np.exp(np.cumsum(ret))
    return pd.DataFrame({"date": pd.bdate_range("2024-01-01", periods=n).date, "close": close})


@pytest.fixture
def prices():
    return make_prices()
