"""Top-seller collection: 15 different product types, each matching a category that
was selling on Amazon's best-seller lists on 3 Nov 2026 (see docs/kdp-playbook.md)."""
from __future__ import annotations

from .catalog import Book
from .specs import TRIM_6x9, TRIM_8_5x11

LOGIC = "Books > Humor & Entertainment > Puzzles & Games > Logic & Brain Teasers"
PUZ = "Books > Humor & Entertainment > Puzzles & Games > Puzzles"
WS = "Books > Humor & Entertainment > Puzzles & Games > Word Search"
SUDOKU = "Books > Humor & Entertainment > Puzzles & Games > Sudoku"
MYSTERY = "Books > Mystery, Thriller & Suspense > Mystery"
COLOR = "Books > Crafts, Hobbies & Home > Coloring Books for Grown-Ups"
MANDALA = "Books > Crafts, Hobbies & Home > Coloring Books for Grown-Ups > Mandalas & Patterns"
RELIG_COLOR = "Books > Crafts, Hobbies & Home > Coloring Books for Grown-Ups > Religious & Inspirational"
CHRISTIAN = "Books > Christian Books & Bibles > Christian Living"
AGING = "Books > Self-Help > Aging"
KIDS_ACT = "Books > Children's Books > Activities, Crafts & Games > Activity Books"
KIDS_GAMES = "Books > Children's Books > Activities, Crafts & Games > Games"
KIDS_HUMOR = "Books > Children's Books > Humor"
KIDS_EDU = "Books > Children's Books > Education & Reference"
KIDS_CRAFT = "Books > Children's Books > Activities, Crafts & Games > Crafts & Hobbies"
CAL = "Books > Calendars"
PLANNER = "Books > Self-Help > Time Management"
SERIES = "Porchlight Puzzle Press"


def tbook(**kw) -> Book:
    kw.setdefault("series", SERIES)
    kw.setdefault("season", "top")
    return Book(**kw)


