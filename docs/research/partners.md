# Partners: vendors for each layer

*Research note. As of 2026-11-14. Prices are from official pricing pages where marked "official"; otherwise from third-party sites and marked **unverified**. Confirm in writing before signing.*

## The short version

For the pilot, **we may not need any integration partner.** The employer can send a weekly spreadsheet (employee ID, hire date, still employed, location, contact), pay payroll bonuses through its own payroll from a file we provide, and fund gift cards through a free gift-card platform. Integrations come later, when there are several employers.

| Layer | Pilot pick | Why | Later |
|---|---|---|---|
| Gift cards | **Tremendous** (or Tango Card) | $0 platform and API fees; gift cards at face value (official) | Runa or Blackhawk Network at scale |
| Payroll / HR data | **CSV from the employer** | No cost, no integration, least data | Finch (read-only Starter is enough for hire dates) or Merge |
| Payroll bonus | **Employer's own payroll** | We move no money | Same |
| Direct-deposit verification ("set up savings") | Self-reported, or a screenshot the member keeps | Avoids sharing bank data | Pinwheel or Atomic (payroll connectivity) |
| Investing (phase 2) | **None** | Not in the pilot | "Route your bonus to your own account" first; then Apex, Bits of Stock, Alpaca, Atomic Invest or DriveWealth if needed |

## 1. Gift card and payout APIs

