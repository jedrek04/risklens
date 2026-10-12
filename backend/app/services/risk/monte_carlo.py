import numpy as np

FAN_PERCENTILES = (5, 25, 50, 75, 95)


def correlation_factor(corr: np.ndarray) -> np.ndarray:
    # eigen factor instead of cholesky so singular matrices (identical assets) still work
    values, vectors = np.linalg.eigh(corr)
    return vectors * np.sqrt(np.clip(values, 0, None))


def simulate(
    vols: np.ndarray,
    corr: np.ndarray,
    weights: np.ndarray,
    n_sim: int,
    seed: int | None = None,
) -> np.ndarray:
    """vols is (horizon, n_assets) daily volatility. returns (horizon, n_sim) portfolio returns."""
    rng = np.random.default_rng(seed)
    horizon, n_assets = vols.shape
    factor = correlation_factor(corr)

    cumulative = np.zeros((n_sim, n_assets))
    paths = np.empty((horizon, n_sim))

    for t in range(horizon):
        shocks = rng.standard_normal((n_sim, n_assets)) @ factor.T
        cumulative += shocks * vols[t]
        paths[t] = np.expm1(cumulative) @ weights

    return paths


def summarize(paths: np.ndarray, confidence: float = 0.95) -> dict:
    final_losses = -paths[-1]
    var = np.percentile(final_losses, confidence * 100)
    cvar = final_losses[final_losses >= var].mean()
    fan = np.percentile(paths, FAN_PERCENTILES, axis=1)

    return {
        "var": float(var),
        "cvar": float(cvar),
        "volatility": float(paths[-1].std()),
        "fan_chart": {
            "day": list(range(1, paths.shape[0] + 1)),
            **{f"p{p}": [float(x) for x in row] for p, row in zip(FAN_PERCENTILES, fan)},
        },
    }
