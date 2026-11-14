"""Pilot policy: what earns points, what never can, what points can be spent on, and privacy guards.

The earning rules and catalog text mirror docs/pilot/data-contract.md. Changing a points value or
label here changes what the dashboard shows, so keep the two in step.
"""
from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .errors import ForbiddenRuleError, PrivacyError, RedemptionDisabledError, RedemptionError, UnknownRuleError

# --- Forbidden rules ---------------------------------------------------------------------------
# Rewards may never be tied to trading, trade counts, account or portfolio balances, or investment
# returns. Gamified trading is a regulatory red flag. The match is deliberately strict: a harmless
# name that trips it (say "work_life_balance") should simply be renamed.
_FORBIDDEN = re.compile(
    r"trad(?:e|es|ed|er|ers|ing)"
    r"|portfolio|balance|return|profit|crypto"
    r"|(?<![a-z])(?:gains?|stocks?|equit(?:y|ies)|holdings?|positions?|pnl|aum|net_?worth|account_?value)(?![a-z])",
    re.IGNORECASE,
)


def _strings(value: Any):
    """Every string inside a value, including dict keys, so nested configs are checked too."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from _strings(k)
            yield from _strings(v)
    elif isinstance(value, (list, tuple, set, frozenset)):
        for v in value:
            yield from _strings(v)


def forbidden_terms(*values: Any) -> list[str]:
    """The forbidden words found anywhere in the given names, labels or configs (lowercased)."""
    hits: list[str] = []
    for text in (s for v in values for s in _strings(v)):
        for m in _FORBIDDEN.finditer(text):
            word = m.group(0).lower()
            if word not in hits:
                hits.append(word)
    return hits


def check_rule_allowed(name: str, label: str = "", config: Any = None) -> None:
    """Raise ForbiddenRuleError if a rule's name, label or config is tied to trading or balances."""
    hits = forbidden_terms(name, label, config)
    if hits:
        raise ForbiddenRuleError(
            f"Rule {name!r} is not allowed: points may never reward trading, trade counts, account or "
            f"portfolio balances, or investment returns (matched: {', '.join(hits)})."
        )


# --- Earning rules -----------------------------------------------------------------------------
class Rule(BaseModel):
    """One way to earn points. Building a Rule runs the forbidden-rule check."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    label: str = Field(min_length=1)
    points: int = Field(gt=0)
    max_awards: int = Field(default=1, ge=1, description="How many times one member can earn it")
    tenure_days: int | None = Field(default=None, gt=0)
    config: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def _not_forbidden(cls, data: Any) -> Any:
        # Runs before field validation. ForbiddenRuleError is not a ValueError, so pydantic lets it
        # through unchanged and callers get the clear error rather than a generic ValidationError.
        if isinstance(data, dict):
            check_rule_allowed(str(data.get("name", "")), str(data.get("label", "")), data.get("config"))
        return data


def define_rule(name: str, label: str, points: int, *, max_awards: int = 1, config: dict | None = None) -> Rule:
    """Validate a proposed rule. The pilot only awards the seven default rules; any future custom
    rule has to pass through here, which rejects anything tied to trading or balances."""
    return Rule(name=name, label=label, points=points, max_awards=max_awards, config=config or {})


_DEFAULT_RULES = [
    Rule(name="tenure_30", label="30 days on the job", points=300, tenure_days=30),
    Rule(name="tenure_90", label="90 days on the job", points=300, tenure_days=90),
    Rule(name="tenure_180", label="180 days on the job", points=600, tenure_days=180),
    Rule(name="tenure_365", label="One year on the job", points=1000, tenure_days=365),
    Rule(name="lesson_completed", label="Finished a lesson", points=50, max_awards=10),
    Rule(name="checklist_completed", label='Finished the "before you invest" checklist', points=200),
    Rule(name="savings_setup", label="Set up direct deposit to savings", points=300),
]
PILOT_RULES: dict[str, Rule] = {r.name: r for r in _DEFAULT_RULES}
TENURE_RULES: list[Rule] = sorted((r for r in _DEFAULT_RULES if r.tenure_days), key=lambda r: r.tenure_days)
MAX_LESSONS = PILOT_RULES["lesson_completed"].max_awards

# Ledger rules that are not earning rules (kind "adjust").
REFUND_RULE = "redemption_cancelled"
MANUAL_RULE = "manual_adjustment"
ADJUST_LABELS = {
    REFUND_RULE: "Redemption cancelled, points returned",
    MANUAL_RULE: "Manual correction",
}


def pilot_rule(name: str) -> Rule:
    """Look up a pilot rule. Forbidden names fail with ForbiddenRuleError before the lookup."""
    check_rule_allowed(name)
    try:
        return PILOT_RULES[name]
    except KeyError:
        raise UnknownRuleError(f"{name!r} is not a pilot rule. Pilot rules: {', '.join(PILOT_RULES)}.") from None


# --- Redemption catalog ------------------------------------------------------------------------
class RedemptionType(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    type: str
    label: str
    min_points: int = Field(gt=0)
    note: str
    enabled: bool = True
    disabled_reason: str = ""


INVEST_DEPOSIT_DISABLED = (
    "invest_deposit is disabled: a deposit into a member's own investing account requires a licensed "
    "brokerage partner and is not part of the pilot. The pilot moves no money and offers no securities."
)

CATALOG: dict[str, RedemptionType] = {
    "payroll_bonus": RedemptionType(
        type="payroll_bonus", label="Payroll bonus", min_points=500,
        note="Paid by your employer in your next paycheck. Taxed like regular pay.",
    ),
    "gift_card": RedemptionType(
        type="gift_card", label="Gift card", min_points=500,
        note="Delivered by email within 5 business days.",
    ),
    "invest_deposit": RedemptionType(
        type="invest_deposit", label="Deposit to your own investing account", min_points=500,
        note="Not available in the pilot.", enabled=False, disabled_reason=INVEST_DEPOSIT_DISABLED,
    ),
}
ENABLED_CATALOG: list[RedemptionType] = [t for t in CATALOG.values() if t.enabled]


def redemption_type(type_: str) -> RedemptionType:
    """Look up an enabled redemption type, or raise a clear error."""
    rtype = CATALOG.get(type_)
    if rtype is None:
        raise RedemptionError(f"Unknown redemption type {type_!r}. Pilot types: {', '.join(t.type for t in ENABLED_CATALOG)}.")
    if not rtype.enabled:
        raise RedemptionDisabledError(rtype.disabled_reason)
    return rtype


def ledger_label(kind: str, rule: str) -> str:
    """Plain-English label for a ledger row, as shown in the member's history."""
    if kind == "earn" and rule in PILOT_RULES:
        return PILOT_RULES[rule].label
    if kind == "redeem" and rule in CATALOG:
        return CATALOG[rule].label
    return ADJUST_LABELS.get(rule, rule.replace("_", " ").capitalize())


# --- Privacy -----------------------------------------------------------------------------------
_EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[A-Za-z]{2,}")
_ISO_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_PHONE = re.compile(r"(?:\+?\d{1,2}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}")


def looks_like_contact(text: str) -> bool:
    """True if the text contains something shaped like an email address or phone number."""
    return bool(_EMAIL.search(text) or "@" in text or _PHONE.search(_ISO_DATE.sub(" ", text)))


def check_no_contact(value: Any, where: str) -> None:
    for text in _strings(value):
        if looks_like_contact(text):
            raise PrivacyError(f"{where} contains something that looks like an email or phone number; "
                               "the pilot stores and exports display names only.")
