from google.cloud import bigquery
from backend.app.config import PROJECT_ID, DATASET, PRICE_TABLE
from backend.app.services.market_data.data_fetcher import fetch_all_prices

client = bigquery.Client(project=PROJECT_ID)

STAGING_TABLE = f"{PROJECT_ID}.{DATASET}.market_prices_staging"
TARGET_TABLE = f"{PROJECT_ID}.{DATASET}.{PRICE_TABLE}"


def recreate_staging():
    client.delete_table(STAGING_TABLE, not_found_ok=True)

    schema = [
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

    client.create_table(bigquery.Table(STAGING_TABLE, schema=schema))


def load_to_staging(df):
    job = client.load_table_from_dataframe(
        df,
        STAGING_TABLE,
        job_config=bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND"
        )
    )
    job.result()

def ensure_target_table():

    schema = [
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

    client.create_table(
        bigquery.Table(
            TARGET_TABLE,
            schema=schema
        ),
        exists_ok=True
    )

def merge_staging_to_target():
    query = f"""
    MERGE `{TARGET_TABLE}` T
    USING (
        SELECT *
        FROM `{STAGING_TABLE}`
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY date, ticker
            ORDER BY date DESC
        ) = 1
    ) S
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
        INSERT (
            date, open, high, low, close, volume,
            ticker, daily_return, name, category
        )
        VALUES (
            S.date, S.open, S.high, S.low, S.close, S.volume,
            S.ticker, S.daily_return, S.name, S.category
        )
    """

    job = client.query(query)
    job.result()


def clear_staging():
    client.delete_table(STAGING_TABLE, not_found_ok=True)


def run(days: int):
    print(f"STARTING MARKET DATA LOAD (lookback={days} days)")

    df, failed = fetch_all_prices(days=days)

    print(f"Fetched rows: {len(df)}")
    print(f"Failed tickers: {len(failed)}")

    if df.empty:
        print("No data")
        return

    df["date"] = df["date"].astype("datetime64[ns]").dt.date

    df = df.drop_duplicates(subset=["date", "ticker"])

    # ensure numeric safety
    for col in ["open", "high", "low", "close", "volume", "daily_return"]:
        df[col] = df[col].astype("float64")


    recreate_staging()

    ensure_target_table()

    print("Loading staging...")
    load_to_staging(df)

    print("Merging...")
    merge_staging_to_target()

    print("Cleaning staging...")
    clear_staging()

    print("DONE")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7)

    args = parser.parse_args()

    run(days=args.days)