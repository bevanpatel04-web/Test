"""Checks invest/data/curriculum.json against docs/app/contracts.md section 1 and the curriculum design rules.

Contract rules: 5 levels and only Level 1 free; unique slugs that are safe as file names; prerequisites point to
earlier lessons; 3 questions x 3 choices with valid answer indexes; allowed try_it tools; needs_facts keys exist
and are verified; a risk note wherever a lesson touches investing; every word passes the claims filter.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import pytest

from invest.claims import find_violations

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM_PATH = ROOT / "invest" / "data" / "curriculum.json"
FACTS_PATH = ROOT / "invest" / "data" / "facts.json"
DOC_PATH = ROOT / "docs" / "app" / "curriculum.md"

RAW = CURRICULUM_PATH.read_text(encoding="utf-8")
CURRICULUM = json.loads(RAW)
FACTS = {f["key"]: f for f in json.loads(FACTS_PATH.read_text(encoding="utf-8"))["facts"]}

TOP_KEYS = {"version", "updated", "levels"}
LEVEL_KEYS = {"id", "number", "title", "summary", "free", "modules"}
MODULE_KEYS = {"id", "title", "summary", "lessons"}
LESSON_KEYS = {"slug", "title", "minutes", "objectives", "key_points", "prerequisites", "needs_facts",
               "risk_note", "try_it", "quiz"}
QUIZ_KEYS = {"q", "choices", "answer", "why"}
TOOLS = {"calculator", "crash-sim", "money-map", "none"}
SLUG = re.compile(r"^[a-z0-9-]+$")
# Words that mean a lesson touches returns, investing products, leverage, options or crypto.
TOUCHES_INVESTING = re.compile(r"\b(?:invest\w*|stocks?|funds?|crypto\w*|options?|leverag\w*|returns?)\b", re.I)
PERCENT = re.compile(r"\d+(?:\.\d+)?\s*%")

LEVELS = CURRICULUM["levels"]
MODULES = [m for lv in LEVELS for m in lv["modules"]]
LESSONS = [lesson for m in MODULES for lesson in m["lessons"]]
SLUGS = [lesson["slug"] for lesson in LESSONS]


def _lesson_text(lesson: dict) -> str:
    """Every member-facing string in a lesson except the risk note itself."""
    parts = [lesson["title"], *lesson["objectives"], *lesson["key_points"], lesson["try_it"]["prompt"]]
    for item in lesson["quiz"]:
        parts += [item["q"], *item["choices"], item["why"]]
    return "\n".join(parts)


def _strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from _strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _strings(value)


def _nonempty_str(value) -> bool:
    return isinstance(value, str) and value.strip() != ""


lesson_cases = pytest.mark.parametrize("lesson", LESSONS, ids=SLUGS)


# ---- File and level structure ----

def test_top_level_shape():
    assert set(CURRICULUM) == TOP_KEYS, "don't add or rename keys without updating docs/app/contracts.md"
    assert CURRICULUM["version"] == 1
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", CURRICULUM["updated"])


def test_five_levels_numbered_in_order():
    assert [lv["number"] for lv in LEVELS] == [1, 2, 3, 4, 5]
    assert [lv["id"] for lv in LEVELS] == ["L1", "L2", "L3", "L4", "L5"]
    for lv in LEVELS:
        assert set(lv) == LEVEL_KEYS, lv["id"]
        assert _nonempty_str(lv["title"]) and _nonempty_str(lv["summary"]), lv["id"]


def test_only_level_1_is_free():
    assert [lv["free"] for lv in LEVELS] == [True, False, False, False, False]
    assert all(isinstance(lv["free"], bool) for lv in LEVELS)


def test_modules_are_well_formed():
    for lv in LEVELS:
        assert 2 <= len(lv["modules"]) <= 3, f"{lv['id']} should have 2-3 modules"
        for k, m in enumerate(lv["modules"], start=1):
            assert set(m) == MODULE_KEYS, m.get("id")
            assert m["id"] == f"{lv['id']}-M{k}"
            assert _nonempty_str(m["title"]) and _nonempty_str(m["summary"]), m["id"]
            assert m["lessons"], f"{m['id']} has no lessons"


def test_lesson_counts():
    assert 40 <= len(LESSONS) <= 50, len(LESSONS)
    for lv in LEVELS:
        count = sum(len(m["lessons"]) for m in lv["modules"])
        assert 8 <= count <= 10, f"{lv['id']} has {count} lessons"


# ---- Lessons ----

@lesson_cases
def test_lesson_shape(lesson):
    assert set(lesson) == LESSON_KEYS
    assert _nonempty_str(lesson["title"])
    assert isinstance(lesson["minutes"], int) and not isinstance(lesson["minutes"], bool)
    assert 2 <= lesson["minutes"] <= 10
    assert 2 <= len(lesson["objectives"]) <= 3 and all(map(_nonempty_str, lesson["objectives"]))
    assert len(lesson["key_points"]) == 3 and all(map(_nonempty_str, lesson["key_points"]))


def test_slugs_are_unique_and_file_safe():
    duplicates = [s for s, n in Counter(SLUGS).items() if n > 1]
    assert not duplicates, duplicates
    bad = [s for s in SLUGS if not SLUG.fullmatch(s)]
    assert not bad, bad


def test_prerequisites_point_to_earlier_lessons():
    earlier: set[str] = set()
    for i, lesson in enumerate(LESSONS):
        prereqs = lesson["prerequisites"]
        assert isinstance(prereqs, list), lesson["slug"]
        assert len(prereqs) == len(set(prereqs)), f"{lesson['slug']}: duplicate prerequisite"
        for p in prereqs:
            assert p in earlier, f"{lesson['slug']}: prerequisite {p!r} isn't an earlier lesson"
        if i > 0:
            assert prereqs, f"{lesson['slug']}: every lesson after the first builds on an earlier one"
        earlier.add(lesson["slug"])
    assert LESSONS[0]["prerequisites"] == []


@lesson_cases
def test_quiz_is_three_by_three(lesson):
    quiz = lesson["quiz"]
    assert len(quiz) == 3
    for item in quiz:
        assert set(item) == QUIZ_KEYS
        assert _nonempty_str(item["q"]) and _nonempty_str(item["why"])
        assert len(item["choices"]) == 3 and all(map(_nonempty_str, item["choices"]))
        assert len(set(item["choices"])) == 3, f"duplicate choice in {item['q']!r}"
        assert isinstance(item["answer"], int) and not isinstance(item["answer"], bool)
        assert 0 <= item["answer"] < 3


def test_right_answers_are_not_always_in_the_same_place():
    # With a 2-of-3 mastery rule, a guessable answer position would let people pass without learning.
    positions = Counter(item["answer"] for lesson in LESSONS for item in lesson["quiz"])
    total = sum(positions.values())
    for pos in range(3):
        assert positions[pos] >= total * 0.25, positions


@lesson_cases
def test_try_it_uses_an_allowed_tool(lesson):
    assert set(lesson["try_it"]) == {"tool", "prompt"}
    assert lesson["try_it"]["tool"] in TOOLS
    assert _nonempty_str(lesson["try_it"]["prompt"])


@lesson_cases
def test_needs_facts_exist_and_are_verified(lesson):
    keys = lesson["needs_facts"]
    assert isinstance(keys, list) and len(keys) == len(set(keys))
    for key in keys:
        assert key in FACTS, f"{key!r} isn't in invest/data/facts.json"
        assert FACTS[key]["verified"] is True, f"{key!r} isn't verified yet"


@lesson_cases
def test_risk_note_where_lesson_touches_investing(lesson):
    note = lesson["risk_note"]
    assert note is None or _nonempty_str(note)
    hit = TOUCHES_INVESTING.search(_lesson_text(lesson))
    if hit:
        assert _nonempty_str(note), f"mentions {hit.group(0)!r} but has no risk_note"


@lesson_cases
def test_percentages_are_cited_facts_or_labeled_hypothetical(lesson):
    # A lesson that cites a statistic must list it; any other number has to be a labeled hypothetical.
    text = _lesson_text(lesson) + "\n" + (lesson["risk_note"] or "")
    cited = {FACTS[k]["display"] for k in lesson["needs_facts"] if k in FACTS}
    loose = [p for p in PERCENT.findall(text) if p not in cited]
    if loose:
        assert re.search(r"hypothetical", text, re.I), f"unlabeled figures {loose}"


# ---- Claims filter ----

def test_whole_file_passes_claims_filter():
    assert find_violations(RAW) == []


@lesson_cases
def test_every_string_in_lesson_passes_claims_filter(lesson):
    # Same check, string by string, so a failure names the exact text (wrong answers included).
    for text in _strings(lesson):
        assert find_violations(text) == [], text


def test_level_and_module_text_passes_claims_filter():
    for lv in LEVELS:
        for text in (lv["title"], lv["summary"], *(t for m in lv["modules"] for t in (m["title"], m["summary"]))):
            assert find_violations(text) == [], text


# ---- The plain-English summary stays in sync ----

def test_doc_lists_every_lesson_and_passes_claims_filter():
    doc = DOC_PATH.read_text(encoding="utf-8")
    missing = [lesson["title"] for lesson in LESSONS if lesson["title"] not in doc]
    assert not missing, f"docs/app/curriculum.md is out of date: {missing}"
    assert find_violations(doc) == []
