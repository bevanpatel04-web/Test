"""Captions: narration split into readable cues (2 lines of about 42 characters) and written as WebVTT."""
from __future__ import annotations

import math
import re
from dataclasses import dataclass

LINE = 42          # characters per caption line (a common broadcast/web limit)
CUE = 2 * LINE     # characters per cue

_SENTENCE = re.compile(r"(?<=[.!?])[\"”’)]*\s+")
_CLAUSE = re.compile(r"(?<=[,;:])\s+|\s+(?=—)")
_TS = re.compile(r"^(\d{2,}):([0-5]\d):([0-5]\d)\.(\d{3})$")


@dataclass
class Cue:
    start: float
    end: float
    text: str


def _balanced(words: list[str], parts: int) -> list[str]:
    """Split words into `parts` chunks of similar length."""
    total = len(" ".join(words))
    out, cur = [], []
    for w in words:
        cur.append(w)
        if len(out) < parts - 1 and len(" ".join(cur)) >= total / parts:
            out.append(" ".join(cur))
            cur = []
    if cur:
        out.append(" ".join(cur))
    return out


def chunks(text: str, limit: int = CUE) -> list[str]:
    """Split narration into cue-sized chunks at sentence ends, then commas, then evenly by words."""
    out = []
    for sentence in filter(None, (x.strip() for x in _SENTENCE.split(text.strip()))):
        if len(sentence) <= limit:
            out.append(sentence)
            continue
        cur = ""
        for clause in filter(None, (x.strip() for x in _CLAUSE.split(sentence))):
            pieces = [clause] if len(clause) <= limit else _balanced(clause.split(), math.ceil(len(clause) / limit))
            for p in pieces:
                if cur and len(cur) + 1 + len(p) > limit:
                    out.append(cur)
                    cur = p
                else:
                    cur = f"{cur} {p}".strip()
        if cur:
            out.append(cur)
    # Fold a tiny trailing fragment ("Yes.") into the previous cue when it fits.
    merged: list[str] = []
    for c in out:
        if merged and len(c) < 12 and len(merged[-1]) + 1 + len(c) <= limit:
            merged[-1] = f"{merged[-1]} {c}"
        else:
            merged.append(c)
    return merged


def wrap(text: str, width: int = LINE) -> list[str]:
    """One line if it fits, else two balanced lines broken at a space."""
    if len(text) <= width:
        return [text]
    words = text.split()
    best, best_score = None, None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        score = max(len(a), len(b))
        if best_score is None or score < best_score:
            best, best_score = [a, b], score
    return best or [text]


def ts(seconds: float) -> str:
    ms = int(round(max(0.0, seconds) * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def to_vtt(cues: list[Cue]) -> str:
    lines = ["WEBVTT", ""]
    for i, c in enumerate(cues, 1):
        lines += [str(i), f"{ts(c.start)} --> {ts(c.end)}", *wrap(c.text), ""]
    return "\n".join(lines)


def _parse_ts(s: str) -> float | None:
    m = _TS.match(s.strip())
    if not m:
        return None
    h, mi, se, ms = (int(x) for x in m.groups())
    return h * 3600 + mi * 60 + se + ms / 1000


def validate_vtt(text: str, duration: float | None = None) -> list[str]:
    """Problems with a WebVTT file: header, cue timing (ordered, positive, no overlap), and text."""
    problems = []
    if not text.startswith("WEBVTT") or (len(text) > 6 and text[6] not in "\n \t"):
        problems.append("file must start with 'WEBVTT'")
    blocks = [b for b in re.split(r"\n\s*\n", text.replace("\r\n", "\n").strip()) if b.strip()][1:]
    if not blocks:
        problems.append("no cues")
    prev_end = 0.0
    for n, block in enumerate(blocks, 1):
        rows = block.split("\n")
        timing = next((r for r in rows if "-->" in r), None)
        if timing is None:
            problems.append(f"cue {n} has no timing line")
            continue
        body = rows[rows.index(timing) + 1:]
        start_s, _, end_s = timing.partition("-->")
        start, end = _parse_ts(start_s), _parse_ts(end_s.split()[0] if end_s.split() else "")
        if start is None or end is None:
            problems.append(f"cue {n} has a malformed timestamp: {timing!r}")
            continue
        if end <= start:
            problems.append(f"cue {n} ends before it starts")
        if start < prev_end - 1e-6:
            problems.append(f"cue {n} overlaps the previous cue")
        if duration is not None and end > duration + 0.05:
            problems.append(f"cue {n} runs past the end of the video")
        if not any(r.strip() for r in body):
            problems.append(f"cue {n} has no text")
        if any(len(r) > LINE + 8 for r in body):
            problems.append(f"cue {n} has a line over {LINE + 8} characters")
        if len(body) > 2:
            problems.append(f"cue {n} has more than 2 lines")
        prev_end = end
    return problems
