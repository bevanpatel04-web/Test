# Patient Money curriculum (v1, 2026-11-15)

The source of truth is `invest/data/curriculum.json` (format: `docs/app/contracts.md`, section 1). This page summarizes it in plain English. `tests/test_curriculum.py` checks that the two stay in sync.

**At a glance:** 5 levels, 15 modules, 46 lessons, about 3 hours in total (179 minutes). Each lesson takes 3-5 minutes.

## The path

Lesson minutes are in brackets.

| Level | Module | Lessons (minutes) |
|---|---|---|
| **1. Money foundations** (free) | Where your money goes | What a budget is actually for (3); Reading your paycheck: gross pay, take-home pay and deductions (4); Tracking a month of spending, without the guilt (3) |
|  | Your safety net | Why a cash cushion comes first (3); Where to keep your cushion (3) |
|  | Debt and credit | How credit card interest really works (4); Paying down debt: avalanche or snowball (4); What a credit score is, and what moves it (4); Paying down a card or investing: comparing the math (4) |
| **2. Your first investments** | How growth and risk work | What investing is: owning and lending (3); Compound growth, explained with $100 a month (4); What “risk” actually means when you invest (4) |
|  | Spreading risk | Diversification: not keeping all your eggs in one basket (3); What a fund is: mutual funds and ETFs (4); Index funds vs. single stocks: what's the difference? (4) |
|  | Costs and accounts | How a 1% fee adds up over time (4); Account types: where investments live (4); Before you open an investing account: what to check (3) |
| **3. Building a long-term plan** | Retirement and health accounts | How a 401(k) works (4); What a 401(k) match is, and why people call it “free money” (4); IRAs and Roth IRAs: when you pay the tax (4); HSA basics: a health account with tax breaks (4) |
|  | Choosing and keeping a mix | Asset allocation: your mix of stocks, bonds and cash (4); Rebalancing: why your mix drifts (3); Target-date funds, as a concept (3) |
|  | Putting it on autopilot | Automating your money: pay future you first (3); Your money plan on one page (5) |
| **4. Advanced investor** | Bonds, rates and inflation | How bonds work: lending with an end date (4); Why bond prices fall when interest rates rise (4); Inflation: why a dollar buys less over time (4) |
|  | Taxes and fund details | Taxes on investments: gains, dividends and time held (5); Dividends and total return (3); Reading a fund fact sheet (4) |
|  | Markets and your mind | Market crashes: 2000, 2008, 2020 and 2022 (5); Why “waiting for the dip” is harder than it sounds (4); Mind traps: the biases that cost people money (4) |
| **5. Expert topics explained** | High-risk products, explained | Leverage: how borrowing magnifies gains and losses (4); Options: how calls and puts work (5); How options can hurt beginners (4); Crypto: how it works and what can go wrong (5) |
|  | The long game | Real estate and REITs: the basics (4); Retirement withdrawal math: making savings last (5); Beneficiaries and estate basics (4) |
|  | Protecting yourself | Spotting investment scams (4); Hype, finfluencers and red flags online (4); Getting help: checking who gives money advice (4) |

Lessons per level: L1 9, L2 9, L3 9, L4 9, L5 10. Minutes per level: 32, 33, 34, 37, 43.

## How the learning works

**Each lesson** has a 2-4 minute video, 3 key points, a "Try it" step and a 3-question check. "Try it" uses one of four tools: the start-now-vs-later calculator, the crash simulator, a Money Map worksheet, or a short thinking exercise. Every lesson after the first lists the earlier lessons it builds on.

**Order:** lessons unlock one at a time, in the order shown above. Members can go back to any completed lesson at any time.

**Mastery rule: 2 of 3 to complete.**
- The explanation ("why") shows after every answer, right or wrong.
- Getting 2 or 3 right completes the lesson and starts its review schedule.
- With fewer than 2 right, the member can retry straight away. After two misses, the app suggests rewatching the video. Nothing ever locks.
- If the app shuffles the choices, it has to remap `answer`, which points at the stored order. The right answers are already spread across all three positions.

**Spaced review: 3, 10 and 30 days after completion.**
- When a review is due, the lesson's 3 questions come back with the choices shuffled.
- 2 of 3 moves the lesson to its next review. Fewer than 2 sends it back to a 3-day review.
- Passing the 30-day review marks the lesson as "mastered". An optional 90-day check can come later.
- Reviews never block new lessons. The app stores the next due date in `review_due` (contracts.md, section 3).

## What's free

- **Free:** Level 1 (9 lessons, 32 minutes) and the existing calculator.
- **Members:** Levels 2-5 (37 lessons), the crash simulator and the Money Map. No free lesson uses the crash simulator.
- **Decision needed:** 8 of the 9 Level 1 lessons end with a Money Map worksheet, as the seed lessons did. The suggestion is that free users can fill in those worksheets on their own device, as a taste of the product, while the combined Money Map and the Level 2-5 worksheets stay members-only.

## Content rules applied

- **No advice:** no securities, funds, coins, brokers or apps are named. The only names used are public regulator tools and agencies: FINRA BrokerCheck, the SEC's adviser search, the FDIC and NCUA, SIPC, the IRS, the BLS, and the official options disclosure document.
- **Risk notes:** every lesson that touches returns, investing products, leverage, options or crypto has one (34 of 46).
- **Numbers:** statistics come only from verified facts in `invest/data/facts.json`, listed under each lesson's `needs_facts` (5 lessons cite one). Lesson text holds no statistics; the video and page pull the current figure from the registry. Any other number is simple arithmetic labeled "hypothetical".
- **Level 5:** these lessons explain how things work and how they go wrong. They never present anything as a strategy to use.
- **Claims filter:** every string passes, including the wrong quiz answers.

