from google.cloud import bigquery

from backend.app.config import PROJECT_ID, DATASET, PRICE_TABLE
from backend.app.services.market_data.data_fetcher import fetch_all_prices

client = bigquery.Client(project=PROJECT_ID)

STAGING_TABLE = f"{PROJECT_ID}.{DATASET}.market_prices_staging"
TARGET_TABLE = f"{PROJECT_ID}.{DATASET}.{PRICE_TABLE}"

SCHEMA = [
    bigquery.SchemaField("date", "DATE"),
    bigquery.SchemaField("ticker", "STRING"),
    bigquery.SchemaField("open", "FLOAT"),
    bigquery.SchemaField("high", "FLOAT"),
    bigquery.SchemaField("low", "FLOAT"),
    bigquery.SchemaField("close", "FLOAT"),
    bigquery.SchemaField("volume", "FLOAT"),
    bigquery.SchemaField("daily_return", "FLOAT"),
    bigquery.SchemaField("name", "STRING"),
    bigquery.SchemaField("category", "STRING"),
]

MERGE_QUERY = f"""
MERGE `{TARGET_TABLE}` T
USING `{STAGING_TABLE}` S
ON T.date = S.date AND T.ticker = S.ticker
WHEN MATCHED THEN UPDATE SET
    open = S.open,
    high = S.high,
    low = S.low,
    close = S.close,
    volume = S.volume,
    daily_return = S.daily_return,
    name = S.name,
    category = S.category
WHEN NOT MATCHED THEN
    INSERT (date, ticker, open, high, low, close, volume, daily_return, name, category)
    VALUES (S.date, S.ticker, S.open, S.high, S.low, S.close, S.volume,
            S.daily_return, S.name, S.category)
"""


def run(days: int):
    print(f"STARTING MARKET DATA LOAD (lookback={days} days)")

    df, failed = fetch_all_prices(days=days)
    print(f"Fetched rows: {len(df)}, failed tickers: {len(failed)}")

    if df.empty:
        print("No data")
        return

    df = df.drop_duplicates(subset=["date", "ticker"])
    for col in ["open", "high", "low", "close", "volume", "daily_return"]:
        df[col] = df[col].astype("float64")

    client.delete_table(STAGING_TABLE, not_found_ok=True)
    client.create_table(bigquery.Table(STAGING_TABLE, schema=SCHEMA))
    client.create_table(bigquery.Table(TARGET_TABLE, schema=SCHEMA), exists_ok=True)

    print("Loading staging...")
    client.load_table_from_dataframe(
        df,
        STAGING_TABLE,
        job_config=bigquery.LoadJobConfig(write_disposition="WRITE_APPEND"),
    ).result()

    print("Merging...")
    client.query(MERGE_QUERY).result()

    client.delete_table(STAGING_TABLE, not_found_ok=True)
    print("DONE")
