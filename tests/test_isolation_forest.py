import numpy as np
import pandas as pd
import pytest

from backend.app.services.risk import isolation_forest as iforest
from tests.conftest import make_prices


def series(n=900, seed=0):
    df = make_prices(n=n, seed=seed).set_index("date")
    rets = np.log(df["close"]).diff().dropna()
    return rets, df["volume"].reindex(rets.index)


def test_features_columns_and_volume_handling():
    rets, volume = series()

    assert list(iforest.build_features(rets, volume).columns) == [
        "return", "volatility_5d", "volatility_20d", "volume_ratio",
    ]
    assert "volume_ratio" not in iforest.build_features(rets).columns
    assert "volume_ratio" not in iforest.build_features(rets, volume * 0).columns


def test_features_are_backward_looking_only():
    rets, volume = series()
    full = iforest.build_features(rets, volume)
    cut = iforest.build_features(rets.iloc[:600], volume.iloc[:600])

    pd.testing.assert_frame_equal(full.loc[cut.index], cut)


def test_injected_shock_is_flagged():
    rets, volume = series()
    shock_day = rets.index[700]
    rets.loc[shock_day] = -0.15
    features = iforest.build_features(rets, volume)

    scored = iforest.rolling_scores(features, start=rets.index[600])

    assert scored.loc[shock_day, "anomaly"]
    assert scored.loc[shock_day, "return_z"] < -5


def test_scoring_is_point_in_time():
    rets, volume = series()
    features = iforest.build_features(rets, volume)
    start = rets.index[600]

    full = iforest.rolling_scores(features, start)
    cut_at = features.index[750]
    truncated = iforest.rolling_scores(features.loc[:cut_at], start)

    common = truncated.index
    np.testing.assert_allclose(full.loc[common[:-1], "score"], truncated.loc[common[:-1], "score"])


def test_fraction_flagged_is_small():
    rets, volume = series(n=1500)
    scored = iforest.rolling_scores(iforest.build_features(rets, volume), start=rets.index[700])

    assert 0 < scored["anomaly"].mean() < 0.12


def test_not_enough_history_raises():
    rets, volume = series(n=200)

    with pytest.raises(ValueError, match="Not enough price history"):
        iforest.rolling_scores(iforest.build_features(rets, volume), start=rets.index[100])


def test_result_structure():
    rets, volume = series()
    features = iforest.build_features(rets, volume)
    scored = iforest.rolling_scores(features, start=rets.index[600])

    out = iforest.to_result("T", features, scored)

    assert len(out["dates"]) == len(out["scores"]) == len(out["anomaly"]) == len(scored)
    assert out["summary"]["anomalies"] == len(out["anomalies"]) == sum(out["anomaly"])
    assert out["anomalies"]
    assert set(out["anomalies"][0]["z_scores"]) == set(features.columns)
