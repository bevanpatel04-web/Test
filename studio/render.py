"""Render stage: a reviewed VideoScript becomes an MP4 (H.264, yuv420p, faststart), a WebVTT caption
file, a JPG poster, and an entry in the video manifest.

Frames are drawn with Pillow (brand tokens from style.css, Inter type) and piped to ffmpeg. Motion is
simple and deliberate: elements fade and slide in, bullet lines appear as the narration reaches them,
charts draw over time, and scenes fade out. Identical frames are reused, so static holds cost nothing.
"""
from __future__ import annotations

import bisect
import json
import math
import re
import subprocess
import tempfile
import time
import wave
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from . import charts, config
from .captions import Cue, chunks, to_vtt, validate_vtt, wrap as cap_wrap
from .charts import Item, ease
from .draw import (BORDER, CAPTION_BG, THEME, badge, balanced, brand_mark, check_icon, circle, faded, fit, font,
                   rounded, text_sprite, wrap)
from .script import VideoScript, find_lesson, word_count

# Timing (seconds)
LEAD = {"title": 0.9}           # quiet time before the first words of a scene
DEFAULT_LEAD = 0.7
GAP_SENTENCE, GAP_CLAUSE = 0.38, 0.2
TAIL = 0.9                      # quiet time after the last words
MIN_SCENE = {"title": 4.0, "chart": 8.0, "end": 6.5}
DEFAULT_MIN_SCENE = 3.5
FADE_OUT = 0.35

PILLS = {"concept": "Key idea", "chart": "The numbers", "example": "Example", "recap": "Recap",
         "quiz_teaser": "Quick check"}
QUIZ_FOOTER = "Answer the questions below the video to finish the lesson."


# ---- Timeline -------------------------------------------------------------------------------------
@dataclass
class SceneTime:
    start: float
    end: float
    speech_start: float
    speech_end: float
    cues: list[Cue]
    words: list[tuple[str, float]] = field(default_factory=list)  # (spoken word, absolute time it starts)

    def spoken_at(self, phrase: str, after: float = 0.0) -> float | None:
        """Seconds into the scene when the narration says `phrase` (or most of its words), else None."""
        want = _tokens(phrase)
        if not want:
            return None
        need = max(1, math.ceil(len(want) * 0.5))
        stems = [w for w, _ in self.words]
        for i, (w, t) in enumerate(self.words):
            if t - self.start < after or w not in want:
                continue
            if len(set(stems[i:i + len(want) + 5]) & set(want)) >= need:
                return t - self.start
        return None


_STOP = set("the a an and or of to in on for is are be it its it's you your that this with at by as from can "
            "but not no so if into what when than then".split())


def _tokens(text: str) -> list[str]:
    """Comparable word stems: '$191,700' -> '191700', 'Promised' -> 'promi'."""
    out = []
    for raw in text.lower().split():
        digits = re.sub(r"[^0-9]", "", raw)
        if digits and re.search(r"\d", raw):
            out.append(digits)
            continue
        w = re.sub(r"[^a-z]", "", raw)
        if len(w) >= 3 and w not in _STOP:
            out.append(w[:5])
    return out


@dataclass
class Timeline:
    scenes: list[SceneTime]
    duration: float
    narration: str = "none"
    audio: np.ndarray | None = None
    sample_rate: int = 0
    words: int = 0
    speech_seconds: float = 0.0

    @property
    def cues(self) -> list[Cue]:
        return [c for s in self.scenes for c in s.cues]

    @property
    def wpm(self) -> float:
        """Narration pace: words per minute from each scene's first word to its last (pauses included)."""
        span = sum(s.speech_end - s.speech_start for s in self.scenes)
        return self.words / span * 60 if span else 0.0


