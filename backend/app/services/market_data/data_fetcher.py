from .tickers import get_all_tickers

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timezone


def fetch_price_history(
    ticker: str,
    days: int
) -> pd.DataFrame:

    end = datetime.today()
    start = end - pd.Timedelta(days=days)

    df = yf.download(
        ticker,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False
    )

    if df is None or df.empty:
        raise ValueError("empty data")

    df = df[[
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]]

    df.columns = [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    df["ticker"] = ticker
    df["daily_return"] = df["close"].pct_change()
    df["daily_return"] = np.log(
    df["close"] / df["close"].shift(1))

    df.index.name = "date"
    df = df.reset_index()

    # IMPORTANT: BigQuery DATE
    df["date"] = pd.to_datetime(df["date"]).dt.date

    numeric_cols = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "daily_return"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def fetch_all_prices(days: int):

    tickers = get_all_tickers()

    all_data = []
    failed = []

    for t in tickers:

        symbol = t["symbol"]
        name = t["name"]
        category = t["category"]

        try:
            df = fetch_price_history(
                ticker=symbol,
                days=days
            )

            df["name"] = name
            df["category"] = category

            all_data.append(df)

            print(f"OK   -> {symbol}")

        except Exception as e:
            print(f"FAIL -> {symbol}")

            failed.append({
                "symbol": symbol,
                "name": name,
                "category": category,
                "error": str(e)
            })

    result_df = (
        pd.concat(all_data, ignore_index=True)
        if all_data else pd.DataFrame()
    )

    return result_df, failed