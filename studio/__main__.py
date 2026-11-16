"""python -m studio <command>

  script <slug> [--dry-run] [--force]     write studio/scripts/<slug>.json with Claude (FakeLLM with --dry-run)
  render <slug> [--vertical] [--voice V]  render the MP4, captions, poster and manifest entry
  render-level <n> [--vertical]           render every lesson in a level that has a script
  approve <slug>                          mark a video approved in the manifest (founder only)
  check [<slug> ...]                      run the claims filter and structure checks on saved scripts
"""
from __future__ import annotations

import argparse
import sys

from . import config, manifest
from . import script as scripts
from . import voice as voices


def _facts():
    return scripts.verified_public_facts()


def cmd_script(a) -> int:
    from company.llm import FakeLLM
    if a.dry_run:
        llm = FakeLLM()
        out = config.OUT_DIR / "dry-run" / f"{a.slug}.json"
    else:
        try:
            from company.llm import ClaudeLLM
            llm = ClaudeLLM()
        except Exception as exc:  # no key or package: say so plainly
            print(f"Can't reach Claude ({exc}). Set ANTHROPIC_API_KEY, or use --dry-run.", file=sys.stderr)
            return 2
        out = scripts.script_path(a.slug)
        if out.exists() and not a.force:
            print(f"{out} already exists (it may be hand-edited). Use --force to replace it.", file=sys.stderr)
            return 1
    s = scripts.generate(a.slug, llm, facts=_facts())
    scripts.save(s, out)
    secs = scripts.estimated_seconds(s)
    words = sum(scripts.word_count(x.narration) for x in s.scenes)
    print(f"Wrote {out}: {len(s.scenes)} scenes, {words} words, about {secs:.0f}s"
          + (" (dry run: FakeLLM example content)" if a.dry_run else ""))
    return 0


def _render_one(slug: str, a, facts) -> bool:
    try:
        s = scripts.load(slug, facts)
    except scripts.ScriptError as exc:
        print(f"  {slug}: {exc}", file=sys.stderr)
        return False
    from .render import render
    v = voices.get_voice(a.voice)
    r = render(s, vertical=a.vertical, voice=v, seconds=a.seconds, update_manifest=not a.no_manifest)
    print(f"  {slug}: {r.mp4} ({r.duration:.0f}s, {r.bytes / 1e6:.2f} MB, narration={r.narration}, "
          f"{r.wpm:.0f} wpm, rendered in {r.seconds_taken:.0f}s)")
    return True


def cmd_render(a) -> int:
    return 0 if _render_one(a.slug, a, _facts()) else 1


def cmd_render_level(a) -> int:
    lessons = scripts.lessons_in_level(a.level)
    if not lessons:
        print(f"No level {a.level} in the curriculum.", file=sys.stderr)
        return 1
    facts, ok, missing = _facts(), 0, []
    for lesson in lessons:
        slug = lesson["slug"]
        if not scripts.script_path(slug).exists():
            missing.append(slug)
            continue
        ok += _render_one(slug, a, facts)
    print(f"Level {a.level}: rendered {ok} of {len(lessons)} lessons.")
    if missing:
        print("No script yet (run `python -m studio script <slug>` first): " + ", ".join(missing))
    return 0 if ok + len(missing) == len(lessons) else 1


def cmd_approve(a) -> int:
    try:
        scripts.load(a.slug, _facts())  # never approve a video whose script fails the checks
        entry = manifest.approve(a.slug)
    except (scripts.ScriptError, KeyError, FileNotFoundError) as exc:
        print(f"Not approved: {exc}", file=sys.stderr)
        return 1
    print(f"Approved {a.slug} ({entry['mp4']}). Re-rendering it will reset approval.")
    return 0


def cmd_check(a) -> int:
    slugs = a.slugs or sorted(p.stem for p in config.SCRIPTS_DIR.glob("*.json"))
    facts, bad = _facts(), 0
    for slug in slugs:
        try:
            s = scripts.load(slug, facts)
            print(f"  ok  {slug}: about {scripts.estimated_seconds(s):.0f}s")
        except scripts.ScriptError as exc:
            bad += 1
            print(f"  FAIL {slug}: {exc}")
    return 1 if bad else 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m studio", description="Patient Money video studio")
    sub = p.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("script", help="generate a reviewed script for a lesson")
    sp.add_argument("slug")
    sp.add_argument("--dry-run", action="store_true", help="use FakeLLM (no API key, no cost)")
    sp.add_argument("--force", action="store_true", help="replace an existing script")
    sp.set_defaults(fn=cmd_script)
    for name, fn in (("render", cmd_render), ("render-level", cmd_render_level)):
        rp = sub.add_parser(name)
        rp.add_argument("level" if name == "render-level" else "slug", type=int if name == "render-level" else str)
        rp.add_argument("--vertical", action="store_true", help="1080x1920 cut with burned-in captions")
        rp.add_argument("--voice", default="auto", help=f"auto (default), or one of: {', '.join(voices.PROVIDERS)}")
        rp.add_argument("--seconds", type=float, default=None, help="render only the first N seconds (preview)")
        rp.add_argument("--no-manifest", action="store_true", help="don't touch the manifest")
        rp.set_defaults(fn=fn)
    ap = sub.add_parser("approve", help="mark a rendered video approved")
    ap.add_argument("slug")
    ap.set_defaults(fn=cmd_approve)
    cp = sub.add_parser("check", help="check saved scripts")
    cp.add_argument("slugs", nargs="*")
    cp.set_defaults(fn=cmd_check)
    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
