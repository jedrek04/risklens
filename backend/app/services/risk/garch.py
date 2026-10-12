import numpy as np
import pandas as pd
from arch import arch_model

MIN_OBSERVATIONS = 100
TRADING_DAYS = 252


def log_returns(df: pd.DataFrame) -> np.ndarray:
    prices = df.sort_values("date")["close"]
    return np.log(prices / prices.shift(1)).dropna().to_numpy(dtype=float)


def forecast_volatility(returns: np.ndarray, horizon: int) -> tuple[np.ndarray, float]:
    # arch converges better on percent-scaled returns
    result = arch_model(returns * 100, vol="Garch", p=1, q=1, mean="Zero", dist="normal").fit(disp="off")

    variance = result.forecast(horizon=horizon).variance.values[-1]
    return np.sqrt(variance) / 100, float(result.aic)


def analyze(df: pd.DataFrame, ticker: str, horizon: int) -> dict:
    returns = log_returns(df)

    if len(returns) < MIN_OBSERVATIONS:
        raise ValueError(
            f"Not enough price history for {ticker}: {len(returns)} returns, need {MIN_OBSERVATIONS}"
        )

    vol, aic = forecast_volatility(returns, horizon)

    return {
        "ticker": ticker,
        "horizon": horizon,
        "volatility": {
            "current": float(vol[0]),
            "forecast": [float(v) for v in vol],
        },
        "returns_stats": {
            "annualized_vol": float(np.std(returns) * np.sqrt(TRADING_DAYS)),
            "mean": float(np.mean(returns)),
            "std": float(np.std(returns)),
        },
        "model": {"p": 1, "q": 1, "aic": aic},
    }