def plan_timeline(script: VideoScript, voice=None) -> Timeline:
    """Scene and caption timing. With a voice, each caption chunk is synthesized and timed from its
    real audio; without one, from the words-per-minute rate."""
    t, scenes, clips, words, speech = 0.0, [], [], 0, 0.0
    for sc in script.scenes:
        lead = LEAD.get(sc.kind, DEFAULT_LEAD)
        cur, cues, words_t = t + lead, [], []
        for ch in chunks(sc.narration):
            n = word_count(ch)
            words += n
            if voice is not None and getattr(voice, "name", "none") != "none":
                a, sr = voice.synthesize(ch)
                d = len(a) / sr if sr else 0.0
                clips.append((cur, a, sr))
            else:
                d = max(0.9, n / config.WPM * 60)
            speech += d
            cues.append(Cue(cur, cur + d, ch))
            total = max(1, len(ch))
            pos = 0
            for raw in ch.split():  # word start times, spread by character count within the chunk
                idx = ch.index(raw, pos)
                for tok in _tokens(raw):
                    words_t.append((tok, cur + d * idx / total))
                pos = idx + len(raw)
            cur += d + (GAP_SENTENCE if ch.rstrip("\"”’)")[-1:] in ".!?" else GAP_CLAUSE)
        speech_end = cues[-1].end if cues else t + lead
        end = max(speech_end + TAIL, t + MIN_SCENE.get(sc.kind, DEFAULT_MIN_SCENE))
        for i, c in enumerate(cues):  # let each caption linger briefly, never into the next one
            limit = cues[i + 1].start - 0.04 if i + 1 < len(cues) else end - 0.05
            c.end = min(c.end + 0.3, limit)
        scenes.append(SceneTime(t, end, t + lead, speech_end, cues, words_t))
        t = end
    tl = Timeline(scenes, t, words=words, speech_seconds=speech)
    if clips:
        sr = clips[0][2]
        buf = np.zeros(int(math.ceil(t * sr)) + 1, dtype=np.float32)
        for start, a, rate in clips:
            if rate != sr:  # simple linear resample to the first clip's rate
                a = np.interp(np.linspace(0, len(a), int(len(a) * sr / rate), endpoint=False),
                              np.arange(len(a)), a).astype(np.float32)
            i = int(start * sr)
            buf[i:i + len(a)] += a[: max(0, len(buf) - i)]
        peak = float(np.abs(buf).max()) or 1.0
        tl.audio, tl.sample_rate = np.clip(buf * (0.89 / peak), -1, 1), sr
        tl.narration = voice.name
    return tl


def _truncate(tl: Timeline, seconds: float) -> Timeline:
    if seconds >= tl.duration:
        return tl
    scenes = []
    for s in tl.scenes:
        if s.start >= seconds:
            break
        cues = [Cue(c.start, min(c.end, seconds - 0.01), c.text) for c in s.cues if c.start < seconds - 0.2]
        scenes.append(SceneTime(s.start, min(s.end, seconds), s.speech_start, min(s.speech_end, seconds), cues, s.words))
    audio = tl.audio[: int(seconds * tl.sample_rate) + 1] if tl.audio is not None else None
    words = sum(word_count(c.text) for s in scenes for c in s.cues)
    return Timeline(scenes, seconds, tl.narration, audio, tl.sample_rate, words, tl.speech_seconds)


# ---- Layout ---------------------------------------------------------------------------------------
BASE = {
    False: dict(margin=88, brand_y=44, top=132, bottom=64, cap_top=604, brand=22, pill=17, title=70, heading=48,
                body=40, small=20, chart=22, caption=29, hero=150),
    True: dict(margin=96, brand_y=150, top=290, bottom=330, cap_top=1330, brand=32, pill=26, title=92, heading=68,
               body=54, small=32, chart=34, caption=44, hero=210),
}


@dataclass
class Layout:
    W: int
    H: int
    vertical: bool
    captions: bool
    u: float = field(init=False)

    def __post_init__(self):
        self.u = self.W / (1080 if self.vertical else 1280)

    def px(self, k: str) -> float:
        return BASE[self.vertical][k] * self.u

    @property
    def mx(self):
        return self.px("margin")

    @property
    def cw(self):
        return self.W - 2 * self.mx

    @property
    def top(self):
        return self.px("top")

    @property
    def bottom(self):
        """Lowest y for scene content (above burned-in captions, and above app UI on phones)."""
        if self.captions:
            return self.px("cap_top") - 28 * self.u
        return self.H - self.px("bottom")


# ---- Scenes ---------------------------------------------------------------------------------------
@dataclass
class Built:
    items: list[Item]
    chart: charts.ChartParts | None = None


def _heading(text: str, L: Layout, t_in: float = 0.1, y: float | None = None):
    f, lines = fit(text, "db", L.px("heading"), L.cw, 2)
    spr = text_sprite(lines, f, THEME["text"], lh=1.1)
    y = L.top if y is None else y
    return [Item(spr, L.mx, y, t_in)], y + spr.height


