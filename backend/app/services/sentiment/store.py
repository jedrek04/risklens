from datetime import datetime, timedelta
from functools import cache
from typing import Protocol

from google.cloud import bigquery

from backend.app.config import PROJECT_ID, DATASET, NEWS_TABLE, NEWS_FETCH_TABLE
from backend.app.services.risk.data_provider import get_client

HEADLINES_SCHEMA = [
    bigquery.SchemaField("ticker", "STRING"),
    bigquery.SchemaField("url", "STRING"),
    bigquery.SchemaField("title", "STRING"),
    bigquery.SchemaField("source", "STRING"),
    bigquery.SchemaField("published_at", "TIMESTAMP"),
    bigquery.SchemaField("positive", "FLOAT"),
    bigquery.SchemaField("negative", "FLOAT"),
    bigquery.SchemaField("neutral", "FLOAT"),
    bigquery.SchemaField("fetched_at", "TIMESTAMP"),
]
FETCHES_SCHEMA = [
    bigquery.SchemaField("ticker", "STRING"),
    bigquery.SchemaField("fetched_at", "TIMESTAMP"),
    bigquery.SchemaField("raw_articles", "INTEGER"),
    bigquery.SchemaField("kept_articles", "INTEGER"),
]


class NewsStore(Protocol):
    def last_fetches(self, tickers: list[str]) -> dict[str, datetime]: ...
    def headlines_for(self, tickers: list[str], since: datetime) -> dict[str, list[dict]]: ...
    def save_headlines(self, rows: list[dict]) -> None: ...
    def save_fetch(self, ticker: str, fetched_at: datetime, raw: int, kept: int) -> None: ...


class MemoryStore:
    def __init__(self):
        self.rows: list[dict] = []
        self.fetches: list[dict] = []

    def last_fetches(self, tickers):
        out = {}
        for f in self.fetches:
            if f["ticker"] in tickers and f["fetched_at"] > out.get(f["ticker"], f["fetched_at"] - timedelta(1)):
                out[f["ticker"]] = f["fetched_at"]
        return out

    def headlines_for(self, tickers, since):
        out = {t: [] for t in tickers}
        for r in self.rows:
            if r["ticker"] in out and r["published_at"] >= since:
                out[r["ticker"]].append(r)
        return out

    def save_headlines(self, rows):
        self.rows.extend(rows)

    def save_fetch(self, ticker, fetched_at, raw, kept):
        self.fetches.append({"ticker": ticker, "fetched_at": fetched_at, "raw": raw, "kept": kept})


class BigQueryStore:
    def __init__(self):
        self.client = get_client()
        self.headlines_table = f"{PROJECT_ID}.{DATASET}.{NEWS_TABLE}"
        self.fetches_table = f"{PROJECT_ID}.{DATASET}.{NEWS_FETCH_TABLE}"
        self._ready = False

    def _ensure_tables(self):
        if not self._ready:
            for table_id, schema in ((self.headlines_table, HEADLINES_SCHEMA), (self.fetches_table, FETCHES_SCHEMA)):
                self.client.create_table(bigquery.Table(table_id, schema=schema), exists_ok=True)
            self._ready = True

    def _query(self, sql: str, tickers: list[str], since: datetime | None = None):
        params = [bigquery.ArrayQueryParameter("tickers", "STRING", tickers)]
        if since is not None:
            params.append(bigquery.ScalarQueryParameter("since", "TIMESTAMP", since))
        config = bigquery.QueryJobConfig(query_parameters=params)
        return list(self.client.query(sql, job_config=config).result())

    def last_fetches(self, tickers):
        self._ensure_tables()
        rows = self._query(
            f"""
            SELECT ticker, MAX(fetched_at) AS fetched_at
            FROM `{self.fetches_table}`
            WHERE ticker IN UNNEST(@tickers)
            GROUP BY ticker
            """,
            tickers,
        )
        return {r["ticker"]: r["fetched_at"] for r in rows}

    def headlines_for(self, tickers, since):
        self._ensure_tables()
        rows = self._query(
            f"""
            SELECT ticker, url, title, source, published_at, positive, negative, neutral
            FROM `{self.headlines_table}`
            WHERE ticker IN UNNEST(@tickers) AND published_at >= @since
            ORDER BY published_at DESC
            """,
            tickers,
            since,
        )
        out = {t: [] for t in tickers}
        for r in rows:
            out[r["ticker"]].append(dict(r))
        return out

    def save_headlines(self, rows):
        if not rows:
            return
        self._ensure_tables()
        payload = [
            {**r, "published_at": r["published_at"].isoformat(), "fetched_at": r["fetched_at"].isoformat()}
            for r in rows
        ]
        errors = self.client.insert_rows_json(self.headlines_table, payload)
        if errors:
            raise RuntimeError(f"could not save headlines: {errors}")

    def save_fetch(self, ticker, fetched_at, raw, kept):
        self._ensure_tables()
        errors = self.client.insert_rows_json(
            self.fetches_table,
            [{"ticker": ticker, "fetched_at": fetched_at.isoformat(), "raw_articles": raw, "kept_articles": kept}],
        )
        if errors:
            raise RuntimeError(f"could not save fetch log: {errors}")
