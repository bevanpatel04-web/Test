"""The video manifest the app reads: invest/site/media/videos/manifest.json (docs/app/contracts.md, section 2).

Every render resets `approved` to false, because the founder approved a different file. Only
`python -m studio approve <slug>` sets it to true.
"""
from __future__ import annotations

import json
import re
from datetime import date

from . import config

ENTRY_KEYS = {"mp4", "captions", "poster", "duration_s", "narration", "ai_label", "approved"}


def load() -> dict:
    if config.MANIFEST.exists():
        return json.loads(config.MANIFEST.read_text())
    return {"updated": date.today().isoformat(), "videos": {}}


def save(doc: dict) -> None:
    problems = validate(doc, check_files=False)
    if problems:
        raise ValueError("manifest would break the contract: " + "; ".join(problems))
    config.MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    config.MANIFEST.write_text(json.dumps(doc, indent=2) + "\n")


def _rel(path) -> str:
    return path.relative_to(config.SITE_DIR).as_posix()


def _order(slugs) -> list[str]:
    """Curriculum order where known, so the file reads like the course."""
    try:
        from .script import load_curriculum
        doc = load_curriculum()
        order = [x["slug"] for lv in doc["levels"] for m in lv["modules"] for x in m["lessons"]]
    except (OSError, ValueError, KeyError):
        order = []
    pos = {s: i for i, s in enumerate(order)}
    return sorted(slugs, key=lambda s: (pos.get(s, len(pos)), s))


def upsert(slug: str, duration: float, narration: str) -> dict:
    doc = load()
    videos = dict(doc.get("videos", {}))
    videos[slug] = {
        "mp4": _rel(config.MEDIA_DIR / f"{slug}.mp4"),
        "captions": _rel(config.MEDIA_DIR / f"{slug}.vtt"),
        "poster": _rel(config.MEDIA_DIR / f"{slug}.jpg"),
        "duration_s": int(round(duration)),
        "narration": narration,
        "ai_label": config.AI_LABEL,
        "approved": False,
    }
    doc = {"updated": date.today().isoformat(), "videos": {s: videos[s] for s in _order(videos)}}
    save(doc)
    return doc["videos"][slug]


def approve(slug: str) -> dict:
    doc = load()
    entry = doc.get("videos", {}).get(slug)
    if entry is None:
        raise KeyError(f"{slug} has no video yet. Render it first: python -m studio render {slug}")
    missing = [entry[k] for k in ("mp4", "captions", "poster") if not (config.SITE_DIR / entry[k]).exists()]
    if missing:
        raise FileNotFoundError(f"missing files for {slug}: {', '.join(missing)}")
    entry["approved"] = True
    doc["updated"] = date.today().isoformat()
    save(doc)
    return entry


def validate(doc: dict, check_files: bool = True) -> list[str]:
    """Contract check for the manifest (exact keys and types, paths relative to invest/site/)."""
    p = []
    if set(doc) != {"updated", "videos"}:
        p.append(f"top-level keys must be exactly 'updated' and 'videos' (got {sorted(doc)})")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(doc.get("updated", ""))):
        p.append("'updated' must be an ISO date (YYYY-MM-DD)")
    videos = doc.get("videos")
    if not isinstance(videos, dict):
        return p + ["'videos' must be an object keyed by lesson slug"]
    for slug, e in videos.items():
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            p.append(f"{slug}: slug must be lowercase letters, digits and hyphens")
        if not isinstance(e, dict) or set(e) != ENTRY_KEYS:
            p.append(f"{slug}: keys must be exactly {sorted(ENTRY_KEYS)}")
            continue
        for key, ext in (("mp4", "mp4"), ("captions", "vtt"), ("poster", "jpg")):
            if e[key] != f"media/videos/{slug}.{ext}":
                p.append(f"{slug}: {key} must be 'media/videos/{slug}.{ext}'")
            elif check_files and not (config.SITE_DIR / e[key]).exists():
                p.append(f"{slug}: {e[key]} does not exist")
        if not isinstance(e["duration_s"], int) or isinstance(e["duration_s"], bool) or e["duration_s"] <= 0:
            p.append(f"{slug}: duration_s must be a positive whole number of seconds")
        if not isinstance(e["narration"], str) or not e["narration"]:
            p.append(f"{slug}: narration must be 'none' or a voice provider name")
        if e["ai_label"] != config.AI_LABEL:
            p.append(f"{slug}: ai_label must be '{config.AI_LABEL}'")
        if not isinstance(e["approved"], bool):
            p.append(f"{slug}: approved must be true or false")
    return p
