"""Employers, members, earning, redemptions and balances.

Every change to points is a new ledger row with a unique idempotency key, so repeating a call
(a retried request, a batch job run twice) never grants or spends points twice.
"""
from __future__ import annotations

import re
import sqlite3
from datetime import date, timedelta

from .db import opt_date, to_date, transaction
from .errors import (BelowMinimumError, InsufficientPointsError, NotEligibleError, NotFoundError,
                     PoolExhaustedError, RedemptionError, RewardsError)
from .rules import (DEFAULT_SCHEDULE, MANUAL_RULE, PILOT_RULES, REFUND_RULE, TENURE_RULES, check_no_contact,
                    check_rule_allowed, check_schedule, pilot_rule, redemption_type, schedule_points)

DEFAULT_PILOT_START = date(2026, 6, 1)

_ID = re.compile(r"^[A-Za-z0-9_]{1,40}$")
_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")


def _check_id(value: str, what: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise ValueError(f"{what} must be 1-40 letters, digits or underscores, got {value!r}")
    return value


# --- Employers and members ---------------------------------------------------------------------
def create_employer(conn: sqlite3.Connection, employer_id: str, name: str, *, plan: str = "pilot",
                    pepm_usd: float, points_per_usd: int, pool_funded_usd: float,
                    pilot_start: date | str = DEFAULT_PILOT_START, reward_schedule: str = DEFAULT_SCHEDULE) -> None:
    _check_id(employer_id, "employer id")
    check_schedule(reward_schedule)
    if not name or not name.strip():
        raise ValueError("employer name is required")
    if isinstance(points_per_usd, bool) or not isinstance(points_per_usd, int) or points_per_usd <= 0:
        raise ValueError("points_per_usd must be a positive whole number")
    if pepm_usd < 0 or pool_funded_usd < 0:
        raise ValueError("pepm_usd and pool_funded_usd cannot be negative")
    check_no_contact(name, "employer name")
    with transaction(conn):
        conn.execute(
            "INSERT INTO employers (id, name, plan, pepm_usd, points_per_usd, pool_funded_usd, pilot_start,"
            " reward_schedule) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (employer_id, name, plan, float(pepm_usd), points_per_usd, float(pool_funded_usd),
             to_date(pilot_start).isoformat(), reward_schedule))


def set_reward_schedule(conn: sqlite3.Connection, employer_id: str, reward_schedule: str) -> None:
    """Switch an employer's points table. Only points earned from now on change; past rows never do."""
    check_schedule(reward_schedule)
    with transaction(conn):
        get_employer(conn, employer_id)
        conn.execute("UPDATE employers SET reward_schedule = ? WHERE id = ?", (reward_schedule, employer_id))


def rule_points(conn: sqlite3.Connection, employer_id: str, rule_name: str) -> int:
    """Points a rule pays at this employer, under its current reward schedule."""
    return schedule_points(get_employer(conn, employer_id)["reward_schedule"], rule_name)


def get_employer(conn: sqlite3.Connection, employer_id: str) -> sqlite3.Row:
    row = conn.execute("SELECT * FROM employers WHERE id = ?", (employer_id,)).fetchone()
    if row is None:
        raise NotFoundError(f"no employer {employer_id!r}")
    return row


def add_member(conn: sqlite3.Connection, member_id: str, employer_id: str, display_name: str,
               hire_date: date | str, *, enrolled_on: date | str | None = None,
               left_on: date | str | None = None) -> None:
    """Add someone on the employer's eligible roster. enrolled_on=None means eligible but not enrolled."""
    _check_id(member_id, "member id")
    if not display_name or not display_name.strip() or len(display_name) > 40:
        raise ValueError("display_name must be 1-40 characters")
    check_no_contact(display_name, "display_name")
    hire = to_date(hire_date)
    enrolled = to_date(enrolled_on) if enrolled_on is not None else None
    left = to_date(left_on) if left_on is not None else None
    if enrolled and enrolled < hire:
        raise ValueError("enrolled_on cannot be before hire_date")
    if left and left <= hire:
        raise ValueError("left_on must be after hire_date")
    if left and enrolled and enrolled >= left:
        raise ValueError("enrolled_on must be before left_on")
    with transaction(conn):
        get_employer(conn, employer_id)
        conn.execute(
            "INSERT INTO members (id, employer_id, display_name, hire_date, enrolled_on, left_on)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (member_id, employer_id, display_name, hire.isoformat(),
             enrolled.isoformat() if enrolled else None, left.isoformat() if left else None))


