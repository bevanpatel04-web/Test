"""The daily loop: CEO plans -> workers run -> outputs wait for approval -> CEO writes the brief."""
from __future__ import annotations

import traceback

from . import config
from .agents import WORKERS, ceo
from .state import APPROVED, AWAITING, FAILED, QUEUED, REJECTED, State


def run_daily(llm, state: State | None = None, max_tasks: int = config.MAX_TASKS_PER_DAY) -> str:
    state = state or State()
    try:
        plan, _ = ceo.plan(state, llm, max_tasks=max_tasks)
        reasoning = plan.reasoning
    except Exception as exc:  # the brief still goes out if planning fails
        state.log("plan_failed", error=str(exc))
        reasoning = f"Planning failed: {exc}"

    ran = []
    for task in state.by_status(QUEUED)[:max_tasks]:
        worker = WORKERS[task["agent"]]
        try:
            result = worker.run(task, llm)
            state.update(task, status=AWAITING, result=result)
        except Exception as exc:
            state.update(task, status=FAILED, error=str(exc))
            state.log("task_error", task_id=task["id"], trace=traceback.format_exc(limit=3))
        ran.append(task)
        state.save()  # save after each task so a crash loses nothing

    path = ceo.write_brief(state, llm, ran, reasoning)
    state.save()
    return path


def approve(task_id: int, state: State | None = None) -> str:
    state = state or State()
    task = state.get(task_id)
    if task["status"] != AWAITING:
        raise ValueError(f"Task #{task_id} is '{task['status']}', not awaiting approval")
    message = WORKERS[task["agent"]].on_approve(task)
    state.update(task, status=APPROVED)
    state.log("approved", task_id=task_id, message=message)
    state.save()
    return message


def reject(task_id: int, reason: str = "", state: State | None = None) -> str:
    state = state or State()
    task = state.get(task_id)
    if task["status"] != AWAITING:
        raise ValueError(f"Task #{task_id} is '{task['status']}', not awaiting approval")
    state.update(task, status=REJECTED, error=reason or "Rejected by founder")
    state.save()
    return f"Rejected #{task_id}"