TOP_BOOKS: list[Book] = [
    tbook(
        id="top-murder-mystery-logic", kind="logic", trim=TRIM_8_5x11, seed=7001, volume=1, price=12.99,
        title="Whodunit Logic Puzzles: 60 Murder Mystery Cases",
        subtitle="Solve the Crime With Clues and Logic Grids - Who Did It, With What, and Where? Brain Teasers for Adults and Teens",
        keywords=["murder mystery puzzle book", "logic puzzles for adults", "whodunit puzzles", "detective puzzle book",
                  "logic grid puzzles", "mystery games for adults", "brain teasers for adults"],
        categories=[LOGIC, PUZ, MYSTERY],
        description=["60 murder mysteries to crack with nothing but a pencil and your wits. Each case gives you the "
                     "suspects, the weapons, the places and a handful of clues. Fill in the logic grid to work out who "
                     "did it, with what, and where.",
                     "Cases start with three suspects and build to five. Every case has exactly one solution, checked "
                     "by computer. Full answers are in the back."],
        bullets=["60 original murder mystery cases", "Logic grid on every page", "Easy, medium and hard cases",
                 "One unique solution per case", "Great for fans of detective stories"],
        cover_title="Whodunit Logic Puzzles", cover_strap="60 Murder Mystery Cases to Solve",
        cover_badges=["60 Cases", "Logic Grids", "Solutions"], back_headline="Can you name the killer?",
        colors=("#1B1B2F", "#E43F5A", "#FFFFFF"),
        plan=[{"n": 3, "count": 15}, {"n": 4, "count": 30}, {"n": 5, "count": 15}],
    ),
    tbook(
        id="top-crime-word-search", kind="crimews", trim=TRIM_8_5x11, seed=7002, volume=2, price=9.99,
        title="Crime Scene Word Search: 60 Mystery Cases",
        subtitle="Find the Words, Reveal the Secret Clue, Name the Culprit - Detective Word Find Puzzle Book for Adults and Teens",
        keywords=["murder mystery word search", "detective word search", "crime word find", "mystery puzzle book adults",
                  "word search with hidden message", "whodunit word search", "true crime gifts"],
        categories=[WS, LOGIC, PUZ],
        description=["A word search with a mystery inside. In each of 60 cases, find the suspects, places, weapons and "
                     "clues hidden in the grid. Then read the leftover letters: they spell a secret clue that reveals "
                     "where the culprit was hiding.",
                     "Match the clue to the witness statements and name the culprit. All solutions are in the back."],
        bullets=["60 crime cases", "Hidden-message twist on every puzzle", "Witness statements to solve each case",
                 "Full grid solutions and answers", "A clever gift for mystery lovers"],
        cover_title="Crime Scene Word Search", cover_strap="60 Mystery Cases: Find the Culprit",
        cover_badges=["60 Cases", "Hidden Clues", "Solutions"], back_headline="Every grid hides a secret",
        colors=("#2C3E50", "#F1C40F", "#FFFFFF"),
        plan=[{"count": 60}],
    ),
    tbook(
        id="top-big-book-sudoku", kind="sudoku500", trim=TRIM_8_5x11, seed=7003, volume=3, price=10.99,
        title="The Big Book of Sudoku: 500 Puzzles",
        subtitle="Easy to Expert Sudoku for Adults, Four Puzzles Per Page, With Full Solutions",
        keywords=["big book of sudoku", "500 sudoku puzzles", "sudoku for adults", "easy to expert sudoku",
                  "sudoku puzzle book", "sudoku gift for dad", "brain games adults"],
        categories=[SUDOKU, LOGIC, PUZ],
        description=["500 Sudoku puzzles for hours of brain training: 150 easy, 150 medium, 120 hard and 80 expert.",
                     "Every puzzle has exactly one solution, checked by computer. Clear grids, four per page, with "
                     "all the solutions at the back."],
        bullets=["500 puzzles from easy to expert", "One unique solution each", "Clean, easy-to-read grids",
                 "Full solutions included", "Months of puzzling for one low price"],
        cover_title="The Big Book of Sudoku", cover_strap="500 Puzzles, Easy to Expert",
        cover_badges=["500 Puzzles", "Easy to Expert", "Solutions"], back_headline="Five hundred ways to sharpen your mind",
        colors=("#0B5394", "#FFD966", "#FFFFFF"), large_print=False,
        plan=[{"levels": [("easy", 150), ("medium", 150), ("hard", 120), ("expert", 80)]}],
    ),
    tbook(
        id="top-mandala-pattern-coloring", kind="coloring", trim=TRIM_8_5x11, seed=7004, volume=4, price=9.99,
        title="Bold and Easy Patterns: A Coloring Book for Adults",
        subtitle="50 Simple Mandalas and Geometric Designs With Thick Lines for Relaxation, Stress Relief and Beginners",
        keywords=["bold and easy coloring book", "mandala coloring book adults", "pattern coloring book",
                  "stress relief coloring book", "large print coloring book seniors", "simple coloring book adults",
                  "geometric coloring book"],
        categories=[COLOR, MANDALA, AGING],
        description=["50 relaxing designs with bold, thick lines: mandalas, tiles, stars and flowing patterns that are "
                     "easy to color and satisfying to finish.",
                     "Every design is on its own page with a blank back, so you can use markers without bleed-through."],
        bullets=["50 bold and easy designs", "Thick lines, big spaces", "Single-sided pages",
                 "Great for beginners, seniors and relaxation", "Large 8.5 x 11 pages"],
        cover_title="Bold and Easy Patterns", cover_strap="50 Simple Designs to Color",
        cover_badges=["Bold Lines", "50 Designs", "Single-Sided"], back_headline="Slow down and color",
        colors=("#6C3483", "#F5CBA7", "#FFFFFF"),
        plan=[{"count": 50}],
    ),
    tbook(
        id="top-color-by-number-mosaics", kind="cbn", trim=TRIM_8_5x11, seed=7005, volume=5, price=11.99,
        title="Color by Number Mystery Mosaics",
        subtitle="50 Hidden Pictures and Kaleidoscope Patterns to Reveal - Relaxing Pixel Coloring Book for Adults",
        keywords=["color by number for adults", "mystery mosaics coloring book", "pixel art coloring book",
                  "color by number mystery", "hidden picture coloring adults", "relaxing coloring book",
                  "coloring book for seniors"],
        categories=[COLOR, PUZ, AGING],
        description=["Color each numbered square with its matching color and watch a hidden picture appear. "
                     "50 mystery mosaics: cheerful pictures and dazzling kaleidoscope patterns.",
                     "Each mosaic is on its own page with a blank back. Previews of every finished picture are in the back."],
        bullets=["50 mystery mosaics", "Simple 12-color key", "Pictures and kaleidoscope patterns",
                 "Single-sided pages", "Answer previews included"],
        cover_title="Mystery Mosaics", cover_strap="50 Color by Number Pictures",
        cover_badges=["50 Mosaics", "Color by Number", "Answers"], back_headline="What will you reveal?",
        colors=("#117A65", "#F7DC6F", "#FFFFFF"),
        plan=[{"count": 50}],
    ),
    tbook(
        id="top-bible-verse-coloring", kind="verse", trim=TRIM_8_5x11, seed=7006, volume=6, price=9.99,
        title="Bible Verse Coloring Book for Adults",
        subtitle="42 Inspiring KJV Scriptures in Big Outlined Letters With Patterns to Color - A Christian Devotional Gift",
        keywords=["bible coloring book for adults", "christian coloring book", "scripture coloring book",
                  "bible verse coloring", "psalms coloring book", "christian gifts for women", "devotional coloring book"],
        categories=[RELIG_COLOR, CHRISTIAN, COLOR],
        description=["42 beloved verses from the King James Bible, each written in big outlined letters surrounded by "
                     "patterns and flowers to color.",
                     "Single-sided pages for markers and gel pens. A peaceful way to spend time with Scripture."],
        bullets=["42 KJV verses", "Big outlined lettering to color", "Decorative frames and flowers",
                 "Single-sided pages", "A meaningful gift"],
        cover_title="Bible Verse Coloring Book", cover_strap="42 Scriptures to Color",
        cover_badges=["KJV Verses", "42 Pages", "Single-Sided"], back_headline="Color your way through Scripture",
        colors=("#7D6608", "#FDFEFE", "#FFFFFF"),
        plan=[{"count": 42}],
    ),
    tbook(
        id="top-memory-games-seniors", kind="memory", trim=TRIM_8_5x11, seed=7007, volume=7, price=10.99,
        title="Large Print Memory Games for Seniors",
        subtitle="56 Rounds of Brain Games: Memory Lists, Number Patterns, Sayings, Odd One Out and More - With Answers",
        keywords=["memory games for seniors", "large print brain games", "activities for seniors with dementia",
                  "memory activity book adults", "brain exercises for elderly", "large print puzzle book",
                  "gifts for grandparents"],
        categories=[LOGIC, AGING, PUZ],
        description=["Gentle, large-print brain games designed for older adults: remember-the-list rounds, number "
                     "patterns, missing vowels, finish-the-saying, odd one out, mental math and word scrambles.",
                     "Big type, clear pages and no time pressure. All answers are in the back."],
        bullets=["56 rounds of 7 kinds of games", "Large 16-18 point print", "Memory study-and-recall rounds",
                 "All answers included", "Great for caregivers and activity groups"],
        cover_title="Memory Games for Seniors", cover_strap="Large Print Brain Games",
        cover_badges=["Large Print", "56 Rounds", "Answers"], back_headline="Keep your mind active, one round a day",
        colors=("#1F618D", "#F9E79F", "#FFFFFF"),
        plan=[{"count": 56}],
    ),
    tbook(
        id="top-riddles-for-kids", kind="riddles", trim=TRIM_6x9, seed=7008, volume=8, price=8.99, large_print=False,
        reading_age="7 to 12", ai_text=True,
        title="Riddles for Smart Kids: 110 Brain Teasers",
        subtitle="Tricky Riddles and Funny Puzzles for Kids Ages 7-12 and Families, With Answers on Every Page",
        keywords=["riddles for kids", "brain teasers for kids", "riddle book for smart kids", "riddles for kids 8-12",
                  "funny riddles for kids", "family game night book", "car ride activities for kids"],
        categories=[KIDS_GAMES, KIDS_HUMOR, KIDS_ACT],
        description=["110 riddles to stump your friends and family, from classic head-scratchers to silly puns.",
                     "Answers are printed upside down at the bottom of each page, so no peeking!"],
        bullets=["110 riddles", "Answers on every page, upside down", "Classic and silly riddles",
                 "Great for car trips and family game night", "Ages 7-12"],
        cover_title="Riddles for Smart Kids", cover_strap="110 Tricky Brain Teasers",
        cover_badges=["Ages 7-12", "110 Riddles", "Answers"], back_headline="Can you figure them out?",
        colors=("#2874A6", "#F4D03F", "#FFFFFF"),
    ),
    tbook(
        id="top-knock-knock-jokes", kind="jokes", trim=TRIM_6x9, seed=7009, volume=9, price=6.99, large_print=False,
        reading_age="5 to 10", ai_text=True,
        title="Knock-Knock Jokes for Kids: 120 Silly Jokes",
        subtitle="Laugh-Out-Loud Jokes for Kids Ages 5-10 to Share With Family and Friends",
        keywords=["knock knock jokes for kids", "joke book for kids", "funny jokes for kids", "kids joke book 6-8",
                  "silly jokes for kids", "stocking stuffers for kids", "jokes for kids ages 5-7"],
        categories=[KIDS_HUMOR, KIDS_ACT, KIDS_GAMES],
        description=["120 knock-knock jokes guaranteed to get giggles (and a few groans). Easy to read and perfect for "
                     "sharing at the dinner table, in the car or at school.",
                     "Clean, kid-friendly jokes for ages 5 to 10."],
        bullets=["120 knock-knock jokes", "Easy to read aloud", "Clean and kid-friendly",
                 "Perfect for road trips", "Ages 5-10"],
        cover_title="Knock-Knock Jokes for Kids", cover_strap="120 Silly Jokes",
        cover_badges=["Ages 5-10", "120 Jokes", "Clean Fun"], back_headline="Who's there? Laughter!",
        colors=("#D35400", "#FDFEFE", "#FFFFFF"),
    ),
    tbook(
        id="top-would-you-rather", kind="wyr", trim=TRIM_6x9, seed=7010, volume=10, price=7.99, large_print=False,
        reading_age="7 to 13", ai_text=True,
        title="Would You Rather? Book for Kids: 170 Questions",
        subtitle="Silly, Funny and Thought-Provoking Choices for Kids Ages 7-13 and the Whole Family",
        keywords=["would you rather book for kids", "would you rather questions", "family game book",
                  "road trip games for kids", "funny questions for kids", "kids conversation starters",
                  "stocking stuffers for kids 8-12"],
        categories=[KIDS_GAMES, KIDS_HUMOR, KIDS_ACT],
        description=["170 hilarious and imaginative would-you-rather questions. Would you rather have a pet dragon or "
                     "a pet unicorn? Explore space or the deep ocean?",
                     "Tick your choice and explain why. Great for car rides, sleepovers and family dinners."],
        bullets=["170 questions", "Check boxes to pick your answer", "Silly and thoughtful choices",
                 "Great for groups and road trips", "Ages 7-13"],
        cover_title="Would You Rather?", cover_strap="170 Questions for Kids and Families",
        cover_badges=["Ages 7-13", "170 Questions", "Family Fun"], back_headline="You have to choose!",
        colors=("#8E44AD", "#F7DC6F", "#FFFFFF"),
    ),
    tbook(
        id="top-pencil-control", kind="trace", trim=TRIM_8_5x11, seed=7011, volume=11, price=8.99, large_print=False,
        reading_age="3 to 5",
        title="My First Pencil Control Workbook: Tracing Lines and Shapes",
        subtitle="44 Preschool Pages of Straight Lines, Zigzags, Waves, Loops, Spirals and Shapes - Ages 3-5",
        keywords=["pencil control workbook", "tracing lines for toddlers", "preschool workbook ages 3-5",
                  "pre writing practice", "line tracing book", "fine motor skills activities", "pre k workbook"],
        categories=[KIDS_EDU, KIDS_ACT, KIDS_GAMES],
        description=["The first step before writing letters: big, friendly dashed lines to trace, starting from a dot. "
                     "Pages build from straight lines to zigzags, waves, loops, spirals and shapes.",
                     "Builds the pencil control and hand strength little ones need for handwriting."],
        bullets=["44 tracing pages", "Big dashed lines with start dots", "Progresses from easy to harder",
                 "Builds fine motor skills", "Ages 3-5"],
        cover_title="My First Pencil Control", cover_strap="Tracing Lines and Shapes, Ages 3-5",
        cover_badges=["Ages 3-5", "44 Pages", "Pre-Writing"], back_headline="Ready, set, trace!",
        colors=("#16A085", "#FDFEFE", "#FFFFFF"),
        plan=[{"reps": 3}],
    ),
    tbook(
        id="top-scissor-skills", kind="cut", trim=TRIM_8_5x11, seed=7012, volume=12, price=8.99, large_print=False,
        reading_age="3 to 5",
        title="Scissor Skills Activity Book for Preschool",
        subtitle="28 Cutting Practice Pages: Lines, Zigzags, Waves, Spirals and Shapes - Ages 3-5",
        keywords=["scissor skills preschool", "cutting practice for kids", "scissor practice workbook",
                  "preschool activity book", "fine motor skills toddlers", "cutting activity book ages 3-5",
                  "kindergarten prep workbook"],
        categories=[KIDS_CRAFT, KIDS_ACT, KIDS_EDU],
        description=["28 cutting activities that build confidence with safety scissors, from straight lines to zigzags, "
                     "waves, curves, spirals and shapes.",
                     "Every activity is printed on one side only, so kids can cut freely."],
        bullets=["28 cutting activities", "Thick dashed lines with scissors icons", "Single-sided pages",
                 "Progresses from easy to harder", "Ages 3-5"],
        cover_title="Scissor Skills", cover_strap="Cutting Practice for Ages 3-5",
        cover_badges=["Ages 3-5", "28 Activities", "Single-Sided"], back_headline="Snip, snip, hooray!",
        colors=("#E74C3C", "#FDFEFE", "#FFFFFF"),
    ),
    tbook(
        id="top-2027-weekly-planner", kind="planner", trim=TRIM_8_5x11, seed=7013, volume=13, price=12.99,
        large_print=False, low_content=True,
        title="2027 Weekly Planner",
        subtitle="Dated Weekly and Monthly Organizer, January to December 2027 - Holidays, Goals and Notes",
        keywords=["2027 planner weekly and monthly", "2027 weekly planner", "2027 calendar planner",
                  "dated planner 2027", "2027 agenda", "2027 organizer", "planner 8.5 x 11 2027"],
        categories=[CAL, PLANNER, "Books > Calendars > Inspirational"],
        description=["Plan your whole year: 2027 and 2028 at a glance, a monthly calendar for every month with US "
                     "holidays marked, and a two-page weekly spread for all 53 weeks.",
                     "Plus pages for goals, birthdays and notes. Big 8.5 x 11 pages with plenty of room to write."],
        bullets=["Dated January to December 2027", "Monthly calendars and weekly spreads", "US holidays marked",
                 "Goals, birthdays and notes pages", "Large 8.5 x 11 size"],
        cover_title="2027 Weekly Planner", cover_strap="Weekly and Monthly, January to December",
        cover_badges=["Dated 2027", "Weekly", "Monthly"], back_headline="Make 2027 your best year",
        colors=("#212F3D", "#D4AC0D", "#FFFFFF"),
        plan=[{"year": 2027}],
    ),
    tbook(
        id="top-silly-fill-in-stories", kind="stories", trim=TRIM_6x9, seed=7014, volume=14, price=7.99,
        large_print=False, reading_age="7 to 12", ai_text=True,
        title="Silly Fill-In Stories for Kids",
        subtitle="20 Funny Word Game Stories: Ask for Nouns, Verbs and Silly Words, Then Read Them Out Loud - Ages 7-12",
        keywords=["fill in the blank stories for kids", "word game book for kids", "funny stories for kids",
                  "road trip activities for kids", "parts of speech games", "family game night kids",
                  "stocking stuffer for kids 8-12"],
        categories=[KIDS_GAMES, KIDS_HUMOR, KIDS_ACT],
        description=["20 silly stories with the words missing. Ask a friend for a noun, a verb, a silly word or an "
                     "animal, write them in, then read the story out loud and laugh.",
                     "A fun way to practice parts of speech. Great for road trips, classrooms and sleepovers."],
        bullets=["20 fill-in-the-blank stories", "Word list page before each story", "Parts-of-speech help",
                 "Hilarious read-aloud fun", "Ages 7-12"],
        cover_title="Silly Fill-In Stories", cover_strap="20 Funny Word Game Stories",
        cover_badges=["Ages 7-12", "20 Stories", "Word Game"], back_headline="You write it, then you laugh",
        colors=("#F39C12", "#FDFEFE", "#FFFFFF"),
    ),
    tbook(
        id="top-brain-games-adults", kind="compose", trim=TRIM_8_5x11, seed=7015, volume=15, price=9.99,
        title="Brain Games for Adults: 100 Large Print Puzzles",
        subtitle="Word Search, Sudoku, Mazes, Word Scrambles and Cryptograms - A Variety Activity Book for Seniors",
        keywords=["brain games for adults", "activity book for adults", "large print puzzle book variety",
                  "puzzle books for seniors", "variety puzzle book", "brain teasers for seniors", "gifts for elderly"],
        categories=[PUZ, LOGIC, AGING],
        description=["Five kinds of puzzles in one large-print book: word searches, Sudoku, mazes, word scrambles and "
                     "cryptograms of classic quotes. They alternate page by page so there's always something new.",
                     "100 puzzles with every solution in the back."],
        bullets=["100 puzzles, 5 types", "Large print", "Variety on every page", "Full solutions", "A great gift"],
        cover_title="Brain Games for Adults", cover_strap="100 Large Print Puzzles",
        cover_badges=["Large Print", "5 Puzzle Types", "Solutions"], back_headline="A little of everything",
        colors=("#943126", "#FAD7A0", "#FFFFFF"), cover_art="ws", interleave=True,
        plan=[{"kind": "ws", "pool": "GENERAL", "count": 25, "words": 15, "size": 15},
              {"kind": "sudoku", "levels": [("easy", 15), ("medium", 10)]},
              {"kind": "scramble", "pool": "GENERAL", "count": 20, "words": 12},
              {"kind": "maze", "count": 15, "start": (14, 18), "end": (22, 28)},
              {"kind": "crypto", "source": "GENERAL", "count": 15, "hints": 3}],
    ),
]