def get_member(conn: sqlite3.Connection, member_id: str) -> sqlite3.Row:
    row = conn.execute("SELECT * FROM members WHERE id = ?", (member_id,)).fetchone()
    if row is None:
        raise NotFoundError(f"no member {member_id!r}")
    return row


def enroll(conn: sqlite3.Connection, member_id: str, on: date | str) -> None:
    on = to_date(on)
    with transaction(conn):
        m = get_member(conn, member_id)
        if m["enrolled_on"]:
            raise RewardsError(f"{member_id} is already enrolled (since {m['enrolled_on']})")
        if on < to_date(m["hire_date"]) or (m["left_on"] and on >= to_date(m["left_on"])):
            raise NotEligibleError(f"{member_id} is not employed on {on}")
        conn.execute("UPDATE members SET enrolled_on = ? WHERE id = ?", (on.isoformat(), member_id))


def record_departure(conn: sqlite3.Connection, member_id: str, on: date | str) -> None:
    """The member's employment ended. `on` is the first day they are no longer employed."""
    on = to_date(on)
    with transaction(conn):
        m = get_member(conn, member_id)
        if m["left_on"]:
            raise RewardsError(f"{member_id} already left on {m['left_on']}")
        if on <= to_date(m["hire_date"]):
            raise ValueError("left_on must be after hire_date")
        conn.execute("UPDATE members SET left_on = ? WHERE id = ?", (on.isoformat(), member_id))


def is_employed(m: sqlite3.Row, on: date) -> bool:
    """Employed on a day: hired on or before it, and not yet left (left_on is the first day gone)."""
    return to_date(m["hire_date"]) <= on and (m["left_on"] is None or on < to_date(m["left_on"]))


def _require_enrolled(conn: sqlite3.Connection, member_id: str, on: date) -> sqlite3.Row:
    m = get_member(conn, member_id)
    if m["enrolled_on"] is None or on < to_date(m["enrolled_on"]):
        raise NotEligibleError(f"{member_id} is not enrolled in the pilot on {on}")
    if not is_employed(m, on):
        raise NotEligibleError(f"{member_id} is not employed on {on}")
    return m


# --- Ledger ------------------------------------------------------------------------------------
def _append(conn: sqlite3.Connection, member_id: str, on: date, kind: str, rule: str, points: int,
            key: str) -> bool:
    """Add one ledger row. Returns False (and changes nothing) if the key was already used."""
    if kind == "earn":
        pilot_rule(rule)                   # forbidden or unknown rules never reach the ledger
    else:
        check_rule_allowed(rule)
    cur = conn.execute(
        "INSERT INTO ledger (member_id, date, kind, rule, points, idempotency_key) VALUES (?, ?, ?, ?, ?, ?)"
        " ON CONFLICT(idempotency_key) DO NOTHING",
        (member_id, on.isoformat(), kind, rule, int(points), key))
    return cur.rowcount == 1


def balance(conn: sqlite3.Connection, member_id: str, as_of: date | str | None = None) -> int:
    if as_of is None:
        row = conn.execute("SELECT COALESCE(SUM(points), 0) FROM ledger WHERE member_id = ?", (member_id,)).fetchone()
    else:
        row = conn.execute("SELECT COALESCE(SUM(points), 0) FROM ledger WHERE member_id = ? AND date <= ?",
                           (member_id, to_date(as_of).isoformat())).fetchone()
    return int(row[0])


