# Unit economics: the Patient Money membership

*Finance, 2026-11-15. Every number here comes from `docs/finance-app/model.py`. Run `python3 docs/finance-app/model.py` to rerun it after you change the inputs at the top of that file. This is not a forecast. It is arithmetic on sourced figures (Stripe, Apple, Claude, voice and video price lists, subscription-app benchmarks) plus assumptions that are labeled, with a range.*

## The short version (base case)

| | Base case | Range (conservative to optimistic) |
|---|---|---|
| Price | **$8/month or $60/year** (draft) | same in all three |
| What we keep from a payment (web checkout, Stripe) | $7.37 of $8 (7.9% fees); $57.24 of $60 (4.6%) | same |
| What we keep through the App Store | $6.80 / $51.00 at 15%; $5.60 / $42.00 at 30% | same |
| Free-to-paid conversion | **4%** of free signups within ~3 months | 2% to 7% |
| Monthly-plan churn | **15% a month** (14% still paying after a year) | 20% to 9% |
| Annual plan, first renewal | 30% | 20% to 40% |
| **LTV** (lifetime gross profit of one new member) | **$61** ($42 monthly plan, $80 annual plan) | $40 to $95 |
| MRR per active member | $5.29 (75% of active members are on annual) | $5.48 to $5.33 |
| **Cost per video, cash** | **$1.69** (Claude $1.26 + voice $0.43) | $6.83 to $0.42 |
| Founder review per video | 55 minutes (about $37 of time at $40/hour) | 106 to 36 minutes |
| Whole 45-lesson library | $76 cash + 41 hours of founder review | $307 + 80 h to $19 + 27 h |
| Running cost per member | $0.25 a month (3% of the price); an AI tutor would add about $0.08 | $0.44 to $0.12 |
| Fixed costs | $131 a month (29 members cover it) | same |
| CAC: creators / paid ads | $167 / $120 per paying member: **both lose money** | $2,000 / $700 to $15 / $24 |
| **Members for $10K MRR** | **1,890**, which needs about 3,500 new free signups a month | 1,826 to 1,876 |
| Month we reach $10K MRR | **month 35** | never in 6 years to month 13 |
| $50K / $100K MRR | not within 6 years in the base case (needs ~17,700 / ~35,400 free signups a month) | never to months 24 / 29 |

**In one sentence:** making the product is almost free (under $2 of cash per video), and serving a member costs about 25 cents a month, so the business lives or dies on **reach** (free signups from short videos) and **retention** (how long members keep paying); at $8/$60 and 4% conversion, paying for signups with creators or ads doesn't pay back.

## The 3 numbers that matter most

1. **Free-to-paid conversion (base 4%).** It sets how many free users we need and what we can afford to pay for them. Each free signup is worth about $2.44 of lifetime gross profit in the base case ($0.79 in the conservative case, $6.67 in the optimistic one). A paid channel is healthy (LTV/CAC of 3) only if a free signup costs under **$0.81**. Today's creator and ad estimates are $4.80 to $6.67. Table 7a shows the trade-off.
2. **Retention: monthly churn and the annual renewal (base 15% and 30%).** Together they set LTV. A monthly member pays for about 6.7 months; an annual member for about 1.7 years. The curriculum is finite: 45 lessons is about 135 minutes of video, so a motivated member can finish Levels 2-5 in a few weeks. The Money Map, spaced review and the crash simulator have to give people a reason to stay after they finish. This is why the annual plan matters: annual members are worth almost twice as much ($80 vs $42).
3. **Organic free signups per month (base 300 in month 1, growing 10% a month to 8,000).** This is the least certain input and it drives the timeline. $10K MRR needs about 3,500 free signups a month to hold, and $100K needs about 35,000. If short-video reach stalls at 4,000 a month, $10K MRR slips from month 35 to month 50 (table 7c).

## What the model says, in plain English

### 1. Revenue per member

