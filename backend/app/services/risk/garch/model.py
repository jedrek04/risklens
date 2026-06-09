import numpy as np
from arch import arch_model


class GARCHModel:
    def __init__(self, p=1, q=1):
        self.p = p
        self.q = q
        self.result = None

    def fit(self, returns: np.ndarray):
        # scaling
        self.scaled_returns = returns * 100

        model = arch_model(
            self.scaled_returns,
            vol="Garch",
            p=self.p,
            q=self.q,
            mean="Zero",
            dist="normal"
        )

        self.result = model.fit(disp="off")
        return self

    def forecast_volatility(self, horizon: int = 1):
        if self.result is None:
            raise RuntimeError("Model not fitted")

        forecast = self.result.forecast(horizon=horizon)

        var = forecast.variance.values[-1]  # array shape: (horizon,)
        vol = np.sqrt(var)

        # unscale back
        vol = vol / 100

        return vol

    def get_params(self):
        return {
            "p": self.p,
            "q": self.q,
            "aic": float(self.result.aic)
        }