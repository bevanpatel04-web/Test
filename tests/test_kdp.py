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
