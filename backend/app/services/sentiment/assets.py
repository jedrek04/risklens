import re
from dataclasses import dataclass

from backend.app.services.market_data.tickers import get_all_tickers

FINANCE_TERMS = re.compile(
    r"\b(stock|stocks|share|shares|earnings|investor|investors|analyst|analysts|revenue|profit|"
    r"market|markets|wall street|dividend|guidance|quarter|price target|upgrade|downgrade|ipo|"
    r"valuation|rally|sell-off|selloff|etf|fund|yield|yields)\b",
    re.IGNORECASE,
)

CUT_AT = re.compile(
    r"\s+(Class [A-Z]\b|Ordinary Shares?|American Depositary|Depositary|Variable Rate|Common Stock|"
    r"common stock|Capital Stock|\d+\.\d+%)"
)
SUFFIXES = re.compile(
    r"\s+(Incorporated|Inc\.?|Corporation|Corp\.?|Company|Co\.?|Ltd\.?|Limited|LLC|plc|PLC|Holdings?|Group)$"
)

GENERIC_FIRST_WORDS = {
    "general", "united", "american", "first", "national", "new", "bank", "china", "international",
    "global", "western", "southern", "northern", "north", "south", "east", "west", "great", "grand",
    "royal", "pacific", "atlantic", "the",
}

# queries and match terms for assets where the name alone gives bad news results
OVERRIDES = {
    "CL=F": ('"crude oil" OR "WTI crude" OR "oil prices"', ("crude", "oil")),
    "BZ=F": ('"Brent crude" OR "Brent oil"', ("brent",)),
    "NG=F": ('"natural gas" AND (price OR prices)', ("natural gas",)),
    "LE=F": ('"live cattle" OR "cattle prices"', ("cattle",)),
    "HE=F": ('"lean hogs" OR "hog prices"', ("hog",)),
    "OJ=F": ('"orange juice" AND (price OR prices)', ("orange juice",)),
    "GLD": ('"gold price" OR "gold prices"', ("gold",)),
    "DIA": ('"Dow Jones" AND (stocks OR index OR industrial)', ("dow",)),
    "UUP": ('"US dollar" AND ("dollar index" OR DXY)', ("dollar",)),
    "SPY": ('"S&P 500"', ("s&p 500",)),
    "VOO": ('"S&P 500"', ("s&p 500",)),
    "CSPX.AS": ('"S&P 500"', ("s&p 500",)),
    "SXR8.DE": ('"S&P 500"', ("s&p 500",)),
    "VUAA.L": ('"S&P 500"', ("s&p 500",)),
    "QQQ": ('"Nasdaq 100" OR "Nasdaq-100" OR Nasdaq', ("nasdaq",)),
    "IWM": ('"Russell 2000"', ("russell 2000",)),
    "TLT": ('"Treasury yields" OR "Treasury bonds"', ("treasury",)),
    "IEF": ('"Treasury yields" OR "Treasury bonds"', ("treasury",)),
    "SHY": ('"Treasury yields" OR "Treasury bills"', ("treasury",)),
    "XLE": ('"energy stocks" OR "oil stocks"', ("energy stocks", "oil stocks")),
    "VDE": ('"energy stocks" OR "oil stocks"', ("energy stocks", "oil stocks")),
    "GDX": ('"gold miners" OR "gold mining stocks"', ("gold miner", "gold mining")),
    "EEM": ('"emerging markets"', ("emerging market",)),
    "VWO": ('"emerging markets"', ("emerging market",)),
    "IWDA.AS": ('"MSCI World" OR "global stocks"', ("msci world", "global stocks")),
    "ACWI": ('"MSCI ACWI" OR "global stocks"', ("msci acwi", "global stocks")),
    "VT": ('"MSCI ACWI" OR "global stocks"', ("msci acwi", "global stocks")),
}


# headlines that match the name but are about something else
EXCLUDES = {
    "V": re.compile(r"\b1B\b|H-?1B|\bvisa (fee|fees|curb|curbs|suspension|rules|ban|policy|application|applications|holders?)\b|\b(work|student|tourist|travel|entry|immigration) visas?\b", re.IGNORECASE),
}


@dataclass(frozen=True)
class NewsAsset:
    ticker: str
    name: str
    category: str
    query: str
    terms: tuple[str, ...]
    case_sensitive: bool
    needs_finance: bool
    exclude: re.Pattern | None = None
    title_only: bool = False


def clean_name(name: str) -> str:
    name = re.sub(r"\s*\([^)]*\)", "", name)
    name = CUT_AT.split(name)[0].strip()
    while True:
        shorter = SUFFIXES.sub("", name).strip()
        if shorter == name:
            return name
        name = shorter


def aliases(name: str) -> tuple[str, ...]:
    words = name.split()
    out = [name]
    if name.isupper() and len(name) > 3:
        out.append(name.capitalize())
    if len(words) > 1:
        out.append("".join(words))
        if len(words[0]) >= 4 and words[0].lower() not in GENERIC_FIRST_WORDS:
            out.append(words[0])
    return tuple(out)


def _lookup() -> dict[str, dict]:
    return {t["symbol"]: t for t in get_all_tickers()}


def build_asset(ticker: str) -> NewsAsset:
    info = _lookup().get(ticker)
    if info is None:
        raise ValueError(f"Unknown ticker: {ticker}")

    name = clean_name(info["name"])
    category = info["category"]
    inherently_financial = category in ("commodities", "crypto")

    if ticker in OVERRIDES:
        query, terms = OVERRIDES[ticker]
        return NewsAsset(ticker, name, category, query, terms, False, not inherently_financial)

    if category == "commodities":
        return NewsAsset(ticker, name, category, f'"{name} price" OR "{name} prices"', (name.lower(),), False, False)

    if category == "crypto":
        return NewsAsset(ticker, name, category, f"{name} AND (crypto OR cryptocurrency OR price)", (name.lower(),), False, False)

    base = ticker.split(".")[0]

    if category.startswith("etf") or category == "market_indexes":
        return NewsAsset(ticker, name, category, f'"{base}" AND (ETF OR fund)', (base,), True, True)

    names = aliases(name)
    terms = names + (base,) if len(base) >= 3 and base.isalpha() else names
    quoted = " OR ".join(f'"{n}"' for n in names)
    return NewsAsset(
        ticker, name, category, f"({quoted}) AND (stock OR stocks OR shares OR earnings)", terms, True, True,
        EXCLUDES.get(ticker),
        True,
    )
