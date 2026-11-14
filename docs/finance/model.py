#!/usr/bin/env python3
"""Patient Money employer rewards pilot: unit economics, employer ROI and company path.

Run it:   python3 docs/finance/model.py
Needs:    Python 3.8+ and nothing else (standard library only).

Edit the INPUTS dict below. Everything after it is arithmetic.

How each input is labeled:
  SOURCED     a published figure. URL and date are in the comment.
  DERIVED     calculated from sourced figures.
  ASSUMPTION  our own estimate. The spread between the three scenarios is
              our honest range of uncertainty. These are what the pilot must test.

"Member" means an enrolled employee (aged 18-25, hourly). "Per member" is
per enrolled employee. All money is US dollars. 100 points = $1.

Main simplifications (read before trusting the output):
  1. Seats: when an enrolled member leaves, the employer backfills the job
     and the new hire enrolls, so the enrolled count stays flat.
  2. Turnover is a monthly chance of leaving. It is higher in the first
     90 days (new_hire_quit_multiplier), then flat. The model calibrates
     the rates so the average monthly quit rate matches the BLS figure.
  3. Tenure points count only for milestones reached after the program
     starts (no back pay for milestones already passed).
  4. One-time points (lessons, checklist, savings setup) are earned in a
     member's first month in the program, if they stay that month.
  5. Retention "lift" = a relative cut in enrolled members' monthly quit
     rate (a 10% lift turns a 4.1% quit rate into 3.69%). Layoffs and
     firings are not affected.
"""
from __future__ import annotations

