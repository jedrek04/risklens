import numpy as np

from backend.app.services.risk import monte_carlo


def test_matches_analytic_volatility():
    vols = np.array([[0.01, 0.02], [0.012, 0.022], [0.011, 0.025]])
    corr = np.array([[1.0, 0.3], [0.3, 1.0]])
    weights = np.array([0.6, 0.4])

    paths = monte_carlo.simulate(vols, corr, weights, n_sim=200000, seed=1)

    expected = np.sqrt(sum(weights @ (np.diag(v) @ corr @ np.diag(v)) @ weights for v in vols))
    assert np.isclose(paths[-1].std(), expected, rtol=0.02)
    assert abs(paths[-1].mean()) < 0.001


def test_var_is_the_95th_percentile_loss_and_cvar_is_worse():
    vols = np.full((10, 1), 0.01)
    paths = monte_carlo.simulate(vols, np.eye(1), np.array([1.0]), n_sim=100000, seed=2)

    out = monte_carlo.summarize(paths, 0.95)

    assert np.isclose(out["var"], 1.645 * 0.01 * np.sqrt(10), rtol=0.03)
    assert out["cvar"] > out["var"] > 0
    assert len(out["fan_chart"]["day"]) == 10
    assert out["fan_chart"]["p5"][-1] < out["fan_chart"]["p50"][-1] < out["fan_chart"]["p95"][-1]


def test_perfectly_correlated_assets_do_not_crash():
    vols = np.full((5, 2), 0.01)
    corr = np.ones((2, 2))

    paths = monte_carlo.simulate(vols, corr, np.array([0.5, 0.5]), n_sim=1000, seed=3)

    assert np.isfinite(paths).all()


def test_same_seed_same_result():
    args = (np.full((3, 2), 0.01), np.eye(2), np.array([0.5, 0.5]), 1000)

    assert np.array_equal(monte_carlo.simulate(*args, seed=7), monte_carlo.simulate(*args, seed=7))
