from functools import cache

import pandas as pd
from google.cloud import bigquery

from backend.app.config import PROJECT_ID, DATASET, PRICE_TABLE

TABLE = f"{PROJECT_ID}.{DATASET}.{PRICE_TABLE}"


@cache
def get_client() -> bigquery.Client:
    return bigquery.Client(project=PROJECT_ID)


def load_price_data(ticker: str, days: int) -> pd.DataFrame:
    query = f"""
    SELECT date, close
    FROM `{TABLE}`
    WHERE ticker = @ticker
      AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL @days DAY)
    ORDER BY date ASC
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("ticker", "STRING", ticker),
            bigquery.ScalarQueryParameter("days", "INT64", days),
        ]
    )

    df = get_client().query(query, job_config=job_config).to_dataframe()

    if df.empty:
        raise ValueError(f"No data for ticker={ticker}")

    return df
