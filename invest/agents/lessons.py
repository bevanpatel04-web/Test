"""Lessons agent: writes one 2-minute lesson from the curriculum, using only verified facts."""
from __future__ import annotations

import json

from .. import config, publish
from ..claims import CLAIMS_POLICY
from ..schemas import Lesson
from .compliance import write_reviewed

WRITER = f"""You write 2-minute lessons for {config.BRAND}, an investing-education site for 18-25 year olds.
Voice: friendly, direct, a little playful, never condescending. Short sentences. Explain jargon the first time.
US English. Like a smart older sibling who's honest about risk. 400-700 words in total: 2-4 sections,
3-4 key takeaways, 2-3 FAQs. The try_it line points to the free "start now vs. later" calculator on the homepage.
Use ONLY the verified facts provided, and list the key of every fact you cite in facts_used. With no facts
provided, don't cite any statistics.

{CLAIMS_POLICY}"""


def lesson_text(x: Lesson) -> str:
    return "\n".join([x.title, x.meta_description, x.hook, *(f"{s.heading}\n{s.body}" for s in x.sections),
                      *x.key_takeaways, x.try_it, *(f"{f.question} {f.answer}" for f in x.faq)])


def run(task: dict, llm) -> dict:
    slug = task["payload"].get("key")
    lesson = publish.find_lesson(slug) if slug else None
    if lesson is None:
        raise ValueError(f"Unknown lesson slug: {slug!r}")
    if lesson.get("published"):
        raise ValueError(f"{slug} is already published")
    verified = publish.verified_facts()
    if not publish.lesson_ready(lesson, verified):
        missing = [k for k in lesson["needs_facts"] if k not in verified]
        raise ValueError(f"{slug} needs facts verified first: {', '.join(missing)}")

    facts = {k: {f: v[f] for f in publish.PUBLIC_FACT_FIELDS} for k, v in verified.items()}
    prompt = (f"Write the lesson '{lesson['title']}' (slug '{slug}').\n"
              f"Facts this lesson is meant to use: {lesson['needs_facts'] or 'none'}.\n"
              f"All verified facts:\n{json.dumps(facts, indent=1)}\n\nCEO notes: {task['instructions']}")

    def cites_only_verified(x: Lesson) -> list[str]:
        bad = [k for k in x.facts_used if k not in verified]
        return [f"facts_used lists unverified or unknown facts: {', '.join(bad)}"] if bad else []

    page = write_reviewed(llm, system=WRITER, prompt=prompt, schema=Lesson, to_text=lesson_text, facts=facts,
                          label="Lesson", extra_check=cites_only_verified)
    page.slug = slug
    return page.model_dump()


def on_approve(task: dict) -> str:
    path = publish.write_lesson_page(Lesson(**task["result"]))
    publish.build_site()
    return f"Published {path}"
