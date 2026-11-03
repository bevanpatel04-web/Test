"""Water Data agent: verifies a city's hardness and disinfectant against the utility's own report."""
from __future__ import annotations

from .. import site
from ..schemas import CityVerification

SYSTEM = """You are the Water Data analyst for a company that helps people with sensitive skin understand their tap water.
Your job is accuracy. Use only the water utility's own Consumer Confidence Report (annual water quality report)
or official utility/government pages. Never use shower-filter sellers or blogs as sources.
Report total hardness in mg/L as CaCO3 (convert grains per gallon x 17.1). If a range is given, report the typical
or average value and explain in notes. Identify the residual disinfectant: chlorine (free chlorine) or chloramine.
If you cannot confirm a value from an official source, say so and lower your confidence."""


def run(task: dict, llm) -> dict:
    slug = task["payload"].get("city_slug")
    city = site.find_city(slug) if slug else None
    if city is None:
        raise ValueError(f"Unknown city slug: {slug!r}")
    findings = llm.research(
        system=SYSTEM,
        prompt=(f"Find the latest water quality report for {city['city']}, {city['state']} "
                f"(utility on file: {city['utility']}). Current estimate on file: hardness "
                f"{city['hardness_mg_l']} mg/L, disinfectant {city['disinfectant']}. "
                "Confirm or correct both values, with source URLs and the report year.\n\n"
                f"Extra instructions from the CEO: {task['instructions']}"),
    )
    verification = llm.structured(
        system=SYSTEM,
        prompt=(f"City slug: {slug}\nTurn these research findings into the required structure. "
                f"Use only facts present in the findings.\n\n{findings}"),
        schema=CityVerification,
        effort="low",
    )
    verification.city_slug = slug
    return verification.model_dump()


def on_approve(task: dict) -> str:
    v = CityVerification(**task["result"])
    doc = site.load_cities()
    for c in doc["cities"]:
        if c["slug"] == v.city_slug:
            c["utility"] = v.utility or c["utility"]
            if v.hardness_mg_l is not None:
                c["hardness_mg_l"] = round(v.hardness_mg_l)
            if v.disinfectant != "unknown":
                c["disinfectant"] = v.disinfectant
            c["sources"] = v.sources
            c["report_year"] = v.report_year
            c["verified"] = bool(v.sources) and v.confidence in ("medium", "high") and v.hardness_mg_l is not None
            break
    site.save_cities(doc)
    site.build_site()
    return f"Updated data/cities.json for {v.city_slug}"
