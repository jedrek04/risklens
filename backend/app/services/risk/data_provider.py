from functools import cache

import pandas as pd
from google.cloud import bigquery

from backend.app.config import PROJECT_ID, DATASET, PRICE_TABLE

TABLE = f"{PROJECT_ID}.{DATASET}.{PRICE_TABLE}"


@cache
def get_client() -> bigquery.Client:
    return bigquery.Client(project=PROJECT_ID)


def load_prices(tickers: list[str], days: int) -> pd.DataFrame:
    query = f"""
    SELECT ticker, date, close, volume
    FROM `{TABLE}`
    WHERE ticker IN UNNEST(@tickers)
      AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL @days DAY)
    ORDER BY ticker, date
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("tickers", "STRING", tickers),
            bigquery.ScalarQueryParameter("days", "INT64", days),
        ]
    )

    df = get_client().query(query, job_config=job_config).to_dataframe()

    missing = sorted(set(tickers) - set(df["ticker"]))
    if missing:
        raise ValueError(f"No data for ticker(s): {', '.join(missing)}")

    return df