| Vendor | What it does | Pricing | Minimums | Fit |
|---|---|---|---|---|
| **Tremendous** | Gift cards, prepaid Visa, donations, PayPal/Venmo/bank payouts; API and bulk sending | **Official ([pricing page](https://www.tremendous.com/pricing), read 2026-11-14):** $0 platform, API and integration fees. Gift cards, prepaid Visa and donations at face value. Venmo/PayPal/Cash App/bank transfers 4-6%. Bank funding $0; credit card funding 3%. Possible volume discounts at $200K+/year | $0.25 minimum on Venmo/PayPal payouts | **Pilot: best fit.** Free, API ready, employer can hold its own account |
| **Tango Card** (owned by Blackhawk Network since May 2024, [Tango](https://www.tangocard.com/about/); deal announced 2024-01-31, [FTV Capital](https://ftvcapital.com/2024/blackhawk-network-signs-agreement-to-acquire-tango-card/)) | Gift card and prepaid rewards catalog with API | **Official:** "No minimums. No sign-up fees" ([pricing page](https://www.tangocard.com/pricing)). Credit card funding 3.5% ([developer docs](https://developers.tangocard.com/docs/funding-operations)). ACH/wire free and other fees (e.g., $450 custom redemption page) per third parties, **unverified** | None stated | **Pilot: good alternative.** Same parent as the gift cards Payactiv is adding |
| **Runa** (formerly WeGift) | Global payouts, gift cards, prepaid; one API | Official page lists a Starter plan with "monthly minimum applies" and an Enterprise tier at $2,000/month platform fee plus $5,000 setup, per a search snippet of [runa.io/pricing](https://runa.io/pricing). I could not read the page directly (**unverified**). One listing says $0.10 per code on Starter ([FitGap](https://us.fitgap.com/products/052689/runa), **unverified**) | Monthly minimum on Starter (amount **unverified**) | **Later**, if we go international or need volume terms |
| **Blackhawk Network (BHN)** | Gift card issuer/distributor; corporate rewards; owns Tango | Enterprise, not public | Not public | **Later**. Already partnering with Payactiv for in-app gift cards (Oct 2026) |

**Notes**
- Prefer **closed-loop store gift cards** in the pilot. Open-loop prepaid Visa cards raise more questions (see `regulatory-checklist.md`, section G).
- Whichever vendor we use, **every gift card is taxable pay.** The vendor must give us a per-employee, per-pay-period report for the employer's payroll.
- Avoid the 3-3.5% card-funding fee: have employers fund by bank transfer.

## 2. Payroll and HR integrations

| Vendor | What it does | Pricing | Minimums | Fit |
|---|---|---|---|---|
| **Finch** | One API to read HR and payroll data from many payroll systems; "Deductions" product writes deductions/contributions back | **Official ([pricing page](https://www.tryfinch.com/pricing)):** Starter $65 per connection per month, up to 15 connections, **organization and payroll data (read)**. Deductions (write) only on Pro/Premier, quote only | None stated on Starter | **Later (first integration).** Read-only Starter covers hire dates and active status, which is all tenure rewards need. Write access isn't needed: the employer pays bonuses itself |
| **Merge** | Unified API across HR, payroll and other categories | Launch plan reported at first 3 linked accounts free, then $650/month for up to 10, plus $65 per extra ([Nango](https://www.nango.dev/blog/merge-pricing), competitor blog, **unverified**) | Annual contracts reported | Later, alternative to Finch |
| **Check** (checkhq.com) | **Embedded payroll** for software platforms that want to *offer payroll* (partners include 7shifts and Homebase) | Quote only; base fee plus per-employee ([HR.software](https://www.hr.software/reviews/check), third-party) | n/a | **Not a fit.** We don't want to run payroll. Useful only to know that 7shifts and Homebase, common in restaurants, run on it |
| **Pinwheel**, **Atomic (atomicfi)**, Argyle | Worker-permissioned payroll connections: direct-deposit switching, income verification | Not public ([Pinwheel](https://pinwheelapi.com/products/deposit-switch); [Sacra overview](https://sacra.com/research/pinwheel-argyle-atomic-direct-deposit-switching/)) | n/a | **Later**, only if we need to *verify* "set up direct deposit to savings." Raises privacy stakes (bank data) |

**Notes**
- **Pilot recommendation: CSV or SFTP from the employer.** It needs no vendor, no per-connection fee, and shares the least data.
- Restaurants often use Toast, 7shifts, Homebase, ADP, Paychex or Gusto. Check that Finch or Merge covers the pilot employer's system before paying for anything.
- Don't confuse **Atomic Financial** (atomicfi.com, payroll connectivity) with **Atomic Invest** (atomicvest.com, brokerage). They are different companies.

## 3. Embedded investing and stock rewards (phase 2 only)

| Vendor | What it does | Pricing / minimums | Status (date) | Fit |
|---|---|---|---|---|
| **Apex Fintech Solutions** | Clearing and custody; **Stock Rewards API** for brands and banks; fractional shares ([Apex](https://apexfintechsolutions.com/who-we-serve/consumer-brands/)) | Not public | Owned by PEAK6; IPO filed confidentially Dec 2023, not completed ([Finance Magnates](https://www.financemagnates.com/fintech/apex-fintech-solutions-renews-ipo-plans-files-documents-with-the-sec/)). Took over some Stockpile accounts at its 2026-04-17 closure | Phase 2 candidate. Stock rewards = securities given to employees, so more legal work |
| **Bits of Stock** | Stock-rewards API; stock-rewards checking for banks and credit unions via Jack Henry and Q2 ([Nasdaq release](https://www.nasdaq.com/press-release/stock-rewards-checking-now-accessible-to-financial-institutions-through-bits-of-stock)) | Not public. Per-partner monthly reward caps ([FAQ](https://bitsofstock.com/app-support/faq)) | Active | **Best fit for the credit-union second payer.** Already sold to CUs |
| **DriveWealth** | Embedded brokerage API | Not public | 2026 focus is international and new products ([DriveWealth 2026](https://www.drivewealth.com/2026/)). FINRA $1.1M fine for fractional-trade reporting failures, conduct 2016-2022 ([AWC](https://data-portal.finra.org/fda_documents/2020067647701%20Drivewealth%2C%20LLC%20CRD%20165429%20AWC%20lp.pdf); date **unverified**) | Phase 2, lower priority. Check BrokerCheck (CRD 165429) |
| **Alpaca** | Broker API for apps; fractional from $1 ([Alpaca](https://alpaca.markets/global-stocks)) | Negotiated ([Broker API](https://alpaca.markets/broker)) | Active | Phase 2 if we ever build our own investing app. Probably not |
| **Atomic Invest** (Atomic Brokerage is the broker-dealer) | Embedded investing API for banks and fintechs | Not public | $30M raised Aug 2025 ([Atomic](https://www.atomicvest.com/news/atomic-raises-30-million-to-accelerate-global-expansion-of-its-embedded-investing-platform)); Bolt partnership Feb 2026 ([Atomic](https://www.atomicvest.com/news/bolt-expands-its-superapp-with-embedded-investing-through-atomic)) | Phase 2 candidate |

**Notes for phase 2**
- The brief says "points become a cash deposit into the member's **own** investing or savings account. The member chooses what to invest in." The simplest version needs **no investing partner at all**: the employer pays the reward as a payroll bonus, and the member routes it by direct deposit to any account they pick. We only teach. That avoids picking a broker for members.
- Stock-rewards APIs (Apex, Bits of Stock) do something different: they give the member **shares**. That brings broker-dealer, FINRA communications and gamification scrutiny ("free stock rewards" were named in Massachusetts' Robinhood order). See `regulatory-checklist.md`, section H.
- Every stock reward from an employer is still taxable wages.

## So what for us

1. **Pilot stack: CSV in, Tremendous (or Tango) for gift cards, employer payroll for bonuses.** Cost to us: about $0 in vendor fees.
2. **Have the employer own the gift-card account**, funded by bank transfer. We send instructions only. This keeps us from holding money.
3. **First integration when we have 3+ employers: Finch Starter ($65/connection/month, read-only).** Tenure rewards only need hire dates.
4. **Don't integrate direct-deposit switching** in the pilot. Self-report the savings habit.
5. **Phase 2: start with "route your bonus to your own account."** Talk to Bits of Stock when a credit union is the payer.
