"""Hard rules on investing claims, checked before anything reaches the founder or the website.

The product stays on the "education, not advice" side of securities rules by being impersonal
(no recommendations for a person or a security), never promising returns, and disclosing risk.
These rules catch the obvious failures; an AI compliance review catches the subtle ones.
"""
from __future__ import annotations

import re
import unicodedata

_I = re.IGNORECASE
_APOS = r"(?:'|’)"
_SEP = r"[\W_]?"  # one optional separator between letters: "guaran-teed", "g u a r a n t e e d"
_LOOKALIKE = {"a": "[a4@]", "e": "[e3]", "i": "[i1!]", "o": "[o0]", "s": "[s5$]"}


def _fuzzy(word: str) -> str:
    """Match a word even when it's split up ("guaran-teed") or uses look-alike digits ("guar4nteed")."""
    return _SEP.join(_LOOKALIKE.get(c, re.escape(c)) for c in word)


_GUARANTEE = rf"(?:{_fuzzy('guarantee')}(?:[ds]|ing)?|gaurantee[ds]?)"
_MARKET = r"(?:stocks?|(?:the\s+)?markets?|prices?|shares?|bitcoin|crypto|it|this\s+(?:stock|coin|token|fund|etf|one))"
_WILL = rf"(?:\s+will|{_APOS}ll|\s+(?:is|are)\s+going\s+to|\s+gonna)"