def ledger(conn: sqlite3.Connection, member_id: str) -> list[dict]:
    rows = conn.execute("SELECT * FROM ledger WHERE member_id = ? ORDER BY date, id", (member_id,)).fetchall()
    return [dict(r) for r in rows]


# --- Earning -----------------------------------------------------------------------------------
def award_tenure(conn: sqlite3.Connection, as_of: date | str, employer_id: str | None = None) -> list[dict]:
    """Grant every enrolled, still-employed member each tenure milestone they have reached.

    A milestone counts only if it was reached on or after the member's enrolled_on date: points
    reward staying from the day you join, not time served before. The ledger row is dated the day
    the milestone was reached. Safe to run as often as you like; a second run grants nothing new.
    """
    as_of = to_date(as_of)
    sql = ("SELECT m.*, e.reward_schedule FROM members m JOIN employers e ON e.id = m.employer_id"
           " WHERE m.enrolled_on IS NOT NULL AND m.enrolled_on <= ? AND (m.left_on IS NULL OR m.left_on > ?)")
    params: list = [as_of.isoformat(), as_of.isoformat()]
    if employer_id is not None:
        sql += " AND m.employer_id = ?"
        params.append(employer_id)
    granted: list[dict] = []
    with transaction(conn):
        done = {(r["member_id"], r["rule"]) for r in conn.execute(
            "SELECT member_id, rule FROM ledger WHERE kind = 'earn' AND rule LIKE 'tenure\\_%' ESCAPE '\\'")}
        for m in conn.execute(sql, params).fetchall():
            hire, enrolled = to_date(m["hire_date"]), to_date(m["enrolled_on"])
            for rule in TENURE_RULES:
                reached = hire + timedelta(days=rule.tenure_days)
                if reached > as_of:
                    break
                if reached < enrolled or (m["id"], rule.name) in done:
                    continue
                points = schedule_points(m["reward_schedule"], rule.name)
                if _append(conn, m["id"], reached, "earn", rule.name, points, f"tenure:{m['id']}:{rule.name}"):
                    granted.append({"member_id": m["id"], "rule": rule.name, "date": reached.isoformat(),
                                    "points": points})
    return granted


def record_lesson(conn: sqlite3.Connection, member_id: str, lesson_slug: str, on: date | str) -> int:
    """Points per distinct lesson (50 on the standard schedule), up to 10 lessons. Returns the points granted."""
    on = to_date(on)
    if not isinstance(lesson_slug, str) or not _SLUG.fullmatch(lesson_slug):
        raise ValueError(f"lesson slug must be lowercase letters, digits and hyphens, got {lesson_slug!r}")
    rule = PILOT_RULES["lesson_completed"]
    with transaction(conn):
        m = _require_enrolled(conn, member_id, on)
        conn.execute("INSERT INTO completions (member_id, kind, ref, date) VALUES (?, 'lesson', ?, ?)"
                     " ON CONFLICT DO NOTHING", (member_id, lesson_slug, on.isoformat()))
        paid = conn.execute("SELECT COUNT(*) FROM ledger WHERE member_id = ? AND kind = 'earn' AND rule = ?",
                            (member_id, rule.name)).fetchone()[0]
        if paid >= rule.max_awards:
            return 0
        points = rule_points(conn, m["employer_id"], rule.name)
        ok = _append(conn, member_id, on, "earn", rule.name, points, f"lesson:{member_id}:{lesson_slug}")
        return points if ok else 0


def _record_once(conn: sqlite3.Connection, member_id: str, on: date | str, rule_name: str, completion: str) -> int:
    on = to_date(on)
    rule = PILOT_RULES[rule_name]
    with transaction(conn):
        m = _require_enrolled(conn, member_id, on)
        conn.execute("INSERT INTO completions (member_id, kind, ref, date) VALUES (?, ?, 'once', ?)"
                     " ON CONFLICT DO NOTHING", (member_id, completion, on.isoformat()))
        points = rule_points(conn, m["employer_id"], rule.name)
        ok = _append(conn, member_id, on, "earn", rule.name, points, f"{rule.name}:{member_id}")
        return points if ok else 0


