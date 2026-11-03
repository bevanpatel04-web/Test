"""Amazon KDP paperback rules: page sizes, margins, spine, printing cost, royalty.

Figures follow KDP's help pages (Paperback Printing Cost, Print Book Pricing,
Cover Calculator) for black ink on white paper sold on Amazon.com.
KDP changes these from time to time: confirm with the royalty calculator on
the KDP pricing page before you publish.
"""
from __future__ import annotations

from dataclasses import dataclass

INCH = 72.0  # PDF points per inch

BLEED = 0.125            # cover bleed on every outside edge, inches
SPINE_PER_PAGE = 0.002252  # white paper, inches per page
MIN_PAGES = 24
MAX_PAGES = 828
SPINE_TEXT_MIN_PAGES = 100  # KDP allows spine text from 80 pages; 100 keeps it legible
BARCODE_W, BARCODE_H = 2.0, 1.2  # clear area KDP prints the barcode in, inches


@dataclass(frozen=True)
class Trim:
    width: float
    height: float

    @property
    def is_large(self) -> bool:
        # KDP "large trim": wider than 6.12" or taller than 9"
        return self.width > 6.12 or self.height > 9.0

    @property
    def label(self) -> str:
        return f'{self.width:g}" x {self.height:g}"'


TRIM_6x9 = Trim(6.0, 9.0)
TRIM_8_5x11 = Trim(8.5, 11.0)


def gutter_for(pages: int) -> float:
    """Minimum inside margin KDP requires for a page count (no-bleed interior)."""
    if pages <= 150:
        return 0.375
    if pages <= 300:
        return 0.5
    if pages <= 500:
        return 0.625
    if pages <= 700:
        return 0.75
    return 0.875


def spine_width(pages: int) -> float:
    return pages * SPINE_PER_PAGE


def cover_size(trim: Trim, pages: int) -> tuple[float, float]:
    """Full-wrap cover (back + spine + front) including bleed, in inches."""
    w = BLEED + trim.width + spine_width(pages) + trim.width + BLEED
    h = BLEED + trim.height + BLEED
    return w, h


def printing_cost(trim: Trim, pages: int) -> float:
    """Amazon.com printing cost in USD, black ink, white paper."""
    if pages < 110:
        return 2.84 if trim.is_large else 2.30
    per_page = 0.017 if trim.is_large else 0.012
    return round(1.00 + pages * per_page, 2)


def royalty(list_price: float, trim: Trim, pages: int) -> float:
    """Royalty per Amazon.com sale: 60% at $9.99 and up, 50% below, minus printing."""
    rate = 0.60 if list_price >= 9.99 else 0.50
    return round(rate * list_price - printing_cost(trim, pages), 2)


def min_price(trim: Trim, pages: int) -> float:
    """Lowest list price KDP accepts (printing cost / royalty rate), rounded up to cents."""
    import math
    cost = printing_cost(trim, pages)
    p = math.ceil(cost / 0.50 * 100) / 100
    return p
