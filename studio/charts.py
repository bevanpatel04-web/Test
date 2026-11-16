"""Chart math and animated chart drawing.

The growth math is a straight port of invest/site/assets/calc.js (`project`, `money`, `compactMoney`,
`niceTicks`), so a video and the calculator always agree: the same amount is added at the start of every
month and the balance grows at a steady hypothetical yearly rate, compounded monthly.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable

from PIL import Image, ImageDraw

from .draw import THEME, badge, bar_shape, font, rounded, text_sprite, wrap


# ---- Math (port of calc.js) ----------------------------------------------------------------------
def monthly_rate(annual: float) -> float:
    return (1 + annual) ** (1 / 12) - 1


def project(start_age: int, end_age: int, monthly: float, rate: float, delay: int = 0) -> list[tuple[int, float, float]]:
    """Yearly points (age, balance, contributed) from start_age to end_age."""
    mr = monthly_rate(rate)
    balance = contributed = 0.0
    points = [(start_age, 0.0, 0.0)]
    for age in range(start_age, end_age):
        for _ in range(12):
            if age >= start_age + delay:
                balance += monthly
                contributed += monthly
            balance *= 1 + mr
        points.append((age + 1, balance, contributed))
    return points


def _js_round(x: float) -> int:
    return int(math.floor(x + 0.5))


def money(n: float) -> str:
    a = abs(n)
    r = _js_round(a / 100) * 100 if a >= 10000 else _js_round(a)
    return ("-$" if n < 0 and r > 0 else "$") + f"{r:,}"


def _trim(x: float) -> str:
    return f"{math.floor(x * 10 + 0.5) / 10:.1f}".rstrip("0").rstrip(".")


def compact_money(n: float) -> str:
    a = abs(n)
    sign = "-" if n < 0 and _js_round(a) > 0 else ""
    if a >= 999950:
        return f"{sign}${_trim(a / 1e6)}M"
    if a >= 999.5:
        return f"{sign}${_trim(a / 1e3)}K"
    return f"{sign}${_js_round(a)}"


def nice_ticks(mx: float, count: int = 4) -> list[float]:
    if not (mx > 0) or not math.isfinite(mx):
        return [0, 1]
    raw = mx / count
    mag = 10 ** math.floor(math.log10(raw))
    step = next((s * mag for s in (1, 2, 2.5, 5, 10) if s * mag >= raw), 10 * mag)
    ticks, k = [], 0
    while k * step <= mx + step * 0.0001:
        ticks.append(float(f"{k * step:.12g}"))
        k += 1
    if ticks[-1] < mx:
        ticks.append(float(f"{len(ticks) * step:.12g}"))
    return ticks


def fmt(v: float, unit: str) -> str:
    if unit == "$":
        return money(v)
    if unit == "%":
        return f"{v:g}%"
    return f"{v:,.0f}" if abs(v) >= 1000 else f"{v:g}"


def fmt_tick(v: float, unit: str) -> str:
    return compact_money(v) if unit == "$" else fmt(v, unit)


def ease(p: float) -> float:
    p = min(1.0, max(0.0, p))
    return 1 - (1 - p) ** 3


def ease_io(p: float) -> float:
    p = min(1.0, max(0.0, p))
    return 4 * p ** 3 if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2


# ---- Drawing --------------------------------------------------------------------------------------
@dataclass
class Item:
    """A sprite that fades (and slides) into place at t_in seconds into its scene."""
    sprite: Image.Image
    x: float
    y: float
    t_in: float = 0.0
    motion: str = "up"      # up | left | fade
    dur: float = 0.55


@dataclass
class ChartParts:
    items: list[Item] = field(default_factory=list)
    # dynamic(tau) -> (cache key, [(sprite, x, y), ...]) for the animated part of the chart
    dynamic: Callable | None = None
    done_at: float = 0.0


def _ss_line(d: ImageDraw.ImageDraw, pts, color, width: float):
    if len(pts) < 2:
        return
    d.line(pts, fill=color, width=max(1, int(round(width))), joint="curve")
    r = width / 2
    for x, y in (pts[0], pts[-1]):
        d.ellipse([x - r, y - r, x + r, y + r], fill=color)


class LinePlot:
    """Lines drawn left to right over time, with a hairline grid, ticks, legend and direct end labels."""

    SS = 2

    def __init__(self, box, L, series, x_ticks, unit, t0, dur, legend=True):
        self.L, self.unit, self.t0, self.dur = L, unit, t0, dur
        u, fs = L.u, L.px("chart")
        x0, y0, x1, y1 = box
        self.f_tick, self.f_leg = font("md", fs * 0.95), font("sb", fs)
        self.f_val, self.f_name = font("b", fs * 1.15), font("md", fs * 0.92)
        self.series = series  # list of (name, color, width, [(x, y)])
        xs = [p[0] for s in series for p in s[3]]
        self.xmin, self.xmax = min(xs), max(xs)
        ymax = max(p[1] for s in series for p in s[3])
        self.ticks = nice_ticks(ymax, 4)
        parts: list[Item] = []

        # Legend: a short colored key line beside each name (text stays in text colors).
        top = y0
        if legend and len(series) > 1:
            gx, gy, row_h = x0, y0, self.f_leg.size * 1.5
            for name, color, *_ in series:
                key = rounded(22 * u, max(2, 4 * u), 2 * u, color)
                t = text_sprite(name, self.f_leg, THEME["muted"], lh=1.0)
                need = key.width + 8 * u + t.width
                if gx > x0 and gx + need > x1:
                    gx, gy = x0, gy + row_h
                parts.append(Item(key, gx, gy + self.f_leg.size * 0.55, 0.25, "fade"))
                parts.append(Item(t, gx + key.width + 8 * u, gy, 0.25, "fade"))
                gx += need + 28 * u
            top = gy + row_h + 14 * u

        tick_labels = [fmt_tick(v, unit) for v in self.ticks]
        ytw = max(self.f_tick.getlength(t) for t in tick_labels)
        self.end_vals = [(s[4] if len(s) > 4 else s[0], s[3][-1][1]) for s in series]
        end_w = max(max(self.f_val.getlength(fmt(v, unit)), self.f_name.getlength(n)) for n, v in self.end_vals)
        self.px0 = x0 + ytw + 14 * u
        self.px1 = x1 - end_w - 26 * u
        self.py0 = top + self.f_val.size * 0.6
        self.py1 = y1 - self.f_tick.size * 1.9
        # Static frame: grid, baseline and tick labels, drawn once.
        frame = Image.new("RGBA", (int(x1 - x0) + 2, int(y1 - y0) + 2), (0, 0, 0, 0))
        d = ImageDraw.Draw(frame)
        hair = max(1, int(round(1.2 * u)))
        for v, label in zip(self.ticks, tick_labels):
            y = self.ty(v) - y0
            d.line([(self.px0 - x0, y), (self.px1 - x0, y)], fill=THEME["axis"] if v == 0 else THEME["grid"],
                   width=hair * (2 if v == 0 else 1))
            lw = self.f_tick.getlength(label)
            d.text((self.px0 - x0 - 12 * u - lw, y - self.f_tick.size * 0.62), label, font=self.f_tick, fill=THEME["faint"])
        for i, (xv, label) in enumerate(x_ticks):
            x = self.tx(xv) - x0
            lw = self.f_tick.getlength(label)
            lx = min(max(x - lw / 2, 0), self.px1 - x0 - lw + 30 * u)
            d.text((lx, self.py1 - y0 + 10 * u), label, font=self.f_tick, fill=THEME["faint"])
        parts.append(Item(frame, x0, y0, 0.1, "fade"))

        # End labels: value in bold text color, name in muted; nudged apart so they never collide.
        blocks = []
        for (name, v), s in zip(self.end_vals, series):
            spr = Image.new("RGBA", (int(end_w) + 4, int(self.f_val.size * 1.25 + self.f_name.size * 1.3)), (0, 0, 0, 0))
            dd = ImageDraw.Draw(spr)
            dd.text((0, 0), fmt(v, unit), font=self.f_val, fill=THEME["text"])
            dd.text((0, self.f_val.size * 1.22), name, font=self.f_name, fill=THEME["muted"])
            blocks.append([self.ty(s[3][-1][1]) - self.f_val.size * 0.65, spr])
        blocks.sort(key=lambda b: b[0])
        for i in range(1, len(blocks)):
            min_y = blocks[i - 1][0] + blocks[i - 1][1].height + 6 * u
            blocks[i][0] = max(blocks[i][0], min_y)
        overflow = blocks[-1][0] + blocks[-1][1].height - (y1 + 4 * u) if blocks else 0
        for b in blocks:
            if overflow > 0:
                b[0] -= overflow
            parts.append(Item(b[1], self.px1 + 18 * u, b[0], t0 + dur, "fade"))
        self.items = parts
        self._cache_key, self._cache = None, None

    def tx(self, x):
        return self.px0 + (x - self.xmin) / max(1e-9, self.xmax - self.xmin) * (self.px1 - self.px0)

    def ty(self, y):
        top = self.ticks[-1] or 1
        return self.py1 - y / top * (self.py1 - self.py0)

    def dynamic(self, tau: float):
        p = ease_io((tau - self.t0) / self.dur) if self.dur > 0 else 1.0
        key = int(p * 600)
        if key == self._cache_key:
            return key, self._cache
        u, S = self.L.u, self.SS
        pad = 12 * u
        ox, oy = self.px0 - pad, self.py0 - pad - 8 * u
        w, h = int(self.px1 - ox + pad), int(self.py1 - oy + pad)
        layer = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        cut = self.xmin + p * (self.xmax - self.xmin)
        heads = []
        for name, color, width, pts, *_ in reversed(self.series):  # first series drawn last, on top
            vis = [(x, y) for x, y in pts if x <= cut]
            nxt = next(((x, y) for x, y in pts if x > cut), None)
            if vis and nxt and p < 1:
                (xa, ya), (xb, yb) = vis[-1], nxt
                f = (cut - xa) / max(1e-9, xb - xa)
                vis.append((cut, ya + f * (yb - ya)))
            if not vis:
                continue
            sp = [((self.tx(x) - ox) * S, (self.ty(y) - oy) * S) for x, y in vis]
            _ss_line(d, sp, color, width * u * S) if len(sp) > 1 else None
            heads.append((sp[-1], color))
        for (x, y), color in heads:
            r, ring = 6.5 * u * S, 2.5 * u * S
            d.ellipse([x - r - ring, y - r - ring, x + r + ring, y + r + ring], fill=THEME["bg"])
            d.ellipse([x - r, y - r, x + r, y + r], fill=color)
        sprite = layer.resize((w, h), Image.LANCZOS)
        self._cache_key, self._cache = key, [(sprite, ox, oy)]
        return key, self._cache


def growth_chart(spec, box, L, t0: float, dur: float) -> ChartParts:
    start, end = int(spec.start_age), int(spec.end_age)
    now = project(start, end, spec.monthly, spec.rate)
    series = [(f"Start at {start}", THEME["s1"], 4.5, [(a, b) for a, b, _ in now])]
    if spec.delay_years:
        later = project(start, end, spec.monthly, spec.rate, int(spec.delay_years))
        series.append((f"Start at {start + spec.delay_years}", THEME["s2"], 4.5,
                       [(a, b) for a, b, _ in later if a >= start + spec.delay_years]))
    series.append((f"Money put in (start at {start})", THEME["field"], 3.0, [(a, c) for a, _, c in now], "Put in"))
    step = 10 if end - start >= 30 else 5
    ages = list(range(start, end + 1, step))
    if ages[-1] != end and end - ages[-1] >= step / 2:
        ages.append(end)
    x_ticks = [(a, f"Age {a}" if i == 0 else str(a)) for i, a in enumerate(ages)]
    plot = LinePlot(box, L, series, x_ticks, "$", t0, dur)
    return ChartParts(plot.items, plot.dynamic, t0 + dur)


def line_chart(spec, box, L, t0: float, dur: float) -> ChartParts:
    pts = list(enumerate(spec.values))
    n = len(pts)
    idx = sorted({0, n // 2, n - 1})
    x_ticks = [(i, spec.labels[i]) for i in idx]
    plot = LinePlot(box, L, [(spec.title or "Hypothetical", THEME["s1"], 4.5, pts)], x_ticks, spec.unit, t0, dur,
                    legend=False)
    return ChartParts(plot.items, plot.dynamic, t0 + dur)


def bars_chart(spec, box, L, t0: float, dur: float) -> ChartParts:
    u, fs = L.u, L.px("chart")
    x0, y0, x1, y1 = box
    f_lab, f_val = font("sb", fs * 1.3), font("b", fs * 1.4)
    n = len(spec.values)
    vmax = max(spec.values) or 1
    lab_w = min(max(f_lab.getlength(x) for x in spec.labels), (x1 - x0) * (0.30 if not L.vertical else 0.36))
    labels = [wrap(x, f_lab, lab_w) for x in spec.labels]
    lab_w = max(f_lab.getlength(line) for ls in labels for line in ls)
    val_w = max(f_val.getlength(fmt(v, spec.unit)) for v in spec.values)
    bx = x0 + lab_w + 28 * u
    full = (x1 - bx) - val_w - 24 * u
    row_h = min((y1 - y0) / n, 128 * u)
    bar_h = min(60 * u, row_h * 0.5)
    top = y0 + ((y1 - y0) - row_h * n) / 2
    items, bars = [], []
    stagger, grow = 0.35, 0.9
    for i, (ls, v) in enumerate(zip(labels, spec.values)):
        cy = top + row_h * (i + 0.5)
        lab = text_sprite(ls, f_lab, THEME["text"], lh=1.12, align="right")
        items.append(Item(lab, bx - 18 * u - lab.width, cy - lab.height / 2, 0.25 + i * 0.12, "fade"))
        length = full * v / vmax
        vt = text_sprite(fmt(v, spec.unit), f_val, THEME["text"], lh=1.0)
        start = t0 + i * stagger
        items.append(Item(vt, bx + length + 14 * u, cy - vt.height / 2, start + grow * 0.8, "fade", 0.4))
        bars.append((cy - bar_h / 2, length, start))
    base = rounded(max(2, 2.5 * u), row_h * n - (row_h - bar_h), 1, THEME["axis"])
    items.append(Item(base, bx - base.width / 2, top + (row_h - bar_h) / 2, 0.15, "fade"))
    cache: dict = {}

    def dynamic(tau):
        out, key = [], []
        for y, length, start in bars:
            w = int(length * ease((tau - start) / grow))
            key.append(w)
            if w >= 2:
                spr = cache.get(w)
                if spr is None:
                    spr = cache[w] = bar_shape(w, bar_h, 6 * u, THEME["accent"])
                out.append((spr, bx + 1 * u, y))
        return tuple(key), out

    return ChartParts(items, dynamic, t0 + (n - 1) * stagger + grow)


def stat_chart(spec, box, L, t0: float, dur: float, body_px: float) -> ChartParts:
    """A sourced percentage as a hero number, with a thin segmented bar showing the part of the whole."""
    u = L.u
    x0, y0, x1, y1 = box
    v = float(spec.values[0])
    f_hero = font("xb", L.px("hero"))
    f_lab = font("sb", body_px)
    hero_w = f_hero.getlength("100%")
    asc, desc = f_hero.getmetrics()
    if L.vertical:
        lab_lines = wrap(spec.labels[0], f_lab, x1 - x0)
        lab = text_sprite(lab_lines, f_lab, THEME["text"], lh=1.2)
        block_h = asc + desc + 24 * u + lab.height
        hy = y0 + max(0, ((y1 - y0) - block_h - 90 * u) / 2)
        lab_xy = (x0, hy + asc + desc + 24 * u)
        bar_y = lab_xy[1] + lab.height + 64 * u
    else:
        lab_lines = wrap(spec.labels[0], f_lab, (x1 - x0) - hero_w - 56 * u)
        lab = text_sprite(lab_lines, f_lab, THEME["text"], lh=1.2)
        block_h = max(asc + desc, lab.height)
        hy = y0 + max(0, ((y1 - y0) - block_h - 90 * u) / 2)
        lab_xy = (x0 + hero_w + 56 * u, hy + (asc + desc - lab.height) / 2)
        bar_y = hy + block_h + 56 * u
    items = [Item(lab, lab_xy[0], lab_xy[1], t0 + 0.3, "up")]
    bar_h, gap = 22 * u, 4 * u
    width = x1 - x0
    f_sc = font("md", L.px("chart") * 0.95)
    for txt, x_al in (("0%", 0), ("100%", 1)):
        s = text_sprite(txt, f_sc, THEME["faint"], lh=1.0)
        items.append(Item(s, x0 + x_al * (width - s.width), bar_y + bar_h + 12 * u, t0 + 0.2, "fade"))
    cache: dict = {}
    grow = 1.4

    def dynamic(tau):
        p = ease((tau - t0) / grow)
        shown = int(round(v * p))
        fill_w = int(width * v / 100 * p)
        key = (shown, fill_w)
        out = []
        hero = cache.get(("h", shown))
        if hero is None:
            hero = cache[("h", shown)] = text_sprite(f"{shown}%", f_hero, THEME["text"], lh=1.0)
        out.append((hero, x0 - 2 * u, hy))
        rest_x = x0 + fill_w + (gap if fill_w > 0 else 0)
        track = cache.get(("t", int(rest_x)))
        if track is None:
            track = cache[("t", int(rest_x))] = rounded(max(2, x1 - rest_x), bar_h, bar_h / 2, THEME["grid"])
        out.append((track, rest_x, bar_y))
        if fill_w >= 2:
            fill = cache.get(("f", fill_w))
            if fill is None:
                fill = cache[("f", fill_w)] = rounded(fill_w, bar_h, bar_h / 2, THEME["accent"])
            out.append((fill, x0, bar_y))
        return key, out

    return ChartParts(items, dynamic, t0 + grow)


def build(spec, box, L, t0: float, dur: float, body_px: float) -> ChartParts:
    if spec.type == "growth":
        return growth_chart(spec, box, L, t0, dur)
    if spec.type == "bars":
        return bars_chart(spec, box, L, t0, dur)
    if spec.type == "stat":
        return stat_chart(spec, box, L, t0, dur, body_px)
    return line_chart(spec, box, L, t0, dur)


__all__ = ["project", "money", "compact_money", "nice_ticks", "build", "Item", "ChartParts", "badge"]
