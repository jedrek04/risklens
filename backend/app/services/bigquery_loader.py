from google.cloud import bigquery
from backend.app.config import PROJECT_ID, DATASET, PRICE_TABLE

# BigQuery client
client = bigquery.Client(project=PROJECT_ID)


def load_dataframe(df):
    """
    Upload pandas DataFrame to BigQuery table.
    """

    table_id = f"{PROJECT_ID}.{DATASET}.{PRICE_TABLE}"

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND"
    )

    job = client.load_table_from_dataframe(
        df,
        table_id,
        job_config=job_config
    )

    job.result()

    print(f"Loaded {len(df)} rows into {table_id}")


if __name__ == "__main__":
    # simple sanity check: list datasets

    datasets = list(client.list_datasets())

    print("DATASETS:")
    for d in datasets:
        print("-", d.dataset_id)