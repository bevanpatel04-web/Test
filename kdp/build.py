"""Build one book: interior PDF, full-wrap cover PDF and listing.md."""
from __future__ import annotations

import random
from pathlib import Path

from . import render, specs, sudoku, wordsearch
from .catalog import Book

HOW_TO_SUDOKU = [
    "Fill every empty square with a number from 1 to 9.",
    "Each row must contain the numbers 1 to 9 once each, with no repeats.",
    "Each column must contain the numbers 1 to 9 once each.",
    "Each of the nine 3 x 3 boxes (outlined in bold) must contain the numbers 1 to 9 once each.",
    "Tip: start with the rows, columns or boxes that already have the most numbers. "
    "Pencil in small possible numbers and erase as you go.",
    "Every puzzle in this book has exactly one solution. The answers are in the back; "
    "the numbers you needed to find are shown in grey.",
]

HOW_TO_WORDSEARCH = [
    "Find each word from the list hidden in the grid of letters.",
    "Words can run across, down, diagonally, and even backwards.",
    "Circle or highlight each word as you find it, then tick its box in the list.",
    "Words with two parts, like ICE CREAM, appear in the grid without the space.",
    "Tip: look for unusual letters such as Q, Z, X or J, or for double letters, to spot words quickly.",
    "All solutions are in the back of the book.",
]


def chunks(seq, n):
    return [seq[i:i + n] for i in range(0, len(seq), n)]


def front_matter(book: Book, how_to: list[str]) -> list:
    return [
        render.title_page(book.title.split(":")[0], book.title.split(":", 1)[-1].strip() if ":" in book.title else book.subtitle, book.author),
        render.copyright_page(book.author),
        render.text_page("How to Play", how_to),
        render.blank_page,
    ]


def end_matter(book: Book) -> list:
    return [render.text_page("Thank You!", [
        "We hope you enjoyed these puzzles.",
        "If you did, a short review on Amazon would mean a great deal. "
        "Reviews help other puzzle fans find this book, and they help us make more.",
        f"Look for the other books in the {book.series} series.",
    ])]


def sudoku_pages(book: Book) -> tuple[list, int]:
    rng = random.Random(book.seed)
    items = []
    num = 1
    for level, count in book.sudoku_levels:
        for _ in range(count):
            puzzle, solution = sudoku.make_puzzle(rng, level)
            items.append((num, level, puzzle, solution))
            num += 1
    pages = front_matter(book, HOW_TO_SUDOKU)
    for group in chunks([(n, lv, p) for n, lv, p, _ in items], book.per_page):
        pages.append(render.sudoku_puzzles_page(group, book.per_page))
    if len(pages) % 2:
        pages.append(render.notes_page)
    pages.append(render.section_page("Solutions"))
    pages.append(render.blank_page)
    cols, rows = (2, 3) if book.trim.is_large else (2, 2)
    for group in chunks([(n, p, s) for n, _, p, s in items], cols * rows):
        pages.append(render.sudoku_solutions_page(group, cols, rows))
    pages += end_matter(book)
    return pages, len(items)


def wordsearch_pages(book: Book) -> tuple[list, int]:
    rng = random.Random(book.seed)
    themes = list(wordsearch.THEMES.items())
    rng.shuffle(themes)
    items = []
    k = 0
    while len(items) < book.wordsearch_count:
        title, words = themes[k % len(themes)]
        round_ = k // len(themes)
        name = title if round_ == 0 else f"{title} {round_ + 1}"
        items.append((len(items) + 1, wordsearch.make_puzzle(rng, name, words)))
        k += 1
    pages = front_matter(book, HOW_TO_WORDSEARCH)
    for num, ws in items:
        pages.append(render.wordsearch_page(num, ws))
    if len(pages) % 2:
        pages.append(render.notes_page)
    pages.append(render.section_page("Solutions"))
    pages.append(render.blank_page)
    for group in chunks(items, 4):
        pages.append(render.wordsearch_solutions_page(group))
    pages += end_matter(book)
    return pages, len(items)


def cover_art(book: Book):
    rng = random.Random(book.seed + 7)
    if book.kind == "sudoku":
        puzzle, _ = sudoku.make_puzzle(rng, "medium", tries=1)

        def art(c, x, y, size):
            render.draw_sudoku(c, x, y, size, puzzle)
        return art
    title, words = next(iter(wordsearch.THEMES.items()))
    ws = wordsearch.make_puzzle(rng, title, words, size=10, count=6, dirs=wordsearch.DIRS_EASY)
    ws.placements = ws.placements[:3]  # highlight a few words as a teaser

    def art(c, x, y, size):
        render.draw_wordsearch(c, x + size * 0.04, y + size * 0.04, size * 0.92, ws, solution=True)
    return art


