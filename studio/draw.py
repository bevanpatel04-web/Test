"""Drawing primitives: brand tokens (from invest/site/assets/style.css, light theme), Inter fonts,
anti-aliased shapes and cached text sprites. Everything is drawn once as an RGBA sprite and then
composited per frame, so a frame costs a few image copies rather than a full redraw."""
from __future__ import annotations

from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

from . import config


def _hex(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


THEME = {k: _hex(v) for k, v in {
    "bg": "#f4f3ef", "surface": "#fcfcfb", "text": "#0b0b0b", "muted": "#52514e", "faint": "#6f6e69",
    "grid": "#e1e0d9", "axis": "#c3c2b7", "field": "#8a8982", "accent": "#5a43d0", "accent_ink": "#ffffff",
    "accent_soft": "#ecebfb", "s1": "#2a78d6", "s2": "#eb6834", "s3": "#1baf7a",
}.items()}
BORDER = (11, 11, 11, 26)          # --border: rgba(11, 11, 11, 0.10)
CAPTION_BG = (11, 11, 11, 224)

FONT_FILES = {
    "xb": "InterDisplay-ExtraBold.otf", "db": "InterDisplay-Bold.otf", "b": "Inter-Bold.otf",
    "sb": "Inter-SemiBold.otf", "md": "Inter-Medium.otf", "rg": "Inter-Regular.otf",
}
SS = 3  # supersampling factor for shapes (Pillow shapes are not anti-aliased)


@lru_cache(maxsize=256)
def font(style: str, px: int) -> ImageFont.FreeTypeFont:
    px = max(6, int(round(px)))
    try:
        return ImageFont.truetype(str(config.FONT_DIR / FONT_FILES[style]), px)
    except OSError:  # no Inter on this machine: Pillow's bundled font keeps renders working
        return ImageFont.load_default(px)


def text_w(text: str, f) -> float:
    return f.getlength(text)


def wrap(text: str, f, max_w: float) -> list[str]:
    """Greedy word wrap by measured width; explicit newlines are kept."""
    lines = []
    for para in text.split("\n"):
        words, cur = para.split(), ""
        for w in words:
            trial = f"{cur} {w}".strip()
            if cur and f.getlength(trial) > max_w:
                lines.append(cur)
                cur = w
            else:
                cur = trial
        lines.append(cur)
    return [x for x in lines if x] or [""]


def balanced(text: str, f, max_w: float) -> list[str]:
    """Wrap into as few lines as greedy wrapping needs, but with even line lengths (no orphan last word)."""
    out = []
    for para in text.split("\n"):
        lines = wrap(para, f, max_w)
        if len(lines) > 1:
            lo, hi = max(f.getlength(w) for w in para.split()), max_w
            for _ in range(14):
                mid = (lo + hi) / 2
                if len(wrap(para, f, mid)) <= len(lines):
                    hi = mid
                else:
                    lo = mid
            lines = wrap(para, f, hi + 0.5)
        out += lines
    return [x for x in out if x] or [""]


def fit(text: str, style: str, px: float, max_w: float, max_lines: int, min_ratio: float = 0.6):
    """Largest font size (down to min_ratio of px) at which the text wraps into max_lines (balanced)."""
    size = px
    while True:
        f = font(style, size)
        lines = wrap(text, f, max_w)
        if len(lines) <= max_lines or size <= px * min_ratio:
            return f, balanced(text, f, max_w)
        size *= 0.93


def line_height(f, ratio: float = 1.18) -> int:
    return int(round(f.size * ratio))


def text_sprite(lines: list[str] | str, f, color, lh: float = 1.18, align: str = "left") -> Image.Image:
    lines = [lines] if isinstance(lines, str) else lines
    asc, desc = f.getmetrics()
    step = line_height(f, lh)
    w = int(max((f.getlength(x) for x in lines), default=1)) + 4
    h = step * (len(lines) - 1) + asc + desc + 2
    im = Image.new("RGBA", (max(1, w), max(1, h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, line in enumerate(lines):
        lw = f.getlength(line)
        x = {"left": 0, "center": (w - lw) / 2, "right": w - lw}[align]
        d.text((x + 1, i * step), line, font=f, fill=color)
    return im


def _ss(w: int, h: int):
    return Image.new("RGBA", (max(1, w * SS), max(1, h * SS)), (0, 0, 0, 0))


def _down(im: Image.Image, w: int, h: int) -> Image.Image:
    return im.resize((max(1, w), max(1, h)), Image.LANCZOS)


def rounded(w: int, h: int, r: float, fill, outline=None, width: float = 0) -> Image.Image:
    w, h = max(1, int(round(w))), max(1, int(round(h)))
    im = _ss(w, h)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * SS - 1, h * SS - 1], radius=min(r, h / 2, w / 2) * SS, fill=fill,
                        outline=outline, width=int(round(width * SS)) if outline else 0)
    return _down(im, w, h)


def bar_shape(w: int, h: int, r: float, fill) -> Image.Image:
    """A horizontal bar: square at the baseline (left), rounded at the data end (right)."""
    w, h = max(1, int(round(w))), max(1, int(round(h)))
    im = _ss(w, h)
    d = ImageDraw.Draw(im)
    rr = min(r, h / 2, w / 2) * SS
    d.rounded_rectangle([0, 0, w * SS - 1, h * SS - 1], radius=rr, fill=fill)
    d.rectangle([0, 0, min(w * SS - 1, rr * 2), h * SS - 1], fill=fill)
    return _down(im, w, h)


def circle(d_px: float, fill, outline=None, width: float = 0) -> Image.Image:
    n = max(2, int(round(d_px)))
    im = _ss(n, n)
    ImageDraw.Draw(im).ellipse([0, 0, n * SS - 1, n * SS - 1], fill=fill, outline=outline,
                               width=int(round(width * SS)) if outline else 0)
    return _down(im, n, n)


def check_icon(d_px: float) -> Image.Image:
    n = max(4, int(round(d_px)))
    im = _ss(n, n)
    d = ImageDraw.Draw(im)
    s = n * SS
    d.ellipse([0, 0, s - 1, s - 1], fill=THEME["accent"])
    d.line([(s * 0.28, s * 0.52), (s * 0.44, s * 0.67), (s * 0.73, s * 0.36)], fill=THEME["accent_ink"],
           width=max(1, int(s * 0.09)), joint="curve")
    return _down(im, n, n)


def badge(text: str, f, fg, bg, pad_x: float, pad_y: float) -> Image.Image:
    """A pill: rounded background with centered text."""
    t = text_sprite(text, f, fg, lh=1.0)
    w, h = t.width + 2 * pad_x, t.height + 2 * pad_y
    im = rounded(w, h, h / 2, bg)
    im.alpha_composite(t, (int(round(pad_x)), int(round(pad_y))))
    return im


def brand_mark(f, square_px: float, color=None) -> Image.Image:
    sq = rounded(square_px, square_px, square_px * 0.28, THEME["accent"])
    t = text_sprite("Patient Money", f, color or THEME["text"], lh=1.0)
    gap = square_px * 0.6
    h = max(sq.height, t.height)
    im = Image.new("RGBA", (int(sq.width + gap + t.width), h), (0, 0, 0, 0))
    asc, _ = f.getmetrics()
    cap_mid = asc * 0.62  # visual middle of capital letters
    im.alpha_composite(sq, (0, max(0, int(cap_mid - sq.height / 2 + 1))))
    im.alpha_composite(t, (int(sq.width + gap), 0))
    return im


_alpha_cache: dict = {}


def faded(sprite: Image.Image, a: float) -> Image.Image:
    """The sprite with its alpha scaled by a (quantized so repeated values are cached)."""
    if a >= 0.999:
        return sprite
    q = max(1, int(a * 32))
    key = (id(sprite), q)
    hit = _alpha_cache.get(key)
    if hit is not None and hit[0] is sprite:
        return hit[1]
    out = sprite.copy()
    out.putalpha(sprite.getchannel("A").point(lambda v, k=q / 32: int(v * k)))
    if len(_alpha_cache) > 4000:
        _alpha_cache.clear()
    _alpha_cache[key] = (sprite, out)
    return out
