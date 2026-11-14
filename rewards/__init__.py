"""Employer-paid rewards pilot for young hourly workers ("Bilt for the first paycheck").

Members earn points for staying on the job, finishing lessons and healthy money habits, never
for trading or balances, and redeem them for a payroll bonus or a gift card. See README.md.

    conn = rewards.connect("pilot.db")
    rewards.award_tenure(conn, "2026-11-14")
    rewards.export_employer(conn, "emp_demo", "2026-11-14")
"""
from __future__ import annotations

from .db import DEFAULT_DB, connect, resolve_db_path, transaction
from .engine import (add_member, adjust, award, award_tenure, balance, cancel_redemption, create_employer,
                     enroll, fulfill_redemption, get_redemption, ledger, pool_remaining, record_checklist,
                     record_departure, record_lesson, record_savings_setup, request_redemption, rule_points,
                     set_reward_schedule)
from .errors import (BelowMinimumError, ForbiddenRuleError, InsufficientPointsError, NotEligibleError,
                     NotFoundError, PoolExhaustedError, PrivacyError, RedemptionDisabledError, RedemptionError,
                     RewardsError, UnknownRuleError)
from .reports import export_employer, export_member, retention, status
from .rules import (CATALOG, DEFAULT_SCHEDULE, PILOT_RULES, RECOMMENDED_SCHEDULE, SCHEDULES, Rule, check_rule_allowed,
                    define_rule, max_first_year_points)
from .seed import SIMULATED_NOTICE, seed_demo

__all__ = [
    "DEFAULT_DB", "connect", "resolve_db_path", "transaction",
    "create_employer", "set_reward_schedule", "rule_points", "add_member", "enroll", "record_departure",
    "award_tenure", "record_lesson", "record_checklist", "record_savings_setup", "award", "adjust",
    "balance", "ledger", "request_redemption", "fulfill_redemption", "cancel_redemption", "get_redemption",
    "pool_remaining", "retention", "export_employer", "export_member", "status", "seed_demo",
    "PILOT_RULES", "CATALOG", "Rule", "define_rule", "check_rule_allowed", "SIMULATED_NOTICE",
    "SCHEDULES", "DEFAULT_SCHEDULE", "RECOMMENDED_SCHEDULE", "max_first_year_points",
    "RewardsError", "ForbiddenRuleError", "UnknownRuleError", "NotFoundError", "NotEligibleError",
    "RedemptionError", "BelowMinimumError", "InsufficientPointsError", "PoolExhaustedError",
    "RedemptionDisabledError", "PrivacyError",
]
