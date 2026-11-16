# Pricing: options, gifts, students, and a simple price test

*Finance, 2026-11-16. Numbers come from `docs/finance-app/model.py` (sections 8a-8c, base case). Changes in conversion and churn at other prices are **assumptions**, and the price test exists to replace them with real numbers. Competitor prices are in the research team's `docs/app-research/competitors.md`.*

## The short version

- **Recommendation:** keep **$60/year** as the main plan and show **$10/month** as the alternative, so a year costs about half of paying monthly. Offer a **$36/year student price**, a **$60 "give a year" gift**, and a **$149 founding-member lifetime path**, capped at the first 200 buyers and sold only for a stated launch window.
- **Why:** monthly members are worth about half as much as annual ones ($42 vs $80 of lifetime gross profit). Monthly payments also lose 7.9% to fees against 4.6% for annual. And the path is finite, so people who pay monthly can leave once they finish. $10/month is the Education-app median (RevenueCat 2026: $9.99), and $60/year sits between the median annual price ($44.99) and paid money apps like YNAB ($109) and Bloom ($99.99), per the research file.
- **The honest caveat:** the four options are within about 10% of each other on 24-month gross profit, except the lifetime path. The differences depend on conversion guesses, so **test, don't argue**. At our traffic, a clean A/B test of conversion would take more than a year (table 8c), so the test plan below uses revenue per free signup and a pre-set decision rule.

## The options (base case, per 1,000 free signups)

```
8a. BASE CASE: PRICING OPTIONS PER 1,000 FREE SIGNUPS (conversion changes are ASSUMPTIONS)
Option                                    Conv.  Members   1st pay       LTV  GP 24 mo Max $/signup  Mbrs $10K
--------------------------------------------------------------------------------------------------------------
A. $8/mo or $60/yr (draft)                 4.0%       40    $28.76    $60.89    $2,067        $0.81      1,890
A2. $10/mo or $60/yr (pricier monthly)     3.8%       38    $36.02    $70.58    $2,233        $0.89      1,887
B. $12/mo or $90/yr                        3.0%       30    $43.29    $88.14    $2,288        $0.88      1,267
C. $149 one-time lifetime path             2.8%       28   $127.05   $120.95    $3,387        $1.13        n/a
```

How to read it: *Conv.* = share of free signups who pay (assumed). *1st pay* = average first payment we keep. *LTV* = lifetime gross profit per paying member. *GP 24 mo* = gross profit from 1,000 free signups over 24 months. *Max $/signup* = the most we could pay for a free signup and still have LTV/CAC of 3. *Mbrs $10K* = paying members needed for $10K MRR.

### Option A: $8/month or $60/year (the draft)

- **Pros:** an easy "less than a lunch a month" price for 18-30 year olds. It is the cheapest to try, so it gets the most members, and the most members means the most learning about churn. The annual plan already saves 37%.
- **Cons:** the lowest lifetime value ($61). The fixed 30-cent Stripe fee takes 7.9% of every $8 payment. And the monthly plan is a cheap way to binge the path and cancel.

### Option A2: $10/month or $60/year (recommended launch price)

- **Pros:** the same $60 year as the draft, with a monthly price that makes the year obviously better ("6 months' price for 12"). The model assumes 15 more points of new members choose annual, and only 5% fewer convert: LTV rises from $61 to $71 and 24-month gross profit by about 8%. It matches the Education median monthly price.
- **Cons:** some price-sensitive people who would have paid $8 monthly won't pay at all. The 5% loss is a guess, which is why it's test arm 1.

### Option B: $12/month or $90/year

- **Pros:** the highest LTV of the subscriptions ($88) and the fewest members needed for $10K MRR (1,267). It's still cheaper than YNAB or Bloom.
- **Cons:** the model assumes 25% fewer people convert and 10% more churn; RevenueCat finds higher-priced apps keep fewer subscribers (23% vs 36% median retention). It's a hard sell for a beginner audience before we have reviews and proof. It needs about 30 paying members per 1,000 signups, so each test takes longer. Revisit after 6 months of reviews and retention data.

### Option C: $149 one-time "lifetime path"

- **Pros:** it fits what the product is: a finite path you finish. The cash arrives up front ($127 kept on average, after student discounts, fees and refunds), there's no churn, and it earns the most gross profit per 1,000 signups even if 30% fewer people buy ($3,387 vs $2,067 over 24 months). It also fits "paid by you, not by banks": one honest price, no renewals.
- **Cons:** no recurring revenue, so MRR targets don't apply and growth depends entirely on new buyers. Every lifetime member keeps costing hosting, support and the yearly refresh for as long as the product runs (the model charges 24 months of running cost). And it caps what we can earn from our happiest members if we later add an AI tutor or new levels. Define "lifetime" as the life of the product and say what's included.
- **How to use it:** as a founding-member offer, capped at 200 buyers and sold for a real, stated window (not a fake countdown). It raises launch cash ($25K if it sells out) and measures willingness to pay. Keep the subscription as the main offer.

