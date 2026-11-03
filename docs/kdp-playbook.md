# Amazon KDP puzzle-book playbook

The `kdp/` folder is a small publishing house: it generates print-ready puzzle books (interior PDF, wrap-around cover PDF and a copy-paste Amazon listing) for **Porchlight Puzzle Press**, a large-print puzzle brand for adults and seniors.

## What is ready now

| Book | Trim | Pages | Price | Est. royalty/sale |
|---|---|---|---|---|
| Large Print Sudoku: 200 Easy Puzzles (vol 1) | 8.5 x 11 | 142 | $9.99 | $2.58 |
| Large Print Sudoku: 200 Medium to Hard (vol 2) | 8.5 x 11 | 142 | $9.99 | $2.58 |
| Travel Sudoku: 150 Puzzles Easy to Hard (vol 3) | 6 x 9 | 196 | $9.99 | $2.64 |
| Large Print Word Search: 80 Themed Puzzles (vol 1) | 8.5 x 11 | 108 | $9.99 | $3.15 |

Files are in `kdp/books/<book-id>/`. Each folder has `listing.md`, which tells you exactly what to type in every KDP box.

Every Sudoku is computer-checked to have exactly one solution, and every word search word appears exactly once. All fonts are embedded (KDP rejects PDFs without embedded fonts).

## Christmas 2026 collection (15 books)

Built from what was on Amazon's Puzzles & Games best-seller lists on 3 Nov 2026: Christmas word searches, themed large-print books for seniors, advent puzzle books, activity books and kids' books. All are in the **Porchlight Christmas Puzzles** series. Each is priced at $9.99 or more, so it earns KDP's 60% royalty.

| # | Book | Pages | Price | Est. royalty |
|---|---|---|---|---|
| 1 | Christmas Word Search for Adults: 50 Large Print Puzzles | 70 | $9.99 | $3.15 |
| 2 | Christmas Advent Puzzle Book: 24 Days of Holiday Puzzles | 124 | $12.99 | $4.68 |
| 3 | Christmas Activity Book for Adults (100 puzzles, 5 types) | 128 | $9.99 | $2.81 |
| 4 | Christmas Activity Book for Kids Ages 6-10 | 130 | $9.99 | $2.78 |
| 5 | Christmas Word Search for Kids Ages 6-10 | 58 | $9.99 | $3.15 |
| 6 | Nostalgic Christmas Word Search for Seniors | 80 | $12.99 | $4.95 |
| 7 | Christmas Sudoku for Adults: 200 Large Print Puzzles | 142 | $9.99 | $2.58 |
| 8 | Pocket Christmas Puzzles (6 x 9 stocking stuffer) | 130 | $9.99 | $3.43 |
| 9 | Christmas Bible Word Search: Large Print | 54 | $9.99 | $3.15 |
| 10 | Christmas Cryptograms: 60 Large Print Puzzles | 64 | $9.99 | $3.15 |
| 11 | Christmas Word Scramble for Adults: 50 Large Print Puzzles | 66 | $9.99 | $3.15 |
| 12 | Christmas Around the World Word Search | 70 | $9.99 | $3.15 |
| 13 | Christmas Mazes for Kids Ages 5-9 | 108 | $9.99 | $3.15 |
| 14 | Christmas Sudoku for Kids Ages 7-12 | 84 | $9.99 | $3.15 |
| 15 | Christmas Mazes for Adults: 60 Large Print Labyrinths | 82 | $9.99 | $3.15 |

Files: `kdp/books/xmas-*/`. Rebuild them all with `python -m kdp build --season christmas --out kdp/books`.

**Timing is everything for these.** Christmas sales fall off sharply after about December 20 (the last shipping days), so every day a book sits unpublished is lost selling time.

- Publish in the order of the table: best sellers first, and the **Advent book (#2) as early as possible**, because buyers want it before December 1.
- KDP can limit how many new titles an account creates per day. Publish a few a day (for example 3 per day over 5 days) rather than all at once.
- Review takes up to 72 hours. Order one proof of the first book while you upload the rest.
- Start Amazon ads as each book goes live and **raise budgets in early December**. Turn them down after about Dec 20 and off on Dec 26.
- After Christmas, leave the books up. They are undated, so they sell again next season and keep their reviews.

## Publish a book (about 15 minutes each)

1. Make a free account at **kdp.amazon.com**. Fill in the tax interview and bank details: you can't get paid without them.
2. Change `PEN_NAME` in `kdp/catalog.py` if you want a different author name, then rebuild (below). The name is printed on the covers.
3. **Create → Paperback**, then follow `listing.md` from top to bottom.
4. Upload the `-interior.pdf` as the manuscript and the `-cover.pdf` as "a cover you already have".
5. In **Launch Previewer**, page through the whole book. Fix anything it flags before you approve.
6. Order an author proof copy (printing cost plus shipping) and check it in your hands before you push marketing.
7. Publish. Review takes up to 72 hours.

## Make more books

```bash
pip install -r requirements.txt
python -m kdp list                          # every book in the catalog
python -m kdp build --all --out kdp/books   # rebuild everything
python -m kdp build wordsearch-vol1         # one book (goes to kdp/out/)
```

To add a volume, copy a `Book(...)` block in `kdp/catalog.py`, then give it a new `id`, `volume` and `seed` (the seed makes the puzzles new). Add word search themes in `kdp/wordsearch.py` → `THEMES`. Good next titles in the same brand:

- Sudoku volumes 4 and up (easy sells best to this audience).
- Seasonal word searches: Christmas, Halloween, Mother's Day and Father's Day gift books. Publish them 6 to 8 weeks before the date.
- Interest-themed word searches (gardening, birds, cats, Bible words, 1960s nostalgia).

A series of related books from one brand sells better than scattered one-off titles: Amazon shows the rest of the series on each page.

## Getting sales

KDP does not market your books. Without traffic, most new puzzle books sell few or no copies. What works:

1. **Amazon Ads (Sponsored Products).** Start each book at about $5/day with a manual exact-match campaign on the 7 listing keywords plus automatic targeting. After 2 weeks, keep keywords that sell, cut those that only spend. This is the main lever: budget for it.
2. **A+ Content and Author Central.** Free. Add comparison charts between your volumes, and claim your author page.
3. **Reviews.** The "Thank You" page in each book asks for one. Never pay for or swap reviews: Amazon bans accounts for it.
4. **Pinterest.** Pins of a sample puzzle page linking to the Amazon listing do well for gift books.

## Honest expectations

- This is not instant or guaranteed income. A typical new KDP author earns little in the first months. Income grows with the number of books, good reviews and steady, profitable ads.
- At $9.99, each sale earns about $2.50 to $3.15. 100 sales a month across the catalog would be roughly $250 to $300 before ad spend.
- Puzzle books are a crowded niche. You win on readability (truly large print), clean design, and a recognizable series. Don't upload many near-identical books quickly: KDP limits how many titles you can create per day and removes "low-quality" or duplicate content.
- KDP asks whether content is AI-generated. These puzzles and layouts are produced by this repo's code. Answer the question truthfully for anything else you add.
- Royalty and printing-cost numbers are estimates from KDP's published formula for Amazon.com (60% royalty at $9.99 and above, 50% below; black ink). KDP's pricing page shows the exact numbers.
