"""Guardrails around the investing AI team: CEO plan checks, fact sources, safe lesson pages, social disclaimers.

Every test runs against a throwaway copy of invest/data and invest/site, with no API calls.
Run: python -m pytest -q tests/qa/test_agent_guardrails.py
"""
import json
import shutil
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture()
def invest(tmp_path, monkeypatch):
    shutil.copytree(REPO / "invest" / "data", tmp_path / "data")
    shutil.copytree(REPO / "invest" / "site", tmp_path / "site")
    from invest import config
    monkeypatch.setattr(config, "ROOT", tmp_path)
    monkeypatch.setattr(config, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(config, "SITE_DIR", tmp_path / "site")
    monkeypatch.setattr(config, "STATE_FILE", tmp_path / "ops" / "state.json")
    monkeypatch.setattr(config, "BRIEFS_DIR", tmp_path / "ops" / "briefs")
    monkeypatch.setattr(config, "OUTBOX_DIR", tmp_path / "ops" / "outbox")
    return tmp_path


def planner(tasks):
    """A fake LLM whose CEO plan is exactly `tasks` (agent, key) pairs."""
    from company.llm import FakeLLM
    from invest.schemas import PlannedTask, TaskPlan

    class Planner(FakeLLM):
        def structured(self, *, system, prompt, schema, effort="medium"):
            if schema is TaskPlan:
                return TaskPlan(reasoning="test", tasks=[
                    PlannedTask(agent=a, title=f"{a} {k}", instructions="", key=k) for a, k in tasks])
            return super().structured(system=system, prompt=prompt, schema=schema, effort=effort)

    return Planner()


def rejections(state):
    return [e["reason"] for e in state.data["events"] if e["kind"] == "plan_rejected"]


# ---- CEO plan guardrails -----------------------------------------------------------------------
def test_ceo_rejects_unknown_fact_key(invest):
    from company.state import State
    from invest.agents import ceo
    state = State(invest / "ops" / "state.json")
    _, created = ceo.plan(state, planner([("facts", "made_up_fact"), ("facts", None)]))
    assert created == []
    assert rejections(state) == ["unknown fact key"] * 2


def test_ceo_rejects_unknown_blocked_and_published_lessons(invest):
    from company.state import State
    from invest import publish
    from invest.agents import ceo
    doc = publish.load_lessons()
    next(x for x in doc["lessons"] if x["slug"] == "fees-add-up")["published"] = True
    publish.save_lessons(doc)
    state = State(invest / "ops" / "state.json")
    _, created = ceo.plan(state, planner([
        ("lessons", "no-such-lesson"),       # unknown
        ("lessons", "market-crashes"),       # needs unverified facts
        ("lessons", "fees-add-up"),          # already published
        ("lessons", None),                   # no slug at all
        ("lessons", "compound-growth"),      # ready: allowed
    ]))
    assert [t["payload"]["key"] for t in created] == ["compound-growth"]
    assert len(rejections(state)) == 4
    assert all("lesson is unknown" in r for r in rejections(state))


def test_ceo_rejects_duplicates_in_plan_and_of_open_tasks(invest):
    from company.state import AWAITING, State
    from invest.agents import ceo
    state = State(invest / "ops" / "state.json")
    waiting = state.add_task("facts", "earlier check", "", key="cc_apr_assessed")
    state.update(waiting, status=AWAITING)
    state.add_task("social", "earlier pack", "")   # still queued
    _, created = ceo.plan(state, planner([
        ("facts", "cc_apr_assessed"),        # awaiting approval already
        ("social", None),                    # queued already
        ("lessons", "compound-growth"),
        ("lessons", "compound-growth"),      # duplicate inside the same plan
    ]))
    assert [(t["agent"], t["payload"]["key"]) for t in created] == [("lessons", "compound-growth")]
    assert rejections(state) == ["duplicate of open task"] * 3


def test_ceo_social_key_is_ignored_so_it_still_dedupes(invest):
    from company.state import State
    from invest.agents import ceo
    state = State(invest / "ops" / "state.json")
    _, created = ceo.plan(state, planner([("social", "anything"), ("social", "else")]))
    assert len(created) == 1 and created[0]["payload"]["key"] is None


def test_ceo_respects_max_tasks_but_skips_rejected_ones(invest):
    from company.state import State
    from invest.agents import ceo
    state = State(invest / "ops" / "state.json")
    plan = [("facts", "nope"), ("lessons", "compound-growth"), ("lessons", "what-risk-means"),
            ("lessons", "index-funds-vs-stocks"), ("lessons", "fees-add-up"), ("social", None)]
    _, created = ceo.plan(state, planner(plan), max_tasks=3)
    assert [t["payload"]["key"] for t in created] == ["compound-growth", "what-risk-means", "index-funds-vs-stocks"]
    assert len(state.data["tasks"]) == 3
    _, none = ceo.plan(State(invest / "ops" / "other.json"), planner(plan), max_tasks=0)
    assert none == []


def test_run_daily_never_runs_more_than_max_tasks(invest):
    from company.state import State
    from invest import runner
    state = State(invest / "ops" / "state.json")
    for i in range(5):
        state.add_task("social", f"left over {i}", "")
    runner.run_daily(planner([]), state, max_tasks=2)
    assert len([t for t in state.data["tasks"] if t["status"] != "queued"]) == 2


# ---- Facts: only official sources count ---------------------------------------------------------
def approve_fact(sources, confidence="high", key="roth_ira_phaseout_single_2027"):
    from invest import publish
    from invest.agents import facts
    from invest.schemas import FactVerification
    v = FactVerification.example()
    v.key, v.sources, v.confidence = key, sources, confidence
    message = facts.on_approve({"result": v.model_dump()})
    return message, publish.find_fact(key)


def public_keys(invest):
    return {f["key"] for f in json.loads((invest / "site" / "data" / "facts.json").read_text())["facts"]}


def test_mixed_sources_keep_only_the_official_ones(invest):
    message, fact = approve_fact(["https://www.some-finance-blog.com/roth", "https://www.irs.gov/retirement-plans/x",
                                  "https://irs.gov.evil.example/x", "https://apps.irs.gov/app/y"])
    assert fact["verified"] is True and "verified" in message
    assert fact["sources"] == ["https://www.irs.gov/retirement-plans/x", "https://apps.irs.gov/app/y"]
    assert "roth_ira_phaseout_single_2027" in public_keys(invest)


def test_unofficial_only_or_low_confidence_stays_hidden(invest):
    _, fact = approve_fact(["https://www.nerdwallet.com/roth"])
    assert fact["verified"] is False and fact["sources"] == [] and fact["verified_on"] is None
    _, fact = approve_fact(["https://www.irs.gov/x"], confidence="low")
    assert fact["verified"] is False
    assert "roth_ira_phaseout_single_2027" not in public_keys(invest)


@pytest.mark.parametrize("url", [
    "javascript://www.irs.gov/%0aalert(document.cookie)",   # hostname irs.gov, but runs script when clicked
    "https://evil.example\\@www.irs.gov/x",                 # Python sees irs.gov; browsers go to evil.example
    "https://user@www.irs.gov/x",
    "ftp://www.irs.gov/x",
    "https://www.irs.gov /x",
    "https://irs.gov.evil.example/x",
    "https://notirs.gov/x",
    "",
])
def test_tricky_urls_are_not_official(url):
    from invest import publish
    assert not publish.is_primary_source(url)


@pytest.mark.parametrize("url", ["https://www.irs.gov/x", "http://www.sec.gov/x", "HTTPS://WWW.FEDERALRESERVE.GOV/x",
                                 "https://www.spglobal.com/spdji/en/"])
def test_official_urls_still_count(url):
    from invest import publish
    assert publish.is_primary_source(url)


def test_script_url_never_reaches_the_site(invest):
    _, fact = approve_fact(["javascript://www.irs.gov/%0aalert(1)"])
    assert fact["verified"] is False
    assert "javascript" not in (invest / "site" / "data" / "facts.json").read_text()


def test_unknown_fact_key_on_approve_raises(invest):
    with pytest.raises(ValueError, match="Unknown fact key"):
        approve_fact(["https://www.irs.gov/x"], key="not_a_fact")


# ---- Lessons: model output is escaped ------------------------------------------------------------
def test_lesson_page_escapes_model_output(invest):
    from invest import publish
    from invest.agents import lessons
    from invest.schemas import FAQ, Lesson, LessonSection
    evil = '<script>alert("x")</script>'
    page = Lesson.example()
    page.title = f"Compound growth {evil}"
    page.meta_description = 'x" onload="alert(1)'
    page.hook = f"<img src=x onerror=alert(1)> {evil}"
    page.sections = [LessonSection(heading=evil, body=f"{evil}\n\n<a href='javascript:alert(1)'>click</a>")]
    page.key_takeaways = [evil]
    page.try_it = evil
    page.faq = [FAQ(question=evil, answer=evil)]
    page.facts_used = ["cc_apr_assessed"]
    message = lessons.on_approve({"result": page.model_dump()})
    html = (invest / "site" / "learn" / "compound-growth.html").read_text()
    assert "Published" in message
    assert "<script" not in html.lower() and "<img" not in html and "<a href='javascript" not in html
    assert "&lt;script&gt;" in html
    assert 'content="x&quot; onload=&quot;alert(1)"' in html
    assert 'href="https://www.federalreserve.gov/' in html          # the cited fact's source is linked
    index = (invest / "site" / "learn" / "index.html").read_text()
    assert "<script" not in index.lower() and 'href="compound-growth.html"' in index
    assert publish.find_lesson("compound-growth")["published"] is True


def test_lesson_slug_comes_from_the_task_not_the_model(invest):
    from company.llm import FakeLLM
    from invest.agents import lessons
    from invest.schemas import Lesson

    class Sneaky(FakeLLM):
        def structured(self, *, system, prompt, schema, effort="medium"):
            out = super().structured(system=system, prompt=prompt, schema=schema, effort=effort)
            if schema is Lesson:
                out.slug = "../../index"
            return out

    result = lessons.run({"payload": {"key": "compound-growth"}, "instructions": ""}, Sneaky())
    assert result["slug"] == "compound-growth"


def test_published_lesson_cannot_be_rewritten(invest):
    from company.llm import FakeLLM
    from invest import publish
    from invest.agents import lessons
    doc = publish.load_lessons()
    doc["lessons"][0]["published"] = True
    publish.save_lessons(doc)
    with pytest.raises(ValueError, match="already published"):
        lessons.run({"payload": {"key": doc["lessons"][0]["slug"]}, "instructions": ""}, FakeLLM())


# ---- Social packs: disclaimers are added in code -------------------------------------------------
def test_social_pack_has_a_disclaimer_on_every_caption_and_the_newsletter(invest):
    from invest import config
    from invest.agents import social
    from invest.schemas import Carousel, SocialPack, VideoScript
    pack = SocialPack.example()
    pack.videos = [pack.videos[0], VideoScript(hook="h2", script="s2", on_screen_text=["a"], caption="Second caption.",
                                               call_to_action="Link in bio.")]
    pack.carousels = [pack.carousels[0], Carousel(title="t2", slides=["one", "two"], caption="Carousel two.")]
    social.on_approve({"id": 7, "result": pack.model_dump()})
    text = next((invest / "ops" / "outbox").glob("*-task-7.md")).read_text()
    captions = [line for line in text.splitlines() if line.startswith("**Caption:**")]
    assert len(captions) == 4
    assert all(line.endswith(config.DISCLAIMER_SHORT) for line in captions)
    newsletter = text.split("## Newsletter", 1)[1]
    assert f"_{config.DISCLAIMER_SHORT}_" in newsletter


def test_social_pack_with_hype_is_dropped_before_approval(invest):
    from company.llm import FakeLLM
    from invest.agents import social
    from invest.schemas import SocialPack

    class Hype(FakeLLM):
        def structured(self, *, system, prompt, schema, effort="medium"):
            out = super().structured(system=system, prompt=prompt, schema=schema, effort=effort)
            if schema is SocialPack:
                out.videos[0].caption = "This coin is going to the moon, don't miss out!"
            return out

    with pytest.raises(ValueError, match="compliance check twice"):
        social.run({"payload": {}, "instructions": ""}, Hype())


def test_dry_run_examples_pass_the_claims_filter():
    """The canned dry-run content must stay clean, or every dry run would fail compliance."""
    from invest.agents.lessons import lesson_text
    from invest.agents.social import pack_text
    from invest.claims import find_violations
    from invest.schemas import Lesson, SocialPack
    assert find_violations(lesson_text(Lesson.example())) == []
    assert find_violations(pack_text(SocialPack.example())) == []
