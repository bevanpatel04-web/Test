"""Tests for the rewards pilot backend (rewards/). Every test uses its own database under tmp_path."""
from __future__ import annotations

import json
import re
import sqlite3
from datetime import date
from pathlib import Path

import pytest

import rewards
from rewards import db as rdb
from rewards.__main__ import main as cli

REPO = Path(__file__).resolve().parent.parent
CONTRACT = REPO / "docs" / "pilot" / "data-contract.md"
DATE_RX = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MONTH_RX = re.compile(r"^\d{4}-\d{2}$")
EMAIL_RX = re.compile(r"[^@\s]+@[^@\s]+\.[A-Za-z]{2,}")
PHONE_RX = re.compile(r"(?:\+?\d{1,2}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}")


@pytest.fixture(autouse=True)
def _never_touch_default_db(tmp_path, monkeypatch):
    """Point the default database somewhere disposable, so a mistake can't touch rewards/data/pilot.db."""
    monkeypatch.setattr(rdb, "DEFAULT_DB", tmp_path / "default-should-not-be-used.db")
    monkeypatch.delenv(rdb.ENV_VAR, raising=False)


@pytest.fixture()
def conn(tmp_path):
    c = rewards.connect(tmp_path / "test.db")
    rewards.create_employer(c, "emp_t", "Test Cafe", pepm_usd=4.0, points_per_usd=100, pool_funded_usd=50.0,
                            pilot_start="2026-06-01")
    yield c
    c.close()


def add(conn, member_id, hire, enrolled="2026-06-01", left=None):
    rewards.add_member(conn, member_id, "emp_t", f"Member {member_id[-3:]}", hire, enrolled_on=enrolled, left_on=left)


@pytest.fixture(scope="module")
def demo_db(tmp_path_factory):
    path = tmp_path_factory.mktemp("demo") / "demo.db"
    rewards.seed_demo(path, seed=42)
    return path


# --- Earning: tenure -----------------------------------------------------------------------------
def test_tenure_awards_are_idempotent(conn):
    add(conn, "m_001", "2026-05-20")
    first = rewards.award_tenure(conn, "2026-09-01")
    assert [g["rule"] for g in first] == ["tenure_30", "tenure_90"]
    assert rewards.balance(conn, "m_001") == 600
    assert rewards.award_tenure(conn, "2026-09-01") == []
    assert rewards.award_tenure(conn, "2026-09-02") == []
    assert rewards.balance(conn, "m_001") == 600
    later = rewards.award_tenure(conn, "2026-12-01")
    assert [g["rule"] for g in later] == ["tenure_180"]
    assert rewards.balance(conn, "m_001") == 1200
    assert len(rewards.ledger(conn, "m_001")) == 3


def test_tenure_only_counts_milestones_reached_on_or_after_enrolling(conn):
    add(conn, "m_001", "2026-01-01")              # 30 and 90 days were reached before the pilot
    add(conn, "m_002", "2026-05-02")              # 30 days falls exactly on the enrolment day
    rewards.award_tenure(conn, "2026-07-15")
    rows = rewards.ledger(conn, "m_001")
    assert [(r["rule"], r["date"]) for r in rows] == [("tenure_180", "2026-06-30")]   # dated the day it was reached
    assert [r["rule"] for r in rewards.ledger(conn, "m_002")] == ["tenure_30"]


def test_tenure_skips_not_enrolled_and_people_who_left(conn):
    add(conn, "m_001", "2026-05-20", enrolled=None)
    add(conn, "m_002", "2026-05-20", left="2026-06-10")
    add(conn, "m_003", "2026-05-20", left="2026-08-01")       # left after 30 days, before 90
    assert rewards.award_tenure(conn, "2026-06-25") == [
        {"member_id": "m_003", "rule": "tenure_30", "date": "2026-06-19", "points": 300}]
    assert rewards.award_tenure(conn, "2026-12-01") == []      # nobody still employed and enrolled
    assert rewards.balance(conn, "m_001") == rewards.balance(conn, "m_002") == 0


