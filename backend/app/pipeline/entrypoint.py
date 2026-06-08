import argparse
from backend.app.pipeline.run_market_data_load import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, required=True)

    args = parser.parse_args()

    run(days=args.days)