from google.cloud import bigquery
import pandas as pd
from backend.app.config import PROJECT_ID

client = bigquery.Client(project=PROJECT_ID)

TABLE = f"{PROJECT_ID}.market_data.market_prices_raw"


def load_price_data(ticker: str, days: int) -> pd.DataFrame:
    query = f"""
    SELECT *
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

    df = client.query(query, job_config=job_config).to_dataframe()

    if df.empty:
        raise ValueError(f"No data for ticker={ticker}")

    return df