# --- Earning: lessons and habits -----------------------------------------------------------------
def test_lesson_cap_and_duplicate_lessons(conn):
    add(conn, "m_001", "2026-05-01")
    assert rewards.record_lesson(conn, "m_001", "compound-growth", "2026-06-02") == 50
    assert rewards.record_lesson(conn, "m_001", "compound-growth", "2026-06-03") == 0    # same lesson again
    for i in range(2, 13):
        rewards.record_lesson(conn, "m_001", f"lesson-{i}", "2026-06-05")
    assert rewards.balance(conn, "m_001") == 500                                        # 10 lessons x 50
    paid = [r for r in rewards.ledger(conn, "m_001") if r["rule"] == "lesson_completed"]
    assert len(paid) == 10
    assert rewards.record_lesson(conn, "m_001", "one-more", "2026-06-06") == 0
    row = next(m for m in rewards.export_employer(conn, "emp_t", "2026-06-30")["members"] if m["id"] == "m_001")
    assert row["lessons_completed"] == 13            # completions are counted even past the points cap
    assert rewards.award(conn, "m_001", "lesson_completed", "2026-06-07", ref="another") == 0


def test_checklist_and_savings_are_one_time(conn):
    add(conn, "m_001", "2026-05-01")
    assert rewards.record_checklist(conn, "m_001", "2026-06-02") == 200
    assert rewards.record_checklist(conn, "m_001", "2026-07-02") == 0
    assert rewards.record_savings_setup(conn, "m_001", "2026-06-03") == 300
    assert rewards.record_savings_setup(conn, "m_001", "2026-06-04") == 0
    assert rewards.award(conn, "m_001", "savings_setup", "2026-06-05") == 0
    assert rewards.balance(conn, "m_001") == 500


def test_earning_needs_an_enrolled_employed_member(conn):
    add(conn, "m_001", "2026-05-01", enrolled=None)
    add(conn, "m_002", "2026-05-01", left="2026-07-01")
    with pytest.raises(rewards.NotEligibleError):
        rewards.record_lesson(conn, "m_001", "compound-growth", "2026-06-02")
    with pytest.raises(rewards.NotEligibleError):
        rewards.record_checklist(conn, "m_002", "2026-05-15")         # before enrolling
    with pytest.raises(rewards.NotEligibleError):
        rewards.record_savings_setup(conn, "m_002", "2026-07-01")     # the day they left
    with pytest.raises(rewards.NotFoundError):
        rewards.record_checklist(conn, "m_999", "2026-06-02")


# --- Forbidden rules -----------------------------------------------------------------------------
FORBIDDEN_NAMES = ["trade_count_bonus", "weekly_trading_streak", "first_trade", "trades_10", "portfolio_milestone",
                   "account_balance_bonus", "savings_balance_1000", "investment_returns_bonus", "beat_the_market_return",
                   "profit_share", "crypto_quest", "stock_picker", "TRADING_BONUS"]


@pytest.mark.parametrize("name", FORBIDDEN_NAMES)
def test_forbidden_rule_names_are_rejected(conn, name):
    add(conn, "m_001", "2026-05-01")
    with pytest.raises(rewards.ForbiddenRuleError, match="not allowed"):
        rewards.define_rule(name, "Some bonus", 100)
    with pytest.raises(rewards.ForbiddenRuleError, match="trading"):
        rewards.award(conn, "m_001", name, "2026-06-02")
    assert rewards.ledger(conn, "m_001") == []


@pytest.mark.parametrize("label, config", [
    ("Bonus when your portfolio grows", {}),
    ("Weekly bonus", {"metric": "trade_count"}),
    ("Weekly bonus", {"min_balance": 100}),
    ("Weekly bonus", {"when": {"field": "investment_return", "above": 0.05}}),
    ("Weekly bonus", {"triggers": ["shift_done", "trades_placed"]}),
])
def test_forbidden_rule_labels_and_configs_are_rejected(label, config):
    with pytest.raises(rewards.ForbiddenRuleError):
        rewards.define_rule("weekly_bonus", label, 100, config=config)
    with pytest.raises(rewards.ForbiddenRuleError):
        rewards.Rule(name="weekly_bonus", label=label, points=100, config=config)


