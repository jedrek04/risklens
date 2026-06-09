import numpy as np
import pandas as pd
from .model import GARCHModel


class GARCHService:

    def __init__(self):
        self.model = GARCHModel()

    def prepare_returns(self, df: pd.DataFrame) -> np.ndarray:
        df = df.sort_values("date")

        returns = np.log(df["close"] / df["close"].shift(1))
        returns = returns.dropna()

        return returns.values.astype(float)

    def run(self, df: pd.DataFrame, ticker: str, horizon: int = 5):

        returns = self.prepare_returns(df)

        self.model.fit(returns)
        vol_forecast = self.model.forecast_volatility(horizon)

        return {
            "ticker": ticker,
            "horizon": horizon,

            "volatility": {
                "current": float(vol_forecast[0]),
                "forecast": [float(v) for v in vol_forecast],
            },

            "returns_stats": {
                "annualized_vol": float(np.std(returns) * np.sqrt(252)),
                "mean": float(np.mean(returns)),
                "std": float(np.std(returns)),
            },

            "model": self.model.get_params()
        }