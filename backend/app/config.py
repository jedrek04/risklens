import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID", "")
DATASET = os.getenv("DATASET", "market_data")
PRICE_TABLE = os.getenv("PRICE_TABLE", "market_prices_raw")