def build(book: Book, out_root: Path) -> dict:
    out = out_root / book.id
    out.mkdir(parents=True, exist_ok=True)
    if book.kind == "sudoku":
        pages, puzzles = sudoku_pages(book)
    elif book.kind == "wordsearch":
        pages, puzzles = wordsearch_pages(book)
    else:
        raise ValueError(book.kind)
    interior = out / f"{book.id}-interior.pdf"
    page_count = render.render_interior(interior, book.trim, pages)
    cover = out / f"{book.id}-cover.pdf"
    cw, ch = render.render_cover(cover, book, page_count, cover_art(book))
    info = {
        "id": book.id,
        "pages": page_count,
        "puzzles": puzzles,
        "interior": interior,
        "cover": cover,
        "cover_size": (cw, ch),
        "spine": specs.spine_width(page_count),
        "printing_cost": specs.printing_cost(book.trim, page_count),
        "royalty": specs.royalty(book.price, book.trim, page_count),
        "min_price": specs.min_price(book.trim, page_count),
    }
    (out / "listing.md").write_text(listing_markdown(book, info))
    return info


def description_html(book: Book) -> str:
    parts = [f"<p>{p}</p>" for p in book.description]
    parts.append("<ul>" + "".join(f"<li>{b}</li>" for b in book.bullets) + "</ul>")
    return "".join(parts)


def listing_markdown(book: Book, info: dict) -> str:
    kw = "\n".join(f"{i}. `{k}`" for i, k in enumerate(book.keywords, 1))
    cats = "\n".join(f"- {c}" for c in book.categories)
    cw, ch = info["cover_size"]
    return f"""# {book.title}

Copy each field below into the matching box on kdp.amazon.com → **Create** → **Paperback**.

## 1. Paperback Details

| Field | Value |
|---|---|
| Language | English |
| Book Title | {book.title.split(':')[0]} |
| Subtitle | {(book.title.split(':', 1)[1].strip() + ' - ') if ':' in book.title else ''}{book.subtitle} |
| Series | {book.series} (volume {book.volume}) |
| Author | {book.author} |
| Primary audience | Not sexually explicit; reading age: leave blank or 18+ |
| Publishing rights | I own the copyright and I hold the necessary publishing rights |
| Large print | {'Yes' if book.large_print else 'No'} |
| Low-content book | No (it has real puzzle content, so it needs an ISBN; take KDP's free one) |

**Description** (paste into the description box; it accepts this HTML):

```html
{description_html(book)}
```

**Keywords** (one per box):

{kw}

**Categories** (search for these in the category picker; pick up to 3):

{cats}

## 2. Paperback Content

| Field | Value |
|---|---|
| ISBN | Get a free KDP ISBN |
| Print options | Black & white interior, white paper |
| Trim size | {book.trim.label} |
| Bleed | No bleed |
| Paperback cover finish | Matte |
| Manuscript | `{info['interior'].name}` |
| Cover | Upload a cover you already have → `{info['cover'].name}` |
| AI-generated content | Answer honestly. The puzzles and layout come from this repo's code, not from an AI image or text generator. If you rewrite text with an AI tool, say so. |

Generated: **{info['pages']} pages**, {info['puzzles']} puzzles. Spine {info['spine']:.3f}\". Cover PDF {cw:.3f}\" x {ch:.3f}\" (includes 0.125\" bleed).

After uploading, open **Launch Previewer** and check every page before you approve.

## 3. Paperback Rights & Pricing

| Field | Value |
|---|---|
| Territories | All territories (worldwide rights) |
| Primary marketplace | Amazon.com |
| List price (USD) | ${book.price:.2f} |
| Printing cost (est.) | ${info['printing_cost']:.2f} |
| Your royalty per sale (est.) | **${info['royalty']:.2f}** |
| Lowest price KDP allows (est.) | ${info['min_price']:.2f} |

Estimates use KDP's Amazon.com black-ink formula. KDP shows the exact figures on this page; trust those.
Expanded Distribution: leave off at this price (the royalty would be near zero).
"""
