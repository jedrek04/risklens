import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

CONTAMINATION = 0.02
TRAIN_WINDOW = 504
MIN_TRAIN = 252
REFIT_EVERY = 21
VOLUME_MIN_COVERAGE = 0.95


def build_features(log_returns: pd.Series, volume: pd.Series | None = None) -> pd.DataFrame:
    features = pd.DataFrame({
        "return": log_returns,
        "volatility_5d": log_returns.rolling(5).std(),
        "volatility_20d": log_returns.rolling(20).std(),
    })

    if volume is not None and (volume > 0).mean() >= VOLUME_MIN_COVERAGE:
        volume = volume.where(volume > 0).ffill()
        features["volume_ratio"] = np.log(volume / volume.rolling(20).mean().shift(1))

    return features.replace([np.inf, -np.inf], np.nan).dropna()


def rolling_scores(features: pd.DataFrame, start: pd.Timestamp) -> pd.DataFrame:
    """score each day with a model trained only on the days before it. higher score = more unusual."""
    blocks = []
    first = features.index.searchsorted(start)

    for block_start in range(first, len(features), REFIT_EVERY):
        train = features.iloc[max(0, block_start - TRAIN_WINDOW):block_start]
        if len(train) < MIN_TRAIN:
            continue

        model = IsolationForest(
            n_estimators=100, contamination=CONTAMINATION, random_state=42
        ).fit(train)

        block = features.iloc[block_start:block_start + REFIT_EVERY]
        z = (block - train.mean()) / train.std().replace(0, np.nan)

        blocks.append(
            z.add_suffix("_z").assign(score=-model.decision_function(block))
        )

    if not blocks:
        raise ValueError("Not enough price history to score anomalies")

    scored = pd.concat(blocks)
    scored["anomaly"] = scored["score"] > 0
    return scored


def to_result(name: str, features: pd.DataFrame, scored: pd.DataFrame) -> dict:
    flagged = scored[scored["anomaly"]]

    return {
        "name": name,
        "dates": [d.date().isoformat() for d in scored.index],
        "scores": [float(s) for s in scored["score"]],
        "anomaly": [bool(a) for a in scored["anomaly"]],
        "summary": {
            "scored_days": len(scored),
            "anomalies": len(flagged),
            "latest_date": scored.index[-1].date().isoformat(),
            "latest_is_anomaly": bool(scored["anomaly"].iloc[-1]),
        },
        "anomalies": [
            {
                "date": d.date().isoformat(),
                "score": float(row["score"]),
                "return": float(features.loc[d, "return"]),
                "z_scores": {
                    c.removesuffix("_z"): float(row[c]) for c in scored.columns if c.endswith("_z")
                },
            }
            for d, row in flagged.iterrows()
        ],
    }