- **Web checkout keeps more.** Stripe takes 2.9% + 30 cents, plus 0.7% for subscriptions and 0.5% for automatic sales tax. That is 7.9% of an $8 payment but only 4.6% of a $60 one, because the 30 cents is fixed. The App Store takes 15% (Small Business Program) or 30% (standard first year).
- **Annual members are most of the base.** Half of new members pick annual in the base case, but they stay so much longer that they become 75% of the people paying at any moment. That's why MRR per member ($5.29) is closer to the annual $5/month than the monthly $8.
- **Discounts and refunds:** the base assumes 20% of members are students at 40% off, and 3% of revenue is refunded. The average monthly payment is $7.36 and the average annual is $55.20.
- **App stores later:** if half of members came through the App Store at 30%, lifetime revenue per member would fall from $64 to $56 (table 1c). In the US, apps can currently link out to web checkout, and Apple charges nothing on that while a court sets a rate (Apple proposed 15%). Keep Stripe checkout as the main door, even in a native app.

```
1a. WHAT WE KEEP FROM ONE PAYMENT (list price, before refunds and student discounts)
                                                     Monthly      Annual  Annual / 12
-------------------------------------------------------------------------------------
List price per payment                                 $8.00      $60.00        $5.00
Stripe fees (2.9% + 30c + 0.7% + 0.5% tax)             $0.63       $2.76
  as % of price                                         7.9%        4.6%
Kept via Stripe web checkout                           $7.37      $57.24        $4.77
Kept via App Store at 15% (small business)             $6.80      $51.00        $4.25
Kept via App Store at 30% (standard, year 1)           $5.60      $42.00        $3.50
```

```
1c. REVENUE KEPT PER NEW MEMBER OVER THEIR LIFETIME, BY CHECKOUT CHANNEL (before running costs)
                                              Conservative          Base    Optimistic
--------------------------------------------------------------------------------------
All web (Stripe)                                       $44           $64           $98
Half via App Store at 15%                              $41           $61           $93
Half via App Store at 30%                              $38           $56           $85
All via App Store at 30%                               $32           $47           $72
```

### 2. Funnel and LTV

- **Conversion:** RevenueCat's 2026 report puts the median freemium app at 2.1% of downloads paying within 35 days, and Education apps at 3.1% (iOS, including hard paywalls). A web signup with an email address is usually a warmer lead than an app download, so the base uses 4% and the conservative case uses the 2% median.
- **Churn:** RevenueCat's median monthly plan keeps only about 8-10% of subscribers after 12 months, which is roughly 18-19% churn a month. Our conservative case (20%) is that median app. The base (15%) assumes we beat it because people chose to pay on the web and the lessons build on each other. That is an assumption to test, not a fact.
- **Annual renewals:** RevenueCat's median first annual renewal is 23-40% by category. The base uses 30%, then 55% at later renewals.

```
2. FUNNEL AND LIFETIME VALUE (LTV = lifetime gross profit; Stripe checkout)
                                              Conservative          Base    Optimistic
--------------------------------------------------------------------------------------
Free-to-paid conversion (within ~3 months)            2.0%          4.0%          7.0%
Monthly plan: churn per month                          20%           15%            9%
  = still paying after 12 months                        7%           14%           32%
  expected months paid                                 5.0           6.7          11.1
Annual plan: first renewal rate                        20%           30%           40%
  later renewals                                       45%           55%           65%
  expected years paid                                 1.36          1.67          2.14
Blended: average months a member stays                 9.0          13.3          19.9

Running cost per member per month                    $0.44         $0.25         $0.12
Gross profit per month, monthly plan                 $5.81         $6.28         $6.64
Gross profit per year, annual plan                  $43.52        $47.93        $51.21
LTV, monthly-plan member                            $29.03        $41.89        $73.78
LTV, annual-plan member                             $59.34        $79.89       $109.73
LTV, blended new member                             $39.64        $60.89        $95.35
Gross profit per member-month (blended)              $4.42         $4.57         $4.80
LTV per FREE signup (LTV x conversion)               $0.79         $2.44         $6.67
```

### 3. Content cost