## Facts to add

These are needed before the related lessons or videos can show a number. The expected values below are from memory, unverified, and must be confirmed at the source.

| Proposed key | What (expected value, to confirm) | Lessons | Official source |
|---|---|---|---|
| `sp500_2008_return`, `sp500_2020_drawdown`, `sp500_2022_return` | Already in facts.json but **unverified** | market-crashes-in-history; the crash simulator | S&P Dow Jones Indices (primary index provider) |
| `sp500_2000_2002_drawdown` | S&P 500 fall from the 2000 high to the 2002 low | market-crashes-in-history; the crash simulator | S&P Dow Jones Indices |
| `roth_ira_phaseout_single_2027` | Already in facts.json but **unverified** | iras-and-roth-iras | IRS Notice 2026-66 or the IRS newsroom release IR-2026-136 (irs.gov) |
| `fdic_insurance_limit` | Deposit insurance limit ($250,000 per depositor, per insured bank, per ownership category) | where-to-keep-your-cushion, crypto-risks | FDIC, fdic.gov/resources/deposit-insurance; for credit unions, NCUA, ncua.gov |
| `sipc_coverage_limit` | SIPC protection limit ($500,000, including $250,000 for cash) | before-you-open-an-account | SIPC, sipc.org ("What SIPC protects") |
| `fica_employee_rates` | Employee Social Security and Medicare tax rates (6.2% and 1.45%) | reading-your-paycheck | IRS Tax Topic 751 (irs.gov/taxtopics/tc751) |
| `early_withdrawal_tax` | Extra tax on early retirement withdrawals (10% before age 59½, with exceptions) | how-a-401k-works, iras-and-roth-iras | IRS Tax Topic 557 (IRAs) and 558 (retirement plans) |
| `hsa_limits_2027` | 2027 HSA contribution limits and the minimum deductible for a high-deductible plan | hsa-basics | IRS Revenue Procedure with the 2027 HSA limits (irs.gov) |
| `ltcg_holding_period` | Holding period for long-term capital gains (more than one year) | taxes-on-investments | IRS Tax Topic 409 (irs.gov/taxtopics/tc409) |
| `ltcg_rates_2027` | 2027 long-term capital gains rates and income brackets | taxes-on-investments | IRS Revenue Procedure with the 2027 inflation adjustments (irs.gov) |
| `cpi_12mo_latest` | Latest 12-month change in the CPI-U | inflation-explained | BLS CPI news release (bls.gov/cpi) |
| `crypto_not_fdic_insured` | Crypto assets aren't covered by FDIC deposit insurance | crypto-risks | FDIC consumer guidance on crypto (fdic.gov) |
| `free_credit_reports` | Free weekly reports from each nationwide credit bureau | credit-scores-explained | FTC, consumer.ftc.gov ("Free credit reports") |
| `rmd_start_age` | Age when required minimum distributions start (73 under current law) | retirement-withdrawal-math | IRS RMD FAQs (irs.gov) |
| `investment_scam_losses_2025` | Reported losses to investment scams in 2025 | spotting-investment-scams | FTC Consumer Sentinel Network Data Book 2025 (ftc.gov) |

## Lessons that need extra legal or compliance care

| Lesson(s) | Why |
|---|---|
| debt-or-invest-first, your-plan-on-one-page | They describe "an order many people follow". The wording must stay descriptive and never become "do this". |
| how-a-401k-match-works | The title quotes the phrase "free money". The match formula is a labeled hypothetical. |
| how-a-401k-works, iras-and-roth-iras, hsa-basics, taxes-on-investments | Tax and eligibility rules. Keep them general, point to IRS.gov, and check each rule against IRS wording. |
| where-to-keep-your-cushion, before-you-open-an-account, crypto-risks | FDIC, NCUA and SIPC coverage is easy to overstate. Describe the limits exactly, once the facts are verified. |
| index-funds-vs-single-stocks, asset-allocation, target-date-funds | These compare products and show example mixes. Videos must not imply that one choice is right for the viewer. |
| market-crashes-in-history, why-timing-the-market-is-hard | They need verified index data before any number appears. The claim that "best days come near worst days" needs a primary source if a video shows data. Show holding and selling fairly. |
| how-leverage-works, how-options-work, how-options-hurt-beginners | Explain only, with no "winning trade" visuals. The risk note says brokers must deliver the options risk disclosure (FINRA Rule 2360); a securities attorney should confirm that wording. |
| crypto-risks, real-estate-and-reits | Explain only. Name no coins, platforms or properties. The note on non-traded REITs should be checked. |
| retirement-withdrawal-math | Never present a rule of thumb as a plan or as reliable. |
| beneficiaries-and-estate-basics | Legal content: rules vary by state, and spouses have special rights in many 401(k) plans. **DRAFT for attorney review.** |
| spotting-investment-scams, hype-and-finfluencers | Never name real people, companies or coins. Quote hype only next to warning words; the claims filter allows quotes only then. |
| checking-who-gives-advice | The description of the fiduciary duty versus the broker standard (Regulation Best Interest) needs a securities attorney's check. **DRAFT for attorney review.** |
| credit-scores-explained | If a video names AnnualCreditReport.com, confirm with the FTC that it is the federally authorized site. |
