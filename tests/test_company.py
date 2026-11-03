import json
import shutil
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture()
def company(tmp_path, monkeypatch):
    """A throwaway copy of the repo's data and site so tests never touch real files."""
    shutil.copytree(REPO / "data", tmp_path / "data")
    shutil.copytree(REPO / "site", tmp_path / "site")
    from company import config
    monkeypatch.setattr(config, "ROOT", tmp_path)
    monkeypatch.setattr(config, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(config, "SITE_DIR", tmp_path / "site")
    monkeypatch.setattr(config, "STATE_FILE", tmp_path / "ops" / "state.json")
    monkeypatch.setattr(config, "BRIEFS_DIR", tmp_path / "ops" / "briefs")
    monkeypatch.setattr(config, "OUTBOX_DIR", tmp_path / "ops" / "outbox")
    return tmp_path


def test_claims_guard_blocks_medical_claims():
    from company.claims import find_violations
    assert find_violations("This filter cures eczema.")
    assert find_violations("Clinically proven to calm skin.")
    assert find_violations("Helps prevent eczema flares.")
    assert not find_violations("Your water treatment plant uses chloramine.")
    assert not find_violations("This tool doesn't diagnose, treat or prevent eczema.")
    assert not find_violations("A vitamin C filter reduces chloramine in independent tests.")


def test_full_day_dry_run_then_approvals(company):
    from company import runner, site
    from company.llm import FakeLLM
    from company.state import AWAITING, State

    brief = Path(runner.run_daily(FakeLLM(), State()))
    assert brief.exists() and "Daily brief" in brief.read_text()

    state = State()
    agents = {t["agent"] for t in state.data["tasks"]}
    # Content for an unverified city is blocked by the CEO guardrail.
    assert agents == {"water_data", "marketing"}
    awaiting = state.by_status(AWAITING)
    assert len(awaiting) == 2

    for t in awaiting:
        runner.approve(t["id"])
    phoenix = site.find_city("phoenix-az")
    assert phoenix["verified"] is True and phoenix["sources"]
    assert list((company / "ops" / "outbox").glob("*.md"))
    water = json.loads((company / "site" / "data" / "water.json").read_text())
    assert any(c["slug"] == "phoenix-az" and c["verified"] for c in water["cities"])

    # Next day, the now-verified city gets its guide.
    runner.run_daily(FakeLLM(), State())
    content = [t for t in State().by_status(AWAITING) if t["agent"] == "content"]
    assert len(content) == 1
    runner.approve(content[0]["id"])
    page = (company / "site" / "cities" / "phoenix-az.html").read_text()
    assert "Phoenix" in page and "not medical advice" in page
    assert "phoenix-az.html" in (company / "site" / "sitemap.xml").read_text()


def test_cannot_approve_twice(company):
    from company import runner
    from company.llm import FakeLLM
    from company.state import AWAITING, State

    runner.run_daily(FakeLLM(), State())
    tid = State().by_status(AWAITING)[0]["id"]
    runner.approve(tid)
    with pytest.raises(ValueError):
        runner.approve(tid)


def test_content_rewrites_after_claims_failure(company):
    from company.agents import content
    from company.llm import FakeLLM
    from company.schemas import CityPage

    doc = json.loads((company / "data" / "cities.json").read_text())
    doc["cities"][0]["verified"] = True
    (company / "data" / "cities.json").write_text(json.dumps(doc))

    class BadThenGood(FakeLLM):
        n = 0
        def structured(self, *, system, prompt, schema, effort="medium"):
            if schema is CityPage:
                self.n += 1
                page = CityPage.example()
                if self.n == 1:
                    page.intro = "Our filter cures eczema."
                return page
            return super().structured(system=system, prompt=prompt, schema=schema, effort=effort)

    llm = BadThenGood()
    result = content.run({"payload": {"city_slug": doc["cities"][0]["slug"]}, "instructions": ""}, llm)
    assert llm.n == 2 and "cures" not in result["intro"]
