import numpy as np
import pandas as pd

from backend.app.schemas import AnomalyRequest
from backend.app.services.risk import isolation_forest as iforest
from backend.app.services.risk.data_provider import load_prices

HISTORY_DAYS = int(iforest.TRAIN_WINDOW * 1.5) + 30


def asset_log_returns(prices: pd.DataFrame) -> pd.Series:
    close = prices.set_index("date")["close"].sort_index()
    return np.log(close.where(close > 0).dropna()).diff().dropna()


def portfolio_log_returns(returns: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    return np.log1p(np.expm1(returns) @ weights)


def run(request: AnomalyRequest) -> dict:
    tickers = [a.ticker for a in request.portfolio]
    weights = np.array([a.weight for a in request.portfolio])

    prices = load_prices(tickers, request.days + HISTORY_DAYS)
    prices["date"] = pd.to_datetime(prices["date"])
    start = prices["date"].max() - pd.Timedelta(days=request.days)

    series = []
    wide = {}

    for t in tickers:
        p = prices[prices["ticker"] == t]
        rets = asset_log_returns(p)
        wide[t] = rets
        volume = p.set_index("date")["volume"].sort_index().reindex(rets.index)
        features = iforest.build_features(rets, volume)
        series.append(_score(t, features, start))

    aligned = pd.DataFrame(wide).dropna()
    port = portfolio_log_returns(aligned, weights)
    series.append(_score("portfolio", iforest.build_features(port), start))

    return {
        "meta": {
            "days": request.days,
            "contamination": iforest.CONTAMINATION,
            "train_window": iforest.TRAIN_WINDOW,
            "refit_every": iforest.REFIT_EVERY,
        },
        "portfolio": series[-1],
        "assets": series[:-1],
    }


def _score(name: str, features: pd.DataFrame, start: pd.Timestamp) -> dict:
    try:
        scored = iforest.rolling_scores(features, start)
    except ValueError as e:
        raise ValueError(f"{name}: {e}")

    return iforest.to_result(name, features, scored)