# =============================================================================
# INPUTS: edit these
# =============================================================================
INPUTS = {
    "shared": {
        # ---- Earning rules: docs/pilot/data-contract.md (pilot defaults) ----
        "points_per_usd": 100,
        "tenure_milestones": {1: 300, 3: 300, 6: 600, 12: 1000},  # month on the job -> points
        "points_per_lesson": 50,
        "max_lessons": 10,
        "checklist_points": 200,      # once
        "savings_setup_points": 300,  # once

        # ---- Taxes on rewards ----
        # SOURCED: employer Social Security 6.2% + Medicare 1.45% = 7.65%.
        #   https://www.irs.gov/taxtopics/tc751 (checked 2026-11-14)
        # Payroll bonuses are wages. Gift cards are also taxable wages: IRS Pub 15-B
        # (2026) says gift cards "no matter how little, are never excludable as a de
        # minimis benefit." https://www.irs.gov/publications/p15b (checked 2026-11-14)
        "employer_payroll_tax_rate": 0.0765,

        # ---- Pay of a typical worker (used to size replacement cost) ----
        # SOURCED: BLS Current Employment Statistics, food services and drinking
        # places, production and nonsupervisory employees, Sept 2026 (preliminary).
        #   Avg hourly earnings $20.52: https://data.bls.gov/timeseries/CES7072200008
        #   Avg weekly hours 23.8:      https://data.bls.gov/timeseries/CES7072200007
        #   (both pulled 2026-11-14). 20.52 x 23.8 x 52 = about $25,400 a year.
        "hourly_wage_usd": 20.52,
        "weekly_hours": 23.8,

        # ---- Pricing (see pricing.md) ----
        # Monthly minimum per employer. 0 = the draft price with no minimum.
        # Set it to 500 to apply the recommended minimum everywhere in the model.
        "min_monthly_fee_usd": 0.0,
        "min_fee_option_usd": 500.0,     # ASSUMPTION: minimum shown in section 5
        "price_per_location_usd": 75.0,  # ASSUMPTION: per location per month
        "pilot_flat_fee_usd": 1500.0,    # ASSUMPTION: one fee for a 90-day pilot

        # ---- Report settings ----
        "lift_levels": [0.05, 0.10, 0.15, 0.20, 0.30],
        "mrr_targets": [10_000, 50_000, 100_000],
        "months_to_simulate": 72,
        "sensitivity_prices": [2.0, 3.0, 4.0, 5.0, 6.0],
        "sensitivity_enrolled": [50, 100, 150, 250, 400],
        "reward_scales": [1, 2, 5, 10],   # multiples of the data-contract point values
        "measurement_lifts": [0.10, 0.20, 0.30],
    },

    "scenarios": {
        # ---------------------------------------------------------------------
        "conservative": {
            # -- Employer size and enrollment --
            "eligible_employees": 200,      # ASSUMPTION: hourly staff aged 18-25 at one employer
            "locations": 8,                 # ASSUMPTION
            "enrollment_rate": 0.45,        # ASSUMPTION (demo data in data-contract.md uses 60%)
            "price_pepm_usd": 4.00,         # draft price, same in all scenarios (see sensitivity)

            # -- Turnover --
            # SOURCED: BLS JOLTS Table 4, quits rate, Sept 2026 (preliminary), released
            # 2026-11-03: retail trade 3.1%; accommodation and food services 5.0%
            # (719,000 quits), after 4.1% (June), 3.7% (July), 3.6% (Aug).
            # https://www.bls.gov/news.release/archives/jolts_11032026.htm
            "monthly_quit_rate": 0.031,     # retail trade, Sept 2026
            # SOURCED: same release, accommodation and food services total
            # separations 6.2% minus quits 5.0% = 1.2% (layoffs, firings, other).
            "monthly_other_separation_rate": 0.012,
            "new_hire_quit_multiplier": 2.0,  # ASSUMPTION: quits in first 90 days run 2x later months

            # -- Member engagement (one-time points) --
            "active_share": 0.40,               # ASSUMPTION: share of members who do any lesson
            "avg_lessons_per_active": 3,        # ASSUMPTION (cap is 10)
            "checklist_rate_active": 0.35,      # ASSUMPTION
            "savings_setup_rate_active": 0.10,  # ASSUMPTION

            # -- Redemptions --
            "breakage_rate": 0.00,      # ASSUMPTION: share of points never redeemed (0 = all paid out)
            "gift_card_share": 0.50,    # ASSUMPTION: share of redeemed $ taken as gift cards

            # -- Our costs --
            # SOURCED: Finch Starter plan $65 per connection per month, read-only,
            # https://www.tryfinch.com/pricing (checked 2026-11-14). Writing bonuses
            # into payroll needs the Pro plan (price on request), so conservative adds a margin.
            "integration_per_employer_month": 100.0,
            "account_mgmt_hours_per_employer_month": 3.0,  # ASSUMPTION: onboarding, reports, payroll files
            "staff_cost_per_hour": 40.0,                   # ASSUMPTION: loaded cost of our ops/support person
            "support_tickets_per_member_month": 0.10,      # ASSUMPTION
            "minutes_per_ticket": 12,                      # ASSUMPTION
            # DERIVED: Claude pricing (platform.claude.com/docs/en/about-claude/pricing,
            # as of 2026-11-03): Opus 5.5 $4/$20, Sonnet 5.5 $2/$10, Haiku 5.5 $0.10/$0.50
            # per million input/output tokens. Conservative = 10 messages a month on
            # Opus 5.5 at 3,000 input + 500 output tokens each = about $0.22.
            "ai_per_member_month": 0.22,
            "hosting_per_member_month": 0.10,  # ASSUMPTION
            "sms_per_member_month": 6,         # ASSUMPTION: reminders and milestone texts
            # SOURCED: Twilio US SMS $0.0083 per segment + $0.0035-$0.005 carrier fee,
            # https://www.twilio.com/en-us/sms/pricing/us (checked 2026-11-14)
            "sms_cost_each": 0.0125,
            # SOURCED: Tremendous: sending gift cards is free; funding by credit card
            # "may incur a 3% processing fee"; bank funding is free.
            # https://www.tremendous.com/pricing (checked 2026-11-14)
            "gift_card_fee_rate": 0.03,
            "fraud_loss_rate": 0.01,   # ASSUMPTION: share of redemptions lost to fraud, paid by us
            # SOURCED: Stripe ACH Direct Debit 0.8% capped at $5; Stripe Invoicing 0.4%
            # per paid invoice. https://stripe.com/pricing (checked 2026-11-14)
            "payment_pct": 0.008, "payment_cap_usd": 5.0, "invoicing_pct": 0.004,

            # -- Employer ROI --
            # Replacement cost as a share of a year's pay.
            # SOURCED (base): Center for American Progress (Boushey and Glynn, Nov 2012):
            # "The typical cost of turnover for positions earning less than $30,000
            # annually is 16 percent of an employee's annual salary."
            # https://www.americanprogress.org/article/there-are-significant-business-costs-to-replacing-employees/
            "replacement_cost_pct_of_pay": 0.08,  # ASSUMPTION: direct costs only (ads, interviews, training hours)
            "employer_admin_hours_month": 4,      # ASSUMPTION: manager time to run the program
            "employer_manager_cost_per_hour": 30.0,  # ASSUMPTION

            # -- Company path (sales) --
            "sales_cycle_months": 4,      # ASSUMPTION: first meeting to signed pilot
            "pilot_months": 3,            # brief: 90-day pilot
            "pilot_to_paid_rate": 0.40,   # ASSUMPTION
            "monthly_logo_churn": 0.03,   # ASSUMPTION: share of paying employers lost each month
            "founder_pilots_per_month": 1.0,  # ASSUMPTION: new pilots the founder starts each month
            "rep_hire_months": [12, 24],  # ASSUMPTION: month each salesperson starts
            "rep_ramp_months": 5,         # ASSUMPTION: months before a new rep starts pilots
            "rep_pilots_per_month": 2.0,  # ASSUMPTION
            "rep_cost_per_month": 10_000,  # ASSUMPTION: salary + commission + taxes
            "marketing_per_month": 1_500,  # ASSUMPTION: events, ads, travel
        },
        # ---------------------------------------------------------------------
        "base": {
            "eligible_employees": 250,
            "locations": 10,
            "enrollment_rate": 0.60,
            "price_pepm_usd": 4.00,

            # SOURCED: average of June-Sept 2026 accommodation and food services quit
            # rates (4.1, 3.7, 3.6, 5.0) = 4.1%. Same JOLTS release as above.
            # Cross-check: BLS median job tenure for ages 20-24 was 1.5 years in Jan 2026
            # (https://www.bls.gov/news.release/tenure.t01.htm), which implies roughly a
            # 3.8% monthly chance of leaving across all industries.
            "monthly_quit_rate": 0.041,
            "monthly_other_separation_rate": 0.012,
            "new_hire_quit_multiplier": 2.0,

            "active_share": 0.60,
            "avg_lessons_per_active": 4,
            "checklist_rate_active": 0.50,
            "savings_setup_rate_active": 0.20,

            "breakage_rate": 0.10,
            "gift_card_share": 0.40,

            "integration_per_employer_month": 65.0,   # SOURCED: Finch Starter list price
            "account_mgmt_hours_per_employer_month": 2.0,
            "staff_cost_per_hour": 40.0,
            "support_tickets_per_member_month": 0.05,
            "minutes_per_ticket": 10,
            # DERIVED: 4 messages a month on Sonnet 5.5 at 2,000 input + 300 output
            # tokens = $0.028, plus support triage and retries, rounded up.
            "ai_per_member_month": 0.05,
            "hosting_per_member_month": 0.05,
            "sms_per_member_month": 4,
            "sms_cost_each": 0.0125,
            "gift_card_fee_rate": 0.01,   # ASSUMPTION: mostly bank-funded, some card-funded
            "fraud_loss_rate": 0.005,
            "payment_pct": 0.008, "payment_cap_usd": 5.0, "invoicing_pct": 0.004,

            # SOURCED: 16% of pay (CAP, above) x $25,400 = about $4,060.
            "replacement_cost_pct_of_pay": 0.16,
            "employer_admin_hours_month": 2,
            "employer_manager_cost_per_hour": 30.0,

            "sales_cycle_months": 3,
            "pilot_months": 3,
            "pilot_to_paid_rate": 0.60,
            "monthly_logo_churn": 0.02,
            "founder_pilots_per_month": 1.5,
            "rep_hire_months": [9, 15, 21, 27],
            "rep_ramp_months": 4,
            "rep_pilots_per_month": 3.0,
            "rep_cost_per_month": 9_000,
            "marketing_per_month": 2_000,
        },
        # ---------------------------------------------------------------------
        "optimistic": {
            "eligible_employees": 500,
            "locations": 15,
            "enrollment_rate": 0.70,
            "price_pepm_usd": 4.00,

            # SOURCED: accommodation and food services, Sept 2026 (preliminary), 5.0%.
            "monthly_quit_rate": 0.050,
            "monthly_other_separation_rate": 0.012,
            "new_hire_quit_multiplier": 2.0,

            "active_share": 0.75,
            "avg_lessons_per_active": 6,
            "checklist_rate_active": 0.65,
            "savings_setup_rate_active": 0.30,

            "breakage_rate": 0.20,
            "gift_card_share": 0.30,

            "integration_per_employer_month": 30.0,   # ASSUMPTION: volume discount or file upload
            "account_mgmt_hours_per_employer_month": 1.5,
            "staff_cost_per_hour": 40.0,
            "support_tickets_per_member_month": 0.03,
            "minutes_per_ticket": 8,
            # DERIVED: 4 messages a month on Haiku 5.5 is well under $0.01.
            "ai_per_member_month": 0.01,
            "hosting_per_member_month": 0.02,
            "sms_per_member_month": 2,
            "sms_cost_each": 0.0125,
            "gift_card_fee_rate": 0.00,   # SOURCED: Tremendous, bank-funded = free
            "fraud_loss_rate": 0.002,
            "payment_pct": 0.008, "payment_cap_usd": 5.0, "invoicing_pct": 0.004,

            # Roughly matches the widely cited $5,864 per front-line hospitality employee
            # attributed to Tracey and Hinkin, Cornell Center for Hospitality Research
            # (Dec 2006), https://hdl.handle.net/1813/71149. UNVERIFIED in the original
            # report, and in 2006 dollars.
            "replacement_cost_pct_of_pay": 0.23,
            "employer_admin_hours_month": 1,
            "employer_manager_cost_per_hour": 30.0,

            "sales_cycle_months": 2,
            "pilot_months": 3,
            "pilot_to_paid_rate": 0.75,
            "monthly_logo_churn": 0.01,
            "founder_pilots_per_month": 2.0,
            "rep_hire_months": [6, 10, 14, 18, 22],
            "rep_ramp_months": 3,
            "rep_pilots_per_month": 4.0,
            "rep_cost_per_month": 9_000,
            "marketing_per_month": 3_000,
        },
    },
}

