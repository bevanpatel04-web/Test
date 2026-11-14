# Unit economics: the employer rewards pilot

*Finance and ops, 2026-11-14. Numbers come from `docs/finance/model.py`. Run `python3 docs/finance/model.py` to rerun it after you edit the inputs at the top. Nothing here is a forecast. It is arithmetic on sourced figures plus clearly labeled assumptions.*

## The short version (base case)

| | Base case | Range (conservative to optimistic) |
|---|---|---|
| Our price | **$4 per enrolled member per month** | same in all three |
| Typical first employer | 250 eligible, 150 enrolled, 10 locations | 90 to 350 enrolled |
| Our revenue per employer | **$600 a month** | $360 to $1,400 |
| Our cost to serve them | $226 a month ($1.51 per member) | $334 to $177 |
| **Gross margin** | **62%** | 7% to 87% |
| Rewards the employer pays | about $11 per member per year | $9 to $13 |
| Employer's total cost | $9,679 a year ($5.38 per member per month) | $6,654 to $21,915 |
| One replacement hire costs the employer | about $4,060 | $2,030 to $5,840 |
| **Break-even retention lift** | **3.0% fewer quits** (4.1% a month falls to 3.98%) | 9.2% to 1.6% |
| That is | 2.4 fewer quits a year per 150 members | |
| **Employers needed for $100K a month (MRR)** | **167** (25,000 members) | 278 to 71 |
| Month we reach $100K MRR | **month 49** | never in 6 years to month 21 |

**In one sentence:** the employer's math looks very good on paper (it breaks even if just 2 or 3 people a year stay who would have quit), our margin is healthy only when an employer has 140 or more members, and the speed of the company depends on how many pilots turn into paying customers.

## The 3 numbers that matter most

1. **Retention lift: do members actually quit less?** Everything rests on this. The employer breaks even at about 3% fewer quits (base) and makes about $22,500 a year at 10% fewer. We have no evidence yet that $11 a year in rewards changes anyone's behavior (see "Rewards are small" below). The pilot must test this first.
2. **Members per employer: is each customer big enough?** Our costs are mostly fixed per employer: account management time and the payroll data connection. At $4 we need about **140 members per employer for a 60% margin**. At 50 members the margin is 14%, and we never earn back the cost of the sale. This is why `pricing.md` recommends a $500 monthly minimum.
3. **Pilot-to-paid conversion: how many pilots become customers?** At 60% conversion, a salesperson costs us about **$5,000 per paying employer**, and we earn it back in about 13 months. At 40% conversion and slower sales, it costs $12,500 and we never earn it back. This number also decides how much money we need to raise.

## What the model says, in plain English

### 1. Per employer

- **Revenue.** 150 members x $4 = $600 a month.
- **Costs.** The big ones are fixed per employer. Our account management time is about 2 hours a month ($80). The payroll data connection is $65 (the Finch Starter list price). Per-member costs are small: about $0.40 a month for AI, hosting, texts and support time combined. Gift card fees are near zero if the gift card account is funded by bank transfer; Tremendous charges 3% only for credit card funding.
- **Margin.** 62% in the base case. It rises to 72% at 250 members and 78% at 400 (table 4b). It falls to 7% for a small employer with 90 members and heavier support needs.

### The reward pool (paid by the employer, passed through at cost)

- The earning rules (`docs/pilot/data-contract.md`) cap one person at **3,200 points ($32) in a first year**: $22 for tenure milestones plus $10 for lessons, the checklist and savings setup.
- On average a member earns far less: about **1,210 points ($12.10) in year 1**, or $10.89 after 10% of points are never redeemed. The reasons:
  - Many members have already passed their milestones when the program starts. The model gives no back pay for milestones passed before launch.
  - People who quit early never reach the 180-day and one-year milestones.
- Year 2 is a bit lower (about $9.15) because existing staff only earn the one-time points once.
- **90-day pilot:** about 448 points per member, about **$672 for a 150-member employer**. The model suggests a **$1,000 pilot pool budget** (1.5x the expected amount). The employer is billed only for what is redeemed.
- **Rewards are small.** A new hire who stays a full year can earn at most $32, about 1.5 hours of pay at the BLS average of $20.52 an hour. That may be too little to change behavior. The employer can afford much more: at 5 times the point values, the employer's cost rises to about $16,700 a year and break-even rises only to 5.2% fewer quits (table 4c). **Consider testing bigger milestone rewards in at least one pilot.**

