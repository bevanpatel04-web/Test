"""Settings for the investing-education product. Override any of these with environment variables."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(os.environ.get("INVEST_ROOT", Path(__file__).resolve().parent))

DATA_DIR = ROOT / "data"
SITE_DIR = ROOT / "site"
OPS_DIR = ROOT / "ops"
STATE_FILE = OPS_DIR / "state.json"
BRIEFS_DIR = OPS_DIR / "briefs"
OUTBOX_DIR = OPS_DIR / "outbox"

# Cost guardrail: the CEO agent may schedule at most this many tasks per daily run.
MAX_TASKS_PER_DAY = int(os.environ.get("INVEST_MAX_TASKS", "3"))

BRAND = os.environ.get("INVEST_BRAND", "Patient Money")
SITE_URL = os.environ.get("INVEST_SITE_URL", "https://example.com")

MISSION = (
    f"{BRAND} helps 18-25 year olds understand why time matters in investing, and the risks they take on "
    "when they invest. Education only: we never tell anyone what to buy, sell or hold. "
    "Stage 1: free 'start now vs. later' calculator + short lessons + social video + weekly email. "
    "Stage 2: sponsorships and carefully disclosed partnerships. Stage 3: license the lessons and tools "
    "to credit unions, colleges and employers. Every statistic needs an official source."
)

# Facts only count as verified when a source is on one of these official domains (or a subdomain).
PRIMARY_SOURCE_DOMAINS = (
    "irs.gov", "sec.gov", "investor.gov", "finra.org", "federalreserve.gov", "newyorkfed.org",
    "stlouisfed.org", "bls.gov", "bea.gov", "treasury.gov", "treasurydirect.gov", "ssa.gov",
    "consumerfinance.gov", "fdic.gov", "ncua.gov", "dol.gov", "census.gov", "spglobal.com",
)

DISCLAIMER_SHORT = "Education, not financial advice. Investing involves risk, including loss of money."