# =============================================================================
# CALCULATIONS: no need to edit below this line
# =============================================================================
TENURE_BUCKETS = 14  # tenure months 0..12, and 13 = "more than a year"
SCENARIOS = ("conservative", "base", "optimistic")


def annual_pay(sh):
    return sh["hourly_wage_usd"] * sh["weekly_hours"] * 52


def enrolled(s):
    return s["eligible_employees"] * s["enrollment_rate"]


def monthly_fee(s, sh, price=None, min_fee=None):
    """What one employer pays us per month: price x members, or the minimum."""
    p = s["price_pepm_usd"] if price is None else price
    floor = sh["min_monthly_fee_usd"] if min_fee is None else min_fee
    return max(p * enrolled(s), floor)


def scaled_rules(sh, k):
    """Copy of the shared inputs with every point value multiplied by k."""
    out = dict(sh)
    out["tenure_milestones"] = {m: p * k for m, p in sh["tenure_milestones"].items()}
    for key in ("points_per_lesson", "checklist_points", "savings_setup_points"):
        out[key] = sh[key] * k
    return out


def one_time_points(s, sh):
    """Expected one-time points per member: lessons, checklist, savings setup."""
    lessons = min(s["avg_lessons_per_active"], sh["max_lessons"]) * sh["points_per_lesson"]
    per_active = (lessons
                  + s["checklist_rate_active"] * sh["checklist_points"]
                  + s["savings_setup_rate_active"] * sh["savings_setup_points"])
    return s["active_share"] * per_active


