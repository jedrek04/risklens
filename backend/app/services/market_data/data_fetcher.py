import numpy as np
import pandas as pd
import yfinance as yf

from .tickers import get_all_tickers


def fetch_price_history(ticker: str, days: int) -> pd.DataFrame:
    end = pd.Timestamp.today()
    start = end - pd.Timedelta(days=days)

    df = yf.download(
        ticker,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
    )

    if df is None or df.empty:
        raise ValueError("empty data")

    df = df[["Open", "High", "Low", "Close", "Volume"]]
    df.columns = ["open", "high", "low", "close", "volume"]

    df = df.dropna(subset=["close"])

    df["ticker"] = ticker
    df["daily_return"] = np.log(df["close"] / df["close"].shift(1))

    df.index.name = "date"
    df = df.reset_index()
    df["date"] = pd.to_datetime(df["date"]).dt.date

    return df


def fetch_all_prices(days: int):
    all_data = []
    failed = []

    for t in get_all_tickers():
        try:
            df = fetch_price_history(ticker=t["symbol"], days=days)
            df["name"] = t["name"]
            df["category"] = t["category"]
            all_data.append(df)
            print(f"OK   -> {t['symbol']}")
        except Exception as e:
            print(f"FAIL -> {t['symbol']}: {e}")
            failed.append({**t, "error": str(e)})

    result = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
    return result, failed