def test_allowed_rules_pass_the_check():
    for rule in rewards.PILOT_RULES.values():
        rewards.check_rule_allowed(rule.name, rule.label, rule.config)
    assert rewards.define_rule("shift_streak", "Ten shifts in a row", 100).points == 100
    with pytest.raises(rewards.UnknownRuleError):
        rewards.rules.pilot_rule("shift_streak")    # valid, but not one of the pilot's rules


# --- Redemptions ---------------------------------------------------------------------------------
def test_redemption_limits_balance_minimum_and_pool(conn):
    add(conn, "m_001", "2026-05-01")
    add(conn, "m_002", "2026-05-01")
    rewards.adjust(conn, "m_001", 6000, "2026-06-02", key="test-grant")
    rewards.adjust(conn, "m_002", 600, "2026-06-02", key="test-grant")
    with pytest.raises(rewards.BelowMinimumError):
        rewards.request_redemption(conn, "m_001", "gift_card", 499, "2026-06-03")
    with pytest.raises(rewards.InsufficientPointsError):
        rewards.request_redemption(conn, "m_001", "payroll_bonus", 6100, "2026-06-03")
    with pytest.raises(rewards.PoolExhaustedError):                     # $60 > $50 pool
        rewards.request_redemption(conn, "m_001", "payroll_bonus", 6000, "2026-06-03")
    r = rewards.request_redemption(conn, "m_001", "payroll_bonus", 4750, "2026-06-03")
    assert (r["usd"], r["status"]) == (47.5, "requested")
    assert rewards.balance(conn, "m_001") == 1250
    assert rewards.pool_remaining(conn, "emp_t") == 2.5
    with pytest.raises(rewards.PoolExhaustedError):                     # $5 > $2.50 left
        rewards.request_redemption(conn, "m_002", "gift_card", 500, "2026-06-04")
    assert rewards.balance(conn, "m_002") == 600                         # a refused request costs nothing


def test_cancel_refunds_points_with_a_new_ledger_row(conn):
    add(conn, "m_001", "2026-05-01")
    rewards.adjust(conn, "m_001", 1500, "2026-06-02", key="test-grant")
    r = rewards.request_redemption(conn, "m_001", "gift_card", 1000, "2026-06-03")
    before = rewards.ledger(conn, "m_001")
    rewards.cancel_redemption(conn, r["id"], "2026-06-04")
    after = rewards.ledger(conn, "m_001")
    assert after[:len(before)] == before                                 # nothing was changed in place
    assert [(x["kind"], x["rule"], x["points"]) for x in after[len(before):]] == [("adjust", "redemption_cancelled", 1000)]
    assert rewards.balance(conn, "m_001") == 1500
    assert rewards.pool_remaining(conn, "emp_t") == 50.0
    assert rewards.get_redemption(conn, r["id"])["status"] == "cancelled"
    with pytest.raises(rewards.RedemptionError):                         # no second refund
        rewards.cancel_redemption(conn, r["id"], "2026-06-05")
    assert rewards.balance(conn, "m_001") == 1500
    done = rewards.request_redemption(conn, "m_001", "payroll_bonus", 500, "2026-06-06")
    rewards.fulfill_redemption(conn, done["id"], "2026-06-10")
    with pytest.raises(rewards.RedemptionError):                         # paid out: can't be cancelled
        rewards.cancel_redemption(conn, done["id"], "2026-06-11")


def test_redemption_retry_with_same_id_is_safe(conn):
    add(conn, "m_001", "2026-05-01")
    rewards.adjust(conn, "m_001", 1000, "2026-06-02", key="test-grant")
    a = rewards.request_redemption(conn, "m_001", "gift_card", 500, "2026-06-03", redemption_id="r_tap1")
    b = rewards.request_redemption(conn, "m_001", "gift_card", 500, "2026-06-03", redemption_id="r_tap1")
    assert a == b and rewards.balance(conn, "m_001") == 500
    with pytest.raises(rewards.RedemptionError):
        rewards.request_redemption(conn, "m_001", "gift_card", 600, "2026-06-03", redemption_id="r_tap1")


