# Launch plan: the first 90 days

*Owner: marketing. Draft of 2026-11-15. Window: Monday Nov 16, 2026 to Sunday Feb 14, 2027 (13 weeks). Built for one founder with an AI team (Lessons, Facts, Social and Video studio agents). Prices are DRAFT. Audience: adults 18-30, never anyone under 18. Positioning and voice: `docs/marketing-app/positioning.md`.*

## The plan on one page

| Weeks | Dates | What happens | Gate |
|---|---|---|---|
| 1-2 | Nov 16-29 | Waitlist live on `pricing.html`. Clips start, using the 10 calculator scripts from `docs/marketing/consumer-launch-kit.md` while Level 1 videos are reviewed. 10 interviews | |
| 3-5 | Nov 30-Dec 20 | Level 1 opens free (waitlist first, then everyone). Level 1 clips daily. Gift-interest test for December graduations and holidays. First creator outreach | **Day 30: Tue Dec 15** |
| 6-7 | Dec 21-Jan 3 | Light weeks: clips pre-scheduled, founder mostly offline. Checkout and Level 2 get finished | |
| 8-10 | Jan 4-24 | Membership opens (waitlist first on Jan 4, everyone on Jan 11). Gift sales open. Referral program on from Jan 18. First 2 creator posts | **Day 60: Thu Jan 14** |
| 11-13 | Jan 25-Feb 14 | Double down on what worked. Prepare the May-June graduation campaign | **Day 90: Sat Feb 13** |

**Biggest dependency:** membership can't open until real checkout exists, and that isn't built yet. If checkout slips past Jan 4, everything from week 8 slides by the same amount. The free parts (waitlist, clips, Level 1) don't depend on it.

---

## What has to be true first

| Item | Owner | Needed by |
|---|---|---|
| Email provider picked and its form URL pasted into `signupEndpoint` in `invest/site/assets/config.js` (until then every form says "Sign-ups aren't connected yet") | Founder | Week 1 |
| `pricing.html` linked from the site nav and added to the sitemap | App builder (owns the nav and `invest/publish.py`) | Week 1 |
| Level 1 in the app at `invest/site/app/` | App builder | Week 3 |
| Level 1 videos approved (`"approved": true` in `invest/site/media/videos/manifest.json`) | Video studio, then founder | Weeks 2-4 |
| Real checkout (web, Stripe per the brief) with monthly, yearly and gift options | App builder, founder | Week 8 |
| Attorney review of refund, gift, referral and creator terms, plus a consumer privacy notice | Founder | Before week 8 |
| Trademark search on the name | Founder | Before any paid promotion |
| A way to count Level 1 learners without collecting personal data (see "Measuring without tracking people") | Founder decision, App builder | Week 3 |

## Founder time budget

Assumption: about 10-15 founder hours a week on marketing. The AI team drafts, cuts, captions, checks and reports; the founder approves, replies and decides.

| Task | Founder time per week | AI team does |
|---|---|---|
| Approve lesson videos and the clips cut from them | 2-3 hours | Drafts, renders, cuts, captions, runs the claims filter |
| Reply to comments and DMs | 2-3 hours (about 20 minutes a day) | Drafts replies to common questions for the founder to edit |
| Interviews (weeks 1-5) | 2 hours | Summarizes notes, pulls out exact phrases for hooks |
| Creator outreach and briefs (from week 3) | 1 hour | Finds candidates, checks their past posts against the vetting list, drafts emails |
| Email to the list | 30 minutes | Drafts the weekly lesson email |
| Friday review | 30 minutes | Compiles the metrics table below |

---

## 1. The waitlist

**Where people join:** the form on `pricing.html` (source `pricing`), the existing form on the calculator page (source `calculator`), and the link in every bio. Add `?src=` tags to bio and creator links (for example `?src=tiktok`, `?src=creator-01`) so the Friday report can show which channel brought each sign-up. The pricing form also has a "gift" checkbox, which tags people interested in giving a membership.

**What joining gets you (say exactly this):** an email when Level 1 opens, a short lesson by email each week, and one email when membership opens. No discount is promised, and none is needed.

**Email sequence**

