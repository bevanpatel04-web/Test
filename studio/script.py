"""Script stage: a lesson from the curriculum becomes a reviewed, scene-by-scene video script.

Generation goes through `company.llm` (Claude, or `FakeLLM` for dry runs) and
`invest.agents.compliance.write_reviewed`, so every script passes the hard claims filter and the
AI compliance review before it is saved to `studio/scripts/<slug>.json`. Hand-written scripts are
checked the same way (claims filter + structure) whenever they are loaded for rendering.
"""
from __future__ import annotations

import json
import re
from typing import Literal, Optional

from pydantic import BaseModel, Field

from invest.claims import CLAIMS_POLICY, find_violations

from . import config

SceneKind = Literal["title", "concept", "chart", "example", "recap", "quiz_teaser", "end"]
ChartType = Literal["growth", "bars", "stat", "line"]


class ScriptError(ValueError):
    pass


class ChartSpec(BaseModel):
    type: ChartType = Field(description="growth: monthly deposits compounding over time (same math as the site "
                            "calculator); bars: up to 4 labeled amounts; stat: one sourced percentage; "
                            "line: a labeled hypothetical series")
    title: str = Field("", description="Optional short label above the chart")
    monthly: Optional[float] = Field(None, description="growth: dollars added at the start of every month")
    rate: Optional[float] = Field(None, description="growth: hypothetical yearly rate as a decimal, 0 to 0.10")
    start_age: Optional[int] = Field(None, description="growth: age at the first deposit")
    end_age: Optional[int] = Field(None, description="growth: age at the end of the chart")
    delay_years: Optional[int] = Field(None, description="growth: adds a second line that starts this many years later")
    labels: list[str] = Field(default_factory=list, description="bars/line: one label per value; stat: [label]")
    values: list[float] = Field(default_factory=list, description="bars/line: the values; stat: [percent 0-100]")
    unit: Literal["$", "%", ""] = ""
    note: str = Field("", description="Shown under the chart: the assumptions ('Hypothetical: ... Not a prediction.') "
                      "or the source and date of a statistic")


class Scene(BaseModel):
    kind: SceneKind
    heading: str = Field(description="Short heading shown at the top of the scene, under 45 characters")
    narration: str = Field(description="The words spoken over this scene, plain and warm, in full sentences")
    on_screen: str = Field(description="Short text on screen: up to 4 lines separated by newlines, each under "
                           "40 characters. 'Label: value' lines show as two columns. quiz_teaser: the question, "
                           "then its 3 choices, one per line")
    chart: Optional[ChartSpec] = Field(None, description="Required when kind is chart; otherwise null")


class VideoScript(BaseModel):
    slug: str
    title: str
    scenes: list[Scene]
    facts_used: list[str] = Field(default_factory=list, description="Keys of every verified fact the script cites")
    risk_note: Optional[str] = Field(None, description="Copied from the lesson; spoken and shown on the end card")

    @classmethod
    def example(cls) -> "VideoScript":
        """What FakeLLM returns in dry runs and tests: a short, compliant, complete script."""
        return cls(
            slug="dry-run", title="Dry run: compound growth in one minute",
            scenes=[
                Scene(kind="title", heading="Compound growth in one minute", on_screen="Why time matters",
                      narration="This is a dry-run script. It shows the shape of a lesson video, from the title "
                                "card to the end card."),
                Scene(kind="concept", heading="Growth on growth", on_screen="Gains can earn gains\nTime does the work",
                      narration="Compound growth means your gains can earn gains of their own. The longer money "
                                "stays invested, the more years that effect has to build."),
                Scene(kind="chart", heading="$100 a month, two start dates", on_screen="Start at 25 or at 30",
                      chart=ChartSpec(type="growth", monthly=100, rate=0.06, start_age=25, end_age=65, delay_years=5,
                                      note="Hypothetical: $100 a month, 6% a year, compounded monthly. "
                                           "Not a prediction."),
                      narration="Here is a hypothetical. One person adds $100 a month from age 25, another from "
                                "age 30, and both assume a steady 6% a year. By 65, the early starter could have "
                                "about $191,700, and the later starter about $138,000. Real returns go up and down, "
                                "so this is an illustration, not a prediction."),
                Scene(kind="recap", heading="Recap", on_screen="Gains can earn gains\nTime is the input you control\n"
                                                              "Growth is never promised",
                      narration="Quick recap. Gains can earn gains of their own. Starting earlier gives money more "
                                "years to grow. And growth is never promised: investments can lose value."),
                Scene(kind="quiz_teaser", heading="Quick check",
                      on_screen="Compound growth means...\nYour gains can earn gains\nPrices rise every year\n"
                                "Your bank pays a bonus",
                      narration="Ready for a quick check? Answer three short questions below the video."),
                Scene(kind="end", heading="Your turn", on_screen="Try your own numbers in the calculator",
                      narration="Now try your own numbers in the calculator."),
            ],
        )


# ---- Curriculum -----------------------------------------------------------------------------------
def load_curriculum() -> dict:
    return json.loads(config.CURRICULUM.read_text())


