"""Retention and the two dashboard exports defined in docs/pilot/data-contract.md.

The exports are built through strict pydantic models with extra="forbid", so a missing key, an
extra key or a wrong type fails here instead of in the dashboard.
"""
from __future__ import annotations

import os
import sqlite3
from datetime import date, timedelta
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .db import to_date, using
from .engine import get_employer, get_member, is_employed, pool_remaining, tenure_days
from .errors import NotEligibleError
from .rules import (ENABLED_CATALOG, MANUAL_RULE, MAX_LESSONS, PILOT_RULES, REFUND_RULE, TENURE_RULES,
                    ADJUST_LABELS, check_no_contact, ledger_label)

ACTIVE_WINDOW_DAYS = 30


# --- Contract models ---------------------------------------------------------------------------
class _Out(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class EmployerInfo(_Out):
    id: str
    name: str
    plan: str
    pepm_usd: float
    points_per_usd: int
    pool_funded_usd: float
    pool_remaining_usd: float


class Summary(_Out):
    eligible: int
    enrolled: int
    active_30d: int
    points_issued: int
    points_redeemed: int
    points_outstanding: int


class RetentionPoint(_Out):
    month: str = Field(pattern=r"^\d{4}-\d{2}$")
    enrolled_pct: float
    not_enrolled_pct: float


class RuleTotal(_Out):
    rule: str
    label: str
    points: int


class RedemptionTotal(_Out):
    type: str
    label: str
    count: int
    usd: float


class MemberRow(_Out):
    id: str
    display_name: str
    tenure_days: int
    points_balance: int
    lessons_completed: int
    last_active: date


class EmployerExport(_Out):
    as_of: date
    employer: EmployerInfo
    summary: Summary
    retention: list[RetentionPoint]
    earning_by_rule: list[RuleTotal]
    redemptions: list[RedemptionTotal]
    members: list[MemberRow]


class MemberInfo(_Out):
    id: str
    display_name: str
    employer_name: str
    tenure_days: int


class HistoryItem(_Out):
    date: date
    kind: Literal["earn", "redeem", "adjust"]
    rule: str
    label: str
    points: int


class Milestone(_Out):
    rule: str
    label: str
    points: int
    progress_pct: float


class CatalogItem(_Out):
    type: str
    label: str
    min_points: int
    note: str


class MemberExport(_Out):
    as_of: date
    member: MemberInfo
    points_balance: int
    points_per_usd: int
    history: list[HistoryItem]
    next_milestones: list[Milestone]
    catalog: list[CatalogItem]


# --- Retention ---------------------------------------------------------------------------------
def _month_starts(start: date, as_of: date) -> list[date]:
    """The pilot start, then the first day of each later month, up to as_of."""
    if as_of < start:
        return []
    points = [start]
    y, m = start.year, start.month
    while True:
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
        d = date(y, m, 1)
        if d > as_of:
            return points
        points.append(d)


def retention(conn: sqlite3.Connection, employer_id: str, as_of: date | str) -> list[dict]:
    """Share of each starting group still employed at each month start since the pilot began.

    Both groups are people employed on the pilot start date: those enrolled by then, and eligible
    employees who were not (the comparison group). The first month is 100.0 for both.
    """
    as_of = to_date(as_of)
    start = to_date(get_employer(conn, employer_id)["pilot_start"])
    staff = [m for m in conn.execute("SELECT * FROM members WHERE employer_id = ?", (employer_id,))
             if is_employed(m, start)]
    enrolled = [m for m in staff if m["enrolled_on"] and to_date(m["enrolled_on"]) <= start]
    others = [m for m in staff if not (m["enrolled_on"] and to_date(m["enrolled_on"]) <= start)]

    def pct(group: list, on: date) -> float:
        if not group:
            return 0.0
        return round(100.0 * sum(1 for m in group if is_employed(m, on)) / len(group), 1)

    out = []
    for i, d in enumerate(_month_starts(start, as_of)):
        first = i == 0
        out.append({"month": d.strftime("%Y-%m"),
                    "enrolled_pct": 100.0 if first else pct(enrolled, d),
                    "not_enrolled_pct": 100.0 if first else pct(others, d)})
    return out


# --- Shared queries ----------------------------------------------------------------------------
def _ledger_totals(conn: sqlite3.Connection, employer_id: str, as_of: date) -> dict[tuple[str, str], int]:
    rows = conn.execute(
        "SELECT l.kind, l.rule, SUM(l.points) AS pts FROM ledger l JOIN members m ON m.id = l.member_id"
        " WHERE m.employer_id = ? AND l.date <= ? GROUP BY l.kind, l.rule", (employer_id, as_of.isoformat()))
    return {(r["kind"], r["rule"]): int(r["pts"]) for r in rows}


def _redemption_totals(conn: sqlite3.Connection, employer_id: str, as_of: date) -> dict[str, tuple[int, float]]:
    """Count and USD per type of redemptions requested by as_of and not cancelled by then."""
    d = as_of.isoformat()
    rows = conn.execute(
        "SELECT r.type, COUNT(*) AS n, COALESCE(SUM(r.usd), 0) AS usd FROM redemptions r"
        " JOIN members m ON m.id = r.member_id WHERE m.employer_id = ? AND r.requested_on <= ?"
        " AND NOT (r.status = 'cancelled' AND r.cancelled_on <= ?) GROUP BY r.type", (employer_id, d, d))
    return {r["type"]: (int(r["n"]), round(float(r["usd"]), 2)) for r in rows}


def _member_rows(conn: sqlite3.Connection, employer_id: str, as_of: date) -> list[dict]:
    d = as_of.isoformat()
    members = conn.execute(
        "SELECT * FROM members WHERE employer_id = ? AND enrolled_on IS NOT NULL AND enrolled_on <= ? ORDER BY id",
        (employer_id, d)).fetchall()
    balances = dict(conn.execute(
        "SELECT l.member_id, SUM(l.points) FROM ledger l JOIN members m ON m.id = l.member_id"
        " WHERE m.employer_id = ? AND l.date <= ? GROUP BY l.member_id", (employer_id, d)).fetchall())
    lessons = dict(conn.execute(
        "SELECT c.member_id, COUNT(*) FROM completions c JOIN members m ON m.id = c.member_id"
        " WHERE m.employer_id = ? AND c.kind = 'lesson' AND c.date <= ? GROUP BY c.member_id",
        (employer_id, d)).fetchall())
    last = dict(conn.execute(
        "SELECT member_id, MAX(date) FROM ("
        "  SELECT member_id, date FROM completions WHERE date <= ?"
        "  UNION ALL SELECT member_id, requested_on FROM redemptions WHERE requested_on <= ?"
        ") GROUP BY member_id", (d, d)).fetchall())
    rows = []
    for m in members:
        last_active = max(filter(None, [m["enrolled_on"], last.get(m["id"])]))
        rows.append({"id": m["id"], "display_name": m["display_name"], "tenure_days": tenure_days(m, as_of),
                     "points_balance": int(balances.get(m["id"], 0)), "lessons_completed": int(lessons.get(m["id"], 0)),
                     "last_active": to_date(last_active)})
    return rows


# --- Exports -----------------------------------------------------------------------------------
def export_employer(db: sqlite3.Connection | str | os.PathLike, employer_id: str, as_of: date | str) -> dict:
    """The employer dashboard JSON (contract section 1). `db` is a connection or a database path."""
    with using(db) as conn:
        return _export_employer(conn, employer_id, to_date(as_of))


def _export_employer(conn: sqlite3.Connection, employer_id: str, as_of: date) -> dict:
    emp = get_employer(conn, employer_id)
    totals = _ledger_totals(conn, employer_id, as_of)
    members = _member_rows(conn, employer_id, as_of)
    window_start = as_of - timedelta(days=ACTIVE_WINDOW_DAYS - 1)

    earned = {rule: pts for (kind, rule), pts in totals.items() if kind == "earn"}
    manual = totals.get(("adjust", MANUAL_RULE), 0)
    refunds = totals.get(("adjust", REFUND_RULE), 0)
    redeemed = -sum(pts for (kind, _), pts in totals.items() if kind == "redeem") - refunds
    issued = sum(earned.values()) + manual
    outstanding = sum(totals.values())

    earning_by_rule = [{"rule": r.name, "label": r.label, "points": earned.get(r.name, 0)} for r in PILOT_RULES.values()]
    if manual:
        earning_by_rule.append({"rule": MANUAL_RULE, "label": ADJUST_LABELS[MANUAL_RULE], "points": manual})

    red = _redemption_totals(conn, employer_id, as_of)
    data = {
        "as_of": as_of,
        "employer": {"id": emp["id"], "name": emp["name"], "plan": emp["plan"], "pepm_usd": float(emp["pepm_usd"]),
                     "points_per_usd": int(emp["points_per_usd"]), "pool_funded_usd": float(emp["pool_funded_usd"]),
                     "pool_remaining_usd": float(pool_remaining(conn, employer_id, as_of))},
        "summary": {
            "eligible": conn.execute("SELECT COUNT(*) FROM members WHERE employer_id = ? AND hire_date <= ?",
                                     (employer_id, as_of.isoformat())).fetchone()[0],
            "enrolled": len(members),
            "active_30d": sum(1 for m in members if m["last_active"] >= window_start),
            "points_issued": issued,
            "points_redeemed": redeemed,
            "points_outstanding": outstanding,
        },
        "retention": retention(conn, employer_id, as_of),
        "earning_by_rule": earning_by_rule,
        "redemptions": [{"type": t.type, "label": t.label, "count": red.get(t.type, (0, 0.0))[0],
                         "usd": float(red.get(t.type, (0, 0.0))[1])} for t in ENABLED_CATALOG],
        "members": members,
    }
    out = EmployerExport.model_validate(data).model_dump(mode="json")
    check_no_contact(out, "employer export")
    return out


def _next_milestones(conn: sqlite3.Connection, m: sqlite3.Row, as_of: date, days: int) -> list[dict]:
    """The next tenure milestone, then the lesson and habit rules the member can still earn."""
    if not is_employed(m, as_of):
        return []
    out = []
    upcoming = [r for r in TENURE_RULES if r.tenure_days > days]
    if upcoming:
        r = upcoming[0]
        out.append({"rule": r.name, "label": r.label, "points": r.points,
                    "progress_pct": round(100.0 * days / r.tenure_days, 1)})
    earned = dict(conn.execute(
        "SELECT rule, COUNT(*) FROM ledger WHERE member_id = ? AND kind = 'earn' AND date <= ? GROUP BY rule",
        (m["id"], as_of.isoformat())).fetchall())
    lessons = earned.get("lesson_completed", 0)
    if lessons < MAX_LESSONS:
        r = PILOT_RULES["lesson_completed"]
        out.append({"rule": r.name, "label": r.label, "points": r.points,
                    "progress_pct": round(100.0 * lessons / MAX_LESSONS, 1)})
    for name in ("checklist_completed", "savings_setup"):
        if not earned.get(name):
            r = PILOT_RULES[name]
            out.append({"rule": r.name, "label": r.label, "points": r.points, "progress_pct": 0.0})
    return out


def export_member(db: sqlite3.Connection | str | os.PathLike, member_id: str, as_of: date | str) -> dict:
    """The member view JSON (contract section 2). History is oldest first. `db` is a connection or a path."""
    with using(db) as conn:
        return _export_member(conn, member_id, to_date(as_of))


def _export_member(conn: sqlite3.Connection, member_id: str, as_of: date) -> dict:
    m = get_member(conn, member_id)
    if m["enrolled_on"] is None or to_date(m["enrolled_on"]) > as_of:
        raise NotEligibleError(f"{member_id} is not enrolled in the pilot on {as_of}")
    emp = get_employer(conn, m["employer_id"])
    days = tenure_days(m, as_of)
    rows = conn.execute("SELECT * FROM ledger WHERE member_id = ? AND date <= ? ORDER BY date, id",
                        (member_id, as_of.isoformat())).fetchall()
    data = {
        "as_of": as_of,
        "member": {"id": m["id"], "display_name": m["display_name"], "employer_name": emp["name"], "tenure_days": days},
        "points_balance": sum(int(r["points"]) for r in rows),
        "points_per_usd": int(emp["points_per_usd"]),
        "history": [{"date": to_date(r["date"]), "kind": r["kind"], "rule": r["rule"],
                     "label": ledger_label(r["kind"], r["rule"]), "points": int(r["points"])} for r in rows],
        "next_milestones": _next_milestones(conn, m, as_of, days),
        "catalog": [{"type": t.type, "label": t.label, "min_points": t.min_points, "note": t.note}
                    for t in ENABLED_CATALOG],
    }
    out = MemberExport.model_validate(data).model_dump(mode="json")
    check_no_contact(out, "member export")
    return out


def status(conn: sqlite3.Connection, as_of: date | str) -> list[dict]:
    """Plain counts per employer, for the CLI."""
    as_of = to_date(as_of)
    out = []
    for emp in conn.execute("SELECT * FROM employers ORDER BY id").fetchall():
        members = conn.execute("SELECT * FROM members WHERE employer_id = ?", (emp["id"],)).fetchall()
        red = dict(conn.execute(
            "SELECT r.status, COUNT(*) FROM redemptions r JOIN members m ON m.id = r.member_id"
            " WHERE m.employer_id = ? GROUP BY r.status", (emp["id"],)).fetchall())
        ledger_rows, outstanding = conn.execute(
            "SELECT COUNT(*), COALESCE(SUM(l.points), 0) FROM ledger l JOIN members m ON m.id = l.member_id"
            " WHERE m.employer_id = ?", (emp["id"],)).fetchone()
        out.append({
            "id": emp["id"], "name": emp["name"], "plan": emp["plan"],
            "eligible": len(members),
            "enrolled": sum(1 for m in members if m["enrolled_on"]),
            "employed_now": sum(1 for m in members if is_employed(m, as_of)),
            "enrolled_employed_now": sum(1 for m in members if m["enrolled_on"] and is_employed(m, as_of)),
            "ledger_rows": ledger_rows, "points_outstanding": int(outstanding),
            "redemptions": {s: red.get(s, 0) for s in ("requested", "fulfilled", "cancelled")},
            "pool_funded_usd": float(emp["pool_funded_usd"]),
            "pool_remaining_usd": pool_remaining(conn, emp["id"]),
        })
    return out