def test_redeeming_needs_an_enrolled_employed_member(conn):
    add(conn, "m_001", "2026-05-01", left="2026-07-01")
    rewards.adjust(conn, "m_001", 1000, "2026-06-02", key="test-grant")
    with pytest.raises(rewards.NotEligibleError):
        rewards.request_redemption(conn, "m_001", "payroll_bonus", 500, "2026-07-02")


def test_invest_deposit_is_disabled(conn):
    add(conn, "m_001", "2026-05-01")
    rewards.adjust(conn, "m_001", 1000, "2026-06-02", key="test-grant")
    with pytest.raises(rewards.RedemptionDisabledError, match="licensed brokerage partner"):
        rewards.request_redemption(conn, "m_001", "invest_deposit", 500, "2026-06-03")
    with pytest.raises(rewards.RedemptionDisabledError, match="not part of the pilot"):
        rewards.request_redemption(conn, "m_001", "invest_deposit", 500, "2026-06-03")
    assert rewards.balance(conn, "m_001") == 1000
    catalog = rewards.export_member(conn, "m_001", "2026-06-03")["catalog"]
    assert [c["type"] for c in catalog] == ["payroll_bonus", "gift_card"]


# --- Append-only ledger ----------------------------------------------------------------------------
def test_ledger_refuses_update_and_delete(conn):
    add(conn, "m_001", "2026-05-01")
    rewards.record_checklist(conn, "m_001", "2026-06-02")
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        conn.execute("UPDATE ledger SET points = 9999")
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        conn.execute("DELETE FROM ledger")
    assert rewards.balance(conn, "m_001") == 200
    with pytest.raises(rewards.InsufficientPointsError):                 # corrections can't go below zero
        rewards.adjust(conn, "m_001", -500, "2026-06-03", key="fix-1")
    assert rewards.adjust(conn, "m_001", -50, "2026-06-03", key="fix-1") is True
    assert rewards.adjust(conn, "m_001", -50, "2026-06-03", key="fix-1") is False   # retried: no double correction
    assert [r["points"] for r in rewards.ledger(conn, "m_001")] == [200, -50]


def test_code_never_updates_or_deletes_ledger_rows():
    bad = re.compile(r"UPDATE\s+ledger\b|DELETE\s+FROM\s+ledger\b|REPLACE\s+INTO\s+ledger\b|INSERT\s+OR\s+REPLACE", re.I)
    for path in (REPO / "rewards").glob("*.py"):
        assert not bad.search(path.read_text()), path


# --- Retention -------------------------------------------------------------------------------------
def test_retention_cohorts_by_month(conn):
    for i in range(1, 5):
        add(conn, f"m_00{i}", "2026-03-01")                           # enrolled at pilot start
    rewards.record_departure(conn, "m_004", "2026-06-15")
    add(conn, "m_005", "2026-03-01", enrolled=None)                    # comparison group
    add(conn, "m_006", "2026-03-01", enrolled=None, left="2026-07-01")  # gone on the morning of July 1
    add(conn, "m_007", "2026-06-20", enrolled="2026-06-20")             # hired after the start: in neither group
    add(conn, "m_008", "2026-03-01", left="2026-08-20")
    out = rewards.retention(conn, "emp_t", "2026-09-10")
    assert out == [
        {"month": "2026-06", "enrolled_pct": 100.0, "not_enrolled_pct": 100.0},
        {"month": "2026-07", "enrolled_pct": 80.0, "not_enrolled_pct": 50.0},
        {"month": "2026-08", "enrolled_pct": 80.0, "not_enrolled_pct": 50.0},
        {"month": "2026-09", "enrolled_pct": 60.0, "not_enrolled_pct": 50.0},
    ]
    assert rewards.retention(conn, "emp_t", "2026-05-31") == []


def test_demo_retention_starts_at_100(demo_db):
    out = rewards.export_employer(demo_db, "emp_demo", "2026-11-14")["retention"]
    assert out[0] == {"month": "2026-06", "enrolled_pct": 100.0, "not_enrolled_pct": 100.0}
    assert [r["month"] for r in out] == ["2026-06", "2026-07", "2026-08", "2026-09", "2026-10", "2026-11"]
    for r in out:
        for k in ("enrolled_pct", "not_enrolled_pct"):
            assert 0 <= r[k] <= 100 and round(r[k], 1) == r[k]


