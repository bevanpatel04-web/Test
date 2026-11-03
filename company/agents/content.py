"""Content agent: writes a city water guide, then a separate claims check reviews it."""
from __future__ import annotations

import json

from .. import config, site
from ..claims import CLAIMS_POLICY, find_violations
from ..schemas import CityPage, ClaimsReview

WRITER = f"""You write city water guides for {config.BRAND}, a brand for people with eczema and sensitive skin,
founded by someone who has eczema. Tone: warm, plain English, practical, honest about what the science does and
doesn't show. Use ONLY the water data provided; don't invent numbers. Mention the hardness in mg/L and what class
it falls in (soft <=60, moderately hard 61-120, hard 121-180, very hard >180). Explain the disinfectant and which
shower filter types address it (vitamin C or catalytic carbon for chloramine; carbon or KDF for chlorine).
Be clear that shower filters don't soften water. 3-5 practical tips, 3-4 FAQs.

{CLAIMS_POLICY}"""

REVIEWER = f"""You are the compliance reviewer. Check marketing and web copy against the policy below.
Approve only if every sentence complies. List each problem sentence and why.

{CLAIMS_POLICY}"""


def page_text(page: CityPage) -> str:
    parts = [page.title, page.meta_description, page.intro, page.hardness_section, page.disinfectant_section,
             *page.what_you_can_do, *(f"{f.question} {f.answer}" for f in page.faq)]
    return "\n".join(parts)


def review(llm, text: str) -> list[str]:
    issues = find_violations(text)
    if issues:
        return issues
    verdict = llm.structured(system=REVIEWER, prompt=f"Review this copy:\n\n{text}", schema=ClaimsReview, effort="low")
    return [] if verdict.approved else (verdict.issues or ["Reviewer rejected without details"])


def run(task: dict, llm) -> dict:
    slug = task["payload"].get("city_slug")
    city = site.find_city(slug) if slug else None
    if city is None:
        raise ValueError(f"Unknown city slug: {slug!r}")
    if not city.get("verified"):
        raise ValueError(f"{slug} isn't verified yet; the Water Data agent must verify it first")

    data = json.dumps({k: city.get(k) for k in ("city", "state", "utility", "hardness_mg_l", "disinfectant", "report_year")})
    prompt = f"Write the guide for slug '{slug}'. Water data:\n{data}\n\nCEO notes: {task['instructions']}"
    page = llm.structured(system=WRITER, prompt=prompt, schema=CityPage, effort="medium")
    issues = review(llm, page_text(page))
    if issues:  # one rewrite attempt with the reviewer's notes
        page = llm.structured(system=WRITER, schema=CityPage, effort="medium",
                              prompt=prompt + "\n\nYour previous draft broke the claims policy:\n- " + "\n- ".join(issues)
                              + "\nRewrite it to comply.")
        issues = review(llm, page_text(page))
        if issues:
            raise ValueError("Draft failed the claims check twice: " + "; ".join(issues))
    page.slug = slug
    return page.model_dump()


def on_approve(task: dict) -> str:
    path = site.write_city_page(CityPage(**task["result"]))
    site.build_site()
    return f"Published {path}"
