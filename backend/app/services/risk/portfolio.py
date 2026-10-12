import numpy as np

from backend.app.schemas import PortfolioRequest
from backend.app.services.risk import garch, monte_carlo, returns
from backend.app.services.risk.data_provider import load_prices

MIN_OBSERVATIONS = 100
CONFIDENCE = 0.95


def run(request: PortfolioRequest, seed: int | None = None) -> dict:
    tickers = [a.ticker for a in request.portfolio]
    weights = np.array([a.weight for a in request.portfolio])

    rets = returns.aligned_log_returns(load_prices(tickers, request.days))
    rets = rets[tickers]

    if len(rets) < MIN_OBSERVATIONS:
        raise ValueError(
            f"Only {len(rets)} common trading days across the selected assets, need {MIN_OBSERVATIONS}"
        )

    fits = {t: garch.forecast_volatility(rets[t].to_numpy(), request.horizon) for t in tickers}
    vols = np.column_stack([fits[t]["volatility"] for t in tickers])

    corr = returns.correlation(rets)
    paths = monte_carlo.simulate(vols, corr, weights, request.n_sim, seed)
    annual_vol = returns.annualized_volatility(rets)

    return {
        "meta": {
            "days": request.days,
            "horizon": request.horizon,
            "n_sim": request.n_sim,
            "confidence": CONFIDENCE,
            "observations": len(rets),
            "start": rets.index.min().isoformat(),
            "end": rets.index.max().isoformat(),
        },
        "portfolio": monte_carlo.summarize(paths, CONFIDENCE),
        "assets": [
            {
                "ticker": a.ticker,
                "weight": a.weight,
                "annualized_vol": float(annual_vol[a.ticker]),
                "volatility": {
                    "current": float(fits[a.ticker]["volatility"][0]),
                    "forecast": [float(v) for v in fits[a.ticker]["volatility"]],
                },
                "garch": {"aic": fits[a.ticker]["aic"], "converged": fits[a.ticker]["converged"]},
            }
            for a in request.portfolio
        ],
        "correlation": {"tickers": tickers, "matrix": corr.tolist()},
    }