# ---- Turnover ---------------------------------------------------------------
def _hazards(s, quit_scale, lift=0.0):
    """List of (quit chance, other-leave chance) for each tenure month."""
    out = []
    for t in range(TENURE_BUCKETS):
        mult = s["new_hire_quit_multiplier"] if t < 3 else 1.0
        quit = min(0.9, quit_scale * s["monthly_quit_rate"] * mult) * (1.0 - lift)
        out.append((quit, s["monthly_other_separation_rate"]))
    return out


def _steady_state(haz):
    """Share of the workforce at each tenure month when hiring just replaces leavers."""
    pop = [0.0] * TENURE_BUCKETS
    pop[0] = 1.0
    for t in range(TENURE_BUCKETS - 2):
        pop[t + 1] = pop[t] * (1.0 - sum(haz[t]))
    last = TENURE_BUCKETS - 1
    pop[last] = pop[last - 1] * (1.0 - sum(haz[last - 1])) / sum(haz[last])
    total = sum(pop)
    return [p / total for p in pop]


def _calibrated_scale(s):
    """Scale quit chances so the workforce-wide average equals monthly_quit_rate."""
    target = s["monthly_quit_rate"]
    lo, hi = 0.05, 5.0
    for _ in range(80):
        mid = (lo + hi) / 2
        haz = _hazards(s, mid)
        dist = _steady_state(haz)
        avg_quit = sum(d * h[0] for d, h in zip(dist, haz))
        if avg_quit > target:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def simulate(s, sh, months, lift=0.0):
    """Month-by-month points and quits for one employer's enrolled seats."""
    scale = _calibrated_scale(s)
    start = _steady_state(_hazards(s, scale))          # workforce before the program
    haz = _hazards(s, scale, lift)                     # behavior once the program runs
    seats = enrolled(s)
    pop = [p * seats for p in start]
    one_time = one_time_points(s, sh)
    milestones = sh["tenure_milestones"]
    rows = []
    for month in range(1, months + 1):
        nxt = [0.0] * TENURE_BUCKETS
        tenure_pts = once_pts = quits = leavers = 0.0
        for t, n in enumerate(pop):
            q, o = haz[t]
            stay = n * (1.0 - q - o)
            quits += n * q
            leavers += n * (q + o)
            new_t = min(t + 1, TENURE_BUCKETS - 1)
            if (t + 1) in milestones and t + 1 < TENURE_BUCKETS - 1:
                tenure_pts += stay * milestones[t + 1]
            if t == 0 or month == 1:      # first month in the program
                once_pts += stay * one_time
            nxt[new_t] += stay
        nxt[0] += leavers                 # backfilled seat, new hire enrolls
        pop = nxt
        rows.append({"tenure": tenure_pts, "once": once_pts, "quits": quits})
    return rows


def _sum(rows, a, b, key=None):
    sel = rows[a - 1:b]
    if key:
        return sum(r[key] for r in sel)
    return sum(r["tenure"] + r["once"] for r in sel)


# ---- Per-employer unit economics ----------------------------------------------
def unit_economics(s, sh, price=None, seats=None, min_fee=None):
    s = dict(s)
    if price is not None:
        s["price_pepm_usd"] = price
    if seats is not None:
        s["eligible_employees"] = seats / s["enrollment_rate"]
    E = enrolled(s)
    p = s["price_pepm_usd"]
    rows = simulate(s, sh, 24)
    ppu = sh["points_per_usd"]
    pts_pilot = _sum(rows, 1, 3)
    pts_y1 = _sum(rows, 1, 12)
    pts_y2 = _sum(rows, 13, 24)
    redeemed_y1 = pts_y1 / ppu * (1.0 - s["breakage_rate"])
    redeemed_month = redeemed_y1 / 12.0

    revenue = monthly_fee(s, sh, min_fee=min_fee)
    costs = {
        "Payroll/HR data connection": s["integration_per_employer_month"],
        "Account management (our time)": s["account_mgmt_hours_per_employer_month"] * s["staff_cost_per_hour"],
        "Payment processing": min(revenue * s["payment_pct"], s["payment_cap_usd"]) + revenue * s["invoicing_pct"],
        "AI (Claude API)": s["ai_per_member_month"] * E,
        "Hosting": s["hosting_per_member_month"] * E,
        "Text messages": s["sms_per_member_month"] * s["sms_cost_each"] * E,
        "Member support (our time)": s["support_tickets_per_member_month"] * s["minutes_per_ticket"] / 60.0
                                     * s["staff_cost_per_hour"] * E,
        "Gift card fees + fraud": redeemed_month * (s["gift_card_share"] * s["gift_card_fee_rate"]
                                                    + s["fraud_loss_rate"]),
    }
    total_cost = sum(costs.values())
    gp = revenue - total_cost
    return {
        "E": E, "price": p, "revenue": revenue, "costs": costs, "total_cost": total_cost,
        "gross_profit": gp, "gross_margin": gp / revenue if revenue else float("nan"),
        "pts_pilot_pm": pts_pilot / E, "pts_y1_pm": pts_y1 / E, "pts_y2_pm": pts_y2 / E,
        "tenure_y1_pm": _sum(rows, 1, 12, "tenure") / E, "once_y1_pm": _sum(rows, 1, 12, "once") / E,
        "pool_pilot": pts_pilot / ppu, "pool_y1": redeemed_y1, "pool_y1_pm": redeemed_y1 / E,
        "pool_y2_pm": pts_y2 / ppu * (1.0 - s["breakage_rate"]) / E,
    }


