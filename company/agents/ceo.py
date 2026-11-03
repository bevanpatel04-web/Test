"""CEO / Orchestrator agent: decides today's work and writes the founder's daily brief."""
from __future__ import annotations

import json
from datetime import date

from .. import config, site
from ..schemas import DailyBrief, TaskPlan
from ..state import AWAITING, FAILED, State

SYSTEM = f"""You are the CEO agent of {config.BRAND}. {config.MISSION}
You run a small team of AI agents:
- water_data: verifies one city's hardness and disinfectant from the utility's own report (needs city_slug).
- content: writes one city water guide (needs city_slug; ONLY for verified cities without a published page).
- marketing: produces a weekly pack of Pinterest pins, short-video scripts and a newsletter (no city_slug).
The founder approves every output before it goes live, and has 2-4 hours a week.
Priorities: 1) accurate, verified data; 2) city guides for verified cities (SEO); 3) one marketing pack per week.
Don't create work that duplicates an open or awaiting-approval task. Keep the daily plan small and high-value."""


def snapshot(state: State) -> dict:
    cities = site.load_cities()["cities"]
    published = set(site.published_slugs())
    week_ago_marketing = [t for t in state.data["tasks"] if t["agent"] == "marketing"][-1:]
    return {
        "today": date.today().isoformat(),
        "unverified_cities": [c["slug"] for c in cities if not c.get("verified")],
        "verified_without_page": [c["slug"] for c in cities if c.get("verified") and c["slug"] not in published],
        "published_pages": sorted(published),
        "awaiting_approval": [f"#{t['id']} {t['title']}" for t in state.by_status(AWAITING)],
        "open_tasks": [f"{a}:{s}" for a, s in state.open_task_keys()],
        "last_marketing_task": week_ago_marketing[0]["created"] if week_ago_marketing else None,
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
    valid = {c["slug"]: c for c in site.load_cities()["cities"]}
    taken = state.open_task_keys()
    created = []
    for t in result.tasks:
        if len(created) >= max_tasks:
            break
        key = (t.agent, t.city_slug)
        if t.agent in ("water_data", "content") and t.city_slug not in valid:
            state.log("plan_rejected", reason="unknown city", title=t.title)
            continue
        if t.agent == "content" and (not valid[t.city_slug].get("verified") or t.city_slug in snap["published_pages"]):
            state.log("plan_rejected", reason="content needs a verified, unpublished city", title=t.title)
            continue
        if key in taken:
            state.log("plan_rejected", reason="duplicate of open task", title=t.title)
            continue
        taken.add(key)
        created.append(state.add_task(t.agent, t.title, t.instructions, city_slug=t.city_slug))
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
    lines = [f"# Daily brief — {today}", "", f"**{brief.headline}**", ""]
    for heading, items in [("Done today", brief.completed), ("Needs your approval", brief.needs_your_approval),
                           ("Next up", brief.next_up), ("Risks or blockers", brief.risks_or_blockers)]:
        if items:
            lines += [f"## {heading}", *[f"- {i}" for i in items], ""]
    if approvals:
        lines += ["## Approval queue", "Approve or reject from GitHub → Actions → **Approve agent work**, "
                  "or run `python -m company approve <id>`.", ""]
        lines += [f"- **#{t['id']}** ({t['agent']}) {t['title']}" for t in approvals] + [""]
    lines += [f"_AI usage today: {llm.input_tokens:,} input / {llm.output_tokens:,} output tokens._", ""]
    config.BRIEFS_DIR.mkdir(parents=True, exist_ok=True)
    path = config.BRIEFS_DIR / f"{today}.md"
    path.write_text("\n".join(lines))
    return str(path)