# --- Exports vs the data contract -------------------------------------------------------------------
def contract_examples() -> tuple[dict, dict]:
    blocks = re.findall(r"```json\s*\n(.*?)\n```", CONTRACT.read_text(encoding="utf-8"), re.S)
    assert len(blocks) == 2, "expected the employer and member examples in the data contract"
    return json.loads(blocks[0]), json.loads(blocks[1])


def assert_same_shape(example, actual, path="$"):
    """Same keys at every level, same JSON types (int and float kept apart), ISO dates where the contract has them."""
    if isinstance(example, dict):
        assert isinstance(actual, dict), f"{path}: expected an object"
        assert set(actual) == set(example), f"{path}: extra {set(actual) - set(example)}, missing {set(example) - set(actual)}"
        for key, value in example.items():
            assert_same_shape(value, actual[key], f"{path}.{key}")
    elif isinstance(example, list):
        assert isinstance(actual, list), f"{path}: expected a list"
        assert actual, f"{path}: empty list, nothing to check"
        for item in example[1:]:
            assert_same_shape(example[0], item, f"{path} (contract example)")
        for i, item in enumerate(actual):
            assert_same_shape(example[0], item, f"{path}[{i}]")
    else:
        assert type(actual) is type(example), f"{path}: {type(actual).__name__}, contract has {type(example).__name__}"
        if isinstance(example, str) and DATE_RX.match(example):
            assert DATE_RX.match(actual) and date.fromisoformat(actual), f"{path}: not an ISO date: {actual!r}"
        if isinstance(example, str) and MONTH_RX.match(example):
            assert MONTH_RX.match(actual), f"{path}: not YYYY-MM: {actual!r}"


def all_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield k
            yield from all_strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from all_strings(v)


def test_demo_exports_match_the_contract_exactly(demo_db):
    employer_example, member_example = contract_examples()
    employer = rewards.export_employer(demo_db, "emp_demo", "2026-11-14")
    member = rewards.export_member(demo_db, "m_001", "2026-11-14")
    assert_same_shape(employer_example, employer)
    assert_same_shape(member_example, member)
    # Round-trips through JSON unchanged (no dates or other Python objects left in it).
    assert json.loads(json.dumps(employer)) == employer and json.loads(json.dumps(member)) == member
    assert {h["kind"] for h in member["history"]} <= {"earn", "redeem", "adjust"}
    assert member["catalog"] == member_example["catalog"]                 # same types, labels, minimums, notes
    dates = [h["date"] for h in member["history"]]
    assert dates == sorted(dates)                                        # oldest first


def test_exports_with_refunds_and_corrections_match_the_contract(conn):
    employer_example, member_example = contract_examples()
    add(conn, "m_001", "2026-05-02")                  # 30 days falls on the enrolment day, so it counts
    rewards.award_tenure(conn, "2026-06-30")
    rewards.record_lesson(conn, "m_001", "compound-growth", "2026-06-02")
    rewards.adjust(conn, "m_001", 500, "2026-06-03", key="goodwill")
    r = rewards.request_redemption(conn, "m_001", "gift_card", 500, "2026-06-04")
    rewards.cancel_redemption(conn, r["id"], "2026-06-05")
    rewards.request_redemption(conn, "m_001", "payroll_bonus", 750, "2026-06-06")
    employer = rewards.export_employer(conn, "emp_t", "2026-06-30")
    member = rewards.export_member(conn, "m_001", "2026-06-30")
    assert_same_shape(employer_example, employer)
    assert_same_shape(member_example, member)
    assert {h["kind"] for h in member["history"]} == {"earn", "redeem", "adjust"}
    s = employer["summary"]
    assert s["points_issued"] == 300 + 50 + 500 and s["points_redeemed"] == 750
    assert s["points_outstanding"] == s["points_issued"] - s["points_redeemed"] == member["points_balance"] == 100
    assert sum(e["points"] for e in employer["earning_by_rule"]) == s["points_issued"]
    assert employer["redemptions"] == [{"type": "payroll_bonus", "label": "Payroll bonus", "count": 1, "usd": 7.5},
                                       {"type": "gift_card", "label": "Gift card", "count": 0, "usd": 0.0}]
    assert employer["employer"]["pool_remaining_usd"] == 42.5


