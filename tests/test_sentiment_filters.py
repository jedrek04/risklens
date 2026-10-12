from backend.app.services.sentiment.assets import build_asset
from backend.app.services.sentiment.filters import dedupe, is_relevant
from tests.helpers import article


def test_company_name_must_be_capitalised_and_in_finance_context():
    visa = build_asset("V")

    assert is_relevant(article("Visa Stock (V) Closes at All-Time High"), visa)
    assert not is_relevant(
        article("TCS shares rally, shrug off H 1B visa suspension", "IT stocks add Rs 56,000 cr"), visa
    )


def test_gossip_without_finance_words_is_dropped():
    meta = build_asset("META")

    assert not is_relevant(article("Sony trolls Meta Platforms CEO with an Instagram ad"), meta)
    assert is_relevant(article("Meta Platforms shares jump after earnings beat"), meta)


def test_promotional_crypto_is_dropped():
    btc = build_asset("BTC-USD")

    assert is_relevant(article("Bitcoin falls below key support level"), btc)
    assert not is_relevant(article("Bitcoin Price Prediction: Remittix to explode 100x"), btc)
    assert not is_relevant(article("Bitcoin news today", source="TechBullion"), btc)
    assert not is_relevant(article("Bitcoin news today", url="https://techbullion.com/x"), btc)


def test_commodities_need_no_finance_word():
    assert is_relevant(article("Gold prices slip as dollar firms"), build_asset("GC=F"))
    assert not is_relevant(article("Silver medal for the home team"), build_asset("GC=F"))


def test_dedupe_by_url_and_title():
    a = article("Apple stock rises", url="u1")
    b = article("Apple stock rises!", url="u2")
    c = article("Something else", url="u1")
    d = article("Different story", url="u3")

    assert [x["url"] for x in dedupe([a, b, c, d])] == ["u1", "u3"]


def test_visa_immigration_stories_are_excluded():
    visa = build_asset("V")

    assert not is_relevant(article("1B Visa Concerns As TCS, Infosys Lead IT Rally", "IT stocks rally"), visa)
    assert not is_relevant(article("US tightens work visa rules, shares of IT firms fall"), visa)
    assert is_relevant(article("Visa and Mastercard shares slip as regulators target fees"), visa)
