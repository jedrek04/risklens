import json
import re

NUMBER = re.compile(r"\d+(?:\.\d+)?")
MAX_WORDS = 550


def _numbers(text: str) -> list[float]:
    return [float(n) for n in NUMBER.findall(text)]


def draft_text(draft) -> str:
    parts = [draft.title, draft.risk_outlook, draft.unusual_activity, draft.news_sentiment, draft.summary]
    return "\n".join(parts + list(draft.recommendations))


def check(draft, facts: dict) -> list[str]:
    allowed = set(_numbers(json.dumps(facts)))
    text = draft_text(draft)
    problems = []

    unknown = sorted({n for n in NUMBER.findall(text) if float(n) not in allowed}, key=float)
    if unknown:
        problems.append("it contains numbers that are not in the fact sheet: " + ", ".join(unknown))

    if len(text.split()) > MAX_WORDS:
        problems.append(f"it is longer than {MAX_WORDS} words")

    for field in ("risk_outlook", "unusual_activity", "news_sentiment", "summary"):
        if not getattr(draft, field).strip():
            problems.append(f"the {field} part is empty")

    if not draft.recommendations:
        problems.append("it has no recommendations")

    return problems