### 2. Employer ROI

- **Baseline quits.** BLS reports a 4.1% average monthly quit rate in accommodation and food services for June to Sept 2026. Sept alone was 5.0% (719,000 quits), a spike. At 4.1%, about 74 of 150 members quit in a year.
- **Cost of a quit.** CAP found the typical turnover cost for jobs under $30,000 a year is 16% of annual pay. That is about $4,060 on BLS pay data ($20.52 an hour, 23.8 hours a week). The range we use runs from $2,030 (direct costs only) to $5,840 (close to the widely cited Cornell $5,864, unverified and in 2006 dollars).
- **Employer cost.** $7,200 fee + $1,634 rewards + $125 employer payroll tax + $720 manager time = **$9,679 in year 1**. Both payroll bonuses and gift cards count as taxable wages (IRS Pub 15-B).
- **Break-even.** About 2.4 avoided quits a year, a 3.0% cut in quits. In the conservative case (retail-level quits, $2,030 replacement cost, small employer) it takes a 9.2% cut. Table 2b in the output shows net savings at each lift level.

### 3. Company path

- **$10K, $50K and $100K MRR** need 2,500, 12,500 and 25,000 members. That is 17, 83 and 167 employers in the base case.
- **Sales assumptions (base).**
  - It takes 3 months from first meeting to a signed pilot, then a 3-month pilot.
  - 60% of pilots convert, and we lose 2% of paying employers a month.
  - The founder starts 1.5 pilots a month. Salespeople start in months 9, 15, 21 and 27, each starting 3 pilots a month once ramped.
- **Result.**
  - Base: $10K MRR in month 19, $50K in month 35, $100K in month 49. About **$1.25M of sales and marketing spend** gets us to $100K MRR, so a $750K pre-seed alone does not get there.
  - Optimistic: $100K MRR in month 21.
  - Conservative: never gets past about $19K MRR in 6 years.
- **Cash from pilot fees** ($1,500 each) is small, about $20K in year 1. Its job is to prove that employers will pay, not to fund the company.

### 4. Sensitivities (base case)

- **Price** (table 4a). At $5 the margin is 70% and we need 133 employers for $100K MRR. At $3 it is 50% and we need 222. Break-even lift barely moves, so price is not what decides the employer's ROI. Retention is.
- **Employer size** (table 4b) matters more than price. This is why we should **target employers with 150+ members** (roughly 250+ hourly staff aged 18-25), such as multi-unit franchisees, regional restaurant groups and hotel management companies.

## What a 90-day pilot can and cannot prove

**A 90-day pilot at one employer cannot prove a retention lift with statistics.** In 90 days about 12% of members quit, about 18 people at a 150-member employer. To tell a 30% drop from noise you need about 1,125 members in each group. Over 12 months you need about 245 per group for a 30% drop, or 572 for a 20% drop (table 6). People at the same location also behave alike, which raises these numbers further.

So the pilot should:

1. **Prove the things a pilot can prove:** enrollment, engagement, our costs, the employer's admin time, and whether they pay to continue.
2. **Get a fair retention read.** Use one of two designs:
   - a **staggered start**: half the locations start on day 1 and the rest on day 91; or
   - a comparison with the **employer's own retention for the same months last year**.

   Comparing members with employees who chose not to join is biased. People who sign up for a perk are probably less likely to quit anyway. The `not_enrolled_pct` line in the data contract is useful but not proof.
3. **Pool the data** across the first 3 to 4 employers and keep measuring for 6 to 12 months.

## What to measure in the pilot

| Measure | Model assumes (base) | Why it matters | Where it comes from |
|---|---|---|---|
| Enrollment rate (enrolled / eligible) | 60% | Revenue per employer and margin | `summary.enrolled`, `summary.eligible` |
| 30-day active rate | 60% do lessons | Engagement and pool size | `summary.active_30d` |
| Points earned per member, first 90 days | 448 | Pool budget accuracy | `points_issued`, `earning_by_rule` |
| Redemption mix (payroll vs gift card) | 60/40 | Gift card fees, payroll work | `redemptions` |
| Points never redeemed | 10% | Employer cost | `points_outstanding` after the pilot |
| 30- and 90-day retention of **new hires**, program vs comparison | 2x higher early quits | The earliest retention signal | `retention`, plus the employer's hire and end dates |
| Monthly quit rate, all members vs comparison | 4.1% | The break-even test (3% lift) | Employer HR data (voluntary quits only) |
| The employer's own cost per hire | $4,060 | Their ROI, in their own numbers | Ask them: recruiting spend, training hours, overtime |
| Support tickets per member per month, minutes each | 0.05, 10 minutes | Our cost | Our support log |
| Our hours per employer per month | 2 | Biggest cost line | Time log |
| Employer manager hours per month | 2 | Their hidden cost | Ask at day 30, 60 and 90 |
| Sales cycle (first meeting to signed pilot) | 3 months | Path to MRR | CRM |
| Pilot converts to paid, and at what price | 60% at $4 | CAC and growth | The decision at day 90 |

