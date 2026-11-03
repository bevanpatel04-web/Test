"""Settings for the AI company. Override any of these with environment variables."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(os.environ.get("COMPANY_ROOT", Path(__file__).resolve().parent.parent))

DATA_DIR = ROOT / "data"
SITE_DIR = ROOT / "site"
OPS_DIR = ROOT / "ops"
STATE_FILE = OPS_DIR / "state.json"
BRIEFS_DIR = OPS_DIR / "briefs"
OUTBOX_DIR = OPS_DIR / "outbox"

MODEL = os.environ.get("COMPANY_MODEL", "claude-opus-5-5")

# Cost guardrail: the CEO agent may schedule at most this many tasks per daily run.
MAX_TASKS_PER_DAY = int(os.environ.get("COMPANY_MAX_TASKS", "4"))

BRAND = os.environ.get("COMPANY_BRAND", "Mildwell")
SITE_URL = os.environ.get("COMPANY_SITE_URL", "https://example.com")

MISSION = (
    f"{BRAND} helps people with eczema and sensitive skin understand their tap water "
    "(hardness, chlorine, chloramine) and choose gentler showers and baths. "
    "Stage 1: free ZIP-code water tool + city pages + email list + affiliate links. "
    "Stage 2: our own tested shower filter with a cartridge refill subscription. "
    "We never claim to treat, cure or prevent eczema. Every water fact needs a source."
)
