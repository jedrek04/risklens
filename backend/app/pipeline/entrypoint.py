import argparse

from backend.app.pipeline.run_market_data_load import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7)
    run(days=parser.parse_args().days)
