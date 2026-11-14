# Turnover economics: does paying for retention pay off?

*Research note. As of 2026-11-14. Internal, not consumer-facing. All dollar figures are US dollars.*

## 1. How often hourly workers quit (BLS JOLTS)

**Release:** BLS *Job Openings and Labor Turnover Survey*, September 2026 data, released 2026-11-03 ([BLS news release](https://www.bls.gov/news.release/jolts.nr0.htm), [Table 4: quits by industry](https://www.bls.gov/news.release/jolts.t04.htm); release date confirmed by [KPMG, 2026-11-03](https://kpmg.com/us/en/articles/2026/september-2026-jolts-national.html)). September 2026 values are **preliminary** and will be revised.

**How I verified:** bls.gov pages were blocked from this environment, so I pulled the same seasonally adjusted series from the BLS public data API on 2026-11-14: [JTS720000000000000QUR](https://data.bls.gov/timeseries/JTS720000000000000QUR) (accommodation and food services quits rate), [JTS720000000000000QUL](https://data.bls.gov/timeseries/JTS720000000000000QUL) (level), [JTS440000000000000QUR](https://data.bls.gov/timeseries/JTS440000000000000QUR) and [QUL](https://data.bls.gov/timeseries/JTS440000000000000QUL) (retail trade), [JTS000000000000000QUR](https://data.bls.gov/timeseries/JTS000000000000000QUR) (total nonfarm).

**Monthly quits, seasonally adjusted (rate = quits as % of employment)**

| Month | Accommodation & food services | Retail trade | All jobs (total nonfarm) |
|---|---|---|---|
| Sep 2025 | 488,000 (3.4%) | 312,000 (2.0%) | 2,990,000 (1.9%) |
| Oct 2025 | 468,000 (3.3%) | 396,000 (2.6%) | 2,980,000 (1.9%) |
| Nov 2025 | 670,000 (4.7%) | 409,000 (2.7%) | 3,119,000 (2.0%) |
| Dec 2025 | 676,000 (4.7%) | 487,000 (3.2%) | 3,225,000 (2.0%) |
| Jan 2026 | 677,000 (4.7%) | 426,000 (2.8%) | 3,131,000 (2.0%) |
| Feb 2026 | 586,000 (4.1%) | 469,000 (3.0%) | 3,046,000 (1.9%) |
| Mar 2026 | 593,000 (4.2%) | 460,000 (3.0%) | 3,160,000 (2.0%) |
| Apr 2026 | 574,000 (4.0%) | 463,000 (3.0%) | 3,043,000 (1.9%) |
| May 2026 | 598,000 (4.2%) | 440,000 (2.8%) | 3,153,000 (2.0%) |
| Jun 2026 | 589,000 (4.1%) | 464,000 (3.0%) | 3,213,000 (2.0%) |
| Jul 2026 | 527,000 (3.7%) | 472,000 (3.0%) | 3,089,000 (1.9%) |
| Aug 2026 | 522,000 (3.6%) | 450,000 (2.9%) | 3,044,000 (1.9%) |
| **Sep 2026 (p)** | **719,000 (5.0%)** | **475,000 (3.1%)** | **3,365,000 (2.1%)** |

**What this means**
- The brief's figure is correct: **719,000 quits and a 5.0% rate in accommodation and food services in September 2026.** It is preliminary.
- **September was a spike**, up 197,000 from August's 3.6%. KPMG warns that "monthly JOLTS data tend to be noisy so do not take that at face value." For planning, use the **12-month average: 4.2% a month (Oct 2025-Sep 2026), which adds up to about 50 quits per 100 jobs a year.**
- Retail: 3.1% in September; 12-month average 2.9% a month, about **35 quits per 100 jobs a year.**
- Total separations (quits plus layoffs and other exits) in accommodation and food services were 6.2% in Sept 2026 ([JTS720000000000000TSR](https://data.bls.gov/timeseries/JTS720000000000000TSR)).
- Young workers churn more. Median job tenure for 20-24 year olds was about 1.4 years in January 2024 ([USAFacts](https://usafacts.org/articles/how-long-do-americans-stay-at-their-jobs/), citing [BLS Employee Tenure](https://www.bls.gov/news.release/tenure.t01.htm)). One secondary source says 1.3 years, so the exact figure is **unverified**.

## 2. What it costs to replace an hourly worker

To put dollar costs in today's terms I used CPI-U (Oct 2026 = 337.511; [BLS CUUR0000SA0](https://data.bls.gov/timeseries/CUUR0000SA0)). Inflation factors to Oct 2026: 2003 ×1.83, 2006 ×1.67.

A typical hourly worker's pay, from BLS average hourly earnings and weekly hours for production and nonsupervisory employees ([CES series](https://data.bls.gov/timeseries/CES7000000008), preliminary):

| Sector | Hourly pay | Weekly hours | About per year |
|---|---|---|---|
| Leisure & hospitality (Oct 2026) | $21.40 | 24.1 | $26,800 |
| Food services & drinking places (Sep 2026) | $20.52 | 23.8 | $25,400 |
| Retail trade (Oct 2026) | $22.45 | 30.7 | $35,800 |

These are averages for all ages. Workers aged 18-25 probably earn less, which would lower replacement costs tied to pay.

**Estimates of replacement cost (ranked from most to least rigorous)**

| Source | Type | Setting | Estimate | In 2026 terms |
|---|---|---|---|---|
| [Kuhn & Yu, *How Costly Is Turnover? Evidence from Retail*](https://www.nber.org/papers/w26179) (NBER 2019, rev. 2020; *Journal of Labor Economics* 2021) | Academic, uses daily sales data and a 2-week notice rule to isolate cause | Small retail sales teams at one firm | **$1,132 per departure**, "63 days of a typical employee's pay" ([PDF](https://www.nber.org/system/files/working_papers/w26179/w26179.pdf)). "Ten percent higher turnover is about as costly as a 0.6% wage increase." | Study-period dollars; year not confirmed (**unverified**) |
| [Dube, Freeman & Reich, *Employee Replacement Costs*](https://escholarship.org/uc/item/7kc29981) (UC Berkeley IRLE, 2010) | Academic, survey of California employers, 2003 and 2008 | All sectors | Average $4,039 per recruit. Blue-collar/manual: $1,300-$2,350 (2003 dollars). Mean cost is 6-10% of annual pay; median 2-4% | Blue-collar about **$2,400-$4,300** |
| [Boushey & Glynn, Center for American Progress](https://www.americanprogress.org/article/there-are-significant-business-costs-to-replacing-employees/) (2012-11-16) | Review of 30 case studies by a policy think tank | Mixed | **16% of annual pay** for jobs under $30,000; 10-30% for jobs up to $75,000 | 16% of $26,800 ≈ **$4,300** |
| [Tracey & Hinkin, Cornell Center for Hospitality Research](https://ecommons.cornell.edu/entities/publication/af07c95a-83d7-4754-988b-df18c884d890) (Dec 2006) | Academic, web survey of 33 hotels | Hotels | "Almost $6,000 per frontline worker" ([Newswise](https://www.newswise.com/articles/study-finds-hidden-costs-of-hotel-employee-turnover)); widely quoted as $5,864. Lost productivity is the largest part | About **$9,800** if $5,864 is right (**$5,864 unverified** in the report itself) |
| SHRM 2025 recruiting benchmark | HR association survey | All employers | Average non-executive cost per hire reported as $5,475; median about $1,200 (secondary sources) | Recruiting cost only, not lost output. **Unverified**: I could not open SHRM's figures |

**Skeptic's notes**
- The "$5,864 per restaurant employee, Cornell" number on restaurant-industry sites ([example](https://modernrestaurantmanagement.com/?p=39793)) appears to come from the **2006 hotel** study. Don't cite it as restaurant data.
- The most rigorous study (Kuhn & Yu) found turnover costs were **low**, because the firm's staffing practices covered gaps. An employer with good scheduling and cross-training will lose less per quit than the headline numbers suggest.
- Vendor "turnover calculators" often use 30-50% of salary or more. I found no independent support for numbers that high for hourly jobs.

**Ranges used below**
- **Low: $1,500** (near Kuhn & Yu and the low end of Dube et al.).
- **Base: $3,500** (middle of Dube et al. blue-collar, below 16% of pay).
- **High: $6,000** (between 16% of pay and the inflation-adjusted Cornell hotel figure).

## 3. Do financial-wellness or EWA benefits improve retention?

**Short answer: there is no rigorous, independent proof that they do.** Almost every positive number compares people who signed up with people who didn't. Workers who plan to stay are more likely to sign up, so those comparisons overstate the effect.

**Independent or academic**

| Study | Design | Finding | Caveat |
|---|---|---|---|
| [Murillo, Vallée & Yu, HBS working paper](https://www.hbs.edu/faculty/Pages/item.aspx?num=62332) (preliminary, 2022-03-27) | 51,543 workers at 2 Mexican firms; survival model with controls | EWA use "associated with higher employee retention." A search summary reports a 12% lower chance of leaving in the next pay cycle (**unverified**: not in the pages I read) | The authors say the results are "suggestive." Still users vs non-users |
| [Lux & Chung, Harvard Kennedy School](https://www.hks.harvard.edu/sites/default/files/centers/mrcbg/214_AWP_final_2.pdf) (June 2023) | Policy review plus survey | Notes employers *hope* for retention; "data is limited" | No retention measurement |
| Leana et al., University of Pittsburgh, emergency-savings field study (~1,500 drivers), *ILR Review* in press ([via AARP](https://www.aarp.org/pri/topics/work-finances-retirement/financial-security-retirement/does-emergencies-saving-improve-work-productivity/)) | Field intervention | Savings associated with higher job satisfaction and lower turnover | Turnover results **unverified** |

**Vendor-linked (independent authors, vendor data or vendor publication)**

| Study | Finding | Caveat |
|---|---|---|
| Walmart study of 260,000+ new hires, published by Even ([case study](https://www.casestudies.com/company/even/case-study/walmart-study-shows-impact-of-responsible-earned-wage-access)) | **On-demand pay alone did not meaningfully improve retention.** Heavy users of Even's other tools had 30% turnover vs 51% for light users | Vendor-published. The 30% vs 51% is again a usage comparison. Bloomberg reported in 2021 that early-pay users were quitting faster ([PYMNTS](https://www.pymnts.com/walmart/2021/walmart-employee-turnover-up-despite-early-wage-access/)) |
| Baker & Kumar, Harvard Kennedy School (2018) ([summary hosted by Payactiv](https://www.payactiv.com//assets/pdf/4-big-benefits-MRCBG-paper-20181004.pdf)) | 19% lower turnover among active Payactiv users | 6 companies, users vs non-users |

**Vendor claims (no comparison group or self-reported)**
- Rain: average 35% turnover reduction across clients ([Rain](https://www.rainapp.com/blog/earned-wage-access-and-employee-retention-what-the-data-shows-for-frontline-employers)).
- DailyPay / Arizent survey (commissioned): 30% of employers say turnover fell ([DailyPay](https://www.dailypay.com/press-center/press-releases/dailypay-improves-employee-retention-productivity-and-morale-according-to/)).
- Brightside: 41% turnover reduction ([Brightside](https://gobrightside.com)).
- Sunny Day Fund: 5.7% turnover among savers vs 25.2% in the eligible workforce ([Financial Health Network, 2026-02-02](https://finhealthnetwork.org/sunny-day-fund-helping-the-entire-workplace-thrive-with-emergency-savings/)).
- Questis: 33% lower turnover ([SHRM vendor directory](https://vendordirectory.shrm.org/company/900866/news/2955735/case-study-on-employee-retention-navigating-the-great-resignation-finds-financial-wellness-decreases-turnover)).
- SecureSave: 3 in 4 workers *say* a $200/year contribution would make them more likely to stay ([SecureSave](https://www.securesave.com/blog/research-financial-stress-emergency-savings-and-the-impact-on-american-workers)).

**Related independent evidence (not financial wellness, but closer to "small rewards to stay")**
- **Randomized trial, 238 grocery stores, 10,000+ workers:** an employee referral program cut attrition by about 15% ([Friebel, Heinz, Hoffman & Zubanov, *Journal of Political Economy* 2023; NBER w25920](https://www.nber.org/papers/w25920)). This is the best model for how to *test* a retention program: randomize by store.
- **$1,800 annual bonus** for hard-to-staff teachers in North Carolina cut their turnover by about 12% ([Clotfelter, Glennie, Ladd & Vigdor, NBER w12285](https://www.nber.org/papers/w12285); *Public Finance Review* 2008). A much bigger reward than ours.
- **Retention bonus vs. plain bonus** at an Ethiopian garment factory: no significant difference in 3-month retention ([Abebe et al., IGC working paper 2019](https://www.theigc.org/wp-content/uploads/2021/05/Abebe-et-al-2019-Working-paper-2.pdf)). Tying money to staying doesn't automatically work.

**Bottom line:** a reasonable expectation for a small rewards-plus-education program is somewhere between **no effect and a single-digit percent cut in quits.** Anything above 15% would be surprising.

## 4. Break-even math

**Question:** at $4 per enrolled employee per month plus a reward pool of $X, how many fewer quits does the employer need for it to pay off?

**Formula**

> Employer cost per enrolled employee per year = 12 × $4 + X × 1.0765
>
> Break-even = that cost ÷ replacement cost = fewer quits needed per enrolled employee per year

**Assumptions (all stated)**
1. PEPM of $4 is charged only for enrolled employees (as in the brief).
2. X is the **average reward actually paid out per enrolled employee per year**, not the maximum.
3. Rewards are taxable wages, so the employer also pays 7.65% Social Security and Medicare tax on them (see `regulatory-checklist.md`). I ignore state unemployment tax, which is usually capped.
4. Gift card delivery costs $0 extra (Tremendous sends gift cards at face value; see `partners.md`).
5. I ignore employer staff time to run the program and any small overtime "regular rate" cost (see `regulatory-checklist.md`). Both make the real break-even slightly higher.
6. Benefit counts only avoided replacement costs. It ignores softer gains (service quality, less overtime covering gaps), which would make break-even easier.
7. Baseline quits: 50 per 100 jobs a year (accommodation and food services 12-month average) or 35 (retail). The baseline only matters for the "relative cut" column.

**Choosing X.** Under the current earning rules in `docs/pilot/data-contract.md` (100 points = $1), a member who stays a full year and does everything earns at most 3,200 points = **$32** (tenure 2,200 + lessons 500 + checklist 200 + savings set-up 300). Many members leave before 365 days, so the average payout is lower. The demo employer funds $5,000 for 240 enrolled, about $21 each. So:
- **Low pool: X = $25** (current rules)
- **Mid pool: X = $100**
- **Rich pool: X = $300** (about $25 a month)

**Results**

| Pool X (per enrolled per year) | Employer cost per enrolled per year | Replacement cost | Fewer quits needed per 100 enrolled per year | One avoided quit per … enrolled | Relative cut needed at 50% baseline | at 35% baseline |
|---|---|---|---|---|---|---|
| $25 | $74.91 | Low $1,500 | 5.0 | 20 | 10.0% | 14.3% |
| $25 | $74.91 | **Base $3,500** | **2.1** | **47** | **4.3%** | **6.1%** |
| $25 | $74.91 | High $6,000 | 1.2 | 80 | 2.5% | 3.6% |
| $100 | $155.65 | Low $1,500 | 10.4 | 10 | 20.8% | 29.6% |
| $100 | $155.65 | Base $3,500 | 4.4 | 22 | 8.9% | 12.7% |
| $100 | $155.65 | High $6,000 | 2.6 | 39 | 5.2% | 7.4% |
| $300 | $370.95 | Low $1,500 | 24.7 | 4 | 49.5% | 70.7% |
| $300 | $370.95 | Base $3,500 | 10.6 | 9 | 21.2% | 30.3% |
| $300 | $370.95 | High $6,000 | 6.2 | 16 | 12.4% | 17.7% |

**Worked example (demo employer, base case):** 240 enrolled × $48 = $11,520 in fees, plus a $5,000 pool and $383 employer payroll tax = $16,903 a year. At $3,500 per replacement, it pays off if it prevents **about 5 quits a year among 240 people** (2 per 100).

**Read-out**
- **With the current small reward schedule, the bar is low:** about 2 fewer quits per 100 enrolled per year in the base case, a 4-6% relative cut. That is plausible given the evidence, but not proven.
- **Bigger pools raise the bar fast.** At $300 a year, the base case needs a 21% cut in quits. Nothing independent suggests a program like this does that.
- **Price and pool design matter more than the PEPM.** The $4 fee is $48 a year. Every extra $100 in average payout roughly doubles the needed effect.

## 5. The measurement problem

Even if the program works at break-even level, **one pilot employer cannot prove it.** Using a standard test (two groups, 95% confidence, 80% power):

| Real effect | People needed **in each group** (12-month quit rate 50%) | (6-month quit rate 30%) |
|---|---|---|
| 2 fewer quits per 100 (base break-even) | about 9,800 | about 8,100 |
| 5 fewer per 100 | about 1,570 | about 1,250 |
| 10 fewer per 100 | about 390 | about 290 |
| 15 fewer per 100 | about 170 | about 120 |

The demo employer has 400 eligible employees in total. It can only detect a very large effect (10+ points), and only with a fair comparison group.

**Also, the dashboard comparison is biased.** `docs/pilot/data-contract.md` compares enrolled vs "eligible employees who didn't join." That is the same users-vs-non-users comparison behind every vendor claim above. Enrolled workers will look better even if the program does nothing.

**Ways to get a fair read**
- **Randomize by location** (like the grocery trial): offer the program at half an employer's sites first, then the rest. Compare all eligible workers at program sites vs. waiting sites, whether or not they enroll.
- **Pre-commit to one metric**: the 90-day and 180-day quit rate of new hires.
- **Pool results across employers** so the sample reaches the thousands.
- Report the honest comparison to the employer, even if it is "no detectable effect yet."

## So what for us

1. Cite **4.2% a month (about 50% a year)** for accommodation and food services alongside the September 5.0% spike. Both are true; the average is what an employer lives with.
2. Use **$1,500 / $3,500 / $6,000** as the replacement-cost range. Don't use $5,864 as a restaurant number.
3. **Keep the reward pool small and front-loaded** (30 and 90 days, when most quits happen). With the current schedule, break-even is about 2 fewer quits per 100 enrolled per year.
4. **Don't promise proven ROI from one pilot.** Promise a fair test, run across sites or employers.
5. **Fix the dashboard comparison** before showing it to a payer. Enrolled vs not-enrolled will overstate the effect, and a skeptical HR buyer will know it.