| When | Email | Purpose |
|---|---|---|
| Right away | Welcome: what Patient Money is, the "Paid by you, not by banks" promise, a link to Our rules | Set expectations |
| Day 3 | Why we charge: how free money apps earn, and why we earn only from members | The core reason to pay |
| Day 7 | How the path works: five levels, the 3-question checks, the Money Map, the crash simulator | Show the product |
| Weekly | One short Level 1 lesson, with its video | Keep the promise the calculator page already makes |
| Once, at launch | Membership is open (and, to the gift tag only, gifts are open) | Convert |

**Email rules:** every email has an unsubscribe link and the mailing address the law requires (confirm the details with the attorney). Every email passes the claims filter. No countdowns, no fake scarcity, no "spots left". For adults 18 and over, stated next to every form.

## 2. The content engine: every lesson becomes 2-3 short clips

Every lesson video is 2-4 minutes. Each approved video gets cut into 2-3 vertical clips of 20-45 seconds for TikTok, Instagram Reels and YouTube Shorts. With about 45 lessons, that's roughly 90-135 clips: more than this 90-day window needs, as long as approvals keep pace.

**The three clip types**

| Clip | What it is | Example (Level 1, `why-a-cash-cushion-comes-first`) |
|---|---|---|
| **A. The idea** | The lesson's single most surprising point, opened with a hook | "Why your emergency money doesn't belong in the stock market" |
| **B. The math** | The chart moment, with assumptions and the risk line on screen | One month of must-pay costs, added up on screen |
| **C. Try it** | The lesson's worksheet prompt, so viewers do something with their own numbers | "Add up one month of must-pay costs. That's your first target." |

**The pipeline, every week**

1. **Founder approves lesson videos** in the manifest. Only approved videos get cut. *(Founder)*
2. **The Social agent reads each transcript** (the `.vtt` captions) and proposes 3 cut points, each starting on a hook line. It drafts the on-screen hook, the caption and the hashtags. *(AI)*
3. **The Video studio renders** each clip at 1080 by 1920 pixels with burned-in captions. Every clip shows "Made with AI, reviewed by a person" and "Education, not advice" for at least the first 3 seconds. Any number carries "Hypothetical, not a prediction" and a risk line. Any statistic shows its source and date. The end card says which level the clip comes from and that Level 1 is free. *(AI)*
4. **Claims filter** on the spoken text, on-screen text, caption and hashtags. Anything that fails gets fixed, never posted. *(AI)*
5. **Founder approves the batch** in one sitting, about 30-45 minutes for 10-15 clips. This is faster than lesson review, because the source video is already approved. *(Founder)*
6. **Schedule with each platform's own free scheduler.** The same clip goes to all three platforms on the same day, with the platform AI label on. *(Founder, 15 minutes, or AI if the founder gives scheduling access)*
7. **Friday report:** per clip, the share of viewers still watching at 3 seconds, completion rate, profile or link clicks, and sign-ups by `?src=` tag. Compare clips with each other, not with industry numbers. *(AI)*

**Cadence:** 5-7 clips a week in weeks 1-7, then about 10 a week from week 8 if approvals keep up. Never post faster than the founder can review.

**Clip rules**

- Never cut a return or growth number away from its risk line or its assumptions.
- Never cut a sentence in a way that changes its meaning.
- The hook goes on screen in the first 2 seconds.
- No trending sounds or visuals that suggest hype (money rain, sports cars, trading screens).
- No tickers, company logos or named products.
- Replies to "what should I buy?" follow the standard reply in `positioning.md`.
- Hooks and 8 full scripts for Levels 1-2 are in `docs/marketing-app/video-hooks.md`.

**Optional founder presence:** one 30-second "founder note" to camera each week (why we charge, how the videos are made, a correction). This builds trust, but the plan works without it.

## 3. Creator partnerships, with clear #ad disclosure

**Who:** small and mid-sized creators in money education, first jobs, college-to-career and "adulting". Their audience must be mostly 18 or older: ask for a screenshot of their audience-age breakdown before agreeing to anything, and skip anyone whose content is aimed at high-school students.

**Vetting checklist (the AI team checks their last 3 months of posts; the founder decides)**

