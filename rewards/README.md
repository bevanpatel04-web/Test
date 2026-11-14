# Rewards pilot backend

This is the backend for the employer rewards pilot ("Bilt for the first paycheck").

The employer pays a monthly fee per employee and puts money into a reward pool. Young hourly workers who join (members) earn points for:

- staying on the job,
- finishing lessons,
- healthy money habits.

They spend points on a payroll bonus or a gift card. Points are **never** given for trading, number of trades, account balances or investment returns.

The backend keeps the books in one SQLite file. It writes the two JSON files the pilot dashboard reads, exactly as set out in `docs/pilot/data-contract.md`. It uses only the Python standard library and pydantic.

## How to run

From the repo root:

```bash
# 1. Make a demo database (SIMULATED data, see below). It refuses a file that already has data.
python -m rewards seed-demo --db /tmp/demo.db

# 2. Grant tenure milestones reached by a date (run it nightly; running it twice is harmless).
python -m rewards award --as-of 2026-11-14 --db /tmp/demo.db

# 3. See counts and how much of the pool is left.
python -m rewards status --as-of 2026-11-14 --db /tmp/demo.db

# 4. Write employer.json and member.json for the dashboard.
python -m rewards export --employer emp_demo --member m_001 --as-of 2026-11-14 --out /tmp/pilot-data --db /tmp/demo.db
```

Which database it uses: `--db` if given, else the `REWARDS_DB` environment variable, else `rewards/data/pilot.db`. Database files are git-ignored (`rewards/.gitignore`).

Tests: `python -m pytest -q tests/test_rewards.py`. Every test uses its own temporary database.

From Python:

```python
import rewards
conn = rewards.connect("/tmp/demo.db")
rewards.record_lesson(conn, "m_001", "compound-growth", "2026-11-14")
rewards.export_member(conn, "m_001", "2026-11-14")      # or pass a path instead of a connection
```

## Demo data is SIMULATED

`seed-demo` makes up a company called "Demo Diner Group" (`emp_demo`) with 400 eligible employees, 240 of them enrolled on 2026-06-01. It then plays out every day to 2026-11-14: quits, lessons, checklists, savings setups and redemptions. The same seed always gives the same data.

**None of it is real.** The quit rates are assumptions we typed in: 4.5% a month for people who didn't join, 3.5% for members, and higher in the first 90 days. So the gap you see in the retention chart was put there on purpose. It shows what the chart looks like, not that rewards work. The CLI prints a SIMULATED notice whenever it touches a demo database, and the database records `simulated = true`. The export JSON has no spare field for a flag (the contract is exact), so **the dashboard must label demo data as simulated itself.**

Even with real data, members chose to join. People who sign up may be people who were going to stay anyway. A fair test needs a comparison the employer agrees to up front.

## How points work

| rule | what earns it | points |
|---|---|---|
| `tenure_30` / `tenure_90` / `tenure_180` / `tenure_365` | 30 / 90 / 180 / 365 days since hire | 300 / 300 / 600 / 1000 |
| `lesson_completed` | each different lesson, up to 10 | 50 |
| `checklist_completed` | the "before you invest" checklist, once | 200 |
| `savings_setup` | direct deposit to savings, once | 300 |

## Design decisions

**Tenure counts from the day you join.** A milestone pays only if it was reached on or after the member's `enrolled_on` date. Someone hired 200 days ago who joins today gets nothing for 30, 90 or 180 days, and 1000 points at a year. Why: the employer pays for staying from now on, not for time already served, and a pool shouldn't be drained on day one by back pay. A milestone that falls exactly on the joining day does count. The ledger row is dated the day the milestone was reached, so the job gives the same result whenever it runs.

**Only people still employed get tenure points.** `award_tenure` follows the brief and pays enrolled members still employed on the run date. Run it nightly. Someone who quits the day after a milestone, before the job runs, misses it.

**Earning and redeeming need an enrolled, employed member.** That means on or after `enrolled_on` and before `left_on`. `left_on` is the first day someone no longer works there. Cancelling a redemption always refunds, even after someone has left.

**Lessons.** Each lesson pays once. Lessons after the 10th are still recorded, and they count in `lessons_completed` on the dashboard, but they earn nothing.