def find_lesson(slug: str, curriculum: dict | None = None) -> tuple[dict, dict] | None:
    """Return (level, lesson) for a slug, or None."""
    doc = curriculum or load_curriculum()
    for level in doc.get("levels", []):
        for module in level.get("modules", []):
            for lesson in module.get("lessons", []):
                if lesson.get("slug") == slug:
                    return level, lesson
    return None


def lessons_in_level(number: int, curriculum: dict | None = None) -> list[dict]:
    doc = curriculum or load_curriculum()
    for level in doc.get("levels", []):
        if level.get("number") == number:
            return [x for m in level.get("modules", []) for x in m.get("lessons", [])]
    return []


# ---- Text helpers ---------------------------------------------------------------------------------
def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w$%]+", " ", s.lower())).strip()


def word_count(text: str) -> int:
    return len(text.split())


def script_text(s: VideoScript) -> str:
    """Everything a viewer will hear or read, for the claims filter and the AI reviewer."""
    parts = [s.title, s.risk_note or ""]
    for sc in s.scenes:
        parts += [sc.heading, sc.narration, sc.on_screen]
        if sc.chart:
            parts += [sc.chart.title, sc.chart.note, *sc.chart.labels]
    return "\n".join(p for p in parts if p)


def estimated_seconds(s: VideoScript) -> float:
    from .render import plan_timeline  # local import: render pulls in Pillow
    return plan_timeline(s, voice=None).duration


def finalize(draft: VideoScript, lesson: dict | None) -> VideoScript:
    """Deterministic fixes applied to every draft before review: lesson identity, and the risk note spoken."""
    s = draft.model_copy(deep=True)
    if lesson:
        s.slug, s.title = lesson["slug"], lesson["title"]
        s.risk_note = lesson.get("risk_note") or None
    if s.risk_note and _norm(s.risk_note) not in _norm(" ".join(sc.narration for sc in s.scenes)):
        target = next((sc for sc in s.scenes if sc.kind == "recap"), s.scenes[-1] if s.scenes else None)
        if target is not None:
            target.narration = f"{target.narration.rstrip()} {s.risk_note.strip()}".strip()
    return s


def structure_issues(s: VideoScript, verified: dict | None = None) -> list[str]:
    issues = []
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", s.slug or ""):
        issues.append(f"slug {s.slug!r} must be lowercase letters, digits and hyphens")
    if not 4 <= len(s.scenes) <= 12:
        issues.append(f"use 4-12 scenes (got {len(s.scenes)})")
    if s.scenes and s.scenes[0].kind != "title":
        issues.append("the first scene must be kind 'title'")
    if s.scenes and s.scenes[-1].kind != "end":
        issues.append("the last scene must be kind 'end'")
    for i, sc in enumerate(s.scenes, 1):
        if not sc.narration.strip():
            issues.append(f"scene {i} has no narration")
        lines = [x for x in sc.on_screen.split("\n") if x.strip()]
        if len(lines) > (4 if sc.kind == "quiz_teaser" else 5) or any(len(x) > 60 for x in lines):
            issues.append(f"scene {i} on_screen is too long: up to 4 short lines, each under 40 characters")
        if sc.kind == "quiz_teaser" and len(lines) != 4:
            issues.append(f"scene {i} (quiz_teaser) on_screen must be the question then exactly 3 choices")
        if sc.kind == "chart":
            issues += [f"scene {i}: {x}" for x in chart_issues(sc.chart)]
    if s.risk_note and _norm(s.risk_note) not in _norm(" ".join(sc.narration for sc in s.scenes)):
        issues.append("the lesson's risk note must be spoken word for word")
    if verified is not None:
        bad = [k for k in s.facts_used if k not in verified]
        if bad:
            issues.append(f"facts_used lists unverified or unknown facts: {', '.join(bad)}")
    if s.scenes and not issues:
        secs = estimated_seconds(s)
        if not config.MIN_SECONDS <= secs <= config.MAX_SECONDS:
            issues.append(f"runs about {secs:.0f}s; keep it between {config.MIN_SECONDS} and {config.MAX_SECONDS}s")
    return issues


def chart_issues(c: ChartSpec | None) -> list[str]:
    if c is None:
        return ["chart scenes need a chart spec"]
    if c.type == "growth":
        if None in (c.monthly, c.rate, c.start_age, c.end_age):
            return ["growth charts need monthly, rate, start_age and end_age"]
        out = []
        if not 1 <= c.monthly <= 100000:
            out.append("monthly must be between 1 and 100,000")
        if not 0 <= c.rate <= 0.10:
            out.append("rate must be a decimal between 0 and 0.10")
        if not (16 <= c.start_age < c.end_age <= 100):
            out.append("ages must satisfy 16 <= start_age < end_age <= 100")
        if c.delay_years is not None and not (1 <= c.delay_years < (c.end_age - c.start_age)):
            out.append("delay_years must leave at least one year of deposits")
        if "hypothetical" not in c.note.lower():
            out.append("growth chart note must say it is hypothetical and state the assumptions")
        return out
    if c.type == "stat":
        if len(c.values) != 1 or not 0 <= c.values[0] <= 100 or len(c.labels) != 1:
            return ["stat charts need one percent value (0-100) and one label"]
        return [] if c.note.strip() else ["stat charts need the source and date in note"]
    if c.type in ("bars", "line"):
        lo = 1 if c.type == "bars" else 2
        if not (lo <= len(c.values) <= (4 if c.type == "bars" else 40)) or len(c.labels) != len(c.values):
            return [f"{c.type} charts need {lo}-{4 if c.type == 'bars' else 40} values with one label each"]
        if any(v < 0 for v in c.values):
            return [f"{c.type} values must not be negative"]
    return []


