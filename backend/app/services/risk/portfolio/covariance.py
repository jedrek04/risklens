import numpy as np
import pandas as pd


def compute_covariance_matrix(returns_df: pd.DataFrame) -> np.ndarray:

    # returns_df: columns = tickers, rows = time
    return returns_df.cov().values


def compute_mean_returns(returns_df: pd.DataFrame) -> np.ndarray:
    return returns_df.mean().values