## Riskiest assumptions

1. **That small rewards move retention.** Nothing yet shows that $11 to $32 a year changes quitting. This is the biggest risk. It is also the lesson of Bumped: payers stop paying without clear value.
2. **Employer size.** Our margin needs 140+ members per employer. Many restaurant operators are smaller.
3. **Pilot conversion and sales speed.** These are pure assumptions until we run real sales conversations.
4. **Cost per replacement.** Employers may count only direct costs (the $2,030 case), which nearly triples the lift they need.
5. **Legal structure** (see `docs/legal-drafts/`). Four questions:
   - Does limiting eligibility to ages 18-25 raise age-discrimination issues? The ADEA protects workers 40 and over, and covers pay and benefits.
   - Must earned points be paid out when someone leaves (state wage laws)?
   - Can we handle gift card funds without money transmitter licenses?
   - Do we have consent for text messages?

   Any of these could change costs or design.

## Sources (all checked 2026-11-14)

- BLS JOLTS, Sept 2026 release (Nov 3, 2026), Table 4 quits and Table 3 separations: https://www.bls.gov/news.release/archives/jolts_11032026.htm
- BLS employee tenure, Table 1 (median tenure 1.5 years for ages 20-24, Jan 2026): https://www.bls.gov/news.release/tenure.t01.htm
- BLS CES, food services and drinking places, nonsupervisory pay and hours, Sept 2026 (preliminary): https://data.bls.gov/timeseries/CES7072200008 and https://data.bls.gov/timeseries/CES7072200007
- Center for American Progress, turnover costs 16% of pay for jobs under $30,000 (Nov 2012): https://www.americanprogress.org/article/there-are-significant-business-costs-to-replacing-employees/
- Tracey and Hinkin, Cornell CHR (Dec 2006), $5,864 figure widely cited, **unverified** in the original: https://hdl.handle.net/1813/71149
- IRS Topic 751 (employer FICA 7.65%): https://www.irs.gov/taxtopics/tc751
- IRS Publication 15-B (2026), gift cards never de minimis: https://www.irs.gov/publications/p15b
- EEOC, age discrimination (ADEA protects 40+; covers pay and benefits): https://www.eeoc.gov/age-discrimination
- Finch pricing ($65 per connection per month, Starter): https://www.tryfinch.com/pricing
- Tremendous pricing (gift cards free to send; 3% for credit card funding): https://www.tremendous.com/pricing
- Twilio US SMS pricing ($0.0083 per segment plus carrier fees): https://www.twilio.com/en-us/sms/pricing/us
- Stripe pricing (ACH 0.8% capped at $5; Invoicing 0.4%): https://stripe.com/pricing
- Claude API pricing, as of 2026-11-03: https://platform.claude.com/docs/en/about-claude/pricing
- B2B CAC and sales cycle: no primary source verified. Secondary summaries of SaaS benchmark reports put small-business CAC payback at roughly 8 to 15 months. Treat this as **unverified**; our figures are assumptions.

## Full model output (2026-11-14)

