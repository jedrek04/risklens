import numpy as np

from backend.app.services.risk import garch
from backend.app.services.risk.returns import aligned_log_returns
from tests.conftest import make_prices


def test_forecast_shape_and_sanity():
    rets = aligned_log_returns(make_prices())["T"].to_numpy()

    out = garch.forecast_volatility(rets, horizon=5)

    assert out["volatility"].shape == (5,)
    assert np.all((out["volatility"] > 0) & (out["volatility"] < 0.2))
    assert out["converged"]
