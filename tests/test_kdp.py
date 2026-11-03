import random

import pytest

from kdp import catalog, specs, sudoku, wordsearch


@pytest.mark.parametrize("level", ["easy", "medium", "hard"])
def test_sudoku_unique_and_correct(level):
    rng = random.Random(7)
    for _ in range(3):
        puzzle, solution = sudoku.make_puzzle(rng, level)
        assert sudoku.count_solutions(puzzle) == 1
        assert all(p in (0, s) for p, s in zip(puzzle, solution))
        for unit in range(9):
            assert sorted(solution[unit * 9:(unit + 1) * 9]) == list(range(1, 10))
            assert sorted(solution[unit::9]) == list(range(1, 10))
        assert sudoku.clue_count(puzzle) <= sudoku.LEVELS[level] + 4


def test_wordsearch_words_present_once():
    rng = random.Random(3)
    for title, words in list(wordsearch.THEMES.items())[:5]:
        ws = wordsearch.make_puzzle(rng, title, words)
        assert len(ws.placements) == 15
        for p in ws.placements:
            key = wordsearch._key(p.word)
            assert "".join(ws.grid[r][c] for r, c in p.cells()) == key
            assert wordsearch._occurrences(ws.grid, key) == 1


def test_theme_words_fit_grid():
    for title, words in wordsearch.THEMES.items():
        usable = [w for w in words if 3 <= len(wordsearch._key(w)) <= 15]
        assert len(usable) >= 15, title


def test_kdp_math():
    # KDP's own worked example: 300 pages, regular trim, $9.99 -> $1.39 royalty
    assert specs.printing_cost(specs.TRIM_6x9, 300) == 4.60
    assert specs.royalty(9.99, specs.TRIM_6x9, 300) == 1.39
    w, h = specs.cover_size(specs.TRIM_6x9, 200)
    assert round(w, 3) == round(0.25 + 12 + 200 * 0.002252, 3)
    assert h == 9.25


def test_catalog_listings_valid():
    ids = set()
    for b in catalog.BOOKS:
        assert b.id not in ids
        ids.add(b.id)
        assert len(b.keywords) <= 7
        assert all(len(k) <= 50 for k in b.keywords)
        assert len(b.categories) <= 3
        assert len(b.title) + len(b.subtitle) < 200  # KDP limit


# ---------------------------------------------------------------- Christmas catalog

from kdp import compose, puzzles, xmas_words  # noqa: E402
from kdp.catalog_xmas import XMAS_BOOKS  # noqa: E402


def test_maze_is_perfect_and_solvable():
    m = puzzles.make_maze(random.Random(1), 12, 9)
    assert len(m.open) == 12 * 9 - 1  # spanning tree: one path between any two cells
    path = m.solution()
    assert path[0] == (0, 0) and path[-1] == (11, 8)
    assert all(m.is_open(a, b) for a, b in zip(path, path[1:]))


def test_sudoku6_unique():
    rng = random.Random(2)
    for _ in range(5):
        p, s = puzzles.make_sudoku6(rng, 15)
        assert puzzles._count6(list(p)) == 1
        assert all(v in (0, s[i]) for i, v in enumerate(p))
        for r in range(6):
            assert sorted(s[r * 6:(r + 1) * 6]) == list(range(1, 7))


def test_scramble_and_cryptogram():
    rng = random.Random(3)
    sc = puzzles.make_scramble(rng, "t", xmas_words.XMAS["Snow Day"], count=10)
    for w, s in zip(sc.words, sc.scrambled):
        key = w.replace(" ", "").upper()
        assert sorted(s) == sorted(key) and s != key
    q, src = xmas_words.QUOTES[0]
    cg = puzzles.make_cryptogram(rng, q, src)
    assert all(k != v for k, v in cg.key.items())
    rev = {v: k for k, v in cg.key.items()}
    assert "".join(rev.get(ch, ch) for ch in cg.cipher) == q.upper()


def test_word_lists_fit_their_grids():
    for books in XMAS_BOOKS:
        for spec in books.plan:
            if spec["kind"] == "ws":
                for title, words in compose.POOLS[spec["pool"]].items():
                    fits = [w for w in words if 3 <= len(wordsearch._key(w)) <= spec["size"]]
                    assert len(fits) >= spec["words"], (books.id, title)


def test_christmas_catalog():
    assert len(XMAS_BOOKS) >= 15
    assert len({b.id for b in XMAS_BOOKS}) == len(XMAS_BOOKS)
    for b in XMAS_BOOKS:
        assert len(b.keywords) <= 7 and all(len(k) <= 50 for k in b.keywords)
        assert len(b.title) + len(b.subtitle) < 200
        assert b.price >= 9.99  # keeps the 60% royalty rate


def test_build_compose_book(tmp_path):
    from kdp.build import build
    book = next(b for b in XMAS_BOOKS if b.id == "xmas-word-scramble")
    info = build(book, tmp_path)
    assert info["pages"] % 2 == 0 and info["pages"] >= 24
    assert info["interior"].stat().st_size > 10_000 and info["cover"].stat().st_size > 10_000
