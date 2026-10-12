import json
import re

NUMBER = re.compile(r"\d+(?:\.\d+)?")
MAX_WORDS = 450
CODE_WORD = re.compile(r"\b[A-Za-z]+(?:_[A-Za-z0-9]+)+\b")


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

    code_words = sorted(set(CODE_WORD.findall(text)))
    if code_words:
        problems.append("it uses internal field names instead of plain English: " + ", ".join(code_words))

    if len(text.split()) > MAX_WORDS:
        problems.append(f"it is longer than {MAX_WORDS} words")

    for field in ("risk_outlook", "unusual_activity", "news_sentiment", "summary"):
        if not getattr(draft, field).strip():
            problems.append(f"the {field} part is empty")

    if not draft.recommendations:
        problems.append("it has no recommendations")

    return problems
