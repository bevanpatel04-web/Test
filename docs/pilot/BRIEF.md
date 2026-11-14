# Team brief: the employer rewards pilot ("Bilt for the first paycheck")

Read this first. Every agent on the team works from it.

## The company

**Patient Money** (working name) helps 18-25 year olds understand investing, and the risk that comes with it, so they can make their own decisions. What exists today (in this repo):

- `invest/site/` — free "start now vs. later" calculator, lessons page, "Our rules" page (static HTML/CSS/JS, mobile-first, light and dark).
- `invest/` (Python) — a content AI team (CEO, Facts, Lessons, Social agents) with a claims filter (`invest/claims.py`) and founder approval.
- `docs/patient-money-plan.md` — research, legal guardrails, revenue stages, 30-day plan.
- `company/` and `site/` — a separate product (Mildwell). **Don't touch it.**

## The new direction

Copy Bilt's playbook. Bilt signed landlords *before* renters, and landlords pay because rewards keep tenants. We sign **employers of young hourly workers** (restaurants, hotels, retail) before members, and employers pay because rewards keep staff. Accommodation and food services had 719,000 quits in September 2026, a 5.0% monthly quit rate (BLS JOLTS).

**How the pilot works**
- The employer pays a per-employee-per-month (PEPM) fee and funds a reward pool.
- Members (employees aged 18-25) earn points for **work tenure milestones** (30/90/180/365 days), **completing lessons**, and **healthy money habits** (setting up direct deposit to savings, finishing the "before you invest" checklist).
- **Never** for trading, number of trades or account balances. Gamified trading is a regulatory red flag; Massachusetts fined Robinhood $7.5M in 2024 partly over it.
- Pilot redemptions: **payroll bonus** (the employer pays through payroll, so it's taxed as wages) or **gift card**. No securities and no money movement by us in the pilot.
- Later (not in the pilot): points become a cash deposit into the member's **own** investing or savings account through a licensed partner (e.g. Apex or DriveWealth stock-rewards APIs). The member chooses what to invest in. We never pick.
- Second payer later: credit unions that want young members.

**Why it can fail (from research):** Bumped's brand-funded stock rewards shut down in 2022 when brands stopped paying. Wells Fargo reportedly lost up to $10M a month subsidizing the Bilt card. The payer must get clear value (retention) that we can measure.

## Rules for every agent

1. **Education, not advice.** No recommending any security, fund, coin, broker or app. No promised or predicted returns. Risk is shown next to any return. Any consumer-facing copy must pass `python -c "from invest.claims import find_violations; print(find_violations(open('FILE').read()))"` with no hits.
2. **Facts need sources.** Cite a URL and date for every statistic. Prefer government and regulator sources. Mark anything you couldn't verify as **unverified**.
3. **Stay in your lane.** Only create or edit the files and folders your task assigns you. Never edit another agent's files, `company/`, `site/` or `.github/`.
4. **No git.** Don't commit, push, reset, checkout or stash. The lead integrates and commits.
5. **Privacy.** Never put the founder's name, email or other personal details in a web request or in content.
6. **Legal drafts are drafts.** Anything that looks like a contract, terms or policy must say "DRAFT for attorney review" at the top.
7. **Plain English** for anything the founder reads: short sentences, no jargon.
8. **Finish with a short report:** what you made (file paths), what you verified and how, open questions, and anything you couldn't finish.

## Who owns what

| Agent | Owns |
|---|---|
| Backend builder | `rewards/`, `tests/test_rewards.py` |
| Frontend builder | `invest/site/pilot/` |
| Marketing | `docs/marketing/`, `invest/site/employers.html` |
| Research | `docs/research/` |
| QA / testing | `tests/qa/`, plus small bug fixes in `invest/site/assets/` and `invest/*.py` (not `invest/site/pilot/`) |
| Finance and ops | `docs/finance/`, `docs/legal-drafts/` |

Shared data format between the backend and the dashboard: `docs/pilot/data-contract.md`.