def min_enrolled_for_margin(s, sh, target):
    """Smallest enrolled count where gross margin reaches target (None if never)."""
    for seats in range(10, 5001, 5):
        if unit_economics(s, sh, seats=seats)["gross_margin"] >= target:
            return seats
    return None


# ---- Employer ROI -------------------------------------------------------------
def employer_year1(s, sh, lift, price=None):
    base_quits = _sum(simulate(s, sh, 12, 0.0), 1, 12, "quits")
    rows = simulate(s, sh, 12, lift)
    quits = _sum(rows, 1, 12, "quits")
    rewards = _sum(rows, 1, 12) / sh["points_per_usd"] * (1.0 - s["breakage_rate"])
    fee = 12 * monthly_fee(s, sh, price=price)
    tax = rewards * sh["employer_payroll_tax_rate"]
    admin = 12 * s["employer_admin_hours_month"] * s["employer_manager_cost_per_hour"]
    cost = fee + rewards + tax + admin
    repl = s["replacement_cost_pct_of_pay"] * annual_pay(sh)
    avoided = base_quits - quits
    savings = avoided * repl
    return {"fee": fee, "rewards": rewards, "tax": tax, "admin": admin, "cost": cost,
            "base_quits": base_quits, "quits": quits, "avoided": avoided,
            "savings": savings, "net": savings - cost, "repl": repl}


def break_even_lift(s, sh, price=None):
    if employer_year1(s, sh, 0.99, price)["net"] < 0:
        return None
    lo, hi = 0.0, 0.99
    for _ in range(60):
        mid = (lo + hi) / 2
        if employer_year1(s, sh, mid, price)["net"] < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ---- Company path -------------------------------------------------------------
def company_path(s, sh, price=None):
    u = unit_economics(s, sh, price=price)
    mrr_per, gp_per = u["revenue"], u["gross_profit"]
    months = sh["months_to_simulate"]
    pilots = [0.0] * (months + 1)
    paid = won = sm = pilot_fees = 0.0
    out = []
    first_pilot = s["sales_cycle_months"] + 1
    ramp = max(s["rep_ramp_months"], s["sales_cycle_months"])
    for m in range(1, months + 1):
        founder = s["founder_pilots_per_month"] if m >= first_pilot else 0.0
        reps_selling = sum(1 for h in s["rep_hire_months"] if m >= h + ramp)
        reps_paid = sum(1 for h in s["rep_hire_months"] if m >= h)
        pilots[m] = founder + reps_selling * s["rep_pilots_per_month"]
        start = m - s["pilot_months"]
        converts = pilots[start] * s["pilot_to_paid_rate"] if start >= 1 else 0.0
        paid = paid * (1.0 - s["monthly_logo_churn"]) + converts
        won += converts
        sm += reps_paid * s["rep_cost_per_month"] + s["marketing_per_month"]
        pilot_fees += pilots[m] * sh["pilot_flat_fee_usd"]
        out.append({"m": m, "pilots": pilots[m], "paid": paid, "mrr": paid * mrr_per,
                    "won": won, "sm": sm, "pilot_fees": pilot_fees,
                    "cum_pilots": sum(pilots[1:m + 1])})
    rep_cac = s["rep_cost_per_month"] / (s["rep_pilots_per_month"] * s["pilot_to_paid_rate"])
    return {"rows": out, "mrr_per": mrr_per, "gp_per": gp_per, "rep_cac": rep_cac}


def month_reaching(path, target):
    for r in path["rows"]:
        if r["mrr"] >= target:
            return r
    return None


# =============================================================================
# REPORT
# =============================================================================
def money(x, cents=False):
    if x is None:
        return "n/a"
    sign = "-" if x < 0 else ""
    x = abs(x)
    return f"{sign}${x:,.2f}" if cents else f"{sign}${x:,.0f}"


def pct(x, d=0):
    return "n/a" if x is None else f"{x * 100:.{d}f}%"


def num(x, d=0):
    return "n/a" if x is None else f"{x:,.{d}f}"


def payback(cac, gp_per_month):
    if gp_per_month <= 0:
        return "never"
    months = cac / gp_per_month
    return ">120" if months > 120 else f"{months:.1f}"


def members_needed(p0, p1, z_alpha=1.96, z_power=0.84):
    """Members per group to tell quit rate p0 from p1 (two-proportion test)."""
    return (z_alpha + z_power) ** 2 * (p0 * (1 - p0) + p1 * (1 - p1)) / (p0 - p1) ** 2


def table(title, header, rows, widths=None):
    widths = widths or [38] + [14] * (len(header) - 1)
    print(title)
    line = "".join(h.ljust(widths[0]) if i == 0 else h.rjust(widths[i]) for i, h in enumerate(header))
    print(line)
    print("-" * len(line))
    for r in rows:
        if r is None:
            print()
            continue
        print("".join(str(c).ljust(widths[0]) if i == 0 else str(c).rjust(widths[i])
                      for i, c in enumerate(r)))
    print()