def _lines(text: str) -> list[str]:
    return [x.strip() for x in text.split("\n") if x.strip()]


def _reveal_times(lines: list[str], st: SceneTime) -> list[float]:
    """When each on-screen line appears (seconds into the scene): as the narration says it, or, if the
    narration never does, spread evenly across the narration."""
    s0, span = st.speech_start - st.start, max(0.1, st.speech_end - st.speech_start)
    n, out, prev = len(lines), [], 0.0
    for k, line in enumerate(lines):
        t = st.spoken_at(line, after=prev)
        t = (t - 0.15) if t is not None else (s0 - 0.1 + span * k / max(1, n))
        t = max(0.35, t, (out[-1] + 0.3) if out else 0.0)
        out.append(t)
        prev = t
    return out


def _split_label(line: str):
    if ": " in line:
        a, b = line.rsplit(": ", 1)
        if a.strip() and b.strip() and len(b) <= 18:
            return a.strip(), b.strip()
    return None


def build_rows(sc, st: SceneTime, L: Layout, y: float, style: str) -> list[Item]:
    """Concept/example cards and recap checklists, shrunk until they fit between y and L.bottom."""
    u, lines = L.u, _lines(sc.on_screen)
    if not lines:
        return []
    times = _reveal_times(lines, st)
    avail = L.bottom - y - 36 * u
    card = style in ("concept", "example")
    pad = 36 * u if card else 0
    size = L.px("body")
    for _ in range(12):
        rows, inner_w = [], L.cw - 2 * pad
        f_txt, f_lab, f_val = font("sb", size), font("md", size), font("b", size)
        icon = size * (0.95 if style == "recap" else 0.32)
        gap_icon = size * (0.55 if style == "recap" else 0.7)
        for line in lines:
            pair = _split_label(line) if style == "example" else None
            if pair:
                lab = text_sprite(balanced(pair[0], f_lab, inner_w * 0.62), f_lab, THEME["muted"], lh=1.15)
                val = text_sprite(pair[1], f_val, THEME["text"], lh=1.0)
                rows.append(("pair", lab, val, max(lab.height, val.height)))
            else:
                t = text_sprite(balanced(line, f_txt, inner_w - icon - gap_icon), f_txt, THEME["text"], lh=1.18)
                rows.append(("text", t, None, t.height))
        row_gap = size * (0.75 if style == "recap" else 0.6)
        total = sum(r[3] for r in rows) + row_gap * (len(rows) - 1) + 2 * pad
        if total <= avail or size < L.px("body") * 0.62:
            break
        size *= 0.92
    y0 = y + 36 * u + max(0, (avail - total) * (0.42 if L.vertical else 0.25))
    items: list[Item] = []
    if card:
        bg = THEME["accent_soft"] if style == "example" else THEME["surface"]
        outline = None if style == "example" else BORDER
        items.append(Item(rounded(L.cw, total, 24 * u, bg, outline, max(1, 1.5 * u)), L.mx, y0, max(0.2, times[0] - 0.25),
                          "fade"))
    cy = y0 + pad
    x_in = L.mx + pad
    for (kind, a, b, h), t_in in zip(rows, times):
        if kind == "pair":
            items.append(Item(a, x_in, cy + (h - a.height) / 2, t_in))
            items.append(Item(b, L.mx + L.cw - pad - b.width, cy + (h - b.height) / 2, t_in))
            if b is not rows[-1][2]:
                rule = rounded(L.cw - 2 * pad, max(1, 1.5 * u), 0, THEME["grid"])
                items.append(Item(rule, x_in, cy + h + row_gap / 2, t_in, "fade"))
        else:
            asc = font("sb", size).getmetrics()[0]
            if style == "recap":
                ic = check_icon(icon)
                items.append(Item(ic, x_in, cy + asc * 0.62 - ic.height / 2 + 1, t_in, "fade"))
            else:
                dot = circle(icon, THEME["accent"])
                items.append(Item(dot, x_in, cy + asc * 0.66 - dot.height / 2, t_in, "fade"))
            items.append(Item(a, x_in + icon + gap_icon, cy, t_in))
        cy += h + row_gap
    return items


