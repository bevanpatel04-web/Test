# Pricing and retention benchmarks

*Research note for the founder. Checked 2026-11-15. All prices in USD.*

**How to read this.** Each number is labeled by source strength:
- **Filing**: a public company's SEC filing or results release.
- **Benchmark report**: a published report from a large dataset, such as RevenueCat (115,000+ apps) or Adapty (16,000+ apps). These firms sell subscription tooling, so the reports are also marketing. Their data is still the best available.
- **Official**: a company's own price or policy page.
- **Blog claim**: a vendor or affiliate blog with no clear method. Use only as color.
- **Unverified**: not confirmed in a primary source.

App benchmarks come from in-app (App Store / Google Play) purchases. We launch on the web, so treat them as a guide, not a forecast.

## 1. Typical prices

**Benchmark reports**

| Metric | Value | Data period | Source |
|---|---|---|---|
| Education apps, median monthly price | $9.99 | 2025 | [RevenueCat State of Subscription Apps 2026](https://www.revenuecat.com/state-of-subscription-apps-2026/) (benchmark report) |
| Education apps, median yearly price | $44.99, the highest yearly median of any category | 2025 | same |
| All categories, median monthly / yearly | $8 / $34.80 | 2025 | same |
| All categories (Adapty), median monthly / annual | $12.99 / $38.42 | 2025 | [Adapty education benchmarks](https://adapty.io/blog/education-app-subscription-benchmarks/) (benchmark report, 2026-04-07) |
| Education apps' revenue by plan length | Weekly 52%, annual 22%, one-time 17%, monthly 9% | 2025 | same |

*Caveat:* I read the RevenueCat figures from its report web page through an extraction tool. Re-check the education numbers in the report's own charts before quoting them externally.

**Peers we'd be compared with** (official unless marked)

| Product | Monthly | Annual | Annual discount vs 12x monthly | Source, date |
|---|---|---|---|---|
| Patient Money draft | $8 | $60 | 38% | BRIEF.md |
| Financebro: AI Finance Teacher | $14.99 | $59.99 | 67% | [App Store](https://apps.apple.com/app/id6769393561) via search, 2026 (**unverified**) |
| Duolingo Super | ~$12.99 | ~$83.99 | ~46% | third-party, Oct 2026 (**unverified**) |
| Bloom | $15 | $99.99 | 44% | [Bloom FAQ](https://bloomapp.com/faq), 2026-11-15 |
| YNAB | $14.99 | $109 | 39% | [YNAB pricing](https://www.ynab.com/pricing), 2026-11-15 |
| Brilliant | $30 | not shown | n/a | [Brilliant subscribe](https://brilliant.org/subscribe/), 2026-11-15 |
| Finimize Pro | ~$29 | $200 | 43% | [Finimize help](https://intercom.help/finimize-help/en/articles/11644196-what-does-finimize-pro-cost), 2026-11-15 |
| Coursera Plus | $59 | $399 list ($239 promo) | 44% | [Coursera Plus](https://coursera.org/courseraplus), 2026 |
| Khanmigo | ~$4 | ~$44 | ~8% | third-party (**unverified**) |
| Cleo | $5.99-$14.99 | n/a | n/a | [Cleo pricing](https://web.meetcleo.com/products/pricing), 2026-11-15 |

**Takeaway:** $60 a year sits above the education-app median and at the low end of the money-app peers. $8 a month is below every money peer and below the education median. Most peers price annual at 40-50% off monthly. Our draft gives 38%.

## 2. Free-to-paid and trial conversion

**Credible (filings and benchmark reports)**

| Metric | Value | Period | Source |
|---|---|---|---|
| Download to paid within 35 days, all apps (median) | 2.0% (iOS 2.6%, Google Play 0.9%) | 2025 | [RevenueCat 2026](https://www.revenuecat.com/state-of-subscription-apps-2026/) |
| Same, Education apps on iOS | 3.1% | 2025 | same |
| Freemium vs hard paywall, download to paid in 35 days | 2.1% vs 10.7% | 2025 | same |
| Download to trial, Education | 6.5% | 2025 | same |
| Trial to paid, all apps (median) | ~32% | 2025 | same |
| Trial to paid by trial length | 4 days or less: 25.5%; 5-9 days: 37.4%; 17-32 days: 42.5% | 2025 | same |
| Install to trial / trial to paid (Adapty global averages) | 10.9% / 25.6% | 2025 | [Adapty](https://adapty.io/blog/education-app-subscription-benchmarks/) |
| Education trial users vs direct buyers, 12-month value | +50.4% | 2025 | same |
| Duolingo paid subscribers / monthly active users | 13.1M / 153.1M = **8.6%** | Q3 2026 | [Duolingo shareholder letter, SEC](https://www.sec.gov/Archives/edgar/data/0001562088/000162828026069474/q3fy26duolingo9-30x26share.htm) (filing, 2026-11-03) |
| Coursera + Udemy paid subscribers / learners | ~1.6M / ~310M, about 0.5%. Learners are cumulative sign-ups, not active users | Q3 2026 | press summary of Q3 2026 results (**unverified** against the filing) |

**Blog claims (weaker)**
- "Freemium conversion 1-10%", "3-5% typical": common figures, attributed to Lenny's Newsletter and Kyle Poyar's data, which I didn't find in the original ([CrazyEgg](https://www.crazyegg.com/blog/free-to-paid-conversion-rate/), [Single Grain](https://www.singlegrain.com/blog/ms/free-to-paid-conversion-rates/)).
- "Education trial-to-paid 45-55%" ([AppsFinBoard](https://appsfinboard-landing-page.pages.dev/blog/subscription-pricing-paywall-optimization-mobile-apps/)): no stated source, and it conflicts with the reports above.
- "53% median trial-to-paid" attributed to Adapty ([RocketshipHQ](https://www.rocketshiphq.com/?p=5390)): conflicts with Adapty's own 25.6%.

**Takeaway:** For a freemium model like ours (free Level 1, paid Levels 2-5), plan on **2-3% of new sign-ups paying in their first month**. 5% would be strong. Duolingo's 8.6% of monthly users is a mature, best-in-class number.

## 3. Churn and retention

**Credible (benchmark reports)**

| Metric | Value | Period | Source |
|---|---|---|---|
| Still subscribed after 1 year, yearly plans (median) | 28% (was 31%) | 2025 | [RevenueCat 2026](https://www.revenuecat.com/state-of-subscription-apps-2026/) |
| Same, monthly plans | **8%** (was 10%) | 2025 | same |
| Same, weekly plans | 1.2% | 2025 | same |
| Year-1 retention of annual plans by price | Low-priced 36%, mid 26%, high 23% | 2025 | same |
| Share of annual-plan cancellations in month 1 | 35% overall; Education about 30% | 2025 | same, as cross-reported by [heise](https://heise.de/-11310636) |
| Refund rate | ~3-4% in most categories; North America 3.4% | 2025 | same |
| Cancellations from billing errors | Google Play 32.2% vs App Store 15.2% | 2025 | same |
| Monthly / annual trial subscribers still active at day 380 | 14.2% / 19.9% | 2025 | [Adapty](https://adapty.io/blog/education-app-subscription-benchmarks/) |

**What that means per month:** keeping 8% of monthly subscribers after a year works out to an average loss of about **19-20% per month**, heaviest in the first months. Adapty's 14.2% implies about 15% a month.

**Weaker**
- Recurly's churn page describes "a 3.27% average across industries". It's unclear from my read whether that is monthly ([Recurly](https://recurly.com/research/churn-rate-benchmarks/)). A search snippet from the same page gives B2C monthly churn of 6.77% vs 4.91% for B2B (**unverified**). Recurly measures web billing for mature brands, which explains why its churn looks lower than app data.
- Duolingo and Coursera do not publish churn.

**Takeaway:** Monthly members of a learning app mostly leave within a year. Annual plans keep about 3.5 times as many people, and cheaper annual plans keep more. Our curriculum also has an end, which adds a reason to leave.

## 4. Store fees vs web checkout

**The rules (official pages, read 2026-11-15)**
- **Apple Small Business Program:** "a reduced commission rate of 15% on paid apps and Apple In-App Purchases" for developers with up to $1M in proceeds in the prior calendar year, including new developers. You must enroll and list associated accounts ([Apple](https://developer.apple.com/app-store/small-business-program/)). Without it, subscriptions pay 30% in the first paid year, then 15% (widely reported; I didn't re-read Apple's agreement).
- **Google Play, in-app billing:** auto-renewing subscriptions pay "10% + 5% billing fee", 15% in total, for new and existing installs. In the US this applies from 2026-06-30 ([Play Console Help](https://support.google.com/googleplay/android-developer/answer/112622?hl=en)).
- **Stripe (web):** 2.9% + 30¢ per US card charge, +1.5% for international cards, +1% for currency conversion. Billing adds 0.7% of billing volume and Tax 0.5% per transaction (no-code option). Disputes cost $15 each ([Stripe pricing](https://stripe.com/pricing)).

**What we'd keep per charge** (Stripe column = 2.9% + 30¢ + 0.7% Billing + 0.5% Tax)

| Price | Web (Stripe) | Apple 15% (small business) | Apple 30% (year 1, not enrolled) | Google Play 15% | Google US link-out (10% to Google + Stripe) |
|---|---|---|---|---|---|
| $8/mo | **$7.37** (7.9% fees) | $6.80 | $5.60 | $6.80 | $6.57 |
| $9.99/mo | **$9.28** (7.1%) | $8.49 | $6.99 | $8.49 | $8.28 |
| $60/yr | **$57.24** (4.6%) | $51.00 | $42.00 | $51.00 | $51.24 |

Notes:
- Stripe's fixed 30¢ hurts small monthly charges. Annual plans lose under 5%.
- If we want Stripe to act as merchant of record and handle sales tax for us, its "Managed Payments" reportedly adds 3.5% ([vendor blog citing Stripe](https://dodopayments.com/blogs/stripe-managed-payments-fees-explained), **unverified**). Whether each state taxes a digital learning subscription is a question for Finance and a tax adviser.

## 5. US rules on steering users to web checkout (as of 2026-11-15)

**Apple**
- Apple's App Review Guidelines now say external purchase link entitlements "are not required for developers to include buttons, external links, or other calls to action in their United States storefront apps" ([guidelines 3.1.1(a)](https://developer.apple.com/app-store/review/guidelines/), read 2026-11-15).
- **Background.** The district court held Apple in contempt in April 2025 and barred any commission on linked-out purchases. In December 2025 the Ninth Circuit upheld the contempt finding but said Apple may seek a *reasonable* commission, to be set by the district court ([MacRumors](https://www.macrumors.com/2025/12/11/APPLE-APP-STORE-FEES-EXTERNAL-PAYMENT-LINKS/), 2025-12-11).
- **Supreme Court.** It agreed on 2026-06-30 to hear Apple's appeal, limited to the contempt standard (No. 25-1311) ([MacRumors](https://macrumors.com/2026/06/30/apple-epic-games-supreme-court); [docket](https://www.supremecourt.gov/docket/docketfiles/html/public/25-1311.html)). Epic's brief was due 2026-11-13 and Apple's reply 2026-12-14 (per search summaries, **unverified**). Justice Kagan declined to pause the fee-setting process (reported Aug 2026).
- **Apple's proposal.** On 2026-08-13 Apple proposed commissions on linked-out purchases of **15% for standard apps and 5% for Small Business Program apps**, with 10% for some partner programs and renewals ([9to5Mac](https://9to5mac.com/2026/08/13/apple-proposes-commissions-of-up-to-15-for-off-app-store-purchases-in-the-us/)). Epic opposes it.
- **Today:** Apple is reported to charge **0% on US linked-out purchases** while the rate is decided ([Courthouse News](https://www.courthousenews.com/apples-fight-over-commissions-for-linked-out-app-store-purchases-continues-in-district-court/), 2026-08-11). I found no rate set as of 2026-11-15 (**unverified**; this could change at any time).

**Google**
- **US external content links program:** for purchases made within 24 hours of a user following the link, Google charges **10% on recurring subscriptions, including renewals**, and 20% on other digital items (10% on the first $1M). Reporting started 2026-10-01 ([Play Console Help](https://support.google.com/googleplay/android-developer/answer/16470497?hl=en)).
- On Android, linking out saves us almost nothing compared with Google's own 15% billing (table above).
- Epic and Google reportedly withdrew a joint motion to change the injunction on 2026-07-15 ([Stash blog](https://www.stash.gg/blog/why-epic-and-google-just-walked-away-from-their-own-settlement), **unverified**).

**Gift cards inside iOS apps:** Apple's guidelines say "digital gift cards, certificates, vouchers, and coupons which can be redeemed for digital goods or services can only be sold in your app using in-app purchase" ([guidelines](https://developer.apple.com/app-store/review/guidelines/)). A link out to the web may still be allowed on the US storefront.

## 6. Gift subscriptions

**How others do it**
- **Brilliant** sells 1-month or 1-year gifts. The gift period starts when the recipient activates it, not when it was bought ([Brilliant help](https://brilliant.org/help/pricing-and-plans/how-do-i-gift-a-brilliant-premium-subscription/)).
- **Headspace** lets the buyer schedule a send date and write a note ([Headspace gift](https://www.headspace.com/gift)).
- **Duolingo** gifting appears to go through third-party gift cards ([On Me](https://onme.com/brands/duolingo-gift-cards); not confirmed on Duolingo's own site).
- **Apple** has no gifting for subscriptions. Developers use offer codes, up to 1 million per app per quarter, and one-time codes expire within 6 months ([App Store Connect help](https://developer.apple.com/help/app-store-connect/manage-subscriptions/set-up-subscription-offer-codes), via search summary).

**Legal flags (details in `rules.md`; attorney to confirm)**
- **Federal gift-card rules:** codes "redeemable for specific goods or services generally are not subject" to the federal gift-certificate rules because they aren't issued "in a specified amount". A code that states a value, such as "a $50 value", is covered ([CFPB, Reg E official interpretation 1005.20](https://www.consumerfinance.gov/rules-policy/regulations/1005/interp-20/)).
- **California:** a "gift certificate" may not have an expiration date, and one worth under $15 must be redeemable for cash ([Civ. Code 1749.5](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1749.5)). Whether a membership gift counts is an attorney question.
- **Renewal:** a gift should not roll into a paid renewal without the recipient's own express consent (auto-renewal laws).
- **Age:** graduation gifts may reach 17-year-olds (see the age section of `rules.md`).

## So what for us

1. **Recommended launch price: $59.99 a year as the headline, or $9.99 a month.**
   - $59.99 keeps the draft's annual price. It sits at the low end of the money-app peers, and low-priced annual plans retain best (36% vs 23-26% at year 1).
   - Raising monthly from $8 to $9.99 matches the education median and makes annual a clear 50% saving. It also cuts our fee share from 7.9% to 7.1%. Monthly plans mostly churn, so we want most people on annual.
2. **Don't add an auto-converting free trial at launch.** Free Level 1 already does the trial's job, and skipping it avoids the strictest auto-renewal rules. If we add one later, make it 14-30 days: longer trials convert better (42.5% vs 25.5%).
3. **Forecast conservatively.** Assume 2-3% of sign-ups pay in their first month, about 28% of annual members renew, and about 20% of monthly members leave each month. Better results are upside.
4. **Web checkout first is right:** we keep about 92-95% of each charge vs 85% in the stores. When native apps ship, enroll in Apple's Small Business Program and Google's 15% tier on day one. Use the US iOS link-out while it costs 0% (and maybe 5% later). On Android, Google's own billing is about as cheap as linking out.
5. **Gift membership:** $59.99 for 12 months of access.
   - Non-renewing, starting when the recipient redeems it.
   - Make it redeemable for "12 months" rather than a dollar value, and don't let it expire (or ask the attorney for the shortest allowed term).
   - At the end, invite the recipient to subscribe themselves.
6. **Test before locking in:** run $59.99 vs $49.99 annual on the pricing page with the first few hundred visitors. If conversion barely moves, keep $59.99.
