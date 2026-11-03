"""Hard rules on health claims, checked before anything reaches a human or the website.

Selling a water product to people with eczema means the FTC expects every claim to be
backed by evidence. We sell water facts and gentler showers, never treatment.
"""
from __future__ import annotations

import re

BANNED_PATTERNS = [
    r"\bcur(e|es|ed|ing)\b",
    r"\bheal(s|ed|ing)?\b",
    r"\btreat(s|ed|ing|ment)?\b",
    r"\bprevent(s|ed|ing)?\s+(eczema|dermatitis|flare)",
    r"\b(eliminat|stop|end)\w*\s+(your\s+)?(eczema|flare)",
    r"\bclinically\s+(proven|tested)\b",
    r"\bdermatologist[- ](recommended|approved)\b",
    r"\bFDA[- ](approved|cleared)\b",
    r"\bguarantee[ds]?\b",
    r"\bremoves?\s+(all|100%)\b",
]
_RX = [re.compile(p, re.IGNORECASE) for p in BANNED_PATTERNS]

# Phrases that legitimately contain a banned word (e.g. "water treatment plant").
ALLOWED_CONTEXTS = [
    re.compile(r"water[- ]treatment", re.IGNORECASE),
    re.compile(r"treatment plant", re.IGNORECASE),
    re.compile(r"treated (water|with)", re.IGNORECASE),
    re.compile(r"not (medical advice|a treatment)", re.IGNORECASE),
    # Negated disclaimers: "doesn't diagnose, treat or prevent", "not intended to cure" — strip only the verb list.
    re.compile(r"(?:doesn't|does not|don't|do not|won't|will not|never|can't|cannot|isn't meant to|not intended to)\s+"
               r"(?:(?:diagnose|treat|cure|prevent|heal)\b[\s,]*(?:or|and)?\s*)+", re.IGNORECASE),
]


def find_violations(text: str) -> list[str]:
    cleaned = text
    for rx in ALLOWED_CONTEXTS:
        cleaned = rx.sub(" ", cleaned)
    hits = []
    for rx in _RX:
        for m in rx.finditer(cleaned):
            start = max(0, m.start() - 40)
            hits.append(f"…{cleaned[start:m.end() + 40].strip()}… (matched '{m.group(0)}')")
    return hits


CLAIMS_POLICY = """Claims policy (strict):
- Never say or imply the product or water change treats, cures, heals, prevents or stops eczema or any condition.
- Allowed: factual water information with sources; "reduces chlorine/chloramine" only when tied to test data;
  "gentler shower routine"; general skin-care habits widely given by dermatology organizations
  (lukewarm water, short showers, moisturize after bathing).
- Shower filters do NOT soften water. Never imply they reduce hardness.
- No "clinically proven", "dermatologist recommended", "FDA approved", guarantees, or "removes 100%".
- Always encourage seeing a dermatologist for skin concerns. Water is one possible trigger, not the cause."""
