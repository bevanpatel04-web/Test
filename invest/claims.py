"""Hard rules on investing claims, checked before anything reaches the founder or the website.

The product stays on the "education, not advice" side of securities rules by being impersonal
(no recommendations for a person or a security), never promising returns, and disclosing risk.
These rules catch the obvious failures; an AI compliance review catches the subtle ones.
"""
from __future__ import annotations

import re

_I = re.IGNORECASE
_APOS = r"(?:'|’)"

BANNED = [
    re.compile(r"\bguarantee[ds]?\b", _I),                              # promised outcomes
    re.compile(r"\brisk[- ]free\b", _I),
    re.compile(r"\b(?:zero|no)\s+risk\b", _I),
    re.compile(rf"\bcan{_APOS}?t\s+lose\b|\bcannot\s+lose\b", _I),
    re.compile(r"\bsafe\s+(?:bet|investments?|stocks?|returns?)\b", _I),
    re.compile(r"\b(?:steady|consistent|reliable)\s+returns?\b", _I),
    re.compile(r"\bwill\s+(?:earn|return|double|grow\s+to)\b", _I),     # predictions: use "could" + assumptions
    re.compile(r"\bwill\s+make\s+(?:you\s+)?(?:money|rich|\$)", _I),
    re.compile(r"\bget\s+rich\b", _I),
    re.compile(r"\b(?:easy|fast|quick)\s+money\b", _I),
    re.compile(r"\bdouble\s+your\s+money\b", _I),
    re.compile(r"\b\d{2,4}x\b", _I),                                   # "10x", "100x"
    re.compile(r"\bto\s+the\s+moon\b", _I),
    re.compile(r"\byou\s+(?:should|must|need\s+to|have\s+to)\s+(?:buy|sell|invest\s+in|put\s+(?:your\s+)?money\s+in(?:to)?)\b", _I),
    re.compile(r"\b(?:we|i)\s+recommend\s+(?:buying|selling|investing\s+in)\b", _I),
    re.compile(r"\b(?:buy|sell)\s+(?:(?:this|these|it|them)\s+)?now\b", _I),
    re.compile(r"\bprice\s+target\b", _I),
    re.compile(r"\$[A-Z]{1,5}\b"),                                      # cashtags like $TSLA (case-sensitive)
    re.compile(rf"\bact\s+now\b|\bdon{_APOS}?t\s+miss\s+out\b|\blimited\s+time\b", _I),
]

_NEG = rf"(?:not|never|isn{_APOS}?t|aren{_APOS}?t|doesn{_APOS}?t|does\s+not|don{_APOS}?t|do\s+not|can{_APOS}?t|cannot|won{_APOS}?t)"
_TARGET = r"(?:guarantee[ds]?|risk[- ]free|safe)"

# Honest negations ("no investment is risk-free", "past performance doesn't guarantee...") are allowed.
ALLOWED_CONTEXTS = [
    re.compile(rf"\b{_NEG}\s+(?:\w+\s+){{0,2}}?{_TARGET}\b", _I),     # "doesn't guarantee", "isn't a safe bet"
    re.compile(r"\bno\s+guarantees?\b", _I),
    re.compile(r"\bno\s+risk[- ]free\b", _I),
    re.compile(rf"\bno\s+(?:\w+\s+){{0,3}}?(?:is|are)\s+(?:ever\s+)?{_TARGET}\b", _I),  # "no investment is risk-free"
    re.compile(rf"\bnothing\s+(?:\w+\s+){{0,2}}?(?:is|{_APOS}s)\s+(?:ever\s+)?guaranteed\b", _I),
    re.compile(rf"\bno\s+such\s+thing\s+as\s+(?:a\s+)?{_TARGET}\b", _I),
    re.compile(r"\bwithout\s+(?:any\s+)?guarantees?\b", _I),
    re.compile(r"\bbuy\s+now,?\s+pay\s+later\b", _I),                   # the BNPL product name
]


def find_violations(text: str) -> list[str]:
    cleaned = text
    for rx in ALLOWED_CONTEXTS:
        cleaned = rx.sub(" ", cleaned)
    hits = []
    for rx in BANNED:
        for m in rx.finditer(cleaned):
            start = max(0, m.start() - 40)
            hits.append(f"…{cleaned[start:m.end() + 40].strip()}… (matched '{m.group(0)}')")
    return hits


CLAIMS_POLICY = """Education-only policy (strict):
- Explain how investing works in general. Never tell the reader what to buy, sell or hold, or what to do with
  their own money. Describe options and trade-offs neutrally ("some people...", "one approach is...", "the trade-off is...").
- Never name or recommend a specific stock, fund, ETF, crypto coin, brokerage or app. Broad categories are fine
  (index funds, target-date funds, Roth IRA, 401(k), high-yield savings account).
- Never promise or predict returns. Any number about future growth is a labeled hypothetical that states its
  assumptions (amount, rate, years), uses "could", and says it isn't a prediction.
- Whenever you mention growth or returns, also mention risk: investments can fall in value, including the money you put in.
- Only use statistics and historical figures from the verified facts you are given, with their date and source.
  Never invent numbers. Don't cherry-pick only good periods.
- Hypothetical arithmetic must be simple and correct. If you're not sure of a calculation, leave it out.
- No hype or pressure: no "get rich", "easy money", "10x", "to the moon", "act now", "don't miss out",
  and no testimonials or screenshots about anyone's returns.
- No personal tax or legal advice. General rules from the verified facts are fine; point people to official
  sources or a licensed professional for their own situation.
- Audience is adults 18-25. Never address or target minors.
- Never cheer for or attack any company, coin or asset."""
