"""SIMULATED demo data for the dashboard. These are not real pilot results.

Builds "Demo Diner Group": 400 eligible employees hired over the 18 months before the pilot
start (2026-06-01), 240 enrolled on day one, daily quits at a hospitality-like rate, lessons,
checklists, savings setups and redemptions, through 2026-11-14. The same seed always gives the
same database.

The quit rates below are ASSUMPTIONS typed into the simulation. Enrolled members are set to quit
somewhat less, so the retention gap in the demo is put there on purpose: it shows what the chart
looks like, not that rewards work.
"""
from __future__ import annotations

import os
import random
import sqlite3
from collections import defaultdict
from datetime import date, timedelta

from . import engine
from .db import set_meta, to_date, transaction, using
from .errors import PoolExhaustedError, RewardsError
from .rules import RECOMMENDED_SCHEDULE, check_schedule

SIMULATED_NOTICE = "SIMULATED demo data (made up by rewards.seed_demo). Not real pilot results."

PILOT_START = date(2026, 6, 1)
DEMO_AS_OF = date(2026, 11, 14)
DEMO_EMPLOYER = {"employer_id": "emp_demo", "name": "Demo Diner Group", "plan": "pilot",
                 "pepm_usd": 4.0, "points_per_usd": 100}
# The demo runs the recommended (boosted) schedule by default, so the sales demo shows what we
# would actually sell. Bigger rewards need a bigger pool and bigger redemptions.
DEMO_POOL_USD = {"standard": 5000.0, "boosted": 15000.0}
REDEEM_UNIT_POINTS = {"standard": 500, "boosted": 1500}
N_ELIGIBLE = 400
N_ENROLLED = 240
HIRE_WINDOW_DAYS = 548                 # about 18 months before the pilot start

# Assumed monthly quit rates, in the 4-5% range the team brief gives for food service (the brief
# cites 5.0% for accommodation and food services, September 2026, BLS JOLTS, https://www.bls.gov/jlt/;
# not re-checked here, so unverified). People in their first 90 days are assumed to quit more.
MONTHLY_QUIT_NOT_ENROLLED = 0.045
MONTHLY_QUIT_ENROLLED = 0.035
NEW_HIRE_QUIT_FACTOR = 1.4

# Real lesson slugs from invest/data/lessons.json (11 lessons, so a keen member can hit the 10 cap).
LESSON_SLUGS = ["compound-growth", "what-risk-means", "debt-vs-investing", "cash-cushion-first", "401k-match",
                "roth-ira-basics", "index-funds-vs-stocks", "fees-add-up", "market-crashes", "timing-the-market",
                "spot-the-hype"]


def _daily(monthly: float) -> float:
    return 1 - (1 - monthly) ** (1 / 30.44)


def _rand_day(rng: random.Random, first: date, last: date) -> date:
    return first + timedelta(days=rng.randint(0, (last - first).days))


def _roster(rng: random.Random, as_of: date) -> list[dict]:
    people = []
    for _ in range(N_ELIGIBLE):
        # Skewed toward recent hires: in a high-churn job, most of today's staff started recently.
        days_before = 1 + int((HIRE_WINDOW_DAYS - 1) * rng.random() ** 1.3)
        people.append({"hire": PILOT_START - timedelta(days=days_before), "enrolled": False, "left": None})
    for i in rng.sample(range(N_ELIGIBLE), N_ENROLLED):
        people[i]["enrolled"] = True
    for p in people:
        base = MONTHLY_QUIT_ENROLLED if p["enrolled"] else MONTHLY_QUIT_NOT_ENROLLED
        day = PILOT_START + timedelta(days=1)
        while day <= as_of:
            factor = NEW_HIRE_QUIT_FACTOR if (day - p["hire"]).days < 90 else 1.0
            if rng.random() < _daily(base * factor):
                p["left"] = day
                break
            day += timedelta(days=1)
    # Member 001 is the example in the member view: enrolled, still working, and part-way to a
    # year on the job. Pick the first such person and give them id m_001.
    showcase = next((i for i, p in enumerate(people) if p["enrolled"] and p["left"] is None
                     and 200 <= (as_of - p["hire"]).days <= 330), None)
    if showcase is None:
        showcase = next(i for i, p in enumerate(people) if p["enrolled"] and p["left"] is None)
    people.insert(0, people.pop(showcase))
    for n, p in enumerate(people, start=1):
        p["id"], p["name"] = f"m_{n:03d}", f"Member {n:03d}"
    return people


