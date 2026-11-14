"""Adversarial tests for the hard-rule claims filter (invest/claims.py).

The regex filter is the first line of defense; the AI compliance reviewer is the second. These tests pin
down what the regex layer must catch, what honest educational copy must pass, and (as xfail) the known
gaps that are too risky to close with a regex.

Run: python -m pytest -q tests/qa/test_claims_adversarial.py
"""
from pathlib import Path

import pytest

from invest.claims import find_violations

REPO = Path(__file__).resolve().parents[2]

MUST_CATCH = [
    # Promises and guarantees
    "This fund is guaranteed to beat the market.",
    "Returns are GUARANTEED.",
    "We guarantee you'll profit.",
    "Our picks are guaran-teed to grow.",
    "g u a r a n t e e d returns",
    "Guar4nteed gains, every year.",
    "Gu­aranteed returns.",                    # soft hyphen hidden inside the word
    "ｇｕａｒａｎｔｅｅｄ returns",  # full-width letters
    "A risk-free way to invest.",
    "Riskfree profits.",
    "Zero-risk returns.",
    "There's no risk.",
    "You literally cannot lose.",
    "You can't go wrong with index funds.",
    "You cant go wrong with this.",
    "This ETF is 100% safe.",
    "It's totally safe.",
    "Index funds are safe.",
    "This is a safe investment.",
    "It's a sure thing.",
    "Bitcoin is a sure bet.",
    "It's a no-brainer.",
    "Low risk, high reward.",
    "Steady gains with no downside.",
    "Consistent returns every year.",
    # Predictions
    "This stock will double by next year.",
    "This stock is going to double.",
    "The market will go up next year.",
    "Prices will rise.",
    "Stocks always go up.",
    "Your money will grow to $1 million.",
    "This will make you rich.",
    "You'll be a millionaire by 30.",
    "Earn 20% a month.",
    "This token could 1000x.",
    "It's the next Amazon.",
    # Advice and picks
    "You should buy Tesla.",
    "You should definitely buy index funds.",
    "You need to buy this stock.",
    "We recommend buying this ETF.",
    "Our top pick is NVDA.",
    "This stock is a must-buy.",
    "Strong buy.",
    "Our price target is $500.",
    "This is financial advice: buy it.",
    "Buy the dip.",
    # Cashtags and crypto hype
    "Grab some $NVDA.",
    "I'm all in on $GME.",
    "Stacking $btc every week.",
    "Doge to the moon!",
    "Get rich quick with crypto.",
    "Make easy money from home.",
    # Urgency
    "Act now!",
    "Dont miss out on this.",
    "Limited time offer.",
    "Only 3 spots left, hurry.",
    "Last chance to get in.",
    "Get in now before it moons.",
    "Buy now before it's too late.",
    # Quoting hype with no warning word around it is still hype
    'This fund is "guaranteed" to grow.',
]

MUST_PASS = [
    "Past performance doesn't guarantee future results.",
    "No investment is risk-free.",
    "Nothing in investing is guaranteed.",
    "There's no such thing as a guaranteed return.",
    "Investing is never a sure thing.",
    "No investment is a sure bet.",
    "Stocks don't always go up.",
    "Markets don't deliver steady returns.",
    "You probably won't become a millionaire from $25 a month, and that's okay.",
    "Investments can lose money, including the money you put in.",
    "Your balance could grow to about $247,000 at a hypothetical 6% a year.",
    "A hypothetical 6% a year is an assumption, not a prediction.",
    "Some people call an employer match free money.",
    "Index funds spread your money across hundreds of companies.",
    "Fees come out every year, whatever the market does.",
    "Stocks can fall 30% or more in a bad year.",
    "Stock prices will rise and fall over time.",
    "The 401(k) limit will rise to $25,500 in 2027.",
    "Nobody knows whether stocks will rise next year.",
    "No one can predict when the market will recover.",
    "If you need to sell during a downturn, you could lock in a loss.",
    "Savings accounts are insured, but investments aren't.",
    "Is it safe to keep money in a savings account? FDIC insurance has limits.",
    "It's safe to say nobody can time the market perfectly.",
    "There's no downside to checking your plan's match rules.",
    "A 24% APR works out to about 2% a month.",
    "FOMO can push people into decisions they regret.",
    "Buy now, pay later loans can add up.",
    "This will make more sense with an example.",
    "Some people buy index funds; others pick single stocks. Each has trade-offs.",
    "You should know the risks before you invest.",
    "Before you buy any investment, check the fees.",
    # Warning about hype means quoting or reporting it
    "Promised returns are a red flag.",
    "Be wary of anyone who says you can't lose.",
    "If someone says an investment is guaranteed, that's a red flag.",
    'Watch out for "guaranteed returns" pitches.',
    'Scammers often say "act now" to rush you.',
    'Phrases like "can\'t lose" and "to the moon" are classic red flags.',
    "Watch out for anyone promising low risk and high returns.",
    "3. Pressure: 'today only', countdown timers, 'everyone's getting in'.",
]

# Known gaps. The AI compliance reviewer (invest/agents/compliance.py) is the backstop for these.
XFAIL_CATCH = [
    ("It's free money from the market.",
     "'free money' can't be banned: the curriculum's own 401(k)-match lesson uses the phrase"),
    ("Guаranteed returns.",  # Cyrillic 'а'
     "homoglyphs from other scripts need a confusables table, not a regex"),
    ('Forget the red flags, this one is "guaranteed".',
     "a warning word in the same sentence lets quoted hype through (use vs. mention is a judgment call)"),
    ("Index funds are basically a savings account that pays 10%.",
     "implied promises without trigger words need the AI reviewer"),
    ("Everyone I know who bought Bitcoin early is rich now.",
     "testimonial-style hype has no fixed wording"),
]


@pytest.mark.parametrize("text", MUST_CATCH)
def test_hype_and_advice_are_caught(text):
    assert find_violations(text), text


@pytest.mark.parametrize("text", MUST_PASS)
def test_honest_education_passes(text):
    assert find_violations(text) == [], text


@pytest.mark.parametrize("text", [pytest.param(t, marks=pytest.mark.xfail(reason=r, strict=True)) for t, r in XFAIL_CATCH])
def test_known_gaps(text):
    """strict=True: if a gap gets closed, this fails so the case can move to MUST_CATCH."""
    assert find_violations(text), text


def test_suite_size_meets_the_brief():
    assert len(MUST_CATCH) >= 40 and len(MUST_PASS) >= 30


@pytest.mark.parametrize("page", ["index.html", "rules.html", "learn/index.html"])
def test_site_pages_pass_the_filter(page):
    """Team rule 1: consumer copy must pass the filter. rules.html used to fail it."""
    assert find_violations((REPO / "invest" / "site" / page).read_text()) == []


def test_hits_explain_the_match():
    hits = find_violations("Act now, this coin is guaranteed to 10x.")
    assert len(hits) == 3 and all("matched" in h for h in hits)
