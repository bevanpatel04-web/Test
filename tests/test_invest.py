import json
import shutil
from datetime import date
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture()
def invest(tmp_path, monkeypatch):
    """A throwaway copy of the product's data and site so tests never touch real files."""
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


def test_claims_guard_blocks_hype_and_advice():
    from invest.claims import find_violations
    for bad in ["Index funds are guaranteed to grow.", "A risk-free way to invest.", "You should buy index funds.",
                "Your money will grow to $500,000.", "This coin could 100x.", "Grab some $TSLA today.",
                "We recommend investing in tech.", "Act now before prices rise.", "Steady returns every year."]:
        assert find_violations(bad), bad
    for ok in ["Past performance doesn't guarantee future results.", "No investment is risk-free.",
               "There's no guarantee you'll come out ahead.", "Buy now, pay later loans can add up.",
               "Your balance could grow to about $247,000 at a hypothetical 6% a year.",
               "Some people call an employer match free money.", "This will make more sense with an example."]:
        assert not find_violations(ok), ok


def test_full_day_dry_run_then_approvals(invest):
    from invest import publish, runner
    from company.llm import FakeLLM
    from company.state import AWAITING, State

    brief = Path(runner.run_daily(FakeLLM(), State(invest / "ops" / "state.json")))
    assert brief.exists() and "daily brief" in brief.read_text()

    state = runner.load_state()
    created = {(t["agent"], t["payload"].get("key")) for t in state.data["tasks"]}
    # The Roth IRA lesson needs an unverified fact, so the CEO guardrail blocks it.
    assert created == {("facts", "roth_ira_phaseout_single_2027"), ("lessons", "compound-growth"), ("social", None)}
    assert len(state.by_status(AWAITING)) == 3

    for t in state.by_status(AWAITING):
        runner.approve(t["id"])
    assert publish.find_fact("roth_ira_phaseout_single_2027")["verified"] is True
    page = (invest / "site" / "learn" / "compound-growth.html").read_text()
    assert "Compound growth" in page and "Education, not advice" in page
    assert 'href="compound-growth.html"' in (invest / "site" / "learn" / "index.html").read_text()
    assert "/learn/compound-growth.html" in (invest / "site" / "sitemap.xml").read_text()
    assert publish.find_lesson("compound-growth")["published"] is True
    outbox = next((invest / "ops" / "outbox").glob("*.md")).read_text()
    assert "Education, not financial advice." in outbox
    public = json.loads((invest / "site" / "data" / "facts.json").read_text())
    assert "roth_ira_phaseout_single_2027" in {f["key"] for f in public["facts"]}

    # Next day the now-unblocked Roth IRA lesson gets written; the published one isn't repeated.
    runner.run_daily(FakeLLM())
    lessons = [t["payload"]["key"] for t in runner.load_state().by_status(AWAITING) if t["agent"] == "lessons"]
    assert lessons == ["roth-ira-basics"]


def test_fact_needs_an_official_source(invest):
    from invest import publish
    from invest.agents import facts
    from invest.schemas import FactVerification

    v = FactVerification.example()
    v.sources = ["https://www.some-finance-blog.com/roth-limits"]
    facts.on_approve({"result": v.model_dump()})
    assert publish.find_fact("roth_ira_phaseout_single_2027")["verified"] is False
    public = json.loads((invest / "site" / "data" / "facts.json").read_text())
    assert "roth_ira_phaseout_single_2027" not in {f["key"] for f in public["facts"]}
    assert publish.is_primary_source("https://www.irs.gov/newsroom/x")
    assert not publish.is_primary_source("https://irs.gov.example.com/x")


def test_lesson_rewrites_after_violation_then_gives_up(invest):
    from company.llm import FakeLLM
    from invest.agents import lessons
    from invest.schemas import Lesson

    class Writer(FakeLLM):
        def __init__(self, bad_drafts):
            super().__init__()
            self.bad_drafts, self.n = bad_drafts, 0

        def structured(self, *, system, prompt, schema, effort="medium"):
            if schema is Lesson:
                self.n += 1
                page = Lesson.example()
                if self.n <= self.bad_drafts:
                    page.hook = "Index funds are a safe bet that can't lose."
                return page
            return super().structured(system=system, prompt=prompt, schema=schema, effort=effort)

    task = {"payload": {"key": "compound-growth"}, "instructions": ""}
    llm = Writer(bad_drafts=1)
    result = lessons.run(task, llm)
    assert llm.n == 2 and "safe bet" not in result["hook"]

    with pytest.raises(ValueError, match="compliance check twice"):
        lessons.run(task, Writer(bad_drafts=2))


def test_lessons_cannot_use_unverified_facts(invest):
    from company.llm import FakeLLM
    from invest import publish
    from invest.agents import lessons
    from invest.schemas import Lesson

    with pytest.raises(ValueError, match="needs facts verified"):
        lessons.run({"payload": {"key": "market-crashes"}, "instructions": ""}, FakeLLM())

    page = Lesson.example()
    page.facts_used = ["sp500_2008_return"]
    with pytest.raises(ValueError, match="aren't verified"):
        publish.write_lesson_page(page)


def test_stale_facts_are_flagged(invest):
    from invest import publish
    fact = publish.find_fact("cc_apr_assessed")
    assert not publish.is_stale(fact, today=date.fromisoformat(fact["verified_on"]))
    assert publish.is_stale(fact, today=date(2027, 6, 1))
