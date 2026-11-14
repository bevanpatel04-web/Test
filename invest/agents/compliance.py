"""Compliance check used by every writing agent: hard rules first, then an AI review, one rewrite, then drop."""
from __future__ import annotations

import json
from typing import Callable, TypeVar

from pydantic import BaseModel

from ..claims import CLAIMS_POLICY, find_violations
from ..schemas import ClaimsReview

T = TypeVar("T", bound=BaseModel)

REVIEWER = f"""You are the compliance reviewer for an investing-education brand for 18-25 year olds.
You protect readers and keep the brand on the education side of securities rules: no personalized advice,
no recommendations of any security or provider, no promised or predicted returns, risk always disclosed,
every statistic sourced. Also check that any arithmetic is plausible and that every statistic matches the
verified facts provided (anything not in them is unsupported). Approve only if every sentence complies.
List each problem sentence and why.

{CLAIMS_POLICY}"""


def review(llm, text: str, facts: dict) -> list[str]:
    issues = find_violations(text)
    if issues:
        return issues
    verdict = llm.structured(
        system=REVIEWER,
        prompt=f"Verified facts:\n{json.dumps(facts, indent=1)}\n\nReview this copy:\n\n{text}",
        schema=ClaimsReview,
        effort="medium",
    )
    return [] if verdict.approved else (verdict.issues or ["Reviewer rejected without details"])


def write_reviewed(llm, *, system: str, prompt: str, schema: type[T], to_text: Callable[[T], str], facts: dict,
                   label: str, extra_check: Callable[[T], list[str]] | None = None) -> T:
    """Draft, check, rewrite once with the reviewer's notes, and give up if it still fails."""
    def check(draft: T) -> list[str]:
        return (extra_check(draft) if extra_check else []) or review(llm, to_text(draft), facts)

    draft = llm.structured(system=system, prompt=prompt, schema=schema, effort="medium")
    issues = check(draft)
    if issues:
        draft = llm.structured(system=system, schema=schema, effort="medium",
                               prompt=prompt + "\n\nYour previous draft broke the policy:\n- " + "\n- ".join(issues)
                               + "\nRewrite it to comply.")
        issues = check(draft)
        if issues:
            raise ValueError(f"{label} failed the compliance check twice: " + "; ".join(issues))
    return draft
