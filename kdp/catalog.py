"""The book catalog: every title the factory can build, with its Amazon listing.

Change PEN_NAME to the author/brand name you will publish under. Add a new
volume by copying a Book entry and giving it a new id, volume and seed: the
seed makes the puzzles different and repeatable.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .specs import Trim, TRIM_6x9, TRIM_8_5x11

PEN_NAME = "Porchlight Puzzle Press"


@dataclass
class Book:
    id: str
    kind: str                       # "sudoku" or "wordsearch"
    trim: Trim
    seed: int
    # Amazon listing
    title: str
    subtitle: str
    series: str
    volume: int
    price: float
    keywords: list[str]             # KDP allows 7 keyword boxes
    categories: list[str]           # KDP lets you pick up to 3
    description: list[str]          # paragraphs; bullets go in `bullets`
    bullets: list[str]
    # cover
    cover_title: str
    cover_strap: str
    cover_badges: list[str]
    back_headline: str
    colors: tuple[str, str, str]    # background, accent, text
    # content
    sudoku_levels: list[tuple[str, int]] = field(default_factory=list)  # (level, count)
    per_page: int = 2
    wordsearch_count: int = 0
    large_print: bool = True
    author: str = PEN_NAME
    # mixed-puzzle books (kind="compose"); see kdp/compose.py
    plan: list = field(default_factory=list)
    interleave: bool = False
    advent: bool = False
    cover_art: str = ""
    decor: str = ""                 # "snow" adds snowflakes to the cover
    reading_age: str = ""
    copyright_extra: str = ""
    season: str = ""
    low_content: bool = False      # journals/planners: KDP's low-content option, no ISBN needed
    ai_text: bool = False          # written text was produced with AI: KDP requires disclosure

    @property
    def spine_text(self) -> str:
        return self.cover_title

    @property
    def back_paras(self) -> list[str]:
        return self.description[:2]

    @property
    def back_bullets(self) -> list[str]:
        return self.bullets


SUDOKU_CATEGORIES = [
    "Books > Humor & Entertainment > Puzzles & Games > Sudoku",
    "Books > Humor & Entertainment > Puzzles & Games > Logic & Brain Teasers",
    "Books > Self-Help > Aging",
]

WORDSEARCH_CATEGORIES = [
    "Books > Humor & Entertainment > Puzzles & Games > Word Search",
    "Books > Humor & Entertainment > Puzzles & Games > Puzzles",
    "Books > Self-Help > Aging",
]

BOOKS: list[Book] = [
    Book(
        id="sudoku-easy-vol1",
        kind="sudoku",
        trim=TRIM_8_5x11,
        seed=1101,
        title="Large Print Sudoku for Adults: 200 Easy Puzzles",
        subtitle="Big Easy-to-Read Grids With Full Solutions - Relaxing Brain Games for Seniors and Beginners",
        series="Porchlight Large Print Sudoku",
        volume=1,
        price=9.99,
        keywords=[
            "large print sudoku for seniors",
            "easy sudoku puzzle book for adults",
            "big print sudoku beginners",
            "sudoku books for elderly easy",
            "brain games for seniors large print",
            "relaxing puzzle book gift for grandma",
            "jumbo sudoku with solutions",
        ],
        categories=SUDOKU_CATEGORIES,
        description=[
            "Enjoy 200 easy Sudoku puzzles printed big and clear on large 8.5 x 11 pages, "
            "two generous grids per page so the numbers are easy to read and there is room to write.",
            "Every puzzle has exactly one solution, checked by computer, and the full answers are in the back of the book.",
        ],
        bullets=[
            "200 easy puzzles, perfect for beginners and relaxing play",
            "Large print digits and bold grid lines",
            "One unique solution per puzzle, all answers included",
            "Big 8.5 x 11 inch pages with room for pencil notes",
            "A thoughtful gift for parents, grandparents and puzzle lovers",
        ],
        cover_title="Large Print Sudoku",
        cover_strap="200 Easy Puzzles for Adults",
        cover_badges=["Large Print", "200 Puzzles", "Solutions Included"],
        back_headline="Relax, unwind and keep your mind sharp",
        colors=("#1F3A5F", "#F2B544", "#FFFFFF"),
        sudoku_levels=[("easy", 200)],
        per_page=2,
    ),
    Book(
        id="sudoku-medium-hard-vol2",
        kind="sudoku",
        trim=TRIM_8_5x11,
        seed=2202,
        title="Large Print Sudoku for Adults: 200 Medium to Hard Puzzles",
        subtitle="Big Easy-to-Read Grids With Full Solutions - Challenging Brain Games for Seniors and Puzzle Lovers",
        series="Porchlight Large Print Sudoku",
        volume=2,
        price=9.99,
        keywords=[
            "large print sudoku medium hard",
            "hard sudoku puzzle book for adults",
            "challenging sudoku large print seniors",
            "sudoku book with solutions big grids",
            "brain teasers for adults large print",
            "sudoku gift for dad",
            "intermediate sudoku puzzles",
        ],
        categories=SUDOKU_CATEGORIES,
        description=[
            "Ready for more of a challenge? This book has 100 medium and 100 hard Sudoku puzzles, "
            "printed large on 8.5 x 11 pages, two big grids per page.",
            "Every puzzle has exactly one solution, checked by computer, with all the answers in the back.",
        ],
        bullets=[
            "100 medium puzzles, then 100 hard ones to build your skills",
            "Large print digits and bold grid lines",
            "One unique solution per puzzle, all answers included",
            "Big 8.5 x 11 inch pages with room for pencil notes",
            "Volume 2 of the Porchlight Large Print Sudoku series",
        ],
        cover_title="Large Print Sudoku",
        cover_strap="200 Medium to Hard Puzzles",
        cover_badges=["Large Print", "200 Puzzles", "Solutions Included"],
        back_headline="A real challenge, printed big and clear",
        colors=("#7A1F2B", "#F4D58D", "#FFFFFF"),
        sudoku_levels=[("medium", 100), ("hard", 100)],
        per_page=2,
    ),
    Book(
        id="sudoku-pocket-vol3",
        kind="sudoku",
        trim=TRIM_6x9,
        seed=3303,
        title="Travel Sudoku: 150 Puzzles Easy to Hard",
        subtitle="One Puzzle Per Page, Large Print, With Solutions - A Portable Sudoku Book for Adults",
        series="Porchlight Large Print Sudoku",
        volume=3,
        price=9.99,
        keywords=[
            "travel sudoku book adults",
            "pocket sudoku puzzle book",
            "sudoku one puzzle per page",
            "small sudoku book easy to hard",
            "sudoku for plane trips",
            "stocking stuffer puzzle book adults",
            "portable brain games",
        ],
        categories=SUDOKU_CATEGORIES,
        description=[
            "150 Sudoku puzzles in a handy 6 x 9 size that slips into a bag. One puzzle per page, "
            "so every grid is large and easy to read.",
            "Starts with 50 easy, then 50 medium and 50 hard puzzles. Every puzzle has exactly one solution, with answers in the back.",
        ],
        bullets=[
            "150 puzzles: 50 easy, 50 medium, 50 hard",
            "One large grid per page",
            "Compact 6 x 9 inch size for travel and waiting rooms",
            "All solutions included",
        ],
        cover_title="Travel Sudoku",
        cover_strap="150 Puzzles, Easy to Hard",
        cover_badges=["1 Per Page", "Large Print", "Solutions"],
        back_headline="Puzzles to go",
        colors=("#2E6B4F", "#F7E07E", "#FFFFFF"),
        sudoku_levels=[("easy", 50), ("medium", 50), ("hard", 50)],
        per_page=1,
    ),
    Book(
        id="wordsearch-vol1",
        kind="wordsearch",
        trim=TRIM_8_5x11,
        seed=4404,
        title="Large Print Word Search for Adults: 80 Themed Puzzles",
        subtitle="Big Letters, One Puzzle Per Page, With Solutions - Relaxing Word Find Book for Seniors",
        series="Porchlight Large Print Word Search",
        volume=1,
        price=9.99,
        keywords=[
            "large print word search for adults",
            "word search books for seniors",
            "big print word find puzzle book",
            "themed word search with solutions",
            "word search gift for grandma",
            "relaxing activity book for adults",
            "extra large print word puzzles",
        ],
        categories=WORDSEARCH_CATEGORIES,
        description=[
            "80 cheerful themed word searches, from backyard birds and baking day to national parks and classic cars. "
            "Each puzzle fills its own 8.5 x 11 page with big, bold letters.",
            "Words run in all directions, including backwards and diagonally. Every solution is shown in the back.",
        ],
        bullets=[
            "80 themed puzzles, one per page",
            "Large, bold letters in a 15 x 15 grid",
            "Check-off boxes next to every word",
            "Full solutions included",
            "A relaxing gift for parents and grandparents",
        ],
        cover_title="Large Print Word Search",
        cover_strap="80 Themed Puzzles for Adults",
        cover_badges=["Large Print", "80 Puzzles", "Solutions Included"],
        back_headline="Hours of relaxing word-finding fun",
        colors=("#4B2E83", "#FFC857", "#FFFFFF"),
        wordsearch_count=80,
        per_page=1,
    ),
]


def get(book_id: str) -> Book:
    for b in BOOKS:
        if b.id == book_id:
            return b
    raise KeyError(f"unknown book id {book_id!r}; run `python -m kdp list`")


from .catalog_xmas import XMAS_BOOKS  # noqa: E402

BOOKS += XMAS_BOOKS

from .catalog_top import TOP_BOOKS  # noqa: E402

BOOKS += TOP_BOOKS