BANNED = [
    # Promised outcomes and safety claims
    re.compile(rf"\b{_GUARANTEE}\b", _I),
    re.compile(r"\brisk[\W_]?free\b", _I),
    re.compile(r"\b(?:zero|no)[\W_]?risk\b", _I),
    re.compile(rf"\bcan{_APOS}?t\s+lose\b|\bcan(?:not|\s+not)\s+lose\b", _I),
    re.compile(rf"\bcan(?:{_APOS}?t|not|\s+not)\s+go\s+wrong\b", _I),
    re.compile(rf"\bcan{_APOS}?t[\W_]miss\s+(?:opportunit|deal|investment|stock|pick|play|trade|coin)", _I),
    re.compile(r"\bsafe\s+(?:bet|investments?|stocks?|returns?)\b", _I),
    re.compile(r"\b(?:100\s*%|100\s+percent|totally|completely|perfectly|absolutely|super|extremely)\s+safe\b", _I),
    re.compile(rf"\b(?:is|are|it{_APOS}s|they{_APOS}re|that{_APOS}s)\s+(?:(?:really|very|always|so|pretty)\s+)?safe\b"
               r"(?!\s+to\s+(?:say|use)|\s+with\s+us|[\W_]?deposit)", _I),     # "index funds are safe"
    re.compile(r"\bsure[\W_]?(?:thing|bet|fire|win)\b|\bno[\W_]?brainer\b|\bslam[\W_]?dunk\b", _I),
    re.compile(r"\b(?:steady|consistent|reliable)\s+(?:returns?|gains?|profits?)\b", _I),
    re.compile(r"\blow[\W_]?risk,?\s+(?:and\s+|with\s+)?high[\W_]?(?:rewards?|returns?|gains?)\b"
               r"|\bhigh[\W_]?(?:rewards?|returns?|gains?),?\s+(?:and\s+|with\s+)?(?:low|no|little|zero)[\W_]?risk\b", _I),
    re.compile(r"\bno\s+downside\b(?!\s+to\s+\w+ing)|\ball\s+upside\b", _I),
    re.compile(r"\b(?:always|only)\s+go(?:es)?\s+up\b|\bnever\s+go(?:es)?\s+down\b|\bnever\s+loses?\s+(?:money|value)\b", _I),
    # Predictions: use "could" + stated assumptions instead
    re.compile(r"\bwill\s+(?:earn|return|double|triple|grow\s+to|skyrocket|soar|explode|moon)\b", _I),
    re.compile(r"\bwill\s+make\s+(?:you\s+)?(?:money|rich|\$)", _I),
    re.compile(rf"(?:\bgoing\s+to|\bgonna|{_APOS}ll)\s+(?:double|triple|skyrocket|soar|explode|moon|make\s+you\s+rich)\b", _I),
    re.compile(rf"\b{_MARKET}{_WILL}\s+(?:(?:definitely|surely|certainly|probably|keep)\s+)?"
               r"(?:go(?:ing)?\s+up|rise|rising|climb|rally|bounce\s+back|beat\s+the\s+market|outperform)\b"
               r"(?!\s+(?:and|or)\s+(?:fall|drop|go\s+down))", _I),
    re.compile(r"\b(?:be|become|make\s+you)\s+a\s+millionaire\b|\bmillionaire\s+by\s+(?:age\s+)?\d", _I),
    # Hype
    re.compile(r"\bget\s+rich\b", _I),
    re.compile(r"\b(?:easy|fast|quick)\s+money\b", _I),
    re.compile(r"\bdouble\s+your\s+money\b", _I),
    re.compile(r"\b\d{2,4}x\b", _I),                                   # "10x", "100x"
    re.compile(r"\b\d+[\W_]?bagger\b", _I),
    re.compile(r"\bto\s+the\s+moon\b", _I),
    re.compile(r"\bthe\s+next\s+(?:amazon|apple|tesla|nvidia|google|bitcoin|microsoft)\b", _I),
    re.compile(r"\b(?:earn|make|get|return|returns\s+of|gains?\s+of|profits?\s+of|yield)\s+(?:up\s+to\s+|over\s+|at\s+least\s+)?"
               r"\d+(?:\.\d+)?\s*%\s+(?:a|per|each|every)\s+(?:day|week|month)\b", _I),   # "earn 20% a month"
    # Advice and picks
    re.compile(r"\b(?:you|u|ya)\s+(?:should|must|need\s+to|have\s+to|ought\s+to|gotta)\s+"
               r"(?:(?:(?!only\b)\w+ly|just|really|totally|seriously|absolutely)\s+)?"
               r"(?:buy|sell|invest\s+in|put\s+(?:your\s+)?money\s+in(?:to)?|load\s+up\s+on)\b", _I),
    re.compile(r"\b(?:we|i)\s+recommend\s+(?:buying|selling|investing\s+in)\b", _I),
    re.compile(r"\b(?:buy|sell)\s+(?:(?:this|these|it|them)\s+)?now\b", _I),
    re.compile(r"\bbuy\s+the\s+dip\b", _I),
    re.compile(r"\bstrong\s+buy\b|\bmust[\W_]?(?:buy|own)\b|\b(?:buy|sell)\s+rating\b", _I),
    re.compile(r"\b(?:our|my)\s+(?:top\s+|favou?rite\s+|best\s+)?(?:stock\s+|crypto\s+|coin\s+)?picks?\b"
               r"|\btop\s+(?:stock\s+|crypto\s+|coin\s+)?picks?\b", _I),
    re.compile(r"\bbest\s+(?:stocks?|coins?|crypto|etfs?|funds?)\s+to\s+buy\b"
               r"|\bbest\s+investment\s+(?:right\s+now|to\s+buy|of\s+(?:the\s+year|20\d\d))\b", _I),
    re.compile(r"\bthis\s+is\s+(?:financial|investment)\s+advice\b", _I),
    re.compile(r"\bprice\s+target\b", _I),
    re.compile(r"\$[A-Z]{1,5}\b"),                                      # cashtags like $TSLA (case-sensitive)
    re.compile(r"\$[a-z]{2,5}\b"),                                      # ...and lower-case ones like $btc
    # Urgency and pressure
    re.compile(rf"\bact\s+now\b|\b(?:don{_APOS}?t|do\s+not)\s+miss\s+out\b|\blimited\s+time\b", _I),
    re.compile(rf"\bnow\s+or\s+never\b|\bonce[\W_]?in[\W_]?a[\W_]?lifetime\s+(?:opportunit|chance|deal)"
               rf"|\b(?:today|tonight)\s+only\b|\bbefore\s+it{_APOS}?s\s+too\s+late\b", _I),
    re.compile(r"\b\d+\s+(?:spots?|seats?|slots?|places?)\s+left\b"
               r"|\blast\s+chance\s+to\s+(?:get\s+in|buy|invest|grab|join|cash\s+in)\b", _I),
    re.compile(r"\bget\s+in\s+(?:now|early|before|while)\b"
               r"|\bbefore\s+(?:it|they|prices?)\s+(?:moons?|pumps?|takes?\s+off|explodes?|skyrockets?|rips?)\b", _I),
    re.compile(r",\s*hurry\b|\bhurry\s*!|\bhurry\s+(?:up|now|before)\b|^\s*hurry\b", _I | re.M),
]

_NEG = rf"(?:not|never|nor|isn{_APOS}?t|aren{_APOS}?t|doesn{_APOS}?t|does\s+not|don{_APOS}?t|do\s+not|can{_APOS}?t|cannot|won{_APOS}?t)"
_TARGET = (r"(?:guarantee[ds]?|risk[\W_]?free|safe|(?:a\s+)?sure\s+(?:thing|bet)|(?:a\s+)?no[\W_]?brainer"
           r"|(?:steady|consistent|reliable)\s+(?:returns?|gains?|profits?)|(?:always|only)\s+go(?:es)?\s+up"
           r"|(?:be|become|make\s+you)\s+a\s+millionaire)")

