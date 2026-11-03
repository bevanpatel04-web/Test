"""Shared memory for all agents: a task queue, approvals and an event log, stored as JSON.

A plain JSON file keeps the company's state readable in GitHub and lets the daily
GitHub Actions run commit it back, so memory survives between runs.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import config

QUEUED, DONE, FAILED = "queued", "done", "failed"
AWAITING, APPROVED, REJECTED = "awaiting_approval", "approved", "rejected"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class State:
    def __init__(self, path: Path | None = None):
        self.path = path or config.STATE_FILE
        if self.path.exists():
            self.data = json.loads(self.path.read_text())
        else:
            self.data = {"next_id": 1, "tasks": [], "events": []}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data["events"] = self.data["events"][-500:]
        self.path.write_text(json.dumps(self.data, indent=2) + "\n")

    # --- tasks -------------------------------------------------------------
    def add_task(self, agent: str, title: str, instructions: str, **payload: Any) -> dict:
        task = {
            "id": self.data["next_id"], "agent": agent, "title": title,
            "instructions": instructions, "payload": payload, "status": QUEUED,
            "result": None, "error": None, "created": now(), "updated": now(),
        }
        self.data["next_id"] += 1
        self.data["tasks"].append(task)
        self.log("task_created", task_id=task["id"], agent=agent, title=title)
        return task

    def get(self, task_id: int) -> dict:
        for t in self.data["tasks"]:
            if t["id"] == task_id:
                return t
        raise KeyError(f"No task #{task_id}")

    def update(self, task: dict, **changes: Any) -> None:
        task.update(changes, updated=now())
        self.log("task_updated", task_id=task["id"], status=task["status"])

    def by_status(self, *statuses: str) -> list[dict]:
        return [t for t in self.data["tasks"] if t["status"] in statuses]

    def open_task_keys(self) -> set[tuple[str, str | None]]:
        """(agent, city_slug) pairs that already have unfinished work, to avoid duplicates."""
        return {
            (t["agent"], t["payload"].get("city_slug"))
            for t in self.by_status(QUEUED, AWAITING)
        }

    # --- events ------------------------------------------------------------
    def log(self, kind: str, **fields: Any) -> None:
        self.data["events"].append({"at": now(), "kind": kind, **fields})