- **Claude:** about $1.26 per lesson in the base case. That covers 3 script drafts and 3 compliance and fact reviews on Opus 5.5, scene and chart code on Sonnet 5.5, and hooks for 2 short clips. It includes a 1.5x allowance for failed runs. The conservative case runs everything on Opus with twice the retries ($5.10); the optimistic case uses Sonnet, prompt caching and the Batch API ($0.32).
- **Voice (TTS):** since the provider is undecided, the model uses a per-minute range: about $0.04/minute (Google Chirp 3 HD), $0.14 (ElevenLabs at $0.08 per 1,000 characters, 2 takes), and $0.43 (Google Studio voices, 3 takes). A 3-minute lesson costs $0.10 to $1.73 to narrate.
- **Rendering** is local ffmpeg, so it's free.
- **The real cost is founder review:** 55 minutes per lesson in the base case (45 to watch, check facts and approve, plus 5 per short clip), about 41 hours for the library. At $40 an hour that's about $1,650 of time against $76 of cash.
- **Yearly refresh:** re-making 25% of lessons (contribution limits, tax rules and rates change) plus a 10-minute fact check of every lesson costs about $19 cash and 18 hours a year.

```
3. CONTENT COST (Claude for script + review + visuals, TTS per minute, founder review)
                                              Conservative          Base    Optimistic
--------------------------------------------------------------------------------------
CLAUDE TOKENS PER LESSON (incl. retries)
  Script drafts                                      $0.96         $0.38         $0.05
    model, calls                                   opus x4       opus x3     sonnet x2
  Compliance + fact review                           $0.70         $0.26         $0.07
    model, calls                                   opus x4       opus x3       opus x2
  Scenes, charts, animation code                     $3.36         $0.57         $0.19
    model, calls                                   opus x6     sonnet x4     sonnet x3
  Short-clip hooks + captions                        $0.08         $0.04         $0.00
    model, calls                                 sonnet x2     sonnet x2      haiku x2
  Claude total per lesson                            $5.10         $1.26         $0.32
Narration (TTS) per finished minute                  $0.43         $0.14         $0.04
  price per 1,000 characters, takes             $0.16 x3.0    $0.08 x2.0    $0.03 x1.5
Minutes per lesson                                     4.0           3.0           2.5
Narration per lesson                                 $1.73         $0.43         $0.10
Rendering (ffmpeg, local)                            $0.00         $0.00         $0.00
CASH COST PER VIDEO                                  $6.83         $1.69         $0.42
Founder review per lesson + its clips, min             106            55            36
  valued at $40/hour                                $70.67        $36.67        $24.00
ALL-IN COST PER VIDEO (cash + time)                 $77.50        $38.36        $24.42

LIBRARY OF 45 LESSONS
  Minutes of video                                     180           135           112
  Cash                                                $307           $76           $19
  Founder review hours                                79.5          41.2          27.0
  All-in (cash + time)                              $3,487        $1,726        $1,099
YEARLY REFRESH
  Lessons re-made per year                             35%           25%           15%
  Cash per year                                       $108           $19            $3
  Founder hours per year                              39.1          17.8           7.8
  All-in per year                                   $1,671          $732          $315
```

### 4. Running costs

- **Per member:** about $0.25 a month. Most of it is support time (0.04 tickets a month at 10 minutes, valued at $30/hour). Video delivery is about 1.5 cents (Cloudflare Stream: $1 per 1,000 minutes watched).
- **AI tutor, if added:** about $0.08 per member a month on Sonnet 5.5 (10 questions), $0.49 on Opus 5.5 with heavy use (20 questions), or under a cent on Haiku 5.5. It's affordable on any model. The risk is advice and compliance (an "education, not advice" filter on every answer), not cost.
- **Fixed:** about $131 a month for hosting, video storage, a voice plan, Claude for support and social drafts, bookkeeping, domain and email. 29 members cover it.
- **Email grows with the free list:** about $0.009 per free contact a month above 1,000. At 100,000 free contacts that's about $900 a month, so prune inactive contacts.

### 5. Acquisition