# Honest negations ("no investment is risk-free", "past performance doesn't guarantee...") are allowed.
ALLOWED_CONTEXTS = [
    re.compile(rf"\b{_NEG}\s+(?:\w+\s+){{0,2}}?{_TARGET}\b", _I),     # "doesn't guarantee", "isn't a safe bet"
    re.compile(r"\bno\s+guarantees?\b", _I),
    re.compile(r"\bno\s+risk[\W_]?free\b", _I),
    re.compile(rf"\bno\s+(?:\w+\s+){{0,3}}?(?:is|are)\s+(?:ever\s+)?{_TARGET}\b", _I),  # "no investment is risk-free"
    re.compile(rf"\bnothing\s+(?:\w+\s+){{0,2}}?(?:is|{_APOS}s)\s+(?:ever\s+)?{_TARGET}\b", _I),
    re.compile(rf"\bno\s+such\s+thing\s+as\s+(?:a\s+)?{_TARGET}\b", _I),
    re.compile(r"\bwithout\s+(?:any\s+)?guarantees?\b", _I),
    re.compile(r"\bbuy\s+now,?\s+pay\s+later\b", _I),                   # the BNPL product name
    re.compile(r"\b(?:if|when|whenever|unless|before)\s+you\s+(?:need|have)\s+to\s+sell\b", _I),
    # "Nobody knows whether stocks will rise" (up to the next comma, so "..., but it will double" is still caught)
    re.compile(rf"\b(?:nobody|no\s+one|no-one|can{_APOS}?t|cannot|don{_APOS}?t|doesn{_APOS}?t)\s+(?:\w+\s+)?"
               r"(?:knows?|predict|tell|say|guess)\s+(?:for\s+sure\s+)?(?:whether|if|when|how)\b[^,;.!?\n]*", _I),
]

# Mentions, not claims: in a sentence that is clearly warning about hype ("Phrases like 'can't lose' are a
# red flag", "Be wary of anyone who says it's guaranteed"), the quoted or reported words are allowed.
# Deliberately narrow: quoted hype with no warning word in the sentence is still blocked.
_WARNING = (r"red[\W_]?flags?|scam\w*|fraud\w*|beware|wary|watch\s+out|warning\s+signs?|too\s+good\s+to\s+be\s+true"
            r"|hype\w*|pitch\w*|ponzi|pump[\W_]?and[\W_]?dump")
_META = (r"myths?|slogans?|phrases?|buzzwords?|catchphrases?|mantras?|memes?|so[\W_]?called|pressure|urgency|fomo"
         r"|(?:words?|lines?|claims?|promises?|advice|terms?)\s+like")
_QUOTE_CUE = re.compile(rf"\b(?:{_WARNING}|{_META})\b", _I)
_WARNING_CUE = re.compile(rf"\b(?:{_WARNING})\b", _I)
# Straight single quotes count only when they can't be apostrophes ("'today only'", not "everyone's").
_QUOTED = re.compile(r'"[^"\n]{1,80}"|“[^”\n]{1,80}”|‘[^’\n]{1,80}’|(?<!\w)\'[^\'\n]{1,80}\'(?!\w)')
_REPORTED = re.compile(
    r"\b(?:someone|somebody|anyone|anybody|anything|people|they|scammers?|promoters?|sellers?|salespeople|salesperson"
    r"|influencers?|finfluencers?|ads?|posts?|videos?|accounts?|investments?|funds?|products?|offers?|deals?|schemes?"
    r"|apps?|platforms?|coins?|tokens?)\s+(?:who\s+|that\s+)?(?:says?|said|saying|claims?|claimed|claiming|promises?"
    r"|promised|promising|tells?\s+you|told\s+you|telling\s+you|insists?|swears?)\b[^,;:.!?\n]*", _I)
_SENTENCE = re.compile(r'[^.!?\n]+(?:[.!?]+["”’)]*)?|[.!?\n]+')
_INVISIBLE = re.compile("[\u00ad\u200b-\u200f\u2060\ufeff]")      # soft hyphen, zero-width characters


def _drop_mentions(sentence: str) -> str:
    if _QUOTE_CUE.search(sentence):
        sentence = _QUOTED.sub(" ", sentence)
    if _WARNING_CUE.search(sentence):
        sentence = _REPORTED.sub(" ", sentence)
    return sentence


def find_violations(text: str) -> list[str]:
    # Look-alike letters (full-width, math bold, non-breaking spaces) become plain ones; invisible characters go.
    cleaned = _INVISIBLE.sub("", unicodedata.normalize("NFKC", text))
    cleaned = _SENTENCE.sub(lambda m: _drop_mentions(m.group(0)), cleaned)
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
