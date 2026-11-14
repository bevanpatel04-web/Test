# Pilot decisions: reward size and employer size

*Decided Nov 14, 2026. Numbers come from the team's finance model (base case) and can be rerun with `python3 docs/finance/decisions_check.py`. Change these any time; the engine and docs are built so both are settings, not rewrites.*

## 1. Reward size: the "boosted" schedule, up to $150 a year, front-loaded

| Milestone | Standard (original) | **Boosted (pilots)** |
|---|---|---|
| 30 days on the job | $3 | **$30** |
| 90 days on the job | $3 | **$40** |
| 6 months | $6 | **$30** |
| 1 year | $10 | **$30** |
| Each lesson (up to 10) | $0.50 | **$1** |
| "Before you invest" checklist | $2 | **$5** |
| Direct deposit to savings | $3 | **$5** |
| **Most in a first year** | **$32** | **$150** |

**Why**
- **$32 a year is too small to notice.** It's about 1.6 hours of pay at the average food-service wage ($20.52/hour, BLS). $150 is about 7.3 hours of pay.
- **Front-loaded because that's when people quit.** New hires are the most likely to leave, so $70 of the $130 in tenure rewards comes in the first 90 days. Long-tenure staff, who would probably stay anyway, get less of the budget.
- **Our revenue and margin don't change.** Rewards pass straight from the employer to staff.
- **The employer's bar rises, but stays reachable.** For a base-case employer (250 eligible staff, 150 members), year-1 cost goes from $9,679 to about $17,500. The break-even cut in quits goes from 3.5% to 6.2%, about 4.6 fewer quits a year out of roughly 74.
- **One schedule for every early pilot, not a split test.** Splitting one pilot between two reward levels would halve groups that are already too small to measure. Using the same schedule everywhere lets us pool results across pilots. We revisit it after 3 pilots.

| Schedule (base case) | Max $/yr | First 90 days | Avg paid/member/yr | Employer year-1 cost | Break-even cut in quits |
|---|---|---|---|---|---|
| Standard | $32 | $6 | $10.89 | $9,679 | 3.5% |
| 5x, same shape | $160 | $30 | $54.47 | $16,715 | 6.0% |
| Front-loaded, $85 max | $86 | $40 | $33.72 | $13,365 | 4.8% |
| **Boosted, $150 max** | **$150** | **$70** | **$59.28** | **$17,492** | **6.2%** |

**Pilot budget:** for 150 members over 90 days, expect about $2,900 in rewards. Ask the employer to fund about $4,400 (1.5x) so the pool doesn't run dry.

**In the product:** `rewards/rules.py` has `SCHEDULES` (`standard`, `boosted`). Set one per employer with `create_employer(..., reward_schedule="boosted")` or `python -m rewards set-schedule --employer ID --schedule boosted`. The demo dashboard now runs the boosted schedule, so sales demos show what we'd sell.

## 2. Employer size: 250+ eligible hourly staff across 4+ locations

| Eligible staff | Members (60%) | Our revenue/mo | Our margin | Employer break-even | Employer net at 10% fewer quits | Employers for $100K/mo |
|---|---|---|---|---|---|---|
| 80 | 48 | $500 (minimum) | 65% | 10.9% | **-$819** (loses money) | 200 |
| 150 | 90 | $500 (minimum) | 60% | 7.4% | $4,345 | 200 |
| **250** | **150** | **$600** | **61%** | **6.2%** | **$10,522** | **167** |
| 400 | 240 | $960 | 71% | 6.1% | $17,267 | 104 |
| 700 | 420 | $1,680 | 77% | 6.1% | $30,758 | 60 |
| 1,200 | 720 | $2,880 | 81% | 6.0% | $53,242 | 35 |

*(Boosted schedule, $4 per member per month, $500 monthly minimum.)*

**Why**
- **Below about 250 staff, someone loses.** Either our margin falls, or the $500 minimum makes the program too expensive per person for the employer to come out ahead.
- **4+ locations makes a fair test possible.** The program starts at about half the locations, and the rest start after day 90. Comparing the two halves avoids the "steady people sign up" bias of comparing joiners with non-joiners.
- **Bigger employers mean fewer sales to reach the goal.** 104 employers for $100K a month at 400 staff, versus 167 at 250. They also produce more quits to measure.
- **Sweet spot: 400 to 1,200 hourly staff across 5 to 30 locations.** That means multi-unit restaurant franchisees, regional restaurant groups and hotel management companies, where an owner or COO can say yes.
- **Skip for now:** single-location businesses, which are too small. Also skip national chains for the first pilots: procurement, security reviews and payroll integration would slow us down. Revisit them once we have results.

**Price stays** at $4 per enrolled member per month, with a $500 monthly minimum (`docs/finance/pricing.md`).

## What changed because of these decisions
- `rewards/`: per-employer reward schedules, a `set-schedule` command, and tests. The demo seed defaults to boosted with a $15,000 pool.
- `invest/site/pilot/data/`: re-exported from the boosted demo.
- `docs/pilot/data-contract.md` and `docs/pilot/BRIEF.md`: schedules table and decisions.
- `docs/marketing/employer-one-pager.md`, `docs/marketing/target-segments.md` and `invest/site/employers.html`: new size, reward amounts, pilot example and the location-based comparison.
- `docs/finance/pricing.md` and `docs/finance/unit-economics.md`: open questions marked decided, and the boosted numbers noted.

## Still open
- Points when someone leaves (pay out vs. expire). This is an attorney question, since some states may treat earned rewards as wages.
- Gift-card delivery without storing emails.
- Credit for tenure served before joining.
- Pilot pricing (free vs. $1,500 flat).