- **Organic short video** costs no cash. The clips come from the lessons. It costs founder time: 6 hours a week is about $87 per paying member in month 1 at $40/hour, falling to about $30 by month 12 as reach grows.
- **Creators on flat fees:** a $400 post with 25,000 views, 0.8% clicking through and 30% signing up brings about 60 free signups ($6.67 each), so **$167 per paying member against a $61 LTV**. Pay creators per signup or as an affiliate share instead (for example 30-50% of the first payment), so the cost can't exceed what a member is worth.
- **Paid ads:** at a $1.20 click and 25% landing-page signup, a free signup costs $4.80, so **$120 per paying member**. 2026 benchmarks put Meta traffic clicks around $0.60 and education lead clicks at $1.25-2.10, with finance higher.
- **What you can pay:** under $0.81 per free signup for a 3:1 LTV/CAC, or under $1.10 to earn it back within 6 months. The model runs small tests, then stops any channel below 1.5x.

```
5. ACQUISITION BY CHANNEL (CAC = cost per free signup / conversion)
                                              Conservative          Base    Optimistic
--------------------------------------------------------------------------------------
CREATORS (FLAT FEE)
  Free signups per sponsored post                       15            60           240
  Cost per free signup                              $40.00         $6.67         $1.04
  CAC per paying member                             $2,000          $167           $15
  Payback, months of gross profit                     >120          36.5           3.1
  LTV / CAC                                           0.0x          0.4x          6.4x
  Kept after test?                                      no            no           yes
PAID ADS
  Cost per free signup                              $14.00         $4.80         $1.71
  CAC per paying member                               $700          $120           $24
  Payback, months of gross profit                     >120          26.3           5.1
  LTV / CAC                                           0.1x          0.5x          3.9x
  Kept after test?                                      no            no           yes
ORGANIC SHORT VIDEO (clips from lessons)
  Cash CAC                                              $0            $0            $0
  Founder hours per week                                 8             6             5
  Free signups, month 1                                100           300           600
  Growth per month, cap                          6%, 2,000    10%, 8,000   15%, 25,000
  Time-valued CAC, month 1                            $693           $87           $21
  Time-valued CAC, month 12                           $365           $30            $4

MOST YOU CAN PAY PER FREE SIGNUP
  for LTV/CAC = 3                                    $0.26         $0.81         $2.22
  for payback within 6 months                        $0.53         $1.10         $2.02
```

```
7a. BASE CASE: LTV/CAC BY COST PER FREE SIGNUP (rows) AND CONVERSION (columns); 3x is healthy
Cost/signup           2%        4%        6%        8%
------------------------------------------------------
$1.00               1.2x      2.4x      3.7x      4.9x
$2.50               0.5x      1.0x      1.5x      1.9x
$5.00               0.2x      0.5x      0.7x      1.0x
$10.00              0.1x      0.2x      0.4x      0.5x
```

### 6. Targets and timeline

- **Members needed:** about 1,900 for $10K MRR, 9,450 for $50K and 18,900 for $100K. That's roughly the same in all scenarios, because MRR per member hardly changes. What changes is **how many free signups a month it takes to hold that level**: 3,544 in the base case for $10K, but 10,168 in the conservative case.
- **Timeline (base):** 198 members and $1,105 MRR at month 12; 638 and $3,545 at month 24; $10K MRR at month 35. The base plateaus around $21K MRR, because organic reach is capped at 8,000 signups a month and the paid channels fail their tests. Reaching $50K needs better conversion and more reach (6% and 16,000 a month gets there in month 51; table 7c), or a paid channel that passes.
- **Cash:** running costs are so low that the base case covers them from month 7, and the operating cash low point is only about -$860. The real cash needs are the launch budget (see `launch-budget.md`) and the founder's own living costs, which the model does not include.

