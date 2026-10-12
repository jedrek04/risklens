import numpy as np
import pandas as pd

TRADING_DAYS = 252


def aligned_log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    wide = prices.pivot(index="date", columns="ticker", values="close").sort_index()
    wide = wide.where(wide > 0).dropna()
    return np.log(wide).diff().dropna()


def correlation(returns: pd.DataFrame) -> np.ndarray:
    return returns.corr().to_numpy()


def annualized_volatility(returns: pd.DataFrame) -> pd.Series:
    return returns.std() * np.sqrt(TRADING_DAYS)