def test_member_export_next_milestone_progress(conn):
    add(conn, "m_001", "2026-08-11", enrolled="2026-08-11")
    rewards.award_tenure(conn, "2026-11-14")
    rewards.record_lesson(conn, "m_001", "compound-growth", "2026-09-01")
    out = rewards.export_member(conn, "m_001", "2026-11-14")
    assert out["member"]["tenure_days"] == 95
    assert [h["rule"] for h in out["history"]] == ["lesson_completed", "tenure_30", "tenure_90"]
    assert out["next_milestones"][0] == {"rule": "tenure_180", "label": "180 days on the job", "points": 600,
                                         "progress_pct": 52.8}    # the contract's own example
    assert {"rule": "lesson_completed", "label": "Finished a lesson", "points": 50, "progress_pct": 10.0} in out["next_milestones"]
    with pytest.raises(rewards.NotEligibleError):
        add(conn, "m_002", "2026-05-01", enrolled=None)
        rewards.export_member(conn, "m_002", "2026-11-14")


def test_demo_summary_adds_up(demo_db):
    e = rewards.export_employer(demo_db, "emp_demo", "2026-11-14")
    s, emp = e["summary"], e["employer"]
    assert (s["eligible"], s["enrolled"]) == (400, 240)
    assert s["points_outstanding"] == s["points_issued"] - s["points_redeemed"]
    assert sum(r["points"] for r in e["earning_by_rule"]) == s["points_issued"]
    assert sum(m["points_balance"] for m in e["members"]) == s["points_outstanding"]
    assert len(e["members"]) == s["enrolled"] and 0 < s["active_30d"] <= s["enrolled"]
    spent = sum(r["usd"] for r in e["redemptions"])
    assert round(emp["pool_funded_usd"] - spent, 2) == emp["pool_remaining_usd"] > 0
    assert s["points_redeemed"] == round(spent * emp["points_per_usd"])
    assert all(m["points_balance"] >= 0 for m in e["members"])


# --- Privacy -------------------------------------------------------------------------------------
def test_exports_have_no_contact_details(demo_db):
    for out in (rewards.export_employer(demo_db, "emp_demo", "2026-11-14"),
                rewards.export_member(demo_db, "m_001", "2026-11-14")):
        for text in all_strings(out):
            assert not EMAIL_RX.search(text) and "@" not in text, text
            assert not PHONE_RX.search(re.sub(r"\d{4}-\d{2}-\d{2}", "", text)), text
    names = [m["display_name"] for m in rewards.export_employer(demo_db, "emp_demo", "2026-11-14")["members"]]
    assert all(re.fullmatch(r"Member \d{3}", n) for n in names)


@pytest.mark.parametrize("name", ["jo@example.com", "Call 555-123-4567", "(555) 123 4567", "+1 555 123 4567"])
def test_contact_details_are_refused_as_display_names(conn, name):
    with pytest.raises(rewards.PrivacyError):
        rewards.add_member(conn, "m_001", "emp_t", name, "2026-05-01")


def test_schema_has_no_contact_columns(conn):
    cols = {r[1] for t in ("employers", "members", "ledger", "redemptions", "completions")
            for r in conn.execute(f"PRAGMA table_info({t})")}
    assert not {c for c in cols if re.search(r"email|phone|first_name|last_name|full_name|address|ssn", c)}


# --- Demo seed -----------------------------------------------------------------------------------
def test_demo_seed_is_deterministic(tmp_path, demo_db):
    other = tmp_path / "again.db"
    rewards.seed_demo(other, seed=42)
    for fn, ident in ((rewards.export_employer, "emp_demo"), (rewards.export_member, "m_001")):
        assert fn(other, ident, "2026-11-14") == fn(demo_db, ident, "2026-11-14")
    different = tmp_path / "seed7.db"
    rewards.seed_demo(different, seed=7)
    assert rewards.export_employer(different, "emp_demo", "2026-11-14") != rewards.export_employer(demo_db, "emp_demo", "2026-11-14")
    with pytest.raises(rewards.RewardsError, match="already has data"):
        rewards.seed_demo(other, seed=42)


