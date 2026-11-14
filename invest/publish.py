"""Facts registry, lesson curriculum and the static website (facts data, lesson pages, sitemap)."""
from __future__ import annotations

import json
from datetime import date
from html import escape
from urllib.parse import urlparse

from . import config
from .schemas import Lesson

PUBLIC_FACT_FIELDS = ("key", "label", "display", "as_of", "source_name", "sources")


# ---- Facts ----------------------------------------------------------------------------------------
def load_facts() -> dict:
    return json.loads((config.DATA_DIR / "facts.json").read_text())


def save_facts(doc: dict) -> None:
    (config.DATA_DIR / "facts.json").write_text(json.dumps(doc, indent=2) + "\n")


def find_fact(key: str) -> dict | None:
    return next((f for f in load_facts()["facts"] if f["key"] == key), None)


def is_primary_source(url: str) -> bool:
    # Only plain web links count. "javascript://www.irs.gov/%0a..." has an irs.gov hostname but runs
    # script when clicked; "https://evil.com\@irs.gov" is irs.gov to Python but evil.com to browsers.
    if not isinstance(url, str) or any(c.isspace() or c == "\\" for c in url):
        return False
    parsed = urlparse(url)
    if parsed.scheme.lower() not in ("http", "https") or "@" in parsed.netloc:
        return False
    host = (parsed.hostname or "").lower()
    return any(host == d or host.endswith("." + d) for d in config.PRIMARY_SOURCE_DOMAINS)


def is_stale(fact: dict, today: date | None = None) -> bool:
    if not fact.get("verified") or not fact.get("verified_on"):
        return False
    age = ((today or date.today()) - date.fromisoformat(fact["verified_on"])).days
    return age > fact.get("check_every_days", 365)


def verified_facts() -> dict[str, dict]:
    return {f["key"]: f for f in load_facts()["facts"] if f.get("verified")}


# ---- Lessons --------------------------------------------------------------------------------------
def load_lessons() -> dict:
    return json.loads((config.DATA_DIR / "lessons.json").read_text())


def save_lessons(doc: dict) -> None:
    (config.DATA_DIR / "lessons.json").write_text(json.dumps(doc, indent=2) + "\n")


def find_lesson(slug: str) -> dict | None:
    return next((x for x in load_lessons()["lessons"] if x["slug"] == slug), None)


def lesson_ready(lesson: dict, verified: dict[str, dict] | None = None) -> bool:
    """A lesson can be written only when every fact it needs is verified."""
    verified = verified_facts() if verified is None else verified
    return all(k in verified for k in lesson.get("needs_facts", []))


def published_slugs() -> list[str]:
    d = config.SITE_DIR / "learn"
    return sorted(p.stem for p in d.glob("*.html") if p.stem != "index") if d.exists() else []


# ---- Site -----------------------------------------------------------------------------------------
def build_site() -> None:
    """Regenerate site/data/facts.json (verified facts only), the lessons index and sitemap.xml."""
    out = config.SITE_DIR / "data"
    out.mkdir(parents=True, exist_ok=True)
    public = [{k: f.get(k) for k in PUBLIC_FACT_FIELDS} for f in verified_facts().values()]
    (out / "facts.json").write_text(json.dumps({"facts": public}, indent=1) + "\n")

    published = set(published_slugs())
    items = []
    for x in load_lessons()["lessons"]:
        if x["slug"] in published:
            items.append(f'<li><a href="{escape(x["slug"])}.html">{escape(x["title"])}</a></li>')
        else:
            items.append(f'<li class="soon">{escape(x["title"])} <span class="fine">· coming soon</span></li>')
    body = f"""<h1>Learn</h1>
<p class="lede">Two-minute explainers on how investing works. No stock tips, no hype, sources for every number.</p>
<div class="card"><ul class="lesson-list">{''.join(items)}</ul></div>
<div class="card"><a class="btn" href="../">Try the calculator</a></div>"""
    (config.SITE_DIR / "learn").mkdir(parents=True, exist_ok=True)
    (config.SITE_DIR / "learn" / "index.html").write_text(
        _page("Learn to Invest: Plain-English Lessons", "Short, honest lessons on investing basics for your 20s.", body, nav="learn"))

    urls = [f"{config.SITE_URL}/", f"{config.SITE_URL}/rules.html", f"{config.SITE_URL}/learn/"] + [
        f"{config.SITE_URL}/learn/{s}.html" for s in sorted(published)]
    (config.SITE_DIR / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{escape(u)}</loc></url>\n" for u in urls) + "</urlset>\n")


def _paragraphs(text: str) -> str:
    return "".join(f"<p>{escape(p.strip())}</p>" for p in text.split("\n\n") if p.strip())


def render_lesson_page(lesson: Lesson, facts: dict[str, dict]) -> str:
    sections = "".join(f"<h2>{escape(s.heading)}</h2>{_paragraphs(s.body)}" for s in lesson.sections)
    takeaways = "".join(f"<li>{escape(t)}</li>" for t in lesson.key_takeaways)
    faq = "".join(f"<h3>{escape(f.question)}</h3>{_paragraphs(f.answer)}" for f in lesson.faq)
    sources = "".join(
        f'<li>{escape(facts[k]["label"])} ({escape(facts[k]["as_of"])}): '
        f'<a href="{escape(facts[k]["sources"][0])}" rel="noopener">{escape(facts[k]["source_name"])}</a></li>'
        for k in lesson.facts_used if k in facts and facts[k].get("sources"))
    body = f"""<article>
<h1>{escape(lesson.title)}</h1>
<p class="lede">{escape(lesson.hook)}</p>
<div class="card">{sections}</div>
<div class="card"><h2>Key takeaways</h2><ul>{takeaways}</ul></div>
<div class="callout"><p>{escape(lesson.try_it)}</p><a class="btn" href="../">Open the calculator</a></div>
<div class="card"><h2>Questions</h2>{faq}</div>
{f'<div class="card fine"><h2>Sources</h2><ul>{sources}</ul></div>' if sources else ''}
</article>"""
    return _page(lesson.title, lesson.meta_description, body, nav="learn")


def write_lesson_page(lesson: Lesson) -> str:
    facts = verified_facts()
    missing = [k for k in lesson.facts_used if k not in facts]
    if missing:
        raise ValueError(f"Lesson cites facts that aren't verified: {', '.join(missing)}")
    path = config.SITE_DIR / "learn" / f"{lesson.slug}.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_lesson_page(lesson, facts))
    doc = load_lessons()
    for x in doc["lessons"]:
        if x["slug"] == lesson.slug:
            x["published"] = True
    save_lessons(doc)
    return str(path.relative_to(config.ROOT))


def _page(title: str, description: str, body: str, nav: str = "") -> str:
    current = ' aria-current="page"'
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} | {escape(config.BRAND)}</title><meta name="description" content="{escape(description)}">
<link rel="stylesheet" href="../assets/style.css"></head>
<body><div class="wrap lesson">
<header class="top"><a class="brand" href="../">{escape(config.BRAND)}</a>
<nav><a href="../learn/"{current if nav == "learn" else ""}>Learn</a><a href="../rules.html">Our rules</a></nav></header>
{body}
<footer class="card fine disclaimer"><p><strong>Education, not advice.</strong> This is general information about how investing works,
not investment, tax or legal advice, and not a recommendation to buy or sell anything. Examples are hypothetical.
Investing involves risk, including losing money you put in. Past performance doesn't guarantee future results.
Your money, your decision.</p></footer>
</div></body></html>
"""