```
6. TARGETS AND MONTHS TO REACH THEM (month 1 = public launch)
                                                     Conservative               Base          Optimistic
--------------------------------------------------------------------------------------------------------
$10,000 MRR
  Paying members needed                                     1,826              1,890               1,876
  New members per month to hold it                            203                142                  94
  Free signups per month to hold it                        10,168              3,544               1,349
  Month reached (path below)                                  >72           month 35            month 13
  Free signups so far, total                                    -             81,857              35,396
  Marketing cash spent so far                                   -             $3,200             $18,512
$50,000 MRR
  Paying members needed                                     9,128              9,452               9,380
  New members per month to hold it                          1,017                709                 472
  Free signups per month to hold it                        50,841             17,722               6,743
  Month reached (path below)                                  >72                >72            month 24
  Free signups so far, total                                    -                  -             182,744
  Marketing cash spent so far                                   -                  -             $92,972
$100,000 MRR
  Paying members needed                                    18,257             18,904              18,759
  New members per month to hold it                          2,034              1,418                 944
  Free signups per month to hold it                       101,682             35,444              13,485
  Month reached (path below)                                  >72                >72            month 29
  Free signups so far, total                                    -                  -             361,782
  Marketing cash spent so far                                   -                  -            $182,904

PATH SNAPSHOTS (month: members / MRR)
  month 6                                                10 / $60          86 / $498        574 / $3,285
  month 12                                              20 / $117       198 / $1,105      1,684 / $9,452
  month 24                                              44 / $253       638 / $3,545     9,287 / $52,081
  month 36                                              91 / $514    2,007 / $11,142   30,652 / $169,744
  month 48                                           183 / $1,036    3,360 / $18,252   41,114 / $225,552
  month 60                                           308 / $1,724    3,790 / $20,358   46,778 / $254,309
  month 72                                           340 / $1,881    4,008 / $21,376   50,210 / $271,133
  free signups in month 12                                    190                856               4,514
  free signups in month 24                                    382              2,686              24,547
Covers its running + marketing costs from                month 21            month 7             month 4
Lowest cumulative operating cash                          -$1,766              -$859                  $0
Cumulative operating cash at month 24                     -$1,479            $31,988            $422,654
(both exclude founder pay and the launch budget)
```

```
7c. BASE CASE: MONTH EACH TARGET IS REACHED, BY CONVERSION AND ORGANIC REACH (cap on free signups/month)
Conversion    Organic cap     $10,000     $50,000    $100,000
-------------------------------------------------------------
2%                  4,000         >72         >72         >72
2%                  8,000    month 58         >72         >72
2%                 16,000    month 43         >72         >72
4%                  4,000    month 50         >72         >72
4%                  8,000    month 35         >72         >72
4%                 16,000    month 35         >72         >72
6%                  4,000    month 32         >72         >72
6%                  8,000    month 31         >72         >72
6%                 16,000    month 31    month 51         >72
```

## Riskiest assumptions

1. **Organic reach.** 300 free signups in month 1, growing 10% a month, is a guess with no data behind it yet. It's the biggest driver of the timeline.
2. **Conversion of 4%** is about twice the freemium app median (2.1%).
3. **Retention after the path is finished.** Monthly churn of 15% beats the app median (~18-19%), yet the content is finite. If people finish and leave, churn could be worse than the conservative 20%.
4. **Creator and ad costs per signup:** rough guesses from vendor benchmarks, not tests.
5. **Founder review time** (55 minutes per lesson). If it doubles, launch slips by about a week of full-time work, not by money.

## What to measure in the first 90 days

Set these up before launch. Use privacy-friendly analytics that count events, never Money Map numbers or quiz answers (member data stays on the device).

| # | Measure | How | Base target | Red flag |
|---|---|---|---|---|
| 1 | Free signups per week, by source | UTM tags and creator codes on every link (TikTok, Reels, Shorts, each creator, each ad) | ~75/week in month 1, growing | under 25/week after month 2 |
| 2 | Visit-to-signup rate on the landing page | analytics funnel | 25%+ | under 15% |
| 3 | Level 1 completion | share of signups who finish all free lessons within 14 days | 30%+ (ASSUMPTION) | under 15% |
| 4 | **Free-to-paid conversion by weekly cohort** | at 30, 60 and 90 days after signup | **4%** | **under 2%** |
| 5 | Plan mix | share of new members choosing annual | 50%+ | under 30% |
| 6 | **First monthly renewal** | share of month-1 monthly members who pay a second time | **85%** (= 15% churn) | **under 75%** |
| 7 | Annual members who switch off auto-renew | Stripe subscription status (Education apps see ~30% of annual cancellations in month 1) | under 25% by day 90 | over 40% |
| 8 | Lessons per member per week, and days to finish Level 5 | event counts | finishing takes 6+ weeks | most finish in under 3 weeks |
| 9 | Refunds and disputes | Stripe | under 3% of revenue | over 5%, or any dispute pattern |
| 10 | Cost per free signup, each creator or ad test | spend / tagged signups | **under $0.81** to keep going | over $2.50: stop |
| 11 | Claude spend and founder minutes per lesson | Claude Console usage per batch; a timer log | $1.26 and 55 minutes | over $5 or 2 hours |
| 12 | Support tickets per member per month | inbox tag | under 0.04 | over 0.10 |

