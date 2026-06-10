import numpy as np


def run_monte_carlo(mu, cov, weights, horizon=10, n_sim=10000):

    n_assets = len(mu)

    results = []

    for _ in range(n_sim):

        returns = np.random.multivariate_normal(mu, cov, size=horizon)

        # cumulative return over horizon
        port_returns = returns @ weights
        cumulative = np.sum(port_returns)

        results.append(cumulative)

    results = np.array(results)

    var95 = np.percentile(results, 5)
    cvar95 = results[results <= var95].mean()

    return {
        "var95": float(var95),
        "cvar95": float(cvar95),
        "expected_return": float(np.mean(results)),
        "expected_volatility": float(np.std(results)),
        "distribution": results
    }