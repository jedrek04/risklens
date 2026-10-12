import re

from backend.app.services.sentiment.assets import FINANCE_TERMS, NewsAsset

BLOCKED_SOURCES = ("techbullion",)
BLOCKED_TITLES = re.compile(
    r"price prediction|presale|pre-sale|100x|referral code|remittix|pepeto|airdrop|how to buy",
    re.IGNORECASE,
)


def _mentions(text: str, terms: tuple[str, ...], case_sensitive: bool) -> bool:
    flags = 0 if case_sensitive else re.IGNORECASE
    return any(re.search(rf"(?<!\w){re.escape(t)}(?!\w)", text, flags) for t in terms)


def is_relevant(article: dict, asset: NewsAsset) -> bool:
    if any(b in article["source"].lower() or b in article["url"].lower() for b in BLOCKED_SOURCES):
        return False

    if BLOCKED_TITLES.search(article["title"]):
        return False

    text = f"{article['title']} {article['description']}"

    if asset.exclude and asset.exclude.search(text):
        return False

    where = article["title"] if asset.title_only else text
    if not _mentions(where, asset.terms, asset.case_sensitive):
        return False

    return not asset.needs_finance or bool(FINANCE_TERMS.search(text))


def dedupe(articles: list[dict]) -> list[dict]:
    seen_urls, seen_titles, out = set(), set(), []

    for a in articles:
        title = re.sub(r"\W+", " ", a["title"].lower()).strip()
        if a["url"] in seen_urls or title in seen_titles:
            continue
        seen_urls.add(a["url"])
        seen_titles.add(title)
        out.append(a)

    return out
