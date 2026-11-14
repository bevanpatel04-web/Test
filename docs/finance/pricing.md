# Pricing: options and a recommendation for the first 3 pilots

*Finance and ops, 2026-11-14. Numbers come from `docs/finance/model.py` (sections 1, 4 and 5). Prices below are drafts to test, not final.*

## Recommendation in one paragraph

**Charge for the pilot, but keep the fee small and credit it back if they convert.** Pilot 1 can be a discounted "design partner." Pilots 2 and 3 pay a flat **$1,500 for 90 days**. After the pilot, charge **$4 per enrolled member per month with a $500 monthly minimum**, on a 12-month agreement billed monthly by bank transfer (ACH). The employer always funds the rewards separately, **at cost, with no markup**. We only bill rewards that members actually redeem.

## What each option looks like (from the model)

Revenue and gross margin per employer per month, using the same costs to serve:

| Option | Conservative (90 members) | Base (150 members) | Optimistic (350 members) |
|---|---|---|---|
| A. $4 per member per month | $360, 7% margin | $600, 62% | $1,400, 87% |
| A2. Same, with a $500 minimum | $500, 33% | $600, 62% | $1,400, 87% |
| B. $75 per location per month | $600, 44% | $750, 70% | $1,125, 84% |
| C. $1,500 flat for a 90-day pilot | $500/mo, 33% | $500/mo, 55% | $500/mo, 65% |

## Option A: per enrolled employee per month (PEPM)

The employer pays for each employee who joins, each month. Draft: $4.

**Pros**
- Price tracks value: the employer pays only for people in the program, which is where the retention benefit is.
- Easy to explain and compare ("less than a dollar a week per person").
- Grows with the customer as enrollment grows.
- It matches the data contract (`pepm_usd`), so the dashboard already shows it.

**Cons**
- Revenue swings with enrollment. A small or low-enrollment employer costs us more than they pay (7% margin at 90 members).
- Monthly invoices change, which some finance teams dislike.
- There is an odd incentive: the more employees the employer encourages to join, the more they pay. Some may quietly under-promote it.
- Counting "enrolled" each month needs a clear rule, e.g. anyone enrolled on the 1st of the month.

**Fix for the main con:** add a monthly minimum ($500 in the model). It covers our fixed costs per employer (account management plus the payroll data connection, about $150 to $220 a month).

## Option B: per location per month

The employer pays a flat amount for each restaurant, hotel or store. Draft: $75.

**Pros**
- Predictable for the employer. The bill only changes when they add or close a location.
- Fits how multi-unit operators think and budget, and how franchisees buy software.
- Better for us when enrollment is low (44% margin in the conservative case vs 7%).
- No incentive to hold back enrollment.

**Cons**
- Price doesn't track value. A small location pays the same as a big one.
- Large locations get a bargain. In the optimistic case we earn less than with Option A ($1,125 vs $1,400).
- It needs a definition of "location" (a food court counter? a hotel with two restaurants?).
- It is harder to compare with the retention savings, which are per person.

## Option C: flat pilot fee

One fixed fee for a 90-day pilot. Draft: $1,500.

**Pros**
- Simple. A general manager or regional director can often approve it without a long purchasing process. That is an assumption; check it with the first prospects.
- Tests willingness to pay early. An employer that won't pay $1,500 probably won't pay $7,200 a year.
- Makes the employer name an owner and show up to check-ins.
- Credited toward the paid plan if they convert, so it doesn't feel like a penalty.

**Cons**
- It is not a business model, just a test. It covers costs (55% margin in the base case) but doesn't scale.
- Any fee slows down the very first "yes."
- Large employers may expect a free pilot.

## Should we charge for the pilot at all?

**Yes, a small amount**, for four reasons:

1. **Proof for investors.** "Three employers paid us" is much stronger evidence than "three employers tried it for free." See `fundraising.md`.
2. **Commitment.** Free pilots are easy to ignore. The retention data depends on the employer sending hire and end dates on time and promoting enrollment.
3. **Real price discovery.** We learn which objections are about price and which are about value.
4. **Our costs are real.** Even a pilot costs us about $225 a month in our time, data connection and support (base case).

One exception: **Pilot 1 can be discounted (for example $500) or free** if the employer is a well-known name and agrees in writing to give us something in return:

- the data we need, on time;
- a case study and a reference call if results are good;
- a **letter of intent (LOI)** naming the paid price if the pilot hits agreed targets.

## The first 3 pilots: proposed terms

| | Pilot 1 (design partner) | Pilots 2 and 3 |
|---|---|---|
| Fee | $0 to $500 | $1,500 flat for 90 days |
| Credit if they convert | Not needed | Full fee credited against the first 3 paid months |
| Reward pool budget | About $1,000 per 150 members (model: $672 expected, plus a 1.5x buffer) | Same |
| How rewards are paid | Payroll bonus: the employer pays through its own payroll. Gift cards: at cost, invoiced monthly after redemption, or from a gift card account in the employer's name | Same |
| What they give us | Hire and end dates, data on time, a named owner, a case study, an LOI | Data on time, a named owner |
| Price after the pilot | $4 per member per month, $500 minimum, price locked for 12 months | Same |
| Success targets agreed up front | Enrollment of 50% or more, 30-day activity of 50% or more, 90-day new-hire retention better than the comparison group, manager time under 2 hours a month | Same |

Rewards stay at cost because:
- Marking up the pool makes the employer wonder whether we profit when workers earn more.
- It is safer if we never hold the employer's money in the pilot (see `docs/legal-drafts/pilot-agreement-outline.md`).

## After the pilot

- **Default price:** $4 per enrolled member per month, $500 monthly minimum, 12-month term, monthly ACH billing.
- **For chains that want predictability:** offer the per-location price ($75 per location per month), so long as it works out above the PEPM equivalent.
- **Test a higher price** with a new prospect, not a pilot employer. The model says $5 lifts margin to 70% while the employer's break-even lift rises only from 3.0% to 3.5%. We don't know yet whether $5 slows sales.
- **Don't** offer a "money back if retention doesn't improve" deal yet. One pilot can't measure retention reliably (see `unit-economics.md`, "What a 90-day pilot can and cannot prove").

## Open questions for the founder

1. Is the target buyer a franchisee or regional operator with 250+ hourly staff aged 18-25? Smaller operators only work with the minimum fee.
2. Do you want Pilot 1 free in exchange for a well-known logo, or should every pilot pay something?
3. Will the first employers accept the point values in the data contract (at most $32 per person in year 1)? Or should one pilot test bigger rewards, say 5x?
4. Who at the employer signs: the general manager, the HR lead or the owner? That changes the sales cycle and how big a fee they can approve.
