"""Paths and constants for the video studio. Tests point these at temporary folders."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STUDIO_DIR = REPO / "studio"
SCRIPTS_DIR = STUDIO_DIR / "scripts"          # reviewed scripts, one JSON per lesson slug
OUT_DIR = STUDIO_DIR / "out"                  # scratch output (dry runs, temp audio); git-ignored
CURRICULUM = REPO / "invest" / "data" / "curriculum.json"
SITE_DIR = REPO / "invest" / "site"           # manifest paths are relative to this folder
MEDIA_DIR = SITE_DIR / "media" / "videos"     # lesson videos, captions, posters, manifest
VERTICAL_DIR = SITE_DIR / "media" / "vertical"  # 9:16 cuts for TikTok/Reels
MANIFEST = MEDIA_DIR / "manifest.json"

FONT_DIR = Path(os.environ.get("STUDIO_FONT_DIR", "/usr/share/fonts/opentype/inter"))
FFMPEG = os.environ.get("STUDIO_FFMPEG", "ffmpeg")

AI_LABEL = "Made with AI, reviewed by a person"   # manifest label; the app shows it only once approved
# Burned into the picture, so it must be true before the founder reviews the video too.
VIDEO_AI_LABEL = "Made with AI"
EDU_LABEL = "Education, not advice"

FPS = 24
WPM = 145                    # speaking rate used for timing when there is no voice (target band 130-150)
MIN_SECONDS, MAX_SECONDS = 60, 240   # a lesson video is 2-4 minutes; samples may be as short as 1 minute
