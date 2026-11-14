"""SQLite storage. One file per pilot database; the schema is created on first connect.

The ledger is append-only. Database triggers refuse any UPDATE or DELETE on it, so a correction
is always a new row (kind "adjust"), and every balance is the sum of the rows.
"""
from __future__ import annotations

import os
import re
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from typing import Iterator

PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_DB = PACKAGE_DIR / "data" / "pilot.db"
ENV_VAR = "REWARDS_DB"

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS employers (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    plan            TEXT NOT NULL,
    pepm_usd        REAL NOT NULL CHECK (pepm_usd >= 0),
    points_per_usd  INTEGER NOT NULL CHECK (points_per_usd > 0),
    pool_funded_usd REAL NOT NULL CHECK (pool_funded_usd >= 0),
    pilot_start     TEXT NOT NULL
);

-- Everyone on the employer's eligible roster. enrolled_on is NULL for eligible employees who did
-- not join. No emails, phone numbers or real names: display_name only.
CREATE TABLE IF NOT EXISTS members (
    id           TEXT PRIMARY KEY,
    employer_id  TEXT NOT NULL REFERENCES employers(id),
    display_name TEXT NOT NULL,
    hire_date    TEXT NOT NULL,
    enrolled_on  TEXT,
    left_on      TEXT,
    CHECK (enrolled_on IS NULL OR enrolled_on >= hire_date),
    CHECK (left_on IS NULL OR left_on > hire_date)
);
CREATE INDEX IF NOT EXISTS members_by_employer ON members(employer_id);

CREATE TABLE IF NOT EXISTS ledger (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id       TEXT NOT NULL REFERENCES members(id),
    date            TEXT NOT NULL,
    kind            TEXT NOT NULL CHECK (kind IN ('earn', 'redeem', 'adjust')),
    rule            TEXT NOT NULL,
    points          INTEGER NOT NULL CHECK (points <> 0),
    idempotency_key TEXT NOT NULL UNIQUE,
    CHECK ((kind = 'earn' AND points > 0) OR (kind = 'redeem' AND points < 0) OR kind = 'adjust')
);
CREATE INDEX IF NOT EXISTS ledger_by_member ON ledger(member_id, date);

CREATE TRIGGER IF NOT EXISTS ledger_no_update BEFORE UPDATE ON ledger
BEGIN SELECT RAISE(ABORT, 'ledger is append-only: add an adjust entry instead'); END;

CREATE TRIGGER IF NOT EXISTS ledger_no_delete BEFORE DELETE ON ledger
BEGIN SELECT RAISE(ABORT, 'ledger is append-only: add an adjust entry instead'); END;

-- What a member did (lessons, checklist, savings setup), whether or not it earned points.
-- A lesson past the 10-lesson cap is recorded here but earns nothing.
CREATE TABLE IF NOT EXISTS completions (
    member_id TEXT NOT NULL REFERENCES members(id),
    kind      TEXT NOT NULL CHECK (kind IN ('lesson', 'checklist', 'savings_setup')),
    ref       TEXT NOT NULL,
    date      TEXT NOT NULL,
    PRIMARY KEY (member_id, kind, ref)
);

CREATE TABLE IF NOT EXISTS redemptions (
    id           TEXT PRIMARY KEY,
    member_id    TEXT NOT NULL REFERENCES members(id),
    type         TEXT NOT NULL,
    points       INTEGER NOT NULL CHECK (points > 0),
    usd          REAL NOT NULL CHECK (usd >= 0),
    status       TEXT NOT NULL CHECK (status IN ('requested', 'fulfilled', 'cancelled')),
    requested_on TEXT NOT NULL,
    fulfilled_on TEXT,
    cancelled_on TEXT
);
CREATE INDEX IF NOT EXISTS redemptions_by_member ON redemptions(member_id);
"""


def resolve_db_path(path: str | os.PathLike | None = None) -> Path:
    """--db wins, then the REWARDS_DB environment variable, then rewards/data/pilot.db."""
    if path:
        return Path(path)
    env = os.environ.get(ENV_VAR)
    return Path(env) if env else DEFAULT_DB


def connect(path: str | os.PathLike | None = None) -> sqlite3.Connection:
    """Open (and if needed create) a pilot database. Transactions are managed by `transaction()`."""
    p = resolve_db_path(path)
    if str(p) != ":memory:":
        p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(p, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    """All-or-nothing block. Nests safely (savepoints), so one outer block can wrap many calls."""
    conn.execute("SAVEPOINT rewards_tx")
    try:
        yield conn
    except BaseException:
        conn.execute("ROLLBACK TO rewards_tx")
        conn.execute("RELEASE rewards_tx")
        raise
    conn.execute("RELEASE rewards_tx")


@contextmanager
def using(db: sqlite3.Connection | str | os.PathLike | None) -> Iterator[sqlite3.Connection]:
    """Accept either an open connection or a path; close the connection only if we opened it."""
    if isinstance(db, sqlite3.Connection):
        yield db
        return
    conn = connect(db)
    try:
        yield conn
    finally:
        conn.close()


def get_meta(conn: sqlite3.Connection, key: str) -> str | None:
    row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else None


def set_meta(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute("INSERT INTO meta (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                 (key, value))


_ISO = re.compile(r"\d{4}-\d{2}-\d{2}")


def to_date(value: date | str) -> date:
    """A date, or an ISO 'YYYY-MM-DD' string, as a date."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and _ISO.fullmatch(value):
        return date.fromisoformat(value)
    raise ValueError(f"expected a date or 'YYYY-MM-DD' string, got {value!r}")


def opt_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None
