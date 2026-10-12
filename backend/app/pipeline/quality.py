import pandas as pd

from backend.app.config import PROJECT_ID, DATASET, PRICE_TABLE

EXTREME_RETURN = 0.4
MAX_GAP_DAYS = 14
STALE_DAYS = 5
MIN_HISTORY_ROWS = 250


def check_prices(df: pd.DataFrame, today: pd.Timestamp | None = None) -> dict[str, pd.DataFrame]:
    today = pd.Timestamp(today if today is not None else pd.Timestamp.today().normalize())
    df = df.assign(date=pd.to_datetime(df["date"])).sort_values(["ticker", "date"])

    per_ticker = df.groupby("ticker").agg(
        category=("category", "first"),
        rows=("date", "size"),
        first=("date", "min"),
        last=("date", "max"),
    ).reset_index()

    gaps = df.assign(gap=df.groupby("ticker")["date"].diff().dt.days)
    gaps = gaps[gaps["gap"] > MAX_GAP_DAYS][["ticker", "date", "gap"]]

    return {
        "duplicates": df[df.duplicated(["date", "ticker"], keep=False)][["ticker", "date"]],
        "bad_close": df[df["close"].isna() | (df["close"] <= 0)][["ticker", "date", "close"]],
        "extreme_returns": df[df["daily_return"].abs() > EXTREME_RETURN][["ticker", "date", "daily_return"]],
        "gaps": gaps,
        "stale": per_ticker[per_ticker["last"] < today - pd.Timedelta(days=STALE_DAYS)],
        "short_history": per_ticker[per_ticker["rows"] < MIN_HISTORY_ROWS],
    }


def load_prices() -> pd.DataFrame:
    from google.cloud import bigquery

    query = f"""
    SELECT date, ticker, close, daily_return, category
    FROM `{PROJECT_ID}.{DATASET}.{PRICE_TABLE}`
    """
    return bigquery.Client(project=PROJECT_ID).query(query).to_dataframe()


def main():
    df = load_prices()
    problems = check_prices(df)

    print(f"{len(df)} rows, {df['ticker'].nunique()} tickers\n")
    for name, frame in problems.items():
        print(f"{name:16s} {len(frame)}")
        if len(frame):
            print(frame.head(10).to_string(index=False), "\n")


if __name__ == "__main__":
    main()