**Forbidden rules.** Any rule whose name, label or settings mention trading, trades, a balance, a portfolio, returns, profit, gains, stocks, holdings, crypto and similar is refused with `ForbiddenRuleError`. This covers `define_rule()`, `Rule(...)` and `award()`. The check is strict on purpose. If a harmless name trips it ("work_life_balance"), rename the rule. The pilot only awards its seven rules. `define_rule()` is the gate any future rule must pass.

**The ledger is append-only.** Database triggers refuse any UPDATE or DELETE on the ledger, and the code never tries. A correction is a new `adjust` row (`rewards.adjust`), and cancelling a redemption adds a refund row. A balance is the sum of a member's rows, and it can never go below zero. Every row has a unique key (for example `tenure:m_001:tenure_90` or `lesson:m_001:compound-growth`), so retries and re-runs never pay twice.

**Redemptions.**

- Points turn into dollars at the employer's `points_per_usd`, rounded to the cent. With the demo's rate of 100, that's 500 points = $5.00.
- A request is refused if it is under 500 points, more than the member's balance, or more than the pool has left. "Left" means funded minus the dollars of redemptions that are not cancelled.
- The points leave the balance as soon as the request is made. Status then goes from `requested` to `fulfilled` or `cancelled`. Only a `requested` one can be cancelled.
- Passing a `redemption_id` makes a double-tap safe.
- `invest_deposit` exists but is switched off. It raises an error saying it needs a licensed brokerage partner and is not part of the pilot.

**Retention.** Both groups are people employed on the pilot start date: members enrolled by then, and eligible employees who weren't (the comparison group). Each month shows the share of each group still employed on the 1st of that month. The first month is 100.0 for both. Values are rounded to one decimal. People hired after the start are in neither group.

**Exports.** These match the contract's keys and types exactly, and the tests read the contract file to check that. Where the contract left a choice, we went with:

- `eligible` and `enrolled` count everyone on the roster and everyone who has joined, including people who have since left. This is why the demo shows 400 and 240.
- `members` lists everyone who has joined, sorted by id. For people who left, `tenure_days` stops at their leaving date.
- `last_active` is the latest lesson, checklist, savings setup or redemption request. If there is none, it is the joining date. `active_30d` counts members whose `last_active` is in the 30 days ending on `as_of`.
- `points_issued` is earned points plus manual corrections. `points_redeemed` is points in redemptions that are not cancelled. `points_outstanding` is the sum of all balances, so issued minus redeemed equals outstanding.
- `earning_by_rule` always lists all seven rules, including ones at zero. It adds a `manual_adjustment` row only if corrections exist.
- `redemptions` always lists both pilot types, including ones at zero.
- `history` is **oldest first** (by date, then entry order), the same order as the contract example.
- `next_milestones` has the next tenure milestone first. Its `progress_pct` is days on the job ÷ milestone days, so 95 of 180 = 52.8, as in the contract. After it come the rules the member can still earn: lessons (progress = lessons paid ÷ 10), the checklist and savings setup (0.0). The list is empty for someone who has left.
- `catalog` lists only enabled types, with the contract's exact wording.

**Privacy.** We store a `display_name` only. There are no email, phone or name columns. Display names that look like an email address or phone number are refused, and every export is scanned for them before it is returned. Use a pseudonym such as "Member 001".

**Other decisions.** The pilot start date is stored on the employer, because retention needs it. Dates are ISO `YYYY-MM-DD` everywhere.

## Deliberately not built

- **No money movement.** The employer pays payroll bonuses through its own payroll. Gift cards would come from the employer or a vendor. We only record the request and its status.
- **No securities.** There are no deposits into investing accounts, no brokerage link and no investment choices. `invest_deposit` is disabled and waits for a licensed partner after the pilot.
- No logins, web API, HR system import, payroll file, gift card vendor link or notifications.

## Open questions for the team

1. **Gift card delivery.** The contract's note says "Delivered by email", but we store no emails. Who sends the gift card: the employer, or a vendor holding the member's email?
2. **Points after someone leaves.** What happens to their points? Today they stay in the ledger and that person can't redeem them.
3. **Tenure back pay.** Should people who join late get some credit for time already served? Today they don't (see above).
4. **Demo label.** The dashboard needs its own "simulated demo data" label, because the contract has no field for one.