```
================================================================================
PATIENT MONEY: EMPLOYER REWARDS PILOT, FINANCE MODEL
All money in US dollars. 'Member' = enrolled employee. 100 points = $1.
Most one person can earn in a first year: 3,200 points ($32).
================================================================================

1. PER EMPLOYER
                                        Conservative          Base    Optimistic
--------------------------------------------------------------------------------
Eligible employees (18-25, hourly)               200           250           500
Enrollment rate                                  45%           60%           70%
Enrolled members                                  90           150           350
Our price per member per month                 $4.00         $4.00         $4.00
Our revenue per month                           $360          $600        $1,400

REWARD POOL (paid by the employer)                                              
Points earned per member, first 90 days           300           448           652
Points earned per member, year 1                 923         1,210         1,578
  of which tenure milestones                     783           890           972
  of which lessons/checklist/savings             140           320           606
Points earned per member, year 2                 831         1,016         1,234
Rewards paid per member, year 1                $9.23        $10.89        $12.62
Rewards paid per member, year 2                $8.31         $9.15         $9.87
Employer reward pool, year 1 total              $831        $1,634        $4,417
Points earned in 90-day pilot, $ total          $270          $672        $2,283
Suggested pilot pool budget (1.5x)              $400        $1,000        $3,400

OUR COSTS PER MONTH (one employer)                                              
  Payroll/HR data connection                    $100           $65           $30
  Account management (our time)                 $120           $80           $60
  Payment processing                              $4            $7           $11
  AI (Claude API)                                $20            $8            $4
  Hosting                                         $9            $8            $7
  Text messages                                   $7            $8            $9
  Member support (our time)                      $72           $50           $56
  Gift card fees + fraud                          $2            $1            $1
Total cost per month                            $334          $226          $177
Cost per member per month                      $3.71         $1.51         $0.50
Gross profit per month                           $26          $374        $1,223
GROSS MARGIN                                      7%           62%           87%
Members needed for 60% margin                    610           140            70
Members needed for 75% margin                  never           305           125

2. EMPLOYER ROI (first 12 months)
                                        Conservative          Base    Optimistic
--------------------------------------------------------------------------------
Replacement cost per hourly worker            $2,032        $4,063        $5,841
  (share of a year's pay)                         8%           16%           23%
Baseline monthly quit rate                      3.1%          4.1%          5.0%
Quits per year among members, no program          33.5          73.8         210.0
  per 100 members                               37.2          49.2          60.0
Cost of those quits per year                 $68,019      $299,871    $1,226,605

EMPLOYER COST OF THE PROGRAM, YEAR 1                                            
  Our fee                                     $4,320        $7,200       $16,800
  Rewards paid out                              $831        $1,634        $4,417
  Employer payroll tax on rewards                $64          $125          $338
  Manager time                                $1,440          $720          $360
  Total                                       $6,654        $9,679       $21,915
  Total per member per month                   $6.16         $5.38         $5.22

BREAK-EVEN RETENTION LIFT                                                       
  Cut in quits needed (relative)                9.2%          3.0%          1.6%
  = monthly quit rate falls to                 2.81%         3.98%         4.92%
  = quits avoided per year                       3.3           2.4           3.7
  = quits avoided per 100 members/yr             3.6           1.6           1.1

2b. EMPLOYER NET SAVINGS BY RETENTION LIFT (year 1; negative = employer loses money)
                                        Conservative          Base    Optimistic
--------------------------------------------------------------------------------
5% fewer quits: quits avoided                    1.8           4.0          11.4
   employer net savings                      -$3,041        $6,479       $44,999
   return per $1 spent                         $0.54         $1.67         $3.06
10% fewer quits: quits avoided                   3.5           7.9          22.8
   employer net savings                         $551       $22,516      $111,328
   return per $1 spent                         $1.08         $3.33         $6.10
15% fewer quits: quits avoided                   5.3          11.8          34.0
   employer net savings                       $4,121       $38,431      $177,071
   return per $1 spent                         $1.62         $4.99         $9.13
20% fewer quits: quits avoided                   7.0          15.7          45.2
   employer net savings                       $7,669       $54,224      $242,230
   return per $1 spent                         $2.16         $6.64        $12.15
30% fewer quits: quits avoided                  10.5          23.4          67.2
   employer net savings                      $14,702       $85,448      $370,792
   return per $1 spent                         $3.22         $9.92        $18.14

3. COMPANY PATH
                                               Conservative         Base   Optimistic
-------------------------------------------------------------------------------------
Monthly revenue per paying employer                    $360         $600       $1,400
Gross profit per paying employer/month                  $26         $374       $1,223
Members needed for $10,000 MRR                        2,500        2,500        2,500
Employers needed for $10,000 MRR                         28           17            7
Members needed for $50,000 MRR                       12,500       12,500       12,500
Employers needed for $50,000 MRR                        139           83           36
Members needed for $100,000 MRR                      25,000       25,000       25,000
Employers needed for $100,000 MRR                       278          167           71

SALES ASSUMPTIONS                                                                    
Sales cycle (first meeting to pilot), months              4            3            2
Pilot length, months                                      3            3            3
Pilot-to-paid conversion                                40%          60%          75%
Paying employers lost per month                          3%           2%           1%
Pilots the founder starts per month                     1.0          1.5          2.0
Salespeople hired                                         2            4            5
  first one starts in month                              12            9            6
Pilots per salesperson per month                        2.0          3.0          4.0
CAC per paying employer (salesperson)               $12,500       $5,000       $3,000
CAC payback, months of gross profit                    >120         13.4          2.5
Lifetime gross profit per employer                     $880      $18,704     $122,341
Lifetime gross profit / CAC                            0.1x         3.7x        40.8x

MONTHS TO MILESTONE (month 1 = first sales month)                                       
Month reaching $10,000 MRR                         month 41     month 19     month 10
  paying employers then                                  29           17            7
  pilots started by then                                113           48           24
  sales + marketing spent by then                  $541,500     $182,000      $84,000
Month reaching $50,000 MRR                              >72     month 35     month 17
  paying employers then                                   -           89           41
  pilots started by then                                  -          216           90
  sales + marketing spent by then                         -     $718,000     $267,000
Month reaching $100,000 MRR                             >72     month 49     month 21
  paying employers then                                   -          167           74
  pilots started by then                                  -          405          150
  sales + marketing spent by then                         -   $1,250,000     $423,000

MRR AT MONTH                                                                         
  month 6                                                $0           $0       $2,100
  month 12                                             $678       $3,082      $18,466
  month 18                                           $1,367       $8,988      $66,728
  month 24                                           $3,296      $20,385     $149,053
  month 36                                           $8,052      $57,213     $383,173
  month 48                                          $12,935      $97,210     $602,090
  month 60                                          $16,322     $128,596     $796,134
  month 72                                          $18,673     $153,225     $968,132
Pilot fees collected in first 12 months             $12,000      $20,250      $54,000

4a. BASE CASE: WHAT IF THE PRICE CHANGES? (assumes sales pace does not change)
Price/member/mo      Gross margin  Break-even lift  Employers $100K    Reach $100K
----------------------------------------------------------------------------------
$2.00                         26%             1.9%              333            >72
$3.00                         50%             2.4%              222       month 63
$4.00                         62%             3.0%              167       month 49
$5.00                         70%             3.5%              133       month 43
$6.00                         75%             4.1%              111       month 39

4b. BASE CASE: WHAT IF EMPLOYERS ARE BIGGER OR SMALLER?
Members/employer       Revenue/mo   Gross margin   CAC payback mo  Employers $100K
----------------------------------------------------------------------------------
50                           $200            14%             >120              500
100                          $400            50%             24.9              250
150                          $600            62%             13.4              167
250                        $1,000            72%              6.9              100
400                        $1,600            78%              4.0               62

4c. BASE CASE: WHAT IF REWARDS ARE BIGGER? (1x = data-contract point values)
Point values    Max $/person/yr  Avg paid/member   Employer cost  Break-even lift
---------------------------------------------------------------------------------
1x                          $32           $10.89          $9,679             3.0%
2x                          $64           $21.79         $11,438             3.5%
5x                         $160           $54.47         $16,715             5.2%
10x                        $320          $108.93         $25,510             7.8%

5. PRICING OPTIONS: our revenue per employer per month (same costs as section 1)
                                               Conservative         Base   Optimistic
-------------------------------------------------------------------------------------
A. $4 per member per month                             $360         $600       $1,400
   gross margin                                          7%          62%          87%
A2. Same, with $500/month minimum                      $500         $600       $1,400
   gross margin                                         33%          62%          87%
B. $75 per location per month                          $600         $750       $1,125
   gross margin                                         44%          70%          84%
C. $1,500 flat per 90-day pilot (per month)            $500         $500         $500
   gross margin                                         33%          55%          65%
Locations per employer                                    8           10           15

6. BASE CASE: HOW MANY MEMBERS A PILOT NEEDS TO PROVE A LIFT (two groups, 80% power, 5% significance)
                                                 No program    With lift  Members/group
---------------------------------------------------------------------------------------
Chance a member quits within 3 months                 11.8%                            
  members per group to detect a 10% lift                           10.6%         11,202
  members per group to detect a 20% lift                            9.4%          2,668
  members per group to detect a 30% lift                            8.3%          1,125
Chance a member quits within 12 months                39.5%                            
  members per group to detect a 10% lift                           35.5%          2,353
  members per group to detect a 20% lift                           31.6%            572
  members per group to detect a 30% lift                           27.6%            245

One base employer has 150 members; expected quits                                         
  during a 90-day pilot                                                            17.7

Sanity checks: all passed
```
