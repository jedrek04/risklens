import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID", "risklens-498721")
DATASET = os.getenv("DATASET", "market_data")
PRICE_TABLE = os.getenv("PRICE_TABLE", "market_prices_raw")
NEWS_TABLE = os.getenv("NEWS_TABLE", "news_headlines")
NEWS_FETCH_TABLE = os.getenv("NEWS_FETCH_TABLE", "news_fetches")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