def check(s: VideoScript, verified: dict | None = None) -> list[str]:
    """Hard checks every script must pass before it is rendered: structure and the claims filter."""
    return structure_issues(s, verified) or find_violations(script_text(s))


# ---- Generation -----------------------------------------------------------------------------------
WRITER = f"""You write narration scripts for short lesson videos at Patient Money, a money-learning app for
18-30 year olds that members pay for (we never sell financial products).
The video is narrated motion graphics with real charts: never people, faces or avatars.

Voice: plain, warm and direct, like a patient friend who is good with money. Short sentences. Explain any
jargon the first time. US English. Spoken at about 140 words per minute, so a 2-4 minute video is
280-540 words of narration in total.

Structure, in this order: one 'title' scene, 2-5 teaching scenes ('concept', 'chart', 'example'), one
'recap' (the key points), one 'quiz_teaser' (ask the lesson's first quiz question and list its 3 choices
on screen, without revealing the answer), and one 'end' scene that invites the member to try the lesson's
worksheet or tool. Use at least one 'chart' scene when the lesson has numbers. The end card label
("Made with AI, reviewed by a person" and "Education, not advice") is added automatically: don't write it.

Charts: 'growth' uses the site calculator's math (the same amount added at the start of each month,
compounded monthly at a steady hypothetical yearly rate); its note must say 'Hypothetical', state the
amount, rate and that it is not a prediction. Use 'stat' only for a verified fact, with its source and date
in the note. Every number you speak must be correct arithmetic or a verified fact.
If the lesson has a risk note, speak it word for word.
Use ONLY the verified facts provided, and list the key of every fact you cite in facts_used.

{CLAIMS_POLICY}"""


def lesson_prompt(level: dict, lesson: dict, facts: dict) -> str:
    wanted = {k: facts[k] for k in lesson.get("needs_facts", []) if k in facts}
    return (f"Write the video script for Level {level.get('number')} ({level.get('title')}), lesson "
            f"'{lesson['title']}' (slug '{lesson['slug']}').\n\n"
            f"Lesson spec:\n{json.dumps({k: lesson.get(k) for k in ('objectives', 'key_points', 'risk_note', 'try_it', 'quiz')}, indent=1)}\n\n"
            f"Verified facts this lesson is meant to use:\n{json.dumps(wanted, indent=1) if wanted else 'none'}\n")


def verified_public_facts() -> dict:
    from invest import publish
    return {k: {f: v.get(f) for f in publish.PUBLIC_FACT_FIELDS} for k, v in publish.verified_facts().items()}


def generate(slug: str, llm, facts: dict | None = None, curriculum: dict | None = None) -> VideoScript:
    """Draft a script with the LLM, then run it through the claims filter and the AI compliance review."""
    from invest.agents.compliance import write_reviewed

    found = find_lesson(slug, curriculum)
    if found is None:
        raise ScriptError(f"Unknown lesson slug: {slug!r}")
    level, lesson = found
    facts = verified_public_facts() if facts is None else facts
    draft = write_reviewed(
        llm, system=WRITER, prompt=lesson_prompt(level, lesson, facts), schema=VideoScript,
        to_text=lambda d: script_text(finalize(d, lesson)), facts=facts, label=f"Video script for {slug}",
        extra_check=lambda d: structure_issues(finalize(d, lesson), facts))
    return finalize(draft, lesson)


# ---- Storage --------------------------------------------------------------------------------------
def script_path(slug: str):
    return config.SCRIPTS_DIR / f"{slug}.json"


def save(s: VideoScript, path=None):
    path = path or script_path(s.slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(s.model_dump(), indent=2, ensure_ascii=False) + "\n")
    return path


def load(slug_or_path, verified: dict | None = None) -> VideoScript:
    """Load a saved script and refuse it unless it passes the structure checks and the claims filter."""
    from pathlib import Path
    path = Path(slug_or_path) if str(slug_or_path).endswith(".json") else script_path(str(slug_or_path))
    if not path.exists():
        raise ScriptError(f"No script at {path}. Run: python -m studio script <slug>")
    s = VideoScript.model_validate_json(path.read_text())
    issues = check(s, verified)
    if issues:
        raise ScriptError(f"{path.name} failed the checks: " + "; ".join(issues))
    return s