def record_checklist(conn: sqlite3.Connection, member_id: str, on: date | str) -> int:
    """Points once (200 on the standard schedule) for finishing the "before you invest" checklist."""
    return _record_once(conn, member_id, on, "checklist_completed", "checklist")


def record_savings_setup(conn: sqlite3.Connection, member_id: str, on: date | str) -> int:
    """Points once (300 on the standard schedule) for setting up direct deposit to savings."""
    return _record_once(conn, member_id, on, "savings_setup", "savings_setup")


def award(conn: sqlite3.Connection, member_id: str, rule: str, on: date | str, ref: str | None = None) -> int:
    """Award a pilot rule by name. Rules tied to trading or balances raise ForbiddenRuleError."""
    r = pilot_rule(rule)
    if r.tenure_days:
        raise RewardsError("tenure milestones are granted by award_tenure(), not one by one")
    if r.name == "lesson_completed":
        if not ref:
            raise ValueError("lesson_completed needs the lesson slug as ref")
        return record_lesson(conn, member_id, ref, on)
    if r.name == "checklist_completed":
        return record_checklist(conn, member_id, on)
    return record_savings_setup(conn, member_id, on)


def adjust(conn: sqlite3.Connection, member_id: str, points: int, on: date | str, key: str) -> bool:
    """A manual correction, as a new ledger row. `key` makes it safe to retry. Balances never go below 0."""
    on = to_date(on)
    if isinstance(points, bool) or not isinstance(points, int) or points == 0:
        raise ValueError("points must be a non-zero whole number")
    with transaction(conn):
        get_member(conn, member_id)
        if points < 0 and balance(conn, member_id) + points < 0:
            raise InsufficientPointsError(f"correction would take {member_id} below zero points")
        return _append(conn, member_id, on, "adjust", MANUAL_RULE, points, f"adjust:{member_id}:{key}")


# --- Redemptions -------------------------------------------------------------------------------
def _redemption_usd(points: int, points_per_usd: int) -> float:
    return round(points / points_per_usd, 2)


def pool_remaining(conn: sqlite3.Connection, employer_id: str, as_of: date | str | None = None) -> float:
    """Funded pool minus the USD of redemptions that are not cancelled (as of a date, if given)."""
    emp = get_employer(conn, employer_id)
    if as_of is None:
        used = conn.execute(
            "SELECT COALESCE(SUM(r.usd), 0) FROM redemptions r JOIN members m ON m.id = r.member_id"
            " WHERE m.employer_id = ? AND r.status != 'cancelled'", (employer_id,)).fetchone()[0]
    else:
        d = to_date(as_of).isoformat()
        used = conn.execute(
            "SELECT COALESCE(SUM(r.usd), 0) FROM redemptions r JOIN members m ON m.id = r.member_id"
            " WHERE m.employer_id = ? AND r.requested_on <= ?"
            " AND NOT (r.status = 'cancelled' AND r.cancelled_on <= ?)", (employer_id, d, d)).fetchone()[0]
    return round(emp["pool_funded_usd"] - used, 2)


def get_redemption(conn: sqlite3.Connection, redemption_id: str) -> dict:
    row = conn.execute("SELECT * FROM redemptions WHERE id = ?", (redemption_id,)).fetchone()
    if row is None:
        raise NotFoundError(f"no redemption {redemption_id!r}")
    return dict(row)


