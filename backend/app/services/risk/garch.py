import numpy as np
from arch import arch_model


def forecast_volatility(returns: np.ndarray, horizon: int) -> dict:
    # arch converges better on percent-scaled returns
    result = arch_model(returns * 100, vol="Garch", p=1, q=1, mean="Zero", dist="normal").fit(disp="off")

    variance = result.forecast(horizon=horizon).variance.values[-1]

    return {
        "volatility": np.sqrt(variance) / 100,
        "aic": float(result.aic),
        "converged": bool(result.convergence_flag == 0),
    }