**Decision points at day 90:** if conversion is at least 4% and first monthly renewal is at least 85%, the base case holds. Keep the founder on organic video and turn creators into per-signup deals. If conversion is under 2%, fix the free-to-paid step before spending anything on acquisition: the Level 1 ending, the paywall moment, and trust signals. If members finish the path in under 3 weeks, push annual and lifetime pricing (`pricing.md`) and move the Money Map and spaced review earlier.

## Sources (checked 2026-11-15 unless noted)

- Stripe pricing (cards 2.9% + 30c; Billing 0.7%; Tax 0.5%; disputes $15): https://stripe.com/pricing
- Apple Small Business Program (15%): https://developer.apple.com/app-store/small-business-program/ ; subscriptions after year one at 15%: https://www.revenuecat.com/blog/engineering/app-store-fees ; Google Play subscriptions 15%: https://support.google.com/googleplay/android-developer/answer/112622
- US external-purchase links, 0% commission while a court sets a rate (reported Aug 2026): https://macdailynews.com/2026/08/14/u-s-supreme-court-clears-path-for-app-store-commission-showdown-as-apple-must-defend-its-rates-in-lower-court/
- Claude API prices (Opus 5.5 $4/$20, Sonnet 5.5 $2/$10, Haiku 5.5 $0.10/$0.50 per million tokens; Batch 50% off), as of 2026-11-03: platform.claude.com/docs/en/about-claude/pricing
- ElevenLabs API ($0.08 per 1K characters for v2/v3/v4; $0.04 Flash/Turbo; Creator plan $22/month): https://elevenlabs.io/pricing/api
- Google Cloud Text-to-Speech (Chirp 3 HD $30, Neural2 $16, Studio $160 per 1M characters): https://cloud.google.com/text-to-speech/pricing
- Cloudflare Stream ($5 per 1,000 minutes stored, $1 per 1,000 delivered): https://developers.cloudflare.com/stream/pricing/ ; Workers from $5/month: https://developers.cloudflare.com/workers/platform/pricing/ ; Vercel Pro $20/month: https://vercel.com/pricing
- Kit email (free to 10,000; Creator $33/month at 1,000): https://kit.com/pricing
- RevenueCat State of Subscription Apps 2026, Education (median $9.99/month, $44.99/year, 3.1% D35 download-to-paid, refunds ~3-4%): https://www.revenuecat.com/state-of-subscription-apps-2026-education ; retention and renewals: https://www.revenuecat.com/sosa-2026-insights-part-2 ; summaries: https://9to5mac.com/2026/05/27/new-report-shows-annual-app-subscribers-rarely-return-after-they-cancel/
- Freemium conversion benchmarks: https://chartmogul.com/reports/saas-conversion-report/ ; https://userpilot.com/blog/freemium-to-premium
- Meta ads benchmarks 2026 (vendor reports, rough): https://www.webtonic.io/blog/education-coaching-facebook-ads-statistics ; https://searchengineland.com/facebook-ad-costs-fall-as-traffic-and-lead-performance-improves-report-488433
- Creator rates 2026 ($200-1,000 per post at 10K-50K followers): https://ttcalculator.net/learn/brand-deal-rates-by-followers/ ; https://blog.hootsuite.com/influencer-pricing/
