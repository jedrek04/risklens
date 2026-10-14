import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.app.services.market_data.tickers import get_all_tickers

OUT = ROOT / "frontend" / "src" / "data" / "tickers.json"

rows = [{"symbol": t["symbol"], "name": t["name"], "category": t["category"]} for t in get_all_tickers()]
OUT.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")))
print(f"wrote {len(rows)} tickers to {OUT.relative_to(ROOT)}")
