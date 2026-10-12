import argparse
import html
import json
import subprocess
import tempfile
import time
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx

URL = "https://risklens-api-935079797801.europe-west1.run.app"

PORTFOLIO = [
    {"ticker": "AAPL", "weight": 0.3},
    {"ticker": "MSFT", "weight": 0.2},
    {"ticker": "SPY", "weight": 0.2},
    {"ticker": "GC=F", "weight": 0.15},
    {"ticker": "BTC-USD", "weight": 0.15},
]

STYLE = """
:root{--ink:#1d2433;--muted:#667085;--line:#e4e7ec;--accent:#1f5eff;--bg:#f3f5f9}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);font:14px/1.55 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink)}
.page{width:794px;min-height:1000px;margin:24px auto;background:#fff;padding:48px 56px 40px;box-shadow:0 2px 24px rgba(16,24,40,.12)}
.brand{display:flex;justify-content:space-between;align-items:baseline;border-bottom:2px solid var(--accent);padding-bottom:10px;margin-bottom:22px}
.brand b{font-size:15px;letter-spacing:.04em;color:var(--accent)}
.brand span{font-size:12px;color:var(--muted)}
h1{font-size:24px;margin:0 0 14px}
h2{font-size:13px;text-transform:uppercase;letter-spacing:.07em;color:var(--accent);margin:20px 0 4px}
p{margin:0 0 6px}
ul{margin:6px 0 0 18px;padding:0}
li{margin-bottom:4px}
.stats{display:flex;gap:12px;margin:6px 0 18px}
.stat{flex:1;border:1px solid var(--line);border-radius:8px;padding:10px 12px}
.stat .v{font-size:22px;font-weight:650}
.stat .l{font-size:11px;color:var(--muted)}
table{width:100%;border-collapse:collapse;font-size:12px;margin:2px 0 6px}
th{text-align:left;font-weight:600;color:var(--muted);border-bottom:1px solid var(--line);padding:4px 0}
td{padding:4px 0;border-bottom:1px solid var(--line)}
.n{text-align:right;font-variant-numeric:tabular-nums}
th.n{text-align:right}
.t{color:var(--muted);font-size:11px}
.foot{margin-top:26px;padding-top:10px;border-top:1px solid var(--line);font-size:11px;color:var(--muted);font-style:italic}
.meta{font-size:11px;color:var(--muted);margin-top:8px}
@media print{body{background:#fff}.page{box-shadow:none;margin:0;width:auto}}
"""


def get_token() -> str:
    return subprocess.check_output(["gcloud", "auth", "print-identity-token"], text=True).strip()


def render(data: dict) -> str:
    e = html.escape
    report, facts, meta = data["report"], data["facts"]["risk"], data["meta"]

    sections = ""
    for s in report["sections"]:
        bullets = ""
        if s.get("bullets"):
            bullets = "<ul>" + "".join(f"<li>{e(b)}</li>" for b in s["bullets"]) + "</ul>"
        sections += f"<section><h2>{e(s['heading'])}</h2><p>{e(s['body'])}</p>{bullets}</section>"

    rows = "".join(
        f"<tr><td>{e(a['name'])} <span class='t'>{e(a['ticker'])}</span></td>"
        f"<td class='n'>{e(a['weight'])}</td><td class='n'>{e(a['annualized_volatility'])}</td></tr>"
        for a in facts["assets"]
    )
    stats = "".join(
        f"<div class='stat'><div class='v'>{e(value)}</div><div class='l'>{e(label)}</div></div>"
        for label, value in [
            (f"Value at Risk, {facts['confidence']}, {facts['horizon_days']} days", facts["var"]),
            ("Expected shortfall", facts["cvar"]),
            ("Portfolio volatility", facts["portfolio_volatility"]),
        ]
    )

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>RiskLens report</title>
<style>{STYLE}</style></head><body><div class="page">
<div class="brand"><b>RISKLENS</b><span>Portfolio risk report</span></div>
<h1>{e(report['title'])}</h1>
<div class="stats">{stats}</div>
<table><tr><th>Holding</th><th class="n">Weight</th><th class="n">Annualized volatility</th></tr>{rows}</table>
{sections}
<div class="foot">{e(data['disclaimer'])}</div>
<div class="meta">Generated {e(meta['generated_at'][:16].replace('T', ' '))} UTC with {e(meta['model'])}.</div>
</div></body></html>"""


def main():
    parser = argparse.ArgumentParser(description="Run the full RiskLens flow in the cloud and show the report.")
    parser.add_argument("--portfolio", help='JSON list of {"ticker", "weight"}; default is a 5 asset demo portfolio')
    parser.add_argument("--runs", type=int, default=1, help="generate the report this many times from the same results")
    parser.add_argument("--no-open", action="store_true", help="do not open the preview in the browser")
    args = parser.parse_args()

    portfolio = json.loads(args.portfolio) if args.portfolio else PORTFOLIO
    out_dir = Path(tempfile.gettempdir()) / "risklens"
    out_dir.mkdir(exist_ok=True)

    client = httpx.Client(
        base_url=URL, headers={"Authorization": f"Bearer {get_token()}"}, timeout=300
    )

    print("Portfolio:", ", ".join(f"{a['ticker']} {a['weight']:.0%}" for a in portfolio))
    print("\nStep 1: risk, anomalies and sentiment (in parallel)")

    def analyse(name: str) -> dict:
        start = time.time()
        r = client.post(f"/risk/{name}", json={"portfolio": portfolio})
        print(f"  {name:10s} HTTP {r.status_code}  {time.time() - start:5.1f}s")
        r.raise_for_status()
        return r.json()

    names = ("portfolio", "anomalies", "sentiment")
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {n: pool.submit(analyse, n) for n in names}
        results = {n: f.result() for n, f in futures.items()}

    body = {
        "portfolio": portfolio,
        "risk": results["portfolio"],
        "anomalies": results["anomalies"],
        "sentiment": results["sentiment"],
    }
    (out_dir / "request.json").write_text(json.dumps(body))

    print("\nStep 2: report")
    last = None
    for i in range(1, args.runs + 1):
        start = time.time()
        r = client.post("/risk/report", json=body)
        took = time.time() - start

        if r.status_code != 200:
            print(f"  run {i}: HTTP {r.status_code}  {took:5.1f}s  {r.text[:300]}")
            continue

        data = r.json()
        last = data
        print(
            f"  run {i}: HTTP 200  {took:5.1f}s  attempts={data['meta']['attempts']}  "
            f"words={len(data['markdown'].split())}  rejected={data['meta']['rejected_draft_issues']}"
        )

    if last is None:
        raise SystemExit("\nNo report was generated.")

    (out_dir / "report.json").write_text(json.dumps(last))
    preview = out_dir / "report.html"
    preview.write_text(render(last))

    print("\n" + last["markdown"])
    print(f"Files: {out_dir}  (report.json, report.html, request.json)")

    if not args.no_open:
        webbrowser.open(preview.as_uri())


if __name__ == "__main__":
    main()
