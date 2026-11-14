"""CEO / Orchestrator agent: decides today's work and writes the founder's daily brief."""
from __future__ import annotations

import json
from datetime import date

from .. import config, publish
from ..schemas import DailyBrief, TaskPlan
from company.state import AWAITING, FAILED, QUEUED, State

SYSTEM = f"""You are the CEO agent of {config.BRAND}. {config.MISSION}
You run a small team of AI agents:
- facts: checks one figure in the facts registry against an official source (key = fact key).
- lessons: writes one 2-minute lesson from the curriculum (key = lesson slug). ONLY for unpublished lessons
  listed as ready (every fact they need is verified).
- social: one weekly pack of 2 short vertical videos, 1 Instagram carousel and 1 newsletter (no key).
The founder approves every output before it goes live, and has 2-4 hours a week.
Priorities: 1) verify facts that blocked lessons need, and re-check stale facts; 2) publish ready lessons
(at most 2 a day); 3) one social pack a week, ideally once at least one lesson is live.
Don't create work that duplicates an open or awaiting-approval task. Keep the daily plan small and high-value."""


def open_keys(state: State) -> set[tuple[str, str | None]]:
    return {(t["agent"], t["payload"].get("key")) for t in state.by_status(QUEUED, AWAITING)}


def snapshot(state: State) -> dict:
    facts = publish.load_facts()["facts"]
    verified = {f["key"]: f for f in facts if f.get("verified")}
    lessons = publish.load_lessons()["lessons"]
    unpublished = [x for x in lessons if not x.get("published")]
    social = [t for t in state.data["tasks"] if t["agent"] == "social"][-1:]
    return {
        "today": date.today().isoformat(),
        "unverified_facts": [f["key"] for f in facts if not f.get("verified")],
        "stale_facts": [f["key"] for f in facts if publish.is_stale(f)],
        "lessons_ready": [x["slug"] for x in unpublished if publish.lesson_ready(x, verified)],
        "lessons_blocked": {x["slug"]: [k for k in x["needs_facts"] if k not in verified]
                            for x in unpublished if not publish.lesson_ready(x, verified)},
        "published_lessons": publish.published_slugs(),
        "awaiting_approval": [f"#{t['id']} {t['title']}" for t in state.by_status(AWAITING)],
        "open_tasks": [f"{a}:{k}" for a, k in open_keys(state)],
        "last_social_task": social[0]["created"] if social else None,
        "recent_failures": [f"#{t['id']} {t['title']}: {t['error']}" for t in state.by_status(FAILED)[-5:]],
    }


def plan(state: State, llm, max_tasks: int = config.MAX_TASKS_PER_DAY) -> tuple[TaskPlan, list[dict]]:
    snap = snapshot(state)
    result = llm.structured(
        system=SYSTEM,
        prompt=f"Company status:\n{json.dumps(snap, indent=2)}\n\nPlan at most {max_tasks} tasks for today.",
        schema=TaskPlan,
        effort="medium",
    )
    # Guardrails: the CEO's plan is checked in code before anything runs.
    fact_keys = {f["key"] for f in publish.load_facts()["facts"]}
    taken = open_keys(state)
    created = []
    for t in result.tasks:
        if len(created) >= max_tasks:
            break
        key = t.key if t.agent != "social" else None
        reason = None
        if t.agent == "facts" and key not in fact_keys:
            reason = "unknown fact key"
        elif t.agent == "lessons" and key not in snap["lessons_ready"]:
            reason = "lesson is unknown, already published, or needs unverified facts"
        elif (t.agent, key) in taken:
            reason = "duplicate of open task"
        if reason:
            state.log("plan_rejected", reason=reason, title=t.title)
            continue
        taken.add((t.agent, key))
        created.append(state.add_task(t.agent, t.title, t.instructions, key=key))
    return result, created


def write_brief(state: State, llm, ran: list[dict], plan_reasoning: str) -> str:
    summary = [{"id": t["id"], "agent": t["agent"], "title": t["title"], "status": t["status"], "error": t["error"]}
               for t in ran]
    brief = llm.structured(
        system=SYSTEM + "\nWrite a short daily brief for the founder: plain English, no jargon, under 200 words.",
        prompt=(f"Today's plan reasoning: {plan_reasoning}\nTasks run today: {json.dumps(summary)}\n"
                f"Status: {json.dumps(snapshot(state))}"),
        schema=DailyBrief,
        effort="low",
    )
    today = date.today().isoformat()
    approvals = state.by_status(AWAITING)
    lines = [f"# {config.BRAND} daily brief — {today}", "", f"**{brief.headline}**", ""]
    for heading, items in [("Done today", brief.completed), ("Needs your approval", brief.needs_your_approval),
                           ("Next up", brief.next_up), ("Risks or blockers", brief.risks_or_blockers)]:
        if items:
            lines += [f"## {heading}", *[f"- {i}" for i in items], ""]
    if approvals:
        lines += ["## Approval queue", "Review each item with `python -m invest show <id>`, then approve or reject from "
                  "GitHub → Actions → **Approve investing agent work**, or run `python -m invest approve <id>`.", ""]
        lines += [f"- **#{t['id']}** ({t['agent']}) {t['title']}" for t in approvals] + [""]
    lines += [f"_AI usage today: {llm.input_tokens:,} input / {llm.output_tokens:,} output tokens._", ""]
    config.BRIEFS_DIR.mkdir(parents=True, exist_ok=True)
    path = config.BRIEFS_DIR / f"{today}.md"
    path.write_text("\n".join(lines))
    return str(path)
