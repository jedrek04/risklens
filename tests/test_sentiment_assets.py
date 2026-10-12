import pytest

from backend.app.services.sentiment.assets import build_asset, clean_name


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Meta Platforms Class A", "Meta Platforms"),
        ("Goldman Sachs Group (The)", "Goldman Sachs"),
        ("Texas Instruments Incorporated", "Texas Instruments"),
        ("Inditex (Zara)", "Inditex"),
        ("Strategy Inc Variable Rate Series A Perpetual Stretch Preferred Stock", "Strategy"),
        ("Credo Technology Group Holding Ltd Ordinary Shares", "Credo Technology"),
        ("Apple", "Apple"),
    ],
)
def test_clean_name(raw, expected):
    assert clean_name(raw) == expected


def test_unknown_ticker():
    with pytest.raises(ValueError, match="Unknown ticker"):
        build_asset("NOPE123")


def test_stock_query_is_case_sensitive_and_needs_finance_context():
    a = build_asset("V")

    assert a.terms == ("Visa",)
    assert a.case_sensitive and a.needs_finance
    assert "stock" in a.query


def test_crypto_and_commodities_do_not_need_finance_words():
    for t in ("BTC-USD", "GC=F", "CL=F"):
        assert not build_asset(t).needs_finance


def test_overrides_for_etfs():
    assert build_asset("TLT").terms == ("treasury",)
    assert "S&P 500" in build_asset("SPY").query


def test_company_name_variants_are_searched_and_matched():
    a = build_asset("XOM")

    assert {"Exxon Mobil", "ExxonMobil", "Exxon"} <= set(a.terms)
    assert '"ExxonMobil"' in a.query and '"Exxon"' in a.query


def test_generic_first_words_are_not_used_as_aliases():
    assert "Bank" not in build_asset("BAC").terms
    assert "Bank of America" in build_asset("BAC").terms


def test_all_caps_company_names_also_match_normal_capitalisation():
    from backend.app.services.sentiment.filters import is_relevant
    from tests.helpers import article

    nvda = build_asset("NVDA")

    assert "Nvidia" in nvda.terms
    assert is_relevant(article("Nvidia shares fall after OpenAI revenue disclosure"), nvda)
