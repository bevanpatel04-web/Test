"""Facts agent: checks one figure in data/facts.json against an official source."""
from __future__ import annotations

from datetime import date

from .. import config, publish
from ..schemas import FactVerification

SYSTEM = f"""You are the Facts checker for {config.BRAND}, an investing-education site for 18-25 year olds.
Your job is accuracy. Use ONLY official primary sources on these domains: {", ".join(config.PRIMARY_SOURCE_DOMAINS)}.
Never use news sites, blogs, brokerages, fund companies or influencers as sources, even when they quote an official
figure: find the official page itself. Report the figure exactly as published, the period it applies to, and the URL.
If the official source shows a different or newer figure than the one on file, report the official one and explain
in notes. If you can't confirm the figure from an official source, say so and set confidence to low."""


def run(task: dict, llm) -> dict:
    key = task["payload"].get("key")
    fact = publish.find_fact(key) if key else None
    if fact is None:
        raise ValueError(f"Unknown fact key: {key!r}")
    findings = llm.research(
        system=SYSTEM,
        prompt=(f"Fact to check: {fact['label']}.\nOn file: {fact['display']} (as of {fact['as_of']}). "
                f"Notes: {fact.get('notes', '')}\nConfirm or correct it from an official source, with the URL "
                f"and the period it applies to.\n\nExtra instructions from the CEO: {task['instructions']}"),
    )
    verification = llm.structured(
        system=SYSTEM,
        prompt=(f"Fact key: {key}\nTurn these research findings into the required structure. Use only facts "
                f"present in the findings.\n\n{findings}"),
        schema=FactVerification,
        effort="low",
    )
    verification.key = key
    return verification.model_dump()


def on_approve(task: dict) -> str:
    v = FactVerification(**task["result"])
    official = [u for u in v.sources if publish.is_primary_source(u)]
    doc = publish.load_facts()
    for f in doc["facts"]:
        if f["key"] == v.key:
            f.update(value=v.value, display=v.display, as_of=v.as_of, source_name=v.source_name,
                     sources=official, notes=v.notes)
            f["verified"] = bool(official) and v.confidence in ("medium", "high")
            f["verified_on"] = date.today().isoformat() if f["verified"] else None
            break
    else:
        raise ValueError(f"Unknown fact key: {v.key}")
    publish.save_facts(doc)
    publish.build_site()
    status = "verified" if f["verified"] else "NOT verified (needs an official source with medium/high confidence)"
    return f"Updated fact {v.key}: {v.display} — {status}"
