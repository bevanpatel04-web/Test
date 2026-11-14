"""Command line for the rewards pilot.

  python -m rewards seed-demo [--db PATH] [--seed 42] [--schedule boosted|standard]
  python -m rewards set-schedule --employer ID --schedule boosted|standard [--db PATH]
  python -m rewards award --as-of DATE [--employer ID] [--db PATH]
  python -m rewards status [--as-of DATE] [--db PATH]
  python -m rewards export --employer emp_demo --member m_001 --as-of 2026-11-14 --out DIR [--db PATH]

The database is --db, else $REWARDS_DB, else rewards/data/pilot.db.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from .db import connect, get_meta, resolve_db_path, to_date
from .engine import award_tenure, set_reward_schedule
from .errors import RewardsError
from .reports import export_employer, export_member, status
from .rules import RECOMMENDED_SCHEDULE, SCHEDULES, max_first_year_points
from .seed import SIMULATED_NOTICE, seed_demo


def _iso(text: str) -> date:
    try:
        return to_date(text)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e)) from None


def _warn_if_simulated(conn) -> None:
    if get_meta(conn, "simulated") == "true":
        print(f"NOTE: {SIMULATED_NOTICE}")


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--db", default=argparse.SUPPRESS, help="SQLite file (default: $REWARDS_DB or rewards/data/pilot.db)")
    p = argparse.ArgumentParser(prog="python -m rewards", description="Employer rewards pilot backend.")
    p.add_argument("--db", default=None, help=argparse.SUPPRESS)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("seed-demo", parents=[common], help="Fill a new database with SIMULATED demo data")
    s.add_argument("--seed", type=int, default=42)
    s.add_argument("--schedule", choices=sorted(SCHEDULES), default=RECOMMENDED_SCHEDULE,
                   help=f"Reward schedule for the demo employer (default: {RECOMMENDED_SCHEDULE})")
    sc = sub.add_parser("set-schedule", parents=[common], help="Change an employer's reward schedule (future points only)")
    sc.add_argument("--employer", required=True)
    sc.add_argument("--schedule", choices=sorted(SCHEDULES), required=True)
    a = sub.add_parser("award", parents=[common], help="Grant tenure milestones reached by a date")
    a.add_argument("--as-of", type=_iso, required=True)
    a.add_argument("--employer", default=None, help="Only this employer (default: all)")
    st = sub.add_parser("status", parents=[common], help="Counts and pool remaining")
    st.add_argument("--as-of", type=_iso, default=date.today())
    e = sub.add_parser("export", parents=[common], help="Write employer.json and member.json for the dashboard")
    e.add_argument("--employer", required=True)
    e.add_argument("--member", required=True)
    e.add_argument("--as-of", type=_iso, default=date.today())
    e.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)

    db_path = resolve_db_path(args.db)
    try:
        if args.cmd == "seed-demo":
            info = seed_demo(db_path, seed=args.seed, schedule=args.schedule)
            print(f"Seeded {db_path} (reward schedule: {info['schedule']})")
            print(f"  {info['eligible']} eligible, {info['enrolled']} enrolled, {info['left']} left by {info['as_of']}"
                  f" (seed {info['seed']})")
            print(f"NOTE: {SIMULATED_NOTICE}")
            return 0

        conn = connect(db_path)
        try:
            if args.cmd == "set-schedule":
                set_reward_schedule(conn, args.employer, args.schedule)
                print(f"{args.employer} now uses the {args.schedule} schedule: at most "
                      f"{max_first_year_points(args.schedule):,} points in a first year. Points already earned don't change.")
            elif args.cmd == "award":
                granted = award_tenure(conn, args.as_of, args.employer)
                print(f"Granted {len(granted)} tenure milestone(s) as of {args.as_of.isoformat()}, "
                      f"{sum(g['points'] for g in granted)} points.")
                _warn_if_simulated(conn)
            elif args.cmd == "status":
                rows = status(conn, args.as_of)
                print(f"Database: {db_path}")
                _warn_if_simulated(conn)
                if not rows:
                    print("No employers yet. Try: python -m rewards seed-demo --db PATH")
                for r in rows:
                    red = r["redemptions"]
                    print(f"{r['id']}  {r['name']}  (plan {r['plan']}, {r['reward_schedule']} schedule)")
                    print(f"  roster: {r['eligible']} eligible, {r['enrolled']} enrolled; employed on "
                          f"{args.as_of.isoformat()}: {r['employed_now']} ({r['enrolled_employed_now']} enrolled)")
                    print(f"  ledger: {r['ledger_rows']} rows, {r['points_outstanding']} points outstanding")
                    print(f"  redemptions: {red['requested']} requested, {red['fulfilled']} fulfilled, "
                          f"{red['cancelled']} cancelled")
                    print(f"  pool: ${r['pool_funded_usd']:,.2f} funded, ${r['pool_remaining_usd']:,.2f} remaining")
            elif args.cmd == "export":
                employer = export_employer(conn, args.employer, args.as_of)
                member = export_member(conn, args.member, args.as_of)
                args.out.mkdir(parents=True, exist_ok=True)
                _write_json(args.out / "employer.json", employer)
                _write_json(args.out / "member.json", member)
                print(f"Wrote {args.out / 'employer.json'} and {args.out / 'member.json'} (as of {args.as_of.isoformat()})")
                _warn_if_simulated(conn)
        finally:
            conn.close()
    except RewardsError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