## Gift memberships

- **What:** "Give a year of Patient Money" for $60 (the annual price), sold as a code. There's no auto-renew and no card is stored for the recipient. After 12 months the recipient is invited to continue at their own price. Push it twice a year: graduation season (May-June) and the December holidays. It suits parents, grandparents and mentors of new graduates and first-job starters.
- **Numbers (8b):** about $54 of gross profit per gift after fees and a year of running costs. If 20% of recipients then pay for a second year themselves (ASSUMPTION), each gift is worth about $70. That's more than a typical member's $61, with no acquisition cost, because the giver brings the recipient.
- **Watch-outs:** gift codes can count as gift certificates under federal and state rules on expiry and unused balances. Ask the attorney whether a code can expire and what happens to unredeemed codes (part of the legal review in `launch-budget.md`). Keep refunds simple: a full refund before the code is redeemed.
- **Later:** bulk gift codes (e.g. 10 for a graduating class or a mentoring program) at the same price, invoiced through Stripe.

## Student discount

- **What:** 40% off the annual plan: **$36/year** (about $3 a month). Monthly stays at full price, so students are pushed to annual. Verify with a school (.edu) email address at launch. A paid verification service can come later if abuse appears.
- **Numbers (8b):** we keep $34.22 per student annual payment. At the base assumption that 20% of members are students, MRR per member drops from $5.75 to $5.29 (8%). The bet is that student word of mouth brings more than that 8% back.
- **Pros:** the core audience is 18-30, and many have little income. Similar products already do this: Spotify charges students about half price ($6.99 vs $12.99), and YNAB gives college students a free year (research file). And it is generous in a way that matches the brand.
- **Cons:** our target also includes young people who have just started earning and are no longer students; they pay full price, which is fair because they can. There's some cannibalization from students who would have paid full price. Free Level 1 already serves people who can't pay anything.

## Price test plan (simple)

**Rules for every test:** each person sees one price, the same one every time (tied to their account or browser). Members keep the price they joined at. Never show a made-up "was" price crossed out, or a fake deadline. And the checkout states the renewal price, date and how to cancel. Online sign-up must allow online cancellation (California's automatic renewal law, amended effective July 1, 2025; see https://www.cooley.com/news/insight/2025/2025-06-04-california-automatic-renewal-law-amendments-take-effect-on-july-1-2025). Annual plans need a renewal reminder; confirm the timing with the attorney.

1. **Before launch (weeks -4 to 0): ask the waitlist.** Show the waitlist page with the price. Ask 4 willingness-to-pay questions: at what price is it too cheap to trust, a bargain, getting expensive, too expensive? 100+ answers give a range. Open the 200-seat founding-member lifetime offer to the waitlist only.
2. **Launch to day 90: test A vs A2.** Split new visitors 50/50 between $8/$60 and $10/$60 (two Stripe price IDs, assigned at random). The decision metric is **gross profit per free signup at day 60**, not conversion alone, because A2 is designed to move people to annual. Decision rule, written down before starting: **pick A2 unless its conversion is more than 25% lower than A's**, or its revenue per signup is lower. Expect directional evidence only. Telling 4% from 3% conversion takes about 5,300 signups per arm (table 8c), more than the base case gets in its first year. So re-check at month 6.
3. **Months 4-6: try the annual price.** If A2 holds, test $60 vs $90 for the annual plan with new visitors, using the same rule. Pricier annual plans may convert fewer people but bring in more per signup.
4. **Gifts and students run alongside.** They're separate checkouts, so they don't disturb the test. Track gift redemptions and the student share of members.
5. **What to record each week:** visitors, free signups, paying members by plan and price arm, refunds, first monthly renewals, and annual auto-renew switch-offs (the measurement table in `unit-economics.md`).

```
8c. BASE CASE: FREE SIGNUPS PER PRICE ARM TO DETECT A CONVERSION CHANGE (80% power, 5% significance)
Price A conv.     Price B conv.   Signups/arm  Months at m6 pace
----------------------------------------------------------------
4.0%                       2.8%         3,572               11.8
4.0%                       3.0%         5,292               17.5
4.0%                       5.0%         6,735               22.2
4.0%                       6.0%         1,858                6.1
```

```
8b. BASE CASE: GIFTS AND STUDENT DISCOUNT
                                                                 Value
----------------------------------------------------------------------
Gift: 12 months at the annual price, net of costs               $54.19
  + 20% of recipients then pay themselves                       $70.17
Student price: annual                                           $36.00
  kept per student annual payment (Stripe)                      $34.22
MRR per member with no student discounts                         $5.75
MRR per member at base student share                             $5.29
```
