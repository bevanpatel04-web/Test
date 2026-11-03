"""Command line: python -m kdp list | build <id>... | build --all [--out DIR]"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from .build import build
from .catalog import BOOKS, get
from . import specs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m kdp", description="Amazon KDP puzzle-book factory")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="show every book in the catalog")
    b = sub.add_parser("build", help="build interior, cover and listing")
    b.add_argument("ids", nargs="*")
    b.add_argument("--all", action="store_true")
    b.add_argument("--out", default="kdp/out")
    args = ap.parse_args(argv)

    if args.cmd == "list":
        for bk in BOOKS:
            print(f"{bk.id:28} {bk.trim.label:12} ${bk.price:<6.2f} {bk.title}")
        return 0

    books = BOOKS if args.all else [get(i) for i in args.ids]
    if not books:
        ap.error("give book ids or --all")
    out = Path(args.out)
    for bk in books:
        t = time.time()
        info = build(bk, out)
        print(f"{bk.id}: {info['pages']} pages, {info['puzzles']} puzzles, "
              f"royalty ${info['royalty']:.2f}/sale at ${bk.price:.2f}  ({time.time() - t:.0f}s) -> {out / bk.id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
