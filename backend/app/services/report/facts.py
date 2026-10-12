from backend.app.services.market_data.tickers import get_all_tickers


def pct(x: float, digits: int = 1) -> str:
    return f"{x * 100:.{digits}f}%"


def _names() -> dict[str, str]:
    return {t["symbol"]: t["name"] for t in get_all_tickers()}


def _pairs(corr: dict) -> list[tuple[float, str, str]]:
    tickers, matrix = corr["tickers"], corr["matrix"]
    return [
        (matrix[i][j], tickers[i], tickers[j])
        for i in range(len(tickers))
        for j in range(i + 1, len(tickers))
    ]


def risk_facts(risk: dict) -> dict:
    p, meta = risk["portfolio"], risk["meta"]
    assets = risk["assets"]
    pairs = sorted(_pairs(risk["correlation"]))
    names = _names()

    most_volatile = max(assets, key=lambda a: a["annualized_vol"])
    largest = max(assets, key=lambda a: a["weight"])

    out = {
        "horizon_days": meta["horizon"],
        "confidence": pct(meta["confidence"], 0),
        "history_days": meta["days"],
        "simulations": meta["n_sim"],
        "var": pct(p["var"]),
        "cvar": pct(p["cvar"]),
        "portfolio_volatility": pct(p["volatility"]),
        "simulated_range_90pct": {
            "low": pct(p["fan_chart"]["p5"][-1]),
            "high": pct(p["fan_chart"]["p95"][-1]),
        },
        "assets": [
            {
                "ticker": a["ticker"],
                "name": names.get(a["ticker"], a["ticker"]),
                "weight": pct(a["weight"], 0),
                "annualized_volatility": pct(a["annualized_vol"]),
                "current_daily_volatility": pct(a["volatility"]["current"], 2),
            }
            for a in assets
        ],
        "most_volatile_asset": most_volatile["ticker"],
        "largest_position": {"ticker": largest["ticker"], "weight": pct(largest["weight"], 0)},
        "garch_all_converged": all(a["garch"]["converged"] for a in assets),
    }

    if pairs:
        low, high = pairs[0], pairs[-1]
        out["most_correlated_pair"] = {"tickers": [high[1], high[2]], "correlation": f"{high[0]:.2f}"}
        out["least_correlated_pair"] = {"tickers": [low[1], low[2]], "correlation": f"{low[0]:.2f}"}

    return out


def anomaly_facts(anomalies: dict) -> dict:
    port = anomalies["portfolio"]
    summary = port["summary"]
    recent = sorted(port["anomalies"], key=lambda a: a["date"], reverse=True)[:3]

    return {
        "window_days": anomalies["meta"]["days"],
        "portfolio": {
            "flagged_days": summary["anomalies"],
            "scored_days": summary["scored_days"],
            "latest_date": summary["latest_date"],
            "latest_day_is_unusual": summary["latest_is_anomaly"],
            "most_recent_unusual_days": [
                {"date": a["date"], "daily_return": pct(a["return"], 2)} for a in recent
            ],
        },
        "assets": [
            {
                "ticker": a["name"],
                "flagged_days": a["summary"]["anomalies"],
                "scored_days": a["summary"]["scored_days"],
                "latest_day_is_unusual": a["summary"]["latest_is_anomaly"],
            }
            for a in anomalies["assets"]
        ],
    }


def sentiment_facts(sentiment: dict) -> dict:
    assets = []
    for a in sentiment["assets"]:
        item = {"ticker": a["ticker"], "status": a["status"], "headlines": a["headlines"]}
        if a["score"] is not None:
            item.update({
                "score": f"{a['score']:+.2f}",
                "label": a["label"],
                "positive_share": pct(a["share"]["positive"], 0),
                "negative_share": pct(a["share"]["negative"], 0),
            })
        assets.append(item)

    return {
        "window_days": sentiment["meta"]["window_days"],
        "minimum_headlines_for_reliable_score": sentiment["meta"]["min_headlines"],
        "assets": assets,
    }


def unavailable(reason: str) -> dict:
    return {"available": False, "reason": reason}


def build_facts(risk: dict, anomalies: dict | None, sentiment: dict | None, reasons: dict) -> dict:
    return {
        "risk": risk_facts(risk),
        "anomalies": anomaly_facts(anomalies) if anomalies else unavailable(reasons.get("anomalies", "not available")),
        "sentiment": sentiment_facts(sentiment) if sentiment else unavailable(reasons.get("sentiment", "not available")),
    }
