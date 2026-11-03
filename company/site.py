"""Water data files and the static website (ZIP tool data + city pages)."""
from __future__ import annotations

import json
from html import escape

from . import config
from .schemas import CityPage


def load_cities() -> dict:
    return json.loads((config.DATA_DIR / "cities.json").read_text())


def save_cities(doc: dict) -> None:
    (config.DATA_DIR / "cities.json").write_text(json.dumps(doc, indent=2) + "\n")


def find_city(slug: str) -> dict | None:
    return next((c for c in load_cities()["cities"] if c["slug"] == slug), None)


def published_slugs() -> list[str]:
    d = config.SITE_DIR / "cities"
    return sorted(p.stem for p in d.glob("*.html") if p.stem != "index") if d.exists() else []


def build_site() -> None:
    """Regenerate site/data/water.json, the city index page and sitemap.xml."""
    cities = load_cities()["cities"]
    states = json.loads((config.DATA_DIR / "states.json").read_text())["states"]
    out = config.SITE_DIR / "data"
    out.mkdir(parents=True, exist_ok=True)
    public = [
        {k: c[k] for k in ("slug", "city", "state", "zip3", "utility", "hardness_mg_l", "disinfectant", "verified")}
        for c in cities
    ]
    (out / "water.json").write_text(json.dumps({"cities": public, "states": states}, indent=1) + "\n")

    by_slug = {c["slug"]: c for c in cities}
    items = "\n".join(
        f'<li><a href="{escape(s)}.html">{escape(by_slug[s]["city"])}, {escape(by_slug[s]["state"])}</a></li>'
        for s in published_slugs() if s in by_slug
    ) or "<li>No city guides published yet.</li>"
    (config.SITE_DIR / "cities").mkdir(parents=True, exist_ok=True)
    (config.SITE_DIR / "cities" / "index.html").write_text(_page(
        "City Water Guides", "Tap water hardness and disinfectant by city, for sensitive skin.",
        f"<h1>City water guides</h1><ul>{items}</ul>"))

    urls = [f"{config.SITE_URL}/", f"{config.SITE_URL}/cities/"] + [
        f"{config.SITE_URL}/cities/{s}.html" for s in published_slugs()]
    (config.SITE_DIR / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{escape(u)}</loc></url>\n" for u in urls) + "</urlset>\n")


def render_city_page(page: CityPage, city: dict) -> str:
    sources = "".join(f'<li><a href="{escape(u)}" rel="nofollow noopener">{escape(u)}</a></li>' for u in city.get("sources", []))
    status = "Verified against the utility's report." if city.get("verified") else "Estimate — verification in progress."
    tips = "".join(f"<li>{escape(t)}</li>" for t in page.what_you_can_do)
    faq = "".join(f"<h3>{escape(f.question)}</h3><p>{escape(f.answer)}</p>" for f in page.faq)
    body = f"""
<h1>{escape(page.title)}</h1>
<p class="lede">{escape(page.intro)}</p>
<div class="card"><a class="btn" href="../">Check your exact ZIP code</a></div>
<div class="card"><h2>Hardness</h2><p>{escape(page.hardness_section)}</p>
<h2>Disinfectant</h2><p>{escape(page.disinfectant_section)}</p>
<p class="fine">Utility: {escape(city["utility"])}. {status}</p>
{f'<p class="fine">Sources:</p><ul class="fine">{sources}</ul>' if sources else ''}</div>
<div class="card"><h2>What you can do</h2><ul class="recs">{tips}</ul></div>
<div class="card"><h2>Questions</h2>{faq}</div>"""
    return _page(page.title, page.meta_description, body)


def write_city_page(page: CityPage) -> str:
    city = find_city(page.slug)
    if city is None:
        raise ValueError(f"Unknown city {page.slug}")
    path = config.SITE_DIR / "cities" / f"{page.slug}.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_city_page(page, city))
    return str(path.relative_to(config.ROOT))


def _page(title: str, description: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title><meta name="description" content="{escape(description)}">
<link rel="stylesheet" href="../assets/style.css"></head>
<body><div class="wrap"><header><a class="brand" href="../">{escape(config.BRAND)}</a></header>
{body}
<div class="card fine"><strong>Important:</strong> General information about water, not medical advice. It doesn't diagnose, treat or prevent eczema or any other condition. Talk to a dermatologist about your skin.</div>
</div></body></html>
"""