def test_demo_seed_shape(demo_db):
    c = rewards.connect(demo_db)
    try:
        assert rdb.get_meta(c, "simulated") == "true"
        emp = dict(c.execute("SELECT * FROM employers").fetchone())
        assert emp == {"id": "emp_demo", "name": "Demo Diner Group", "plan": "pilot", "pepm_usd": 4.0,
                       "points_per_usd": 100, "pool_funded_usd": 5000.0, "pilot_start": "2026-06-01"}
        ids = [r[0] for r in c.execute("SELECT id FROM members ORDER BY id")]
        assert ids == [f"m_{i:03d}" for i in range(1, 401)]
        hires = [r[0] for r in c.execute("SELECT hire_date FROM members")]
        assert "2024-12-01" <= min(hires) and max(hires) < "2026-06-01"
        m1 = rewards.export_member(c, "m_001", "2026-11-14")
        assert m1["history"] and m1["next_milestones"]
        statuses = {r[0] for r in c.execute("SELECT DISTINCT status FROM redemptions")}
        assert statuses == {"requested", "fulfilled", "cancelled"}
        # The tenure job ran nightly; running it again on the as-of date grants nothing.
        assert rewards.award_tenure(c, "2026-11-14") == []
    finally:
        c.close()


# --- CLI and configuration -------------------------------------------------------------------------
def test_cli_end_to_end(tmp_path, capsys):
    db, out = tmp_path / "cli.db", tmp_path / "export"
    assert cli(["seed-demo", "--db", str(db)]) == 0
    assert "SIMULATED" in capsys.readouterr().out
    assert cli(["award", "--as-of", "2026-11-14", "--db", str(db)]) == 0
    assert "Granted 0 tenure milestone(s)" in capsys.readouterr().out
    assert cli(["status", "--db", str(db), "--as-of", "2026-11-14"]) == 0
    text = capsys.readouterr().out
    assert "SIMULATED" in text and "emp_demo" in text and "remaining" in text
    assert cli(["export", "--db", str(db), "--employer", "emp_demo", "--member", "m_001",
                "--as-of", "2026-11-14", "--out", str(out)]) == 0
    assert "SIMULATED" in capsys.readouterr().out
    employer = json.loads((out / "employer.json").read_text())
    member = json.loads((out / "member.json").read_text())
    assert employer == rewards.export_employer(db, "emp_demo", "2026-11-14")
    assert member == rewards.export_member(db, "m_001", "2026-11-14")
    assert cli(["seed-demo", "--db", str(db)]) == 1                       # refuses to reseed over data
    assert "already has data" in capsys.readouterr().err


def test_db_path_resolution(tmp_path, monkeypatch):
    assert rewards.resolve_db_path(None) == rdb.DEFAULT_DB
    monkeypatch.setenv("REWARDS_DB", str(tmp_path / "env.db"))
    assert rewards.resolve_db_path(None) == tmp_path / "env.db"
    assert rewards.resolve_db_path(tmp_path / "flag.db") == tmp_path / "flag.db"
    assert cli(["status"]) == 0                                           # uses $REWARDS_DB
    assert (tmp_path / "env.db").exists()


def test_bad_inputs_fail_clearly(conn):
    with pytest.raises(ValueError):
        rewards.record_lesson(conn, "m_001", "Not A Slug!", "2026-06-02")
    with pytest.raises(ValueError):
        add(conn, "m_001", "2026/05/01")
    with pytest.raises(rewards.RedemptionError, match="Unknown redemption type"):
        rewards.request_redemption(conn, "m_001", "cash_out", 500, "2026-06-02")
    with pytest.raises(rewards.RewardsError, match="award_tenure"):
        add(conn, "m_002", "2026-05-01")
        rewards.award(conn, "m_002", "tenure_30", "2026-06-02")