- No stock, fund or crypto picks, and no promised returns.
- No undisclosed paid posts.
- No hype language (run a sample of their captions through `invest/claims.py`).
- No attacks on named companies or people.
- Not promoting a trading, crypto, lending or card product in the same post as us. That would clash with "Paid by you, not by banks."
- If the creator holds a financial license, their firm may need to approve the post. Ask.

**The offer (DRAFT for the founder and attorney)**

- A flat fee per video, plus a free membership for the creator. No pay per sign-up in the first 90 days: per-sign-up pay rewards pushy posts.
- Budget assumption: up to $1,500 in total for 2-4 paid posts in this window. This is a planning cap, not a market rate. The founder sets the real number.
- Usage: we can repost their video on our accounts with credit. No paid boosting of creator posts yet.
- Keep creator contact details in a private sheet outside this repo.

**Disclosure rules (in the contract and the brief)**

- "#ad" or "Paid partnership" goes at the start of the caption, not buried in hashtags, **and** in the video itself (said out loud or on screen in the first few seconds). Use the platform's paid-partnership tool as well.
- The free membership counts too. Under FTC guidance, a "material connection" includes being paid or getting free or discounted products or services, and the disclosure has to be hard to miss and in simple language. Source: [FTC, "Disclosures 101 for Social Media Influencers"](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) (published November 2019), checked 2026-11-15.
- Any clip of ours that they use keeps the "Made with AI, reviewed by a person" label.

**The creator brief**

- **They can say:** what Patient Money is, what they actually tried (Level 1, a check, the crash simulator), what they liked, and what they didn't. Honest opinions only. We don't ask for a positive review.
- **They can't say:** anything about returns or making money, any advice about what to buy or sell, any claim that it's the "best" app, or anything about another named company.
- **We review the script** for accuracy and the claims filter, not for how positive it is. We can ask for a correction or a takedown if the rules are broken.

**Outreach email (to the business email listed on their profile)**

