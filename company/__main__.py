"""Command line for the AI company.

  python -m company run-daily [--dry-run] [--max-tasks N]
  python -m company status
  python -m company show <id>
  python -m company approve <id> [<id> ...]
  python -m company reject <id> [--reason TEXT]
  python -m company build-site
"""
from __future__ import annotations

import argparse
import json
import sys

from . import config, runner, site
from .llm import ClaudeLLM, FakeLLM
from .state import AWAITING, State


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m company")
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("run-daily", help="CEO plans, agents work, brief is written")
    d.add_argument("--dry-run", action="store_true", help="No API calls; canned answers")
    d.add_argument("--max-tasks", type=int, default=config.MAX_TASKS_PER_DAY)
    sub.add_parser("status")
    s = sub.add_parser("show"); s.add_argument("id", type=int)
    a = sub.add_parser("approve"); a.add_argument("ids", type=int, nargs="+")
    r = sub.add_parser("reject"); r.add_argument("id", type=int); r.add_argument("--reason", default="")
    sub.add_parser("build-site")
    args = p.parse_args(argv)

    if args.cmd == "run-daily":
        llm = FakeLLM() if args.dry_run else ClaudeLLM()
        print(f"Brief written: {runner.run_daily(llm, max_tasks=args.max_tasks)}")
    elif args.cmd == "status":
        state = State()
        counts: dict[str, int] = {}
        for t in state.data["tasks"]:
            counts[t["status"]] = counts.get(t["status"], 0) + 1
        print("Tasks by status:", counts or "none yet")
        for t in state.by_status(AWAITING):
            print(f"  awaiting approval: #{t['id']} ({t['agent']}) {t['title']}")
    elif args.cmd == "show":
        print(json.dumps(State().get(args.id), indent=2))
    elif args.cmd == "approve":
        failed = False
        for i in args.ids:
            try:
                print(runner.approve(i))
            except (KeyError, ValueError) as exc:
                print(f"#{i}: {exc}", file=sys.stderr); failed = True
        return 1 if failed else 0
    elif args.cmd == "reject":
        print(runner.reject(args.id, args.reason))
    elif args.cmd == "build-site":
        site.build_site(); print("Site data rebuilt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
