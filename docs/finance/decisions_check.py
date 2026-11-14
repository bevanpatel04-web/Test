#!/usr/bin/env python3
"""Numbers behind docs/pilot/decisions.md: reward schedules and employer size.

Run it:   python3 docs/finance/decisions_check.py
Uses the team's finance model (docs/finance/model.py) and its base-case inputs unchanged; only the
reward schedule and the number of eligible staff vary. Standard library only.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("model", Path(__file__).with_name("model.py"))
M = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M)

SH = M.INPUTS["shared"]
BASE = M.INPUTS["scenarios"]["base"]
MIN_FEE = 500.0   # the $500/month minimum recommended in pricing.md


def schedule(tenure, lesson, checklist, savings):
    sh = dict(SH)
    sh.update(tenure_milestones=tenure, points_per_lesson=lesson, checklist_points=checklist,
              savings_setup_points=savings)
    return sh


# Month on the job -> points. Mirrors rewards/rules.py SCHEDULES ("standard" and "boosted").
SCHEDULES = {
    "Standard (today)": schedule({1: 300, 3: 300, 6: 600, 12: 1000}, 50, 200, 300),
    "x5, same shape": M.scaled_rules(SH, 5),
    "Front-loaded, $85 max": schedule({1: 1500, 3: 2500, 6: 1500, 12: 1500}, 100, 300, 300),
    "Boosted, $150 max (chosen)": schedule({1: 3000, 3: 4000, 6: 3000, 12: 3000}, 100, 500, 500),
}


def max_dollars(sh):
    ppu = sh["points_per_usd"]
    return (sum(sh["tenure_milestones"].values()) + sh["points_per_lesson"] * sh["max_lessons"]
            + sh["checklist_points"] + sh["savings_setup_points"]) / ppu


def reward_table():
    print("A. REWARD SIZE (base case: 250 eligible staff, 150 members, $4 per member per month)")
    head = ("Schedule", "Max $/yr", "First 90d $", "Avg paid/yr", "Employer yr-1", "Break-even", "Net @10% lift")
    print(f"{head[0]:28}{head[1]:>10}{head[2]:>13}{head[3]:>13}{head[4]:>15}{head[5]:>12}{head[6]:>15}")
    for name, sh in SCHEDULES.items():
        early = (sh["tenure_milestones"][1] + sh["tenure_milestones"][3]) / sh["points_per_usd"]
        ue = M.unit_economics(BASE, sh)
        cost = M.employer_year1(BASE, sh, 0.0)["cost"]
        be = M.break_even_lift(BASE, sh)
        net = M.employer_year1(BASE, sh, 0.10)["net"]
        print(f"{name:28}{max_dollars(sh):>10.0f}{early:>13.0f}{ue['pool_y1_pm']:>13.2f}{cost:>15,.0f}"
              f"{be * 100:>11.1f}%{net:>15,.0f}")
    sh = SCHEDULES["Boosted, $150 max (chosen)"]
    ue = M.unit_economics(BASE, sh)
    print(f"Boosted 90-day pilot: expected rewards ${ue['pool_pilot']:,.0f} for {ue['E']:.0f} members; "
          f"suggested pool (1.5x) ${1.5 * ue['pool_pilot']:,.0f}.")
    hourly = SH["hourly_wage_usd"]
    print(f"$150 is about {150 / hourly:.1f} hours of pay at ${hourly:.2f}/hour; $32 is about {32 / hourly:.1f} hours.")


def size_table():
    sh = dict(SCHEDULES["Boosted, $150 max (chosen)"], min_monthly_fee_usd=MIN_FEE)
    print()
    print(f"B. EMPLOYER SIZE (base case, boosted schedule, $4 per member per month, ${MIN_FEE:,.0f}/month minimum)")
    head = ("Eligible staff", "Members", "Our rev/mo", "Our margin", "Employer b/e", "Employer net@10%",
            "Quits/yr", "Employers for $100K")
    print(f"{head[0]:>15}{head[1]:>9}{head[2]:>12}{head[3]:>12}{head[4]:>14}{head[5]:>18}{head[6]:>10}{head[7]:>21}")
    for eligible in (80, 150, 250, 400, 700, 1200):
        s = dict(BASE, eligible_employees=eligible)
        ue = M.unit_economics(s, sh, min_fee=MIN_FEE)
        be = M.break_even_lift(s, sh)
        net = M.employer_year1(s, sh, 0.10)["net"]
        quits = M.employer_year1(s, sh, 0.0)["base_quits"]
        be_txt = f"{be * 100:.1f}%" if be is not None else "never"
        print(f"{eligible:>15}{ue['E']:>9.0f}{ue['revenue']:>12,.0f}{ue['gross_margin'] * 100:>11.0f}%{be_txt:>14}"
              f"{net:>18,.0f}{quits:>10.0f}{100_000 / ue['revenue']:>21.0f}")


if __name__ == "__main__":
    reward_table()
    size_table()