def request_redemption(conn: sqlite3.Connection, member_id: str, type_: str, points: int, on: date | str, *,
                       redemption_id: str | None = None) -> dict:
    """Spend points on a payroll bonus or gift card. The points leave the balance straight away.

    Refused if the type is disabled (invest_deposit), below the minimum, more than the member's
    balance, or worth more than the employer's remaining pool. Pass `redemption_id` to make a
    retried request safe: the same id returns the original redemption instead of a second one.
    """
    on = to_date(on)
    rtype = redemption_type(type_)
    if isinstance(points, bool) or not isinstance(points, int):
        raise ValueError("points must be a whole number")
    if redemption_id is not None:
        _check_id(redemption_id, "redemption id")
        existing = conn.execute("SELECT * FROM redemptions WHERE id = ?", (redemption_id,)).fetchone()
        if existing is not None:
            if (existing["member_id"], existing["type"], existing["points"]) != (member_id, rtype.type, points):
                raise RedemptionError(f"redemption id {redemption_id!r} is already used for a different request")
            return dict(existing)
    if points < rtype.min_points:
        raise BelowMinimumError(f"{rtype.label} needs at least {rtype.min_points} points (asked for {points})")
    with transaction(conn):
        m = _require_enrolled(conn, member_id, on)
        available = min(balance(conn, member_id), balance(conn, member_id, on))
        if points > available:
            raise InsufficientPointsError(f"{member_id} has {available} points, asked to redeem {points}")
        emp = get_employer(conn, m["employer_id"])
        usd = _redemption_usd(points, emp["points_per_usd"])
        remaining = pool_remaining(conn, emp["id"])
        if usd > remaining + 1e-9:
            raise PoolExhaustedError(f"${usd:.2f} is more than the ${remaining:.2f} left in {emp['name']}'s reward pool")
        if redemption_id is None:
            n = conn.execute("SELECT COUNT(*) FROM redemptions").fetchone()[0] + 1
            redemption_id = f"r_{n:06d}"
        conn.execute(
            "INSERT INTO redemptions (id, member_id, type, points, usd, status, requested_on)"
            " VALUES (?, ?, ?, ?, ?, 'requested', ?)",
            (redemption_id, member_id, rtype.type, points, usd, on.isoformat()))
        _append(conn, member_id, on, "redeem", rtype.type, -points, f"redeem:{redemption_id}")
    return get_redemption(conn, redemption_id)


def fulfill_redemption(conn: sqlite3.Connection, redemption_id: str, on: date | str) -> dict:
    """The employer paid the bonus or sent the gift card."""
    on = to_date(on)
    with transaction(conn):
        r = get_redemption(conn, redemption_id)
        if r["status"] != "requested":
            raise RedemptionError(f"redemption {redemption_id} is {r['status']}, not requested")
        if on < to_date(r["requested_on"]):
            raise ValueError("fulfilled date cannot be before the request date")
        conn.execute("UPDATE redemptions SET status = 'fulfilled', fulfilled_on = ? WHERE id = ?",
                     (on.isoformat(), redemption_id))
    return get_redemption(conn, redemption_id)


def cancel_redemption(conn: sqlite3.Connection, redemption_id: str, on: date | str) -> dict:
    """Cancel a requested redemption. The points come back as a new ledger row (kind "adjust")."""
    on = to_date(on)
    with transaction(conn):
        r = get_redemption(conn, redemption_id)
        if r["status"] != "requested":
            raise RedemptionError(f"redemption {redemption_id} is {r['status']}; only requested ones can be cancelled")
        if on < to_date(r["requested_on"]):
            raise ValueError("cancel date cannot be before the request date")
        conn.execute("UPDATE redemptions SET status = 'cancelled', cancelled_on = ? WHERE id = ?",
                     (on.isoformat(), redemption_id))
        _append(conn, r["member_id"], on, "adjust", REFUND_RULE, r["points"], f"cancel:{redemption_id}")
    return get_redemption(conn, redemption_id)


def tenure_days(m: sqlite3.Row, as_of: date) -> int:
    """Days on the job as of a date (frozen at the leaving date for people who left)."""
    end = as_of
    left = opt_date(m["left_on"])
    if left and left < end:
        end = left
    return max(0, (end - to_date(m["hire_date"])).days)