def _path_motif(level_no: int | None, L: Layout) -> Image.Image | None:
    """Five connected dots, one per level, with this lesson's level filled in violet."""
    if not level_no or not 1 <= level_no <= 5:
        return None
    u, r = L.u, 24 * L.u
    if L.vertical:
        pts = [(r + 10 * u + i * (L.cw - 2 * r - 20 * u) / 4, r + 14 * u) for i in range(5)]
    else:
        pts = [(r + 10 * u + i * 62 * u, r + 14 * u + (4 - i) * 46 * u) for i in range(5)]
    w = int(max(p[0] for p in pts) + r + 14 * u)
    h = int(max(p[1] for p in pts) + r + 14 * u)
    big = Image.new("RGBA", (w * 3, h * 3), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    for a, b in zip(pts, pts[1:]):
        d.line([(a[0] * 3, a[1] * 3), (b[0] * 3, b[1] * 3)], fill=THEME["axis"], width=int(4 * u * 3))
    im = big.resize((w, h), Image.LANCZOS)
    f = font("sb", 20 * u * (1.2 if L.vertical else 1))
    for i, (x, y) in enumerate(pts, 1):
        if i == level_no:
            halo = circle(2 * r + 18 * u, THEME["accent_soft"])
            im.alpha_composite(halo, (int(x - halo.width / 2), int(y - halo.height / 2)))
            dot, col = circle(2 * r, THEME["accent"]), THEME["accent_ink"]
        else:
            dot, col = circle(2 * r, THEME["surface"], THEME["axis"], 3 * u), THEME["faint"]
        im.alpha_composite(dot, (int(x - r), int(y - r)))
        t = text_sprite(str(i), f, col, lh=1.0)
        asc = f.getmetrics()[0]
        im.alpha_composite(t, (int(x - t.width / 2), int(y - asc * 0.62)))
    return im


def build_title(sc, st, L: Layout, level) -> Built:
    u = L.u
    items: list[Item] = []
    label = f"Level {level['number']} · {level['title']}" if level else "Lesson"
    pill = badge(label, font("sb", L.px("pill") * 1.2), THEME["accent"], THEME["accent_soft"], 16 * u, 8 * u)
    text_w = L.cw if L.vertical else L.cw * 0.64
    f_t, t_lines = fit(sc.heading, "xb", L.px("title"), text_w, 3)
    title = text_sprite(t_lines, f_t, THEME["text"], lh=1.06)
    sub = None
    if sc.on_screen.strip():
        f_s, s_lines = fit(" ".join(_lines(sc.on_screen)), "md", L.px("body") * 0.95, text_w, 2)
        sub = text_sprite(s_lines, f_s, THEME["muted"], lh=1.2)
    foot = text_sprite(f"{config.AI_LABEL} · {config.EDU_LABEL}", font("rg", L.px("small")), THEME["faint"], lh=1.0)
    motif = _path_motif(level["number"] if level else None, L)
    g1, g2 = 26 * u, 24 * u
    group_h = pill.height + g1 + title.height + (g2 + sub.height if sub else 0)
    if L.vertical:
        extra = (110 * u + motif.height) if motif else 0
        y = L.top + max(0, (L.bottom - L.top - group_h - extra - 80 * u) * 0.45)
    else:
        y = L.top + max(0, (L.bottom - L.top - group_h) * 0.42)
    items.append(Item(pill, L.mx, y, 0.15))
    y += pill.height + g1
    items.append(Item(title, L.mx, y, 0.3))
    y += title.height
    if sub:
        y += g2
        items.append(Item(sub, L.mx, y, 0.55))
        y += sub.height
    if motif is not None:
        if L.vertical:
            mx, my = L.mx, y + 110 * u
        else:
            mx, my = L.W - L.mx - motif.width + 10 * u, (L.top + L.bottom) / 2 - motif.height / 2
        items.append(Item(motif, mx, my, 0.75))
        y = max(y, my + motif.height) if L.vertical else y
    fy = (y + 64 * u) if L.vertical else (L.H - L.px("bottom") - foot.height + 8 * u)
    if not L.vertical and L.captions:
        fy = L.bottom - foot.height
    items.append(Item(foot, L.mx, fy, 0.95, "fade"))
    return Built(items)


def build_chart(sc, st, L: Layout) -> Built:
    u = L.u
    items, y = _heading(sc.heading, L)
    if sc.on_screen.strip() and sc.chart.type in ("bars", "stat"):  # line charts carry a legend instead
        f_s, lines = fit(" · ".join(_lines(sc.on_screen)), "md", L.px("body") * 0.78, L.cw, 2)
        sub = text_sprite(lines, f_s, THEME["muted"], lh=1.2)
        items.append(Item(sub, L.mx, y + 12 * u, 0.3))
        y += 12 * u + sub.height
    spec = sc.chart
    note_y = L.bottom
    if spec.note.strip():
        f_n = font("rg", L.px("small") * 1.05)
        note = text_sprite(balanced(spec.note, f_n, L.cw)[:3], f_n, THEME["muted"], lh=1.25)
        note_y = L.bottom - note.height
        items.append(Item(note, L.mx, note_y, 0.6, "fade"))
    box = (L.mx, y + (40 if L.vertical else 30) * u, L.W - L.mx, note_y - (40 if L.vertical else 22) * u)
    if L.vertical and spec.type in ("growth", "line"):  # keep a phone chart from becoming a tall sliver
        h = min(box[3] - box[1], (box[2] - box[0]) * 1.05)
        mid = (box[1] + box[3]) / 2
        box = (box[0], mid - h / 2, box[2], mid + h / 2)
    s0, span = st.speech_start - st.start, max(1.0, st.speech_end - st.speech_start)
    t0, dur = s0 + 0.3, min(9.0, max(3.0, span * 0.55))
    parts = charts.build(spec, box, L, t0, dur, L.px("body"), st.spoken_at)
    return Built(items + parts.items, parts)


def build_quiz(sc, st, L: Layout) -> Built:
    u = L.u
    items, y = _heading(sc.heading, L)
    lines = _lines(sc.on_screen)
    q, choices = (lines[0] if lines else ""), lines[1:4]
    f_q, q_lines = fit(q, "db", L.px("body") * 1.1, L.cw, 2)
    qs = text_sprite(q_lines, f_q, THEME["text"], lh=1.15)
    f_c, f_l = font("md", L.px("body") * 0.88), font("sb", L.px("body") * 0.7)
    box_w = L.cw if L.vertical else min(L.cw, 860 * u)
    ch_h = f_c.size * 2.3
    gap = 16 * u if not L.vertical else 24 * u
    foot = text_sprite(QUIZ_FOOTER, font("md", L.px("small") * 1.05), THEME["muted"], lh=1.0)
    block = qs.height + 30 * u + len(choices) * (ch_h + gap) - gap + 30 * u + foot.height
    y0 = y + 36 * u + max(0, (L.bottom - y - 36 * u - block) * (0.4 if L.vertical else 0.2))
    items.append(Item(qs, L.mx, y0, 0.4))
    cy = y0 + qs.height + 30 * u
    s0 = st.speech_start - st.start
    for i, c in enumerate(choices):
        card = rounded(box_w, ch_h, 14 * u, THEME["surface"], THEME["axis"], max(1, 2 * u))
        letter = circle(ch_h * 0.56, THEME["accent_soft"])
        lt = text_sprite("ABC"[i], f_l, THEME["accent"], lh=1.0)
        asc_l = f_l.getmetrics()[0]
        letter.alpha_composite(lt, (int((letter.width - lt.width) / 2), int(letter.height / 2 - asc_l * 0.62)))
        card.alpha_composite(letter, (int(ch_h * 0.22), int((ch_h - letter.height) / 2)))
        f_cc, c_lines = fit(c, "md", f_c.size, box_w - ch_h * 1.2, 1, 0.7)
        ct = text_sprite(c_lines[:1], f_cc, THEME["text"], lh=1.0)
        asc_c = f_cc.getmetrics()[0]
        card.alpha_composite(ct, (int(ch_h * 0.22 + letter.width + 18 * u), int(ch_h / 2 - asc_c * 0.6)))
        items.append(Item(card, L.mx, cy, max(0.6, s0 + 0.5 + i * 0.3)))
        cy += ch_h + gap
    items.append(Item(foot, L.mx, cy - gap + 30 * u, max(1.2, s0 + 1.6), "fade"))
    return Built(items)


def build_end(sc, st, L: Layout, risk_note: str | None) -> Built:
    u = L.u
    parts = []
    mark = brand_mark(font("db", L.px("heading") * 0.72), L.px("heading") * 0.5)
    parts.append((mark, 0.15, 34 * u))
    f_h, h_lines = fit(sc.heading, "db", L.px("heading") * 1.05, L.cw * 0.9, 2)
    parts.append((text_sprite(h_lines, f_h, THEME["text"], lh=1.1, align="center"), 0.3, 18 * u))
    if sc.on_screen.strip():
        f_o, o_lines = fit(" ".join(_lines(sc.on_screen)), "md", L.px("body") * 0.88, L.cw * (0.95 if L.vertical else 0.78), 3)
        parts.append((text_sprite(o_lines, f_o, THEME["text"], lh=1.22, align="center"), 0.5, 26 * u))
    if risk_note:
        f_r = font("rg", L.px("small") * 1.1)
        r_lines = balanced(risk_note, f_r, L.cw * (0.95 if L.vertical else 0.72))[:3]
        parts.append((text_sprite(r_lines, f_r, THEME["muted"], lh=1.3, align="center"), 0.7, 34 * u))
    a = text_sprite(config.AI_LABEL, font("sb", L.px("body") * 0.66), THEME["text"], lh=1.0)
    b = text_sprite(config.EDU_LABEL, font("md", L.px("body") * 0.56), THEME["muted"], lh=1.0)
    pw, ph = max(a.width, b.width) + 56 * u, a.height + b.height + 12 * u + 36 * u
    card = rounded(pw, ph, 18 * u, THEME["surface"], THEME["axis"], max(1, 2 * u))
    card.alpha_composite(a, (int((pw - a.width) / 2), int(18 * u)))
    card.alpha_composite(b, (int((pw - b.width) / 2), int(18 * u + a.height + 12 * u)))
    parts.append((card, 0.9, 0))
    total = sum(p[0].height + p[2] for p in parts)
    y = L.top + max(0, (L.bottom - L.top - total) * 0.45) - (0 if L.vertical else 24 * u)
    items = []
    for spr, t_in, gap_after in parts:
        items.append(Item(spr, (L.W - spr.width) / 2, y, t_in))
        y += spr.height + gap_after
    return Built(items)


def build_scene(sc, st, L: Layout, script: VideoScript, level) -> Built:
    if sc.kind == "title":
        b = build_title(sc, st, L, level)
    elif sc.kind == "chart" and sc.chart is not None:
        b = build_chart(sc, st, L)
    elif sc.kind == "quiz_teaser":
        b = build_quiz(sc, st, L)
    elif sc.kind == "end":
        b = build_end(sc, st, L, script.risk_note)
    else:
        items, y = _heading(sc.heading, L)
        style = sc.kind if sc.kind in ("example", "recap") else "concept"
        b = Built(items + build_rows(sc, st, L, y, style))
    label = PILLS.get(sc.kind)
    if label:
        pill = badge(label, font("sb", L.px("pill")), THEME["accent"], THEME["accent_soft"], 14 * L.u, 7 * L.u)
        bh = font("sb", L.px("brand")).getmetrics()[0]
        b.items.insert(0, Item(pill, L.W - L.mx - pill.width, L.px("brand_y") + bh * 0.62 - pill.height / 2 + 1, 0.05,
                               "fade"))
    return b


# ---- Frames ---------------------------------------------------------------------------------------
def _composite(frame: Image.Image, spr: Image.Image, x: float, y: float) -> None:
    x, y = int(round(x)), int(round(y))
    if x >= frame.width or y >= frame.height or x + spr.width <= 0 or y + spr.height <= 0:
        return
    if x < 0 or y < 0 or x + spr.width > frame.width or y + spr.height > frame.height:
        l, t = max(0, -x), max(0, -y)
        r, b = min(spr.width, frame.width - x), min(spr.height, frame.height - y)
        spr = spr.crop((l, t, r, b))
        x, y = x + l, y + t
    frame.alpha_composite(spr, (x, y))


def chrome(L: Layout) -> Image.Image:
    im = Image.new("RGBA", (L.W, L.H), THEME["bg"] + (255,))
    mark = brand_mark(font("sb", L.px("brand")), L.px("brand") * 0.72)
    _composite(im, mark, L.mx, L.px("brand_y"))
    return im


def caption_sprite(text: str, L: Layout) -> Image.Image:
    u = L.u
    max_w = L.cw * (0.96 if L.vertical else 0.84)
    size = L.px("caption")
    for _ in range(6):
        f = font("sb", size)
        lines = [x for x in cap_wrap(text)]
        if any(f.getlength(x) > max_w for x in lines) or len(lines) > 2:
            lines = wrap(text, f, max_w)
        if len(lines) <= 2:
            break
        size *= 0.92
    t = text_sprite(lines, f, (255, 255, 255), lh=1.25, align="center")
    pad_x, pad_y = 22 * u, 12 * u
    box = rounded(t.width + 2 * pad_x, t.height + 2 * pad_y - 4 * u, 14 * u, CAPTION_BG)
    box.alpha_composite(t, (int(pad_x), int(pad_y - 2 * u)))
    return box


class FrameMaker:
    def __init__(self, script: VideoScript, tl: Timeline, L: Layout, burn_captions: bool):
        self.script, self.tl, self.L, self.burn = script, tl, L, burn_captions
        found = find_lesson(script.slug) if config.CURRICULUM.exists() else None
        self.level = found[0] if found else None
        self.base = chrome(L)
        self.plain = Image.new("RGBA", (L.W, L.H), THEME["bg"] + (255,))  # end card shows its own brand mark
        self.starts = [s.start for s in tl.scenes]
        self.built: dict[int, Built] = {}
        self.cues = tl.cues
        self.cue_starts = [c.start for c in self.cues]
        self.cap_cache: dict[int, Image.Image] = {}

    def scene(self, i: int) -> Built:
        if i not in self.built:
            self.built = {k: v for k, v in self.built.items() if k >= i - 1}  # keep memory flat
            self.built[i] = build_scene(self.script.scenes[i], self.tl.scenes[i], self.L, self.script, self.level)
        return self.built[i]

    def frame(self, t: float, captions: bool | None = None):
        """Return (state key, RGBA frame) for time t. Equal keys mean identical frames."""
        L = self.L
        i = max(0, bisect.bisect_right(self.starts, t) - 1)
        st = self.tl.scenes[i]
        b = self.scene(i)
        tau = t - st.start
        last = i == len(self.tl.scenes) - 1
        exit_a = 1.0 if last else min(1.0, max(0.0, (st.end - t) / FADE_OUT))
        key: list = [i, round(exit_a, 2)]
        im = (self.plain if self.script.scenes[i].kind == "end" else self.base).copy()
        for n, it in enumerate(b.items):
            p = (tau - it.t_in) / it.dur
            if p <= 0:
                continue
            e = ease(p)
            a = e * exit_a
            if a <= 0.02:
                continue
            dx = -(1 - e) * 40 * L.u if it.motion == "left" else 0
            dy = (1 - e) * 22 * L.u if it.motion == "up" else 0
            key.append((n, int(a * 32), int(dx), int(dy)))
            _composite(im, faded(it.sprite, a), it.x + dx, it.y + dy)
        if b.chart and b.chart.dynamic and exit_a > 0.02:
            k, parts = b.chart.dynamic(tau)
            key.append(("c", k))
            for spr, x, y in parts:
                _composite(im, faded(spr, exit_a), x, y)
        if self.burn if captions is None else captions:
            j = bisect.bisect_right(self.cue_starts, t) - 1
            if j >= 0 and t <= self.cues[j].end:
                spr = self.cap_cache.get(j)
                if spr is None:
                    self.cap_cache = {j: caption_sprite(self.cues[j].text, L)}
                    spr = self.cap_cache[j]
                cy = L.px("cap_top") + (L.H - L.px("bottom") - L.px("cap_top") - spr.height) / 2 if L.vertical \
                    else L.H - 26 * L.u - spr.height
                _composite(im, spr, (L.W - spr.width) / 2, cy)
                key.append(("cap", j))
        return tuple(key), im


# ---- Encoding -------------------------------------------------------------------------------------
@dataclass
class RenderResult:
    mp4: Path
    captions: Path
    poster: Path | None
    duration: float
    narration: str
    wpm: float
    bytes: int
    seconds_taken: float


def _write_wav(path: Path, audio: np.ndarray, sr: int) -> None:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((audio * 32767).astype("<i2").tobytes())


def encode(maker: FrameMaker, out: Path, fps: int, audio_wav: Path | None, crf: int) -> None:
    L, tl = maker.L, maker.tl
    cmd = [config.FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{L.W}x{L.H}", "-r", str(fps), "-i", "-"]
    if audio_wav:
        cmd += ["-i", str(audio_wav)]
    cmd += ["-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
            "-c:v", "libx264", "-preset", "slow", "-tune", "animation", "-crf", str(crf),
            "-profile:v", "high", "-g", str(fps * 10), "-pix_fmt", "yuv420p",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709"]
    if audio_wav:
        cmd += ["-c:a", "aac", "-b:a", "64k", "-ac", "1", "-ar", "24000", "-shortest"]
    cmd += ["-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    n = int(round(tl.duration * fps))
    prev_key, prev_bytes = None, None
    try:
        for f in range(n):
            key, im = maker.frame(f / fps)
            if key != prev_key:
                prev_key, prev_bytes = key, im.convert("RGB").tobytes()
            proc.stdin.write(prev_bytes)
        proc.stdin.close()
    except BrokenPipeError:
        pass
    err = proc.stderr.read().decode(errors="replace")
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg failed: {err.strip()[-800:]}")


def render(script: VideoScript, *, vertical: bool = False, voice=None, size: tuple[int, int] | None = None,
           fps: int = config.FPS, out_dir: Path | None = None, seconds: float | None = None,
           crf: int | None = None, update_manifest: bool = True, poster: bool = True) -> RenderResult:
    """Render one script. `voice` is a voice object from studio.voice (None means captions only)."""
    t_start = time.time()
    if vertical:  # social cut: the quiz lives in the app, so "answer below the video" doesn't belong in a clip
        script = script.model_copy(update={"scenes": [x for x in script.scenes if x.kind != "quiz_teaser"]})
    W, H = size or ((1080, 1920) if vertical else (1280, 720))
    W, H = W - W % 2, H - H % 2
    tl = plan_timeline(script, voice)
    full = seconds is None or seconds >= tl.duration
    if not full:
        tl = _truncate(tl, seconds)
    burn = vertical or tl.audio is None  # a video with no voice carries its words on screen
    L = Layout(W, H, vertical, captions=burn)
    if out_dir is None and not full:  # previews never overwrite real lesson media
        out_dir = config.OUT_DIR / "preview"
    out_dir = Path(out_dir or (config.VERTICAL_DIR if vertical else config.MEDIA_DIR))
    out_dir.mkdir(parents=True, exist_ok=True)
    mp4, vtt = out_dir / f"{script.slug}.mp4", out_dir / f"{script.slug}.vtt"
    vtt_text = to_vtt(tl.cues)
    problems = [x for x in validate_vtt(vtt_text, tl.duration) if full or x != "no cues"]
    if problems:
        raise RuntimeError("caption timing problem: " + "; ".join(problems))
    maker = FrameMaker(script, tl, L, burn)
    with tempfile.TemporaryDirectory() as tmp:
        wav = None
        if tl.audio is not None:
            wav = Path(tmp) / "narration.wav"
            _write_wav(wav, tl.audio, tl.sample_rate)
        encode(maker, mp4, fps, wav, crf or (28 if vertical else 27))
    vtt.write_text(vtt_text)
    poster_path = None
    if poster:
        st = tl.scenes[0]
        _, im = maker.frame(min(st.end - FADE_OUT - 0.1, st.start + 2.8), captions=False)
        poster_path = out_dir / f"{script.slug}.jpg"
        im.convert("RGB").save(poster_path, "JPEG", quality=84, optimize=True, progressive=True)
    if update_manifest and full and not vertical:
        from . import manifest
        manifest.upsert(script.slug, tl.duration, tl.narration)
    return RenderResult(mp4, vtt, poster_path, tl.duration, tl.narration, tl.wpm, mp4.stat().st_size,
                        time.time() - t_start)


def frame_png(script: VideoScript, t: float, path: Path, *, vertical: bool = False, voice=None) -> Path:
    """Draw a single frame (for quick layout checks without encoding)."""
    tl = plan_timeline(script, voice)
    W, H = (1080, 1920) if vertical else (1280, 720)
    maker = FrameMaker(script, tl, Layout(W, H, vertical, captions=vertical or tl.audio is None),
                       vertical or tl.audio is None)
    _, im = maker.frame(t)
    im.convert("RGB").save(path)
    return path


def describe(tl: Timeline) -> str:
    return json.dumps({"duration_s": round(tl.duration, 1), "words": tl.words, "wpm": round(tl.wpm),
                       "scenes": [round(s.end - s.start, 1) for s in tl.scenes]})