> Subject: Paid partnership idea: an honest money-learning app (#ad, flat fee)
>
> Hi, I run Patient Money, a money-learning app people pay for themselves: a path from budgets to advanced investing, with no ads and no referral deals with banks or brokers. I'd like to pay you a flat fee for one video about trying Level 1, labeled #ad. Your honest take, good or bad. No talk of returns or picks, which fits how you already post. Rates and the full brief are attached. Interested? hello@example.com

**Targets:** contact about 6 creators a week from week 3. Aim for 2-4 paid posts between weeks 8 and 13. Track each with its own `?src=` tag.

## 4. The "graduation gift" membership campaign

**The idea:** "Give structure, not a lecture." A one-year membership (DRAFT $60) for a graduate or someone starting their first job.

**Mechanics (DRAFT for attorney review)**

- The giver pays once and picks a delivery date. The recipient gets a code by email and activates it when they're ready.
- Gifts don't renew automatically. When the year ends, the recipient chooses whether to pay for themselves.
- **The gift is private:** the giver never sees the recipient's progress, quiz results or Money Map. Say this in the copy, because it's a real selling point.
- Recipients must be 18 or older. The giver confirms this at checkout.

**Timing, realistically**

| When | What | Why |
|---|---|---|
| Weeks 3-6 (Dec) | **Gift-interest test.** A gift section on `pricing.html` and a "gift" checkbox on the waitlist form. One email to the list: "Know someone graduating or starting a first job?" Interested givers are told plainly that gifts open in January. | December graduations and holiday gifting land before checkout exists. This measures demand without taking money for something we can't deliver yet |
| Weeks 8-13 (Jan-Feb) | **Gift sales open** with checkout. One email to everyone tagged "gift". A printable gift card (PDF) to put in a real card | Turns December interest into real sales and tests the gift flow end to end |
| Week 13 | **May-June campaign ready:** landing copy, 3 clips aimed at givers, a creator brief for parent-audience creators, the email | Spring graduation is the big season. Have everything ready 3 months ahead |

**Message to givers:** "They'll get a clear path from budgets to how markets work, at their own pace, and nobody will try to sell them a credit card along the way." Speak to the giver about an adult recipient. No high-school imagery, and never target ads at teens. Aim gift ads and posts at adults buying for adult graduates.

**Measure:** gift-checkbox ticks (December), gift purchases, the share of codes activated within 30 days, and how many recipients finish Level 1.

## 5. The member referral program

**Starts:** week 10 (Jan 18), once there are paying members and checkout works.

**The offer (DRAFT):** "Give a month, get a month." A member shares a personal link. Their friend gets the first month of membership free. When that friend's first paid charge goes through and the refund window has passed, the member gets a free month. Up to 12 free months a year. No cash and no gift cards.

**Disclosure built in:** because the member gets a free month, they have a material connection (same FTC guidance as above). The pre-written share text says so:

> "I've been learning money basics on Patient Money: short lessons in order, and they don't sell you anything. Level 1 is free. If you join with my link, your first month of membership is free, and I get a free month too."

**No pressure:** no leaderboards, no "invite 5 friends to unlock", no countdowns. Members who never share get exactly the same product.

**Fairness and privacy:** no self-referrals (the same payment card can't earn a reward). We never ask for or upload anyone's contacts; members share their link wherever they like.

**Measure:** the share of members who share a link, sign-ups per sharer, the share of referred friends who become paying members, and whether referred members stay as long as others.

---

## 6. Metrics and weekly targets

### The funnel

| Stage | What we count | Where it comes from |
|---|---|---|
| Reach | Clip views, and the share still watching at 3 seconds | Each platform's analytics |
| Interest | Profile and link clicks, visits to `pricing.html` | Platform analytics, simple page counts |
| Sign-up | New emails on the list, by `?src=` tag | Email provider |
| Learning | People who start Level 1, and people who finish it | Anonymous counts (see below) |
| Paying | New paying members (monthly vs. yearly), gifts sold | Checkout dashboard |
| Staying | Monthly members still paying after their first renewal, refund requests | Checkout dashboard |
| Trust | Published claims-filter failures (target: 0), corrections made, complaints | Social agent's weekly log |

### Measuring without tracking people

Member progress lives only on the member's device (`docs/app/contracts.md`), so we can't see who finished what, and we shouldn't. Two options for the founder:

1. **Count pages only:** a privacy-friendly page counter with no cookies and no personal data. "Level 1 learners" then means visits to the first Level 1 lesson page. It's rough but honest.
2. **Anonymous events:** the app sends a bare "lesson completed: [slug]" count with no ID, no email and no device fingerprint. It's more accurate, but it has to be described in the privacy notice.

Whatever is chosen has to match what the pricing page FAQ says about data.

### Weekly targets

**These are targets to steer by, not forecasts.** They assume:
- we start with close to no audience;
- clips go out at 5-7 a week through week 7 and about 10 a week after that;
- Level 1 opens in week 3 and membership opens on Jan 4 (week 8);
- about 3% of the email list pays in the first week membership is open, then about 12-15 new paying members a week come from the list, Level 1 learners, creators and referrals.

Every one of these is a guess to test, not a benchmark. Short-video reach is unpredictable: a few clips may bring most of the views, and real numbers could come in far below these. Columns are running totals.

| Week | Dates | Focus | Clips posted | Email list | Interviews | Level 1 learners | Paying members |
|---|---|---|---|---|---|---|---|
| 1 | Nov 16-22 | Waitlist live, first calculator clips | 5 | 50 | 5 | - | - |
| 2 | Nov 23-29 | Calculator clips, interviews | 11 | 120 | 10 | - | - |
| 3 | Nov 30-Dec 6 | Level 1 opens to the waitlist | 17 | 190 | 15 | 40 | - |
| 4 | Dec 7-13 | Level 1 opens to everyone, gift-interest test | 23 | 260 | 20 | 100 | - |
| 5 | Dec 14-20 | **Day 30 gate** (Dec 15) | 29 | 330 | 20 | 160 | - |
| 6 | Dec 21-27 | Holiday week, pre-scheduled clips | 34 | 380 | 20 | 200 | - |
| 7 | Dec 28-Jan 3 | Pre-scheduled clips, checkout ready | 39 | 440 | 20 | 250 | - |
| 8 | Jan 4-10 | Membership opens to the waitlist, gifts open | 49 | 520 | 20 | 320 | 20 |
| 9 | Jan 11-17 | Membership opens to everyone, **Day 60 gate** (Jan 14) | 59 | 600 | 20 | 400 | 35 |
| 10 | Jan 18-24 | Referral program on, first creator post | 69 | 680 | 20 | 480 | 50 |
| 11 | Jan 25-31 | Creator post 2, re-cut the best clips | 79 | 760 | 20 | 560 | 62 |
| 12 | Feb 1-7 | Double down on the best channel | 89 | 840 | 20 | 640 | 75 |
| 13 | Feb 8-14 | **Day 90 gate** (Feb 13), May-June gift prep | 99 | 920 | 20 | 720 | 90 |

**What 90 paying members could mean (hypothetical):** if 60% chose the yearly plan and 40% the monthly plan, that's 54 x $60 = $3,240 collected up front, plus 36 x $8 = $288 a month. This is before payment fees, refunds and taxes, at DRAFT prices. It's an illustration of the targets above, not a prediction: membership could open late, convert at a fraction of this rate, or lose monthly members after one month. The Finance agent's model (`docs/finance-app/`) is the place for real unit economics.

### The Friday review (30 minutes)

The Social agent fills in this week's row: actuals next to targets, the top 3 and bottom 3 clips with their hooks, sign-ups by source, and anything in the trust row. The founder picks **one** change for next week (a new hook style, a different posting time, a new creator). One change a week makes it possible to tell what worked.

## 7. Decision gates

| Gate | Keep going if | Change the message if | Stop or rethink if |
|---|---|---|---|
| **Day 30** (Tue Dec 15) | 300+ on the email list, or 5%+ of `pricing.html` visitors join, **and** interviews say structure or "no sales" matters to them | Views but few sign-ups: test hooks that lead with the order, the no-sales promise or the crash simulator. Or interviews say cost is the blocker: lead with free Level 1 | Little interest after 25+ clips and 20 interviews |
| **Day 60** (Thu Jan 14) | 20+ paying members in membership's first week, and few refund requests | Lots of Level 1 learners but few paying: test what the membership page shows first, or let Level 1 finishers try one Level 2 lesson free | Almost no one pays: revisit price and positioning with the founder before spending on creators |
| **Day 90** (Sat Feb 13) | Around 75+ paying members, refunds under about 10% of charges, and monthly members renewing | Members join but don't finish lessons: fix the product before growing marketing | Far below target with no channel working: pause paid spend, keep the free content, and rethink |

---

## Budget (assumptions for the founder to confirm)

| Item | 90-day amount | Notes |
|---|---|---|
| Ads | $0 by default | Optional $200 test boosting the single best clip in week 10. Check each platform's rules for financial-services ads before boosting |
| Creators | Up to $1,500 | 2-4 flat-fee posts. Founder sets the real number |
| Email provider | $0 on a free tier, if the list stays small | Depends on the provider the founder picks |
| Printable gift card | $0 | Made by the Video studio or AI team as a PDF |
| Attorney review | One-off, quote needed | Refunds, gifts, referrals, creator contract, privacy notice |

## Risks and what we do about them

| Risk | What we do |
|---|---|
| Reach is unpredictable, and a slow start feels like failure | Judge clips against each other, keep posting at a pace the founder can sustain, and use the day-30 gate instead of reacting daily |
| People distrust AI-made money videos | Label everything, explain the process in a founder note, and fix mistakes publicly (see `positioning.md`) |
| One hype-sounding clip damages the brand | Claims filter plus founder approval on every clip, and the "never cut a number from its risk line" rule |
| Checkout slips past Jan 4 | Membership, gifts and referrals move back together. Keep the free path and the list growing in the meantime |
| The founder becomes the approval bottleneck | Batch approvals once a week. Cut fewer, better clips rather than skipping review |
| A creator breaks the rules | The contract allows a correction or takedown, we only pay after the post meets the brief, and we stop working with them |
| Gift buyers include parents of under-18 graduates | Recipients must be 18+, givers confirm it, and no high-school imagery or teen targeting |
| The "Paid by you, not by banks" promise gets tested by a sponsor offer | Decline. The promise is the product. Any change goes to the founder and members first |
