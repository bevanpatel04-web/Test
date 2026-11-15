# Short-video hooks and scripts: Levels 1-2

*Owner: marketing. Draft of 2026-11-15. Clips are cut from the AI-made lesson videos (2-4 minutes each) for TikTok, Instagram Reels and YouTube Shorts. See the content engine in `docs/marketing-app/launch-plan.md` and the voice guide in `docs/marketing-app/positioning.md`. For adults 18 and over only.*

**Lesson references:** the curriculum is still the 3-lesson seed (`invest/data/curriculum.json`). Lessons marked *(seed)* exist there with that slug. Lessons marked *(planned)* follow the Level 1-2 summaries in the seed; their final slugs and titles must be checked against the full curriculum before posting.

## Rules for every clip

- **Labels on screen for at least the first 3 seconds:** "Made with AI, reviewed by a person" and "Education, not advice". Turn on the platform's AI label too.
- **Any growth or return number** is a labeled hypothetical with its assumptions (amount, rate, years), uses "could", and sits next to a risk line: "Investments can lose value, including money you put in."
- **Any statistic** shows its source and date on screen and in the caption. The only statistics used here are from the verified facts in `invest/data/facts.json`:
  - 63% of adults would cover a $400 emergency expense with cash or its equivalent. [Federal Reserve SHED, survey fielded Oct 2025, report released May 13, 2026](https://www.federalreserve.gov/newsevents/pressreleases/other20260513a.htm), verified 2026-11-14.
  - 22.36% average APR on credit card accounts charged interest, Q3 2026. [Federal Reserve G.19, released Nov 6, 2026](https://www.federalreserve.gov/releases/g19/current/default.htm), verified 2026-11-14.
- **Hypothetical numbers** come from the site's own calculator math (`invest/site/assets/calc.js`): the same amount added at the start of each month, a steady assumed yearly rate compounded monthly, no fees, taxes or inflation. Re-run them if any assumption changes.
- **No names:** no stock, fund, coin, broker, bank or app is named or shown. No logos or tickers.
- **End card:** which level the clip comes from, and "Level 1 is free: link in bio."
- **Run everything through the claims filter:** spoken text, on-screen text, caption and hashtags.
- **Length:** every script below is under 45 seconds at a normal narration pace (about 150 words a minute).

---

## 20 hooks

The hook goes on screen in the first 2 seconds and is also the first spoken line. Clip types: **A** = the idea, **B** = the math, **C** = try it.

### Level 1: Money foundations (free)

| # | On-screen hook | Lesson | Type | Needs on screen |
|---|---|---|---|---|
| 1 | "A budget isn't a punishment. It's a plan." | `what-a-budget-is-for` *(seed)* | A | - |
| 2 | "Most budgets use just three buckets. Here they are." | `what-a-budget-is-for` *(seed)* | A | - |
| 3 | "The best budget is the one you'll still use in three months." | `what-a-budget-is-for` *(seed)* | A | - |
| 4 | "Your salary isn't your paycheck. Here's where the gap goes." | Take-home pay *(planned)* | A | - |
| 5 | "Find this one number on your pay stub before you plan anything." | Take-home pay *(planned)* | C | - |
| 6 | "Could you cover a surprise $400 bill with cash?" | `why-a-cash-cushion-comes-first` *(seed)* | A | SHED source and date |
| 7 | "Why your emergency money doesn't belong in the stock market." | `why-a-cash-cushion-comes-first` *(seed)* | A | Risk line |
| 8 | "Your first emergency fund target is smaller than you think." | `why-a-cash-cushion-comes-first` *(seed)* | C | - |
| 9 | "A 22% credit card, explained in one number." | How card interest works *(planned)* | B | G.19 source and date, "simplified example" |
| 10 | "What APR actually means, in 30 seconds." | How card interest works *(planned)* | A | - |
| 11 | "Paying off a card is a known saving. Investing isn't." | How card interest works *(planned)* | A | Risk line |

### Level 2: Your first investments (members)

| # | On-screen hook | Lesson | Type | Needs on screen |
|---|---|---|---|---|
| 12 | "Same $100 a month. Five years apart. Look at the gap." | `compound-growth-explained` *(seed)* | B | Assumptions, "hypothetical", risk line |
| 13 | "Compound growth is just growth earning growth. Here's the picture." | `compound-growth-explained` *(seed)* | A | Risk line |
| 14 | "The input you control most isn't money. It's time." | `compound-growth-explained` *(seed)* | A | Risk line |
| 15 | "What risk actually means when you invest." | What risk means *(planned)* | A | - |
| 16 | "A 35% drop needs a 54% gain just to get back to even." | What risk means *(planned)* | B | "Simple math, not a forecast" |
| 17 | "What a 35% drop does to a start-early plan." | What risk means *(planned)* | B | Assumptions, "hypothetical", "real crashes can be worse" |
| 18 | "One company vs. hundreds: what an index fund actually is." | What an index fund is *(planned)* | A | No fund names or logos |
| 19 | "An index fund lowers one kind of risk. Not all of it." | What an index fund is *(planned)* | A | Risk line |
| 20 | "1% sounds tiny. Here's what it adds up to in one 44-year example." | Fees *(planned; confirm it's in Level 2)* | B | Assumptions, "hypothetical", risk line |

**Numbers behind the "B" hooks (hypothetical, from `calc.js`):**
- **Hook 12:** $100 a month to 65 at an assumed 6% a year. Starting at 22, it could reach about $232,300, with $51,600 put in. Starting at 27, about $168,300, with $45,600 put in.
- **Hook 16:** $10,000 falls 35% to $6,500. Getting back to $10,000 takes a $3,500 gain, about 54% of $6,500.
- **Hook 17:** $100 a month from 21 at an assumed 6% a year. A 35% drop at age 40 takes the balance from about $41,800 to about $27,200. Kept at the same assumed rate afterward, it could end near $184,600 at 65 instead of about $247,400.
- **Hook 20:** $100 a month from 21 to 65. At an assumed 6% a year it could reach about $247,400. At 5% (the 1% fee modeled as lower growth) it's about $186,200.

None of these is a prediction. Real investments don't grow at a steady rate, real crashes can be deeper or last longer, and investments can lose value, including money you put in.

### Hook styles that fit our voice

- **A surprising true number** with its source ("Could you cover a surprise $400 bill with cash?").
- **A myth, gently corrected** ("A budget isn't a punishment").
- **A picture of the math** ("Same $100 a month. Five years apart.").
- **A plain-English definition** ("What APR actually means, in 30 seconds").

We don't use hooks about anyone's gains, "how I turned a small amount into a fortune" stories, countdowns, or anything that promises an outcome.

---

## 8 full scripts

### Script 1: A budget is a plan, not a punishment

- **From:** Level 1, `what-a-budget-is-for` *(seed)*. Clip type A.
- **Length:** 87 words, about 35 seconds.
- **On-screen hook (0-2 s):** "A budget isn't a punishment. It's a plan."
- **Spoken:** "A budget isn't a punishment. It's a plan. A lot of people think budgeting means tracking every coffee and feeling bad about it. That's not what it's for. A budget is a plan you make before the month starts, so your money has a job before it arrives. Most budgets use three buckets. Needs, like rent and groceries. Wants, the fun stuff. And future you: savings and paying down debt. The best budget isn't the strictest one. It's the one you'll still be using in three months."
- **On screen:** three buckets filling as each is named: "Needs", "Wants", "Future you". Labels: "Made with AI, reviewed by a person" and "Education, not advice".
- **End card:** "From Level 1 of Patient Money. Level 1 is free: link in bio."
- **Caption:** "A budget is a plan for your money, made before payday. Three buckets, explained. From Level 1, which is free. Made with AI, reviewed by a person. Education, not advice. #budgeting #personalfinance #moneybasics"

### Script 2: Your salary isn't your paycheck

- **From:** Level 1, take-home pay *(planned)*. Clip type A.
- **Length:** 90 words, about 36 seconds.
- **On-screen hook (0-2 s):** "Your salary isn't your paycheck. Here's where the gap goes."
- **Spoken:** "Your salary isn't your paycheck. Your offer letter shows one number, and your bank account sees a smaller one. That gap isn't a mistake. Before your pay lands, money comes out for taxes, and often for things you signed up for, like health insurance or a retirement plan. What's left is your take-home pay. That's the number to plan with, because it's the money you can actually spend or save. It's on your pay stub, usually labeled net pay. Write it down. It's the first line of your Money Map."
- **On screen:** an offer-letter number shrinking into a pay-stub number, with "taxes" and "deductions" peeling off. No real salaries or tax rates. Labels as above.
- **End card:** "From Level 1 of Patient Money. Level 1 is free: link in bio."
- **Caption:** "Gross pay vs. take-home pay, and why you plan with the smaller number. From Level 1, which is free. Made with AI, reviewed by a person. Education, not advice. #firstjob #personalfinance #paycheck"

### Script 3: Could you cover a surprise $400 bill?

- **From:** Level 1, `why-a-cash-cushion-comes-first` *(seed)*. Clip type A.
- **Length:** 83 words, about 33 seconds.
- **On-screen hook (0-2 s):** "Could you cover a surprise $400 bill with cash?"
- **Spoken:** "Could you cover a surprise $400 bill with cash? In the Federal Reserve's latest survey of U.S. adults, 63% said they'd cover it with cash or its equivalent. That leaves a lot of people who'd have to borrow, sell something, or couldn't pay at all. That's what a cash cushion is for: so a surprise doesn't turn into debt. It doesn't have to be big to start. A reachable first target is one month of must-pay costs. Rent, food, transport and minimum payments."
- **On screen:** "63% would cover $400 with cash or its equivalent. Source: Federal Reserve SHED, survey fielded Oct 2025, released May 13, 2026." Labels as above.
- **End card:** "From Level 1 of Patient Money. Level 1 is free: link in bio."
- **Caption:** "Why a cash cushion comes first, and a first target that's actually reachable. Stat: Federal Reserve SHED, released May 2026. From Level 1, which is free. Made with AI, reviewed by a person. Education, not advice. #emergencyfund #personalfinance"

### Script 4: Why emergency money stays out of the stock market

- **From:** Level 1, `why-a-cash-cushion-comes-first` *(seed)*. Clip type A.
- **Length:** 96 words, about 38 seconds.
- **On-screen hook (0-2 s):** "Why your emergency money doesn't belong in the stock market."
- **Spoken:** "Why your emergency money doesn't belong in the stock market. Stock prices move up and down, sometimes a lot, and nobody knows when. Emergencies don't wait for a good day. If your car breaks down in the same month the market drops, you could have to sell at a low price to pay the bill. Money you might need soon has no time to recover from a drop. That's why many people keep their cushion in cash, and invest only money they won't need for years. Investments can lose value, including the money you put in."
- **On screen:** a wobbly price line next to a calendar with "car repair" circled on a low point. "Illustration, not real market data." Labels as above.
- **End card:** "From Level 1 of Patient Money. Level 1 is free: link in bio."
- **Caption:** "Short-term money and the stock market don't mix well, and here's the timing problem. From Level 1, which is free. Made with AI, reviewed by a person. Education, not advice. #emergencyfund #investingbasics"

### Script 5: A 22% credit card in one number

- **From:** Level 1, how card interest works *(planned)*. Clip type B.
- **Length:** 92 words, about 37 seconds.
- **On-screen hook (0-2 s):** "A 22% credit card, explained in one number."
- **Spoken:** "A 22% credit card, explained in one number. Card accounts that were charged interest averaged a 22.36% APR in the third quarter of 2026, according to the Federal Reserve. APR is the yearly interest rate. Here's a simplified example. You owe $1,000 at that rate, and for a year nothing is paid and nothing new is charged. You'd owe more than $200 in interest. Paying the balance off removes that cost, which is a known saving. Investment returns are never known in advance. That's why many people deal with expensive debt first."
- **On screen:** "22.36% average APR, accounts charged interest, Q3 2026. Source: Federal Reserve G.19, released Nov 6, 2026." Then "$1,000 at 22.36% for a year: more than $200 in interest. Simplified: no payments, no new charges. Real cards require minimum payments." Labels as above.
- **End card:** "From Level 1 of Patient Money. Level 1 is free: link in bio."
- **Caption:** "What a 22% APR means in dollars. Simplified example, Federal Reserve data from Nov 2026. From Level 1, which is free. Made with AI, reviewed by a person. Education, not advice. #creditcards #debt #personalfinance"

### Script 6: Same $100 a month, five years apart

- **From:** Level 2, `compound-growth-explained` *(seed)*. Clip type B.
- **Length:** 90 words, about 36 seconds.
- **On-screen hook (0-2 s):** "Same $100 a month. Five years apart. Look at the gap."
- **Spoken:** "Same $100 a month. Five years apart. Two people each invest $100 a month until 65. One starts at 22, the other at 27. We'll assume 6% growth a year. That's an assumption, not a prediction. Starting at 22, the balance could reach about $232,000. Starting at 27, about $168,000. The early starter put in only $6,000 more. That's compound growth: growth earning growth, with more years to do it. But real investments don't grow in a straight line, and they can lose value, including the money you put in."
- **On screen:** two lines on a chart, labeled "Start at 22" and "Start at 27". Text: "Hypothetical: $100/month to age 65, assumed 6% a year compounded monthly, no fees, taxes or inflation. Not a prediction. Investments can lose value." Labels as above.
- **End card:** "From Level 2 of Patient Money (members). Start with Level 1, free: link in bio."
- **Caption:** "Same $100 a month, five years apart. Hypothetical math with an assumed 6% a year, not a prediction: investments can lose money. Made with AI, reviewed by a person. Education, not advice. #compoundinterest #investingbasics"

### Script 7: A 35% drop needs a 54% gain

- **From:** Level 2, what risk means *(planned)*. Clip type B.
- **Length:** 85 words, about 34 seconds.
- **On-screen hook (0-2 s):** "A 35% drop needs a 54% gain just to get back to even."
- **Spoken:** "A 35% drop needs a 54% gain just to get back to even. Here's the math. Say an investment is worth $10,000 and it drops 35%. Now it's worth $6,500. To get back to $10,000, it has to gain $3,500. And $3,500 is about 54% of $6,500. No one can say if or when a recovery like that happens. That's why risk is about more than losing money. It's also about how long you might have to wait, and whether you could wait that long."
- **On screen:** "$10,000 → $6,500 (down 35%)". Then "$6,500 → $10,000 needs +$3,500 (up about 54%)". "Simple math, not a forecast." Labels as above.
- **End card:** "From Level 2 of Patient Money (members). Start with Level 1, free: link in bio."
- **Caption:** "Why losses and gains aren't symmetrical. Simple math, not a forecast. Made with AI, reviewed by a person. Education, not advice. #investingbasics #risk"

### Script 8: What an index fund actually is

- **From:** Level 2, what an index fund is *(planned)*. Clip type A.
- **Length:** 91 words, about 36 seconds.
- **On-screen hook (0-2 s):** "One company vs. hundreds: what an index fund actually is."
- **Spoken:** "One company vs. hundreds: what an index fund actually is. A single stock is a small piece of one company. If that company has a bad year, so does that money. An index fund holds many companies at once, following a list called an index. Some hold hundreds, even thousands. So one company's bad news matters less. That's diversification. But it lowers one kind of risk, not all of it. When the whole market falls, a broad index fund falls too. And funds can charge yearly fees, listed in their documents."
- **On screen:** one box next to a grid of 100 small boxes. No fund names, logos or tickers. Then "Diversification lowers one kind of risk, not all of it." Labels as above.
- **End card:** "From Level 2 of Patient Money (members). Start with Level 1, free: link in bio."
- **Caption:** "Single stock vs. index fund, explained without picking either. This is about what you'd own, not what to buy. Made with AI, reviewed by a person. Education, not advice. #indexfunds #investingbasics"

---

## Before posting any of these

1. Confirm the *(planned)* lessons exist in the final curriculum, and update the lesson names and slugs here.
2. Re-check the two statistics against `invest/data/facts.json`. G.19 updates every quarter and SHED every year: if a newer figure is verified, update the script, the on-screen source and the caption together.
3. Cut the clip only from a video marked `"approved": true` in the manifest.
4. Run the final spoken text, on-screen text, caption and hashtags through the claims filter.