def _plan_events(rng: random.Random, people: list[dict], as_of: date) -> dict[date, list[tuple]]:
    events: dict[date, list[tuple]] = defaultdict(list)
    for p in people:
        if not p["enrolled"]:
            continue
        last = (p["left"] - timedelta(days=1)) if p["left"] else as_of
        if last < PILOT_START:
            continue
        engagement = rng.random()
        if p["id"] == "m_001":
            engagement = max(engagement, 0.6)
        n_lessons = sum(rng.random() < engagement for _ in LESSON_SLUGS)
        for slug in rng.sample(LESSON_SLUGS, n_lessons):
            events[_rand_day(rng, PILOT_START, last)].append(("lesson", p["id"], slug))
        if rng.random() < 0.2 + 0.6 * engagement:
            events[_rand_day(rng, PILOT_START, last)].append(("checklist", p["id"]))
        if rng.random() < 0.1 + 0.4 * engagement:
            events[_rand_day(rng, PILOT_START, last)].append(("savings", p["id"]))
        attempts = (1 + (rng.random() < engagement / 2)) if rng.random() < 0.3 + 0.6 * engagement else 0
        for _ in range(attempts):
            events[_rand_day(rng, PILOT_START, last)].append(("redeem", p["id"], last))
        if p["id"] == "m_001":
            due = p["hire"] + timedelta(days=180 + rng.randint(3, 15))
            if PILOT_START <= due <= last:
                events[due].append(("redeem", p["id"], last))
    return events


def seed_demo(db: sqlite3.Connection | str | os.PathLike | None = None, seed: int = 42,
              as_of: date | str = DEMO_AS_OF, schedule: str = RECOMMENDED_SCHEDULE) -> dict:
    """Fill an EMPTY database with simulated demo data. Refuses a database that already has data."""
    as_of = to_date(as_of)
    check_schedule(schedule)
    rng = random.Random(seed)
    people = _roster(rng, as_of)
    events = _plan_events(rng, people, as_of)
    with using(db) as conn:
        if conn.execute("SELECT COUNT(*) FROM employers").fetchone()[0]:
            raise RewardsError("this database already has data; seed the demo into a new, empty file")
        with transaction(conn):
            engine.create_employer(conn, pilot_start=PILOT_START, reward_schedule=schedule,
                                   pool_funded_usd=DEMO_POOL_USD.get(schedule, 5000.0), **DEMO_EMPLOYER)
            for p in people:
                engine.add_member(conn, p["id"], "emp_demo", p["name"], p["hire"],
                                  enrolled_on=PILOT_START if p["enrolled"] else None, left_on=p["left"])
            day = PILOT_START
            while day <= as_of:
                engine.award_tenure(conn, day, "emp_demo")    # the nightly job
                for ev in sorted(events.pop(day, []), key=lambda e: _ORDER[e[0]]):   # earn, then spend
                    _apply(conn, rng, events, day, as_of, ev, REDEEM_UNIT_POINTS.get(schedule, 500))
                day += timedelta(days=1)
            set_meta(conn, "simulated", "true")
            set_meta(conn, "seed", str(seed))
            set_meta(conn, "schedule", schedule)
            set_meta(conn, "as_of", as_of.isoformat())
            set_meta(conn, "notice", SIMULATED_NOTICE)
        return {"employer_id": "emp_demo", "eligible": len(people), "enrolled": sum(p["enrolled"] for p in people),
                "left": sum(1 for p in people if p["left"]), "seed": seed, "as_of": as_of.isoformat(),
                "schedule": schedule}


_ORDER = {"lesson": 0, "checklist": 1, "savings": 2, "redeem": 3, "fulfill": 4, "cancel": 5}
RETRY_DAYS = 14


def _apply(conn: sqlite3.Connection, rng: random.Random, events: dict, day: date, as_of: date, ev: tuple,
           unit: int = 500) -> None:
    kind, ref = ev[0], ev[1]
    if kind == "lesson":
        engine.record_lesson(conn, ref, ev[2], day)
    elif kind == "checklist":
        engine.record_checklist(conn, ref, day)
    elif kind == "savings":
        engine.record_savings_setup(conn, ref, day)
    elif kind == "redeem":
        member_id, last = ref, ev[2]
        bal = engine.balance(conn, member_id)
        if bal < unit:                       # not enough yet: the member tries again in two weeks
            retry = day + timedelta(days=RETRY_DAYS)
            if retry <= last:
                events[retry].append(ev)
            return
        points = 2 * unit if bal >= 2 * unit and rng.random() < 0.35 else unit
        type_ = "payroll_bonus" if rng.random() < 0.65 else "gift_card"
        try:
            r = engine.request_redemption(conn, member_id, type_, points, day)
        except PoolExhaustedError:
            return
        if rng.random() < 0.06:
            when, follow = day + timedelta(days=rng.randint(1, 3)), "cancel"
        else:
            when, follow = day + timedelta(days=rng.randint(2, 7)), "fulfill"
        if when <= as_of:                    # later ones are still "requested" on the as-of date
            events[when].append((follow, r["id"]))
    elif kind == "fulfill":
        engine.fulfill_redemption(conn, ref, day)
    elif kind == "cancel":
        engine.cancel_redemption(conn, ref, day)