def main():
    sh = INPUTS["shared"]
    sc = INPUTS["scenarios"]
    names = ["Conservative", "Base", "Optimistic"]
    U = {k: unit_economics(sc[k], sh) for k in SCENARIOS}
    R0 = {k: employer_year1(sc[k], sh, 0.0) for k in SCENARIOS}
    BE = {k: break_even_lift(sc[k], sh) for k in SCENARIOS}
    P = {k: company_path(sc[k], sh) for k in SCENARIOS}
    cols = lambda f: [f(k) for k in SCENARIOS]  # noqa: E731

    max_y1 = (sum(sh["tenure_milestones"].values()) + sh["max_lessons"] * sh["points_per_lesson"]
              + sh["checklist_points"] + sh["savings_setup_points"])

    print("=" * 80)
    print("PATIENT MONEY: EMPLOYER REWARDS PILOT, FINANCE MODEL")
    print("All money in US dollars. 'Member' = enrolled employee. 100 points = $1.")
    print(f"Most one person can earn in a first year: {max_y1:,} points (${max_y1 / 100:,.0f}).")
    print("=" * 80)
    print()

    # 1. Per employer ---------------------------------------------------------
    rows = [
        ["Eligible employees (18-25, hourly)", *cols(lambda k: num(sc[k]["eligible_employees"]))],
        ["Enrollment rate", *cols(lambda k: pct(sc[k]["enrollment_rate"]))],
        ["Enrolled members", *cols(lambda k: num(U[k]["E"]))],
        ["Our price per member per month", *cols(lambda k: money(U[k]["price"], True))],
        ["Our revenue per month", *cols(lambda k: money(U[k]["revenue"]))],
        None,
        ["REWARD POOL (paid by the employer)", "", "", ""],
        ["Points earned per member, first 90 days", *cols(lambda k: num(U[k]["pts_pilot_pm"]))],
        ["Points earned per member, year 1", *cols(lambda k: num(U[k]["pts_y1_pm"]))],
        ["  of which tenure milestones", *cols(lambda k: num(U[k]["tenure_y1_pm"]))],
        ["  of which lessons/checklist/savings", *cols(lambda k: num(U[k]["once_y1_pm"]))],
        ["Points earned per member, year 2", *cols(lambda k: num(U[k]["pts_y2_pm"]))],
        ["Rewards paid per member, year 1", *cols(lambda k: money(U[k]["pool_y1_pm"], True))],
        ["Rewards paid per member, year 2", *cols(lambda k: money(U[k]["pool_y2_pm"], True))],
        ["Employer reward pool, year 1 total", *cols(lambda k: money(U[k]["pool_y1"]))],
        ["Points earned in 90-day pilot, $ total", *cols(lambda k: money(U[k]["pool_pilot"]))],
        ["Suggested pilot pool budget (1.5x)", *cols(lambda k: money(round(U[k]["pool_pilot"] * 1.5, -2)))],
        None,
        ["OUR COSTS PER MONTH (one employer)", "", "", ""],
    ]
    for label in U["base"]["costs"]:
        rows.append([f"  {label}", *cols(lambda k, l=label: money(U[k]["costs"][l]))])
    rows += [
        ["Total cost per month", *cols(lambda k: money(U[k]["total_cost"]))],
        ["Cost per member per month", *cols(lambda k: money(U[k]["total_cost"] / U[k]["E"], True))],
        ["Gross profit per month", *cols(lambda k: money(U[k]["gross_profit"]))],
        ["GROSS MARGIN", *cols(lambda k: pct(U[k]["gross_margin"]))],
        ["Members needed for 60% margin", *cols(lambda k: num(min_enrolled_for_margin(sc[k], sh, 0.60))
                                                 if min_enrolled_for_margin(sc[k], sh, 0.60) else "never")],
        ["Members needed for 75% margin", *cols(lambda k: num(min_enrolled_for_margin(sc[k], sh, 0.75))
                                                 if min_enrolled_for_margin(sc[k], sh, 0.75) else "never")],
    ]
    table("1. PER EMPLOYER", ["", *names], rows)

    # 2. Employer ROI ---------------------------------------------------------
    rows = [
        ["Replacement cost per hourly worker", *cols(lambda k: money(R0[k]["repl"]))],
        ["  (share of a year's pay)", *cols(lambda k: pct(sc[k]["replacement_cost_pct_of_pay"]))],
        ["Baseline monthly quit rate", *cols(lambda k: pct(sc[k]["monthly_quit_rate"], 1))],
        ["Quits per year among members, no program", *cols(lambda k: num(R0[k]["base_quits"], 1))],
        ["  per 100 members", *cols(lambda k: num(R0[k]["base_quits"] / U[k]["E"] * 100, 1))],
        ["Cost of those quits per year", *cols(lambda k: money(R0[k]["base_quits"] * R0[k]["repl"]))],
        None,
        ["EMPLOYER COST OF THE PROGRAM, YEAR 1", "", "", ""],
        ["  Our fee", *cols(lambda k: money(R0[k]["fee"]))],
        ["  Rewards paid out", *cols(lambda k: money(R0[k]["rewards"]))],
        ["  Employer payroll tax on rewards", *cols(lambda k: money(R0[k]["tax"]))],
        ["  Manager time", *cols(lambda k: money(R0[k]["admin"]))],
        ["  Total", *cols(lambda k: money(R0[k]["cost"]))],
        ["  Total per member per month", *cols(lambda k: money(R0[k]["cost"] / U[k]["E"] / 12, True))],
        None,
        ["BREAK-EVEN RETENTION LIFT", "", "", ""],
        ["  Cut in quits needed (relative)", *cols(lambda k: pct(BE[k], 1))],
        ["  = monthly quit rate falls to", *cols(lambda k: "n/a" if BE[k] is None else
                                                 pct(sc[k]["monthly_quit_rate"] * (1 - BE[k]), 2))],
        ["  = quits avoided per year", *cols(lambda k: "n/a" if BE[k] is None else
                                             num(employer_year1(sc[k], sh, BE[k])["avoided"], 1))],
        ["  = quits avoided per 100 members/yr", *cols(lambda k: "n/a" if BE[k] is None else
                                                      num(employer_year1(sc[k], sh, BE[k])["avoided"]
                                                          / U[k]["E"] * 100, 1))],
    ]
    table("2. EMPLOYER ROI (first 12 months)", ["", *names], rows)

    rows = []
    for lift in sh["lift_levels"]:
        r = {k: employer_year1(sc[k], sh, lift) for k in SCENARIOS}
        rows.append([f"{pct(lift)} fewer quits: quits avoided", *cols(lambda k: num(r[k]["avoided"], 1))])
        rows.append(["   employer net savings", *cols(lambda k: money(r[k]["net"]))])
        rows.append(["   return per $1 spent", *cols(lambda k: f"${r[k]['savings'] / r[k]['cost']:.2f}")])
    table("2b. EMPLOYER NET SAVINGS BY RETENTION LIFT (year 1; negative = employer loses money)",
          ["", *names], rows)

    # 3. Company path ---------------------------------------------------------
    rows = [
        ["Monthly revenue per paying employer", *cols(lambda k: money(P[k]["mrr_per"]))],
        ["Gross profit per paying employer/month", *cols(lambda k: money(P[k]["gp_per"]))],
    ]
    for t in sh["mrr_targets"]:
        rows.append([f"Members needed for {money(t)} MRR", *cols(lambda k, t=t: num(t / sc[k]["price_pepm_usd"]))])
        rows.append([f"Employers needed for {money(t)} MRR", *cols(lambda k, t=t: num(t / P[k]["mrr_per"]))])
    rows += [
        None,
        ["SALES ASSUMPTIONS", "", "", ""],
        ["Sales cycle (first meeting to pilot), months", *cols(lambda k: num(sc[k]["sales_cycle_months"]))],
        ["Pilot length, months", *cols(lambda k: num(sc[k]["pilot_months"]))],
        ["Pilot-to-paid conversion", *cols(lambda k: pct(sc[k]["pilot_to_paid_rate"]))],
        ["Paying employers lost per month", *cols(lambda k: pct(sc[k]["monthly_logo_churn"]))],
        ["Pilots the founder starts per month", *cols(lambda k: num(sc[k]["founder_pilots_per_month"], 1))],
        ["Salespeople hired", *cols(lambda k: f"{len(sc[k]['rep_hire_months'])}")],
        ["  first one starts in month", *cols(lambda k: num(min(sc[k]["rep_hire_months"]))
                                             if sc[k]["rep_hire_months"] else "-")],
        ["Pilots per salesperson per month", *cols(lambda k: num(sc[k]["rep_pilots_per_month"], 1))],
        ["CAC per paying employer (salesperson)", *cols(lambda k: money(P[k]["rep_cac"]))],
        ["CAC payback, months of gross profit", *cols(lambda k: payback(P[k]["rep_cac"], P[k]["gp_per"]))],
        ["Lifetime gross profit per employer", *cols(lambda k: money(P[k]["gp_per"] / sc[k]["monthly_logo_churn"]))],
        ["Lifetime gross profit / CAC", *cols(lambda k: f"{P[k]['gp_per'] / sc[k]['monthly_logo_churn'] / P[k]['rep_cac']:.1f}x")],
        None,
        ["MONTHS TO MILESTONE (month 1 = first sales month)", "", "", ""],
    ]
    horizon = sh["months_to_simulate"]
    for t in sh["mrr_targets"]:
        hit = {k: month_reaching(P[k], t) for k in SCENARIOS}
        rows.append([f"Month reaching {money(t)} MRR", *cols(lambda k: f"month {hit[k]['m']}" if hit[k]
                                                              else f">{horizon}")])
        rows.append(["  paying employers then", *cols(lambda k: num(hit[k]["paid"]) if hit[k] else "-")])
        rows.append(["  pilots started by then", *cols(lambda k: num(hit[k]["cum_pilots"]) if hit[k] else "-")])
        rows.append(["  sales + marketing spent by then", *cols(lambda k: money(hit[k]["sm"]) if hit[k] else "-")])
    rows.append(None)
    rows.append(["MRR AT MONTH", "", "", ""])
    for m in (6, 12, 18, 24, 36, 48, 60, 72):
        if m <= horizon:
            rows.append([f"  month {m}", *cols(lambda k, m=m: money(P[k]["rows"][m - 1]["mrr"]))])
    rows.append(["Pilot fees collected in first 12 months", *cols(lambda k: money(P[k]["rows"][11]["pilot_fees"]))])
    table("3. COMPANY PATH", ["", *names], rows, [46, 13, 13, 13])

    # 4. Sensitivity ------------------------------------------------------------
    b = sc["base"]
    rows = []
    for price in sh["sensitivity_prices"]:
        u = unit_economics(b, sh, price=price)
        be = break_even_lift(b, sh, price=price)
        path = company_path(b, sh, price=price)
        hit = month_reaching(path, 100_000)
        rows.append([money(price, True), pct(u["gross_margin"]), pct(be, 1),
                     num(100_000 / u["revenue"]), f"month {hit['m']}" if hit else f">{horizon}"])
    table("4a. BASE CASE: WHAT IF THE PRICE CHANGES? (assumes sales pace does not change)",
          ["Price/member/mo", "Gross margin", "Break-even lift", "Employers $100K", "Reach $100K"],
          rows, [18, 15, 17, 17, 15])

    rows = []
    for seats in sh["sensitivity_enrolled"]:
        u = unit_economics(b, sh, seats=seats)
        bs = dict(b)
        bs["eligible_employees"] = seats / b["enrollment_rate"]
        cac = company_path(bs, sh)["rep_cac"]
        rows.append([num(seats), money(u["revenue"]), pct(u["gross_margin"]),
                     payback(cac, u["gross_profit"]), num(100_000 / u["revenue"])])
    table("4b. BASE CASE: WHAT IF EMPLOYERS ARE BIGGER OR SMALLER?",
          ["Members/employer", "Revenue/mo", "Gross margin", "CAC payback mo", "Employers $100K"],
          rows, [18, 15, 15, 17, 17])

    rows = []
    for k_scale in sh["reward_scales"]:
        sh_k = scaled_rules(sh, k_scale)
        u = unit_economics(b, sh_k)
        r = employer_year1(b, sh_k, 0.0)
        be = break_even_lift(b, sh_k)
        top = (sum(sh_k["tenure_milestones"].values()) + sh_k["max_lessons"] * sh_k["points_per_lesson"]
               + sh_k["checklist_points"] + sh_k["savings_setup_points"]) / sh["points_per_usd"]
        rows.append([f"{k_scale}x", money(top), money(u["pool_y1_pm"], True), money(r["cost"]), pct(be, 1)])
    table("4c. BASE CASE: WHAT IF REWARDS ARE BIGGER? (1x = data-contract point values)",
          ["Point values", "Max $/person/yr", "Avg paid/member", "Employer cost", "Break-even lift"],
          rows, [14, 17, 17, 16, 17])

    # 5. Pricing options --------------------------------------------------------
    def option_rows(label, revenue_fn):
        rev = {k: revenue_fn(k) for k in SCENARIOS}
        return [[label, *cols(lambda k: money(rev[k]))],
                ["   gross margin", *cols(lambda k: pct((rev[k] - U[k]["total_cost"]) / rev[k]))]]

    mf = sh["min_fee_option_usd"]
    rows = []
    rows += option_rows(f"A. ${sc['base']['price_pepm_usd']:.0f} per member per month",
                        lambda k: sc[k]["price_pepm_usd"] * U[k]["E"])
    rows += option_rows(f"A2. Same, with ${mf:,.0f}/month minimum",
                        lambda k: max(sc[k]["price_pepm_usd"] * U[k]["E"], mf))
    rows += option_rows(f"B. ${sh['price_per_location_usd']:.0f} per location per month",
                        lambda k: sh["price_per_location_usd"] * sc[k]["locations"])
    rows += option_rows(f"C. ${sh['pilot_flat_fee_usd']:,.0f} flat per 90-day pilot (per month)",
                        lambda k: sh["pilot_flat_fee_usd"] / 3.0)
    rows.append(["Locations per employer", *cols(lambda k: num(sc[k]["locations"]))])
    table("5. PRICING OPTIONS: our revenue per employer per month (same costs as section 1)",
          ["", *names], rows, [46, 13, 13, 13])

    # 6. What a pilot can prove ---------------------------------------------------
    rows = []
    q = b["monthly_quit_rate"]
    for months in (3, 12):
        p0 = 1 - (1 - q) ** months
        rows.append([f"Chance a member quits within {months} months", pct(p0, 1), "", ""])
        for lift in sh["measurement_lifts"]:
            rows.append([f"  members per group to detect a {pct(lift)} lift", "",
                         pct(p0 * (1 - lift), 1), num(members_needed(p0, p0 * (1 - lift)))])
    E = U["base"]["E"]
    rows.append(None)
    rows.append([f"One base employer has {num(E)} members; expected quits", "", "", ""])
    rows.append(["  during a 90-day pilot", "", "", num(E * (1 - (1 - q) ** 3), 1)])
    table("6. BASE CASE: HOW MANY MEMBERS A PILOT NEEDS TO PROVE A LIFT "
          "(two groups, 80% power, 5% significance)",
          ["", "No program", "With lift", "Members/group"], rows, [46, 13, 13, 15])

    # Sanity checks -------------------------------------------------------------
    problems = []
    for k in SCENARIOS:
        u = U[k]
        if u["pool_y1"] < 0 or u["pts_y1_pm"] < 0:
            problems.append(f"{k}: negative reward pool")
        if u["pts_y1_pm"] > max_y1:
            problems.append(f"{k}: points per member above the yearly maximum")
        if not -1.0 < u["gross_margin"] < 1.0:
            problems.append(f"{k}: gross margin out of range")
        if R0[k]["avoided"] != 0:
            problems.append(f"{k}: baseline should avoid zero quits")
    print("Sanity checks:", "all passed" if not problems else "; ".join(problems))


if __name__ == "__main__":
    main()
