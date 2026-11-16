# Rules: questions for an attorney

**DRAFT for attorney review. NOT legal advice.** Research note for the founder, checked 2026-11-15. This file lists questions for counsel, with what I found next to each. I'm not drawing legal conclusions. "Primary" means I read the statute, rule, court opinion or official page myself. "Secondary" means a law-firm summary or news report. **Unverified** means I couldn't confirm it.

Each section has the same parts: our plan, what I found, the questions, and a cautious default until counsel answers.

---

## 1. Where education stops and "investment advice" starts

**Our plan.** Five-level lessons, a Money Map worksheet with the member's own numbers, a crash simulator, and possibly an AI tutor that answers member questions. All of it is paid for by a subscription.

**What I found**
- **Who counts as an adviser (primary).** The federal definition covers anyone who, "for compensation, engages in the business of advising others, either directly or through publications or writings, as to the value of securities or as to the advisability of investing in, purchasing, or selling securities" ([15 U.S.C. 80b-2(a)(11)](https://www.law.cornell.edu/uscode/text/15/80b-2)).
- **The exclusions (primary).** These include "(B) any lawyer, accountant, engineer or teacher whose performance of such services is solely incidental to the practice of his profession" and "(D) the publisher of any bona fide newspaper, news magazine or business or financial publication of general and regular circulation" (statute as quoted in [SEC Release IA-1092](https://www.sec.gov/files/rules/interp/1987/ia-1092.pdf)).
- **The Supreme Court's test for the publisher exclusion (primary).** In *Lowe v. SEC* (1985), the newsletters qualified because their content "was completely disinterested" and they were "offered to the general public on a regular schedule". They "do not offer individualized advice attuned to any specific portfolio or to any client's particular needs" ([Lowe v. SEC, 472 U.S. 181](https://www.law.cornell.edu/supremecourt/text/472/181)).
- **SEC staff view on "advice" (primary; 1987 staff interpretation).** This matters for our curriculum:
  - Advice that doesn't name specific securities "generally" still counts if it concerns securities. That includes "the relative advantages and disadvantages of investing in securities in general as compared to other investments".
  - "Specific investment advice" includes advice "about specific categories of securities (e.g., ... mutual funds ...)" and allocating "certain percentages" to fund types. It "does not include advice limited to a general recommendation to allocate assets in securities, life insurance, and tangible assets."
  - The compensation element "is satisfied by the receipt of any economic benefit", including "a single fee ... for a number of different services."
  - You are "in the business" if you hold yourself out as giving advice, are paid for it, or give specific advice "on anything other than rare, isolated and non-periodic instances" ([IA-1092](https://www.sec.gov/files/rules/interp/1987/ia-1092.pdf)).
- **Online example (secondary).** In *SEC v. Park* ("Tokyo Joe", N.D. Ill. 2000), a paid site with member emails and a chat room didn't get the case dismissed on the publisher exclusion. The court found the SEC had adequately alleged he was an adviser. It was a pleading-stage ruling, and the case settled ([SEC litigation release](https://www.sec.gov/litigation/litreleases/lr-16925)).
- **Market practice.** AI products that give personal money answers are registering as advisers: Origin, through Origin Investment Advisory LLC ([Origin](https://useorigin.com/resources/blog/introducing-the-first-sec-regulated-ai-financial-advisor), vendor claim), and Era ([InvestmentNews](https://www.investmentnews.com/transformation/no-advisors-no-problem-ai-startup-era-files-as-ria/265785)). Commentary says SEC and FINRA obligations don't change when advice comes from generative AI (secondary, e.g. [Debevoise, 2025-10](https://www.debevoise.com/insights/publications/2025/10/agentic-ai-in-retail-investing-navigating-regulato)). I found **no SEC rule or case specific to AI tutors** as of 2026-11-15.
- **State law.** States regulate smaller advisers under their own definitions. California, for example, looks to IA-1092 ([DFPI document](https://dfpi.ca.gov/wp-content/uploads/sites/337/2019/03/80c.pdf)). I didn't check each state (**unverified**).

**Questions for the attorney**
1. Does a paid, on-demand lesson app fit the publisher exclusion? Is it "bona fide", "impersonal", and of "general and regular circulation" when there are no dated issues?
2. Our subscription satisfies "compensation". Which lesson patterns become "specific investment advice" under IA-1092? Please mark up examples:
   - "Many beginners use broad index funds because ..." (describing)
   - "Index funds are a good fit for you" (recommending a category)
   - "People often split between stocks and bonds by age" (general rule of thumb)
3. **AI tutor:** Is any answer that responds to a member's own situation "individualized advice attuned to ... particular needs"? Would these guardrails keep it on the education side?
   - Answers grounded only in approved lessons
   - A refusal for "what should I buy / how much / is X good for me"
   - No access to Money Map numbers
   - Human review of logs

   Or should we drop free-form Q&A at launch?
4. **Money Map:** The member types their numbers and we explain a general rule (for example, months of expenses saved). Where does a calculator become advice? Does "you could" vs "you should" matter?
5. **Crash simulator:** Could "holding would have recovered by [date]" be read as recommending a buy-and-hold strategy? What risk and past-performance language is needed?
6. Does the "teacher" exclusion help an education company, or only individual teachers?
7. Do any states require registration for paid "financial coaching" or education apps even where the federal exclusion applies?

**Default until answered:** ship lessons and tools without free-form AI Q&A, or with a tutor that only explains concepts from our approved lessons. It should refuse personal recommendations and never see the member's numbers. Keep "education, not advice" visible, and run every tutor answer through the claims filter.

---

## 2. Subscriptions and auto-renewal

**What I found**
- **Federal law still in force (primary).** ROSCA requires an online seller using a negative option to (1) "clearly and conspicuously" disclose "all material terms of the transaction before obtaining the consumer's billing information", (2) obtain "express informed consent before charging", and (3) provide "simple mechanisms for a consumer to stop recurring charges" ([15 U.S.C. 8403](https://www.law.cornell.edu/uscode/text/15/8403)).
- **FTC "click-to-cancel" rule (secondary).**
  - The Eighth Circuit vacated the 2024 amended rule in July 2025 on procedural grounds.
  - The FTC opened a new rulemaking with an advance notice on 2026-03-11, with comments due 2026-04-13. It asks whether to revive parts of the vacated rule ([Covington](https://www.cov.com/en/news-and-insights/insights/2026/03/ftc-launches-new-rulemaking-on-the-negative-option-rule); [Cooley](https://www.cooley.com/news/insight/2026/2026-03-19-ftc-issues-new-advance-notice-of-proposed-rulemaking-on-negative-option-marketing)).
  - I found **no proposed rule as of 2026-11-15** (**unverified** that none exists). The FTC keeps enforcing under ROSCA and Section 5.
- **Enforcement example (secondary).** Amazon settled the FTC's Prime case on 2025-09-25 for $2.5B: a $1B civil penalty plus $1.5B in refunds. It must offer a clear decline button and let people cancel by the same method they used to sign up ([Goodwin](https://goodwinlaw.com/en/insights/blogs/2025/09/ftc-settles-with-amazon-over-enrollment-and-cancellation-processes-for-prime-memberships)).
- **California automatic renewal law, as amended by AB 2863 and effective for contracts from 2025-07-01 (primary text):**
  - Terms must be clear and conspicuous, "in visual proximity" to the consent request.
  - The business must get "express affirmative consent" and keep verification "for at least three years, or one year after the contract is terminated, whichever period is longer".
  - Members must be able to cancel "exclusively online, at will, and without engaging any further steps that obstruct or delay".
  - Fee changes need notice "no less than 7 days and no more than 30 days before" they take effect.
  - Free trials must explain the price after the trial.
  - Save offers are allowed only with conditions, such as showing the cancel option at the same time.
  - An annual reminder is required for plans of a year or more. I didn't confirm its exact timing (**unverified**).
  - Source: [Bus. & Prof. Code 17602](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=BPC&sectionNum=17602).
- **Other places (secondary):** New York City's click-to-cancel rule took effect 2026-10-01 ([Skadden](https://www.skadden.com/insights/publications/2026/09/new-york-citys-click-to-cancel-rule), 2026-09). Maryland's law took effect 2026-06-01, and Connecticut and Virginia amendments 2026-07-01. Louisiana added requirements, Massachusetts rules took effect Sept 2025, and Minnesota's in 2025 ([Kelley Drye](https://www.kelleydrye.com/viewpoints/blogs/ad-law-access/summer-2026-autorenewal-roundup-nyc-and-louisiana-enact-new-regulatory-requirements); [Subscription Insider](https://www.subscriptioninsider.com/article-type/news/maryland-automatic-renewal-law-raises-compliance-stakes-for-consumer-subscription-businesses)). I didn't read those texts (**unverified** details).

**Questions for the attorney**
1. What one checkout and cancel flow satisfies ROSCA, California, NYC, Massachusetts and the 2026 state laws together? Please cover consent capture, records, the annual reminder (timing and content), and how many save offers we may show, if any.
2. If we raise prices for existing members, what notice is needed and where?
3. Do any states require refunds of unused time when an annual member cancels?
4. Is a non-renewing gift membership outside the auto-renewal laws entirely? What do federal Regulation E and California Civil Code 1749.5 require of it? See `pricing-and-retention.md` section 6.
5. Once we sell through the app stores, which duties stay with us and which pass to Apple or Google?

**Default until answered:**
- Terms next to the pay button, with a separate unticked consent box, and consent records kept for 3+ years.
- Cancel online from account settings in two clicks, with at most one optional save offer shown beside a working cancel button.
- Email receipts, a renewal reminder about 30 days before annual renewals, and price-change notice 7-30 days ahead.
- No auto-converting trial at launch.

---

## 3. Disclosing AI-generated content

**What I found**
- **No federal labeling law.** I found no general US law requiring labels on AI-generated content as of 2026-11-15 (**unverified** absence). The FTC Act's ban on deception applies. The FTC's Consumer Review Rule (16 CFR Part 465, effective 2024-10-21) bans fake reviews and testimonials, "whether generated by humans or artificial intelligence". Penalties run up to $53,088 per violation (amount after 2025-01-17, adjusted yearly), and the FTC sent warning letters in Dec 2025 ([Venable](https://www.venable.com/insights/publications/2025/12/ftc-signals-heightened-enforcement-of-new); [FTC final rule](https://www.ftc.gov/system/files/ftc_gov/pdf/r311003consumerreviewstestimonialsfinalrulefrn.pdf)).
- **California bot law (secondary summary of statute):** it's unlawful to use a bot to communicate with a person in California online "with the intent to mislead the other person about its artificial identity" to drive a sale. A clear, conspicuous disclosure avoids liability ([Bus. & Prof. Code 17941](https://law.justia.com/codes/california/2019/code-bpc/division-7/part-3/chapter-6/section-17941/)).
- **California SB 243 (companion chatbots), effective 2026-01-01 (secondary).** It covers bots "capable of meeting a user's social needs". It requires notice if a reasonable person could think they're talking to a human, and it allows private lawsuits ([Perkins Coie](https://perkinscoie.com/insights/update/california-companion-chatbot-law-now-effect)). Probably not us, but worth checking.
- **California AI Transparency Act (SB 942), operative 2026-08-02 per AB 853 (secondary).** It aims at AI *providers* with 1M+ monthly users, so it's likely not us ([Nat'l Law Review](https://natlawreview.com/article/californias-ongoing-ai-regulation-key-deadlines-arriving-2026-and-beyond)).
- **Utah (SB 226, effective 2025-05-07; secondary).** A business must disclose generative AI when a consumer clearly asks. It must disclose up front in "high-risk" interactions, which include collecting financial information or giving financial advice in regulated occupations. There's a safe harbor if the AI discloses "at the outset of and throughout" the conversation, and fines of up to $2,500 per violation ([Davis Polk](https://www.davispolk.com/insights/client-update/utah-scales-back-reach-generative-ai-consumer-protection-law)).
- **Maine (LD 1727, 2025).** It requires a "clear and conspicuous" disclosure that a consumer isn't dealing with a human. I didn't confirm the details (**unverified**).
- **Platforms (secondary).** TikTok requires labels on AI-generated content with realistic images, audio or video. YouTube requires disclosure of realistic synthetic content and has auto-labeled since May 2026 ([Billo summary](https://billo.app/blog/ai-labeling/)). Whether an AI narration voice over motion graphics counts as "realistic" audio is **unverified**.
- **EU, only if we take EU members (secondary).** The AI Act's chatbot disclosure and deepfake labeling apply from 2026-08-02. The machine-readable marking duty moved to 2026-12-02 for existing systems ([Jones Walker](https://www.joneswalker.com/en/insights/blogs/ai-law-blog/yes-august-2-still-matters-the-eu-approved-a-high-risk-ai-delay-but-most-trans.html)).
- **Federal preemption (secondary).** A 2025-12-11 executive order directs challenges to state AI laws, and a White House framework from 2026-03-20 urges Congress to preempt them. Congress hasn't acted, so state laws stand ([Morgan Lewis](https://www.morganlewis.com/pubs/2026/03/white-house-ai-framework-puts-federal-preemption-at-the-center-of-the-debate); [Fisher Phillips](https://www.fisherphillips.com/en/news-insights/congress-again-drops-bid-to-block-state-ai-laws.html)).

**Questions for the attorney**
1. Is "Made with AI, reviewed by a person" accurate and sufficient? What must "reviewed" mean in practice: a named reviewer, a date, an approval record?
2. AI narration: do we need extra disclosure for a synthetic voice, and do our voice-provider terms allow commercial and social use?
3. Must short clips on TikTok, Reels and YouTube carry the platform AI label even without realistic people?
4. AI tutor: does a permanent "AI tutor" label plus a first-message disclosure meet California 17941, Utah and Maine? Does Utah's "high-risk" category reach us if we hold no license?
5. Should we block EU sign-ups at launch?

**Default until answered:** label every lesson video and clip. Switch on each platform's AI-content toggle. The tutor says it's an AI in its first message and carries a visible label throughout. No AI-generated people, testimonials or reviews.

---

## 4. Privacy: worksheets on the device vs on a server

**What I found**
- **Financial education may be a regulated "financial activity" (primary).** This was the surprise.
  - The FTC's Safeguards Rule defines a "financial institution" as a business "significantly engaged" in activities that are "financial in nature" under the Bank Holding Company Act ([16 CFR 314.2(h)](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-314/section-314.2)).
  - That list includes "(v) Providing educational courses, and instructional materials to consumers on individual financial management matters" ([12 CFR 225.28(b)(6)](https://www.ecfr.gov/current/title-12/chapter-II/subchapter-A/part-225/subpart-C/section-225.28)).
  - The rule's own examples include "an investment advisory company and a credit counseling service".
  - So a paid money-education company might be a GLBA "financial institution". That would bring privacy-notice duties and a written security program.
- **What data is covered.** "Customer information" means records "handled or maintained by or on behalf of you" ([16 CFR 314.2(d)](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-314/section-314.2)). Worksheet numbers that never leave the member's device may fall outside it. Account email, payment status and progress kept on our servers would not.
- I recall a reduced-duty exemption for institutions with fewer than 5,000 consumers and an FTC breach-report duty for events affecting 500+ people, but didn't confirm either this session (**unverified**).
- **State privacy laws (secondary).** California's CCPA applies above $26.625M revenue, or when a business buys, sells or shares data on 100,000+ California consumers, or earns half its revenue from selling or sharing ([Jackson Lewis FAQ](https://www.jacksonlewis.com/insights/navigating-california-consumer-privacy-act-30-essential-faqs-covered-businesses-including-clarifying-regulations-effective-1126)). Other states mostly start at 100,000 consumers, and some exempt GLBA-covered data or businesses. I didn't check each state (**unverified**).
- **Tracking tools.** The FTC has punished sharing sensitive data through ad pixels and SDKs: GoodRx (2023, $1.5M) and BetterHelp (2023), and in 2026 sued Hims & Hers ([IAPP](https://iapp.org/news/a/a-view-from-dc-the-ftc-sues-hims-over-pixel-tracking)). Those cases involve health data. The same logic plausibly reaches financial data (my inference).
- **Practical facts.**
  - Browser storage can be read by any script running on the same site, so analytics or chat widgets on worksheet pages could read it.
  - Data can be lost when a browser is cleared.
  - **An AI tutor sends each question to a server and an AI provider**, so anything a member types there leaves the device.

**Questions for the attorney**
1. Are we a GLBA "financial institution" because we sell financial education? If so, what applies at launch: a privacy notice, a Safeguards Rule security program, breach reporting?
2. Does keeping worksheets only on the device keep that data outside GLBA and state law? What about the progress and account data we do hold?
3. If we later sync the Money Map to a server for backup, what changes? Think security program, state breach laws, and "sensitive data" rules.
4. Which state privacy laws apply at our expected size, and do GLBA exemptions help us?
5. AI tutor: what may we send to the AI provider? What must the privacy notice say about retention and training use?
6. Are basic analytics allowed anywhere in the app, and which pages must stay script-free?

**Default until answered:**
- Worksheets stay on the device, and the AI tutor never receives them.
- No third-party scripts on worksheet, simulator or tutor pages. Stripe's script loads only on checkout pages.
- Collect only email, plan status and progress on the server.
- Add a "download / delete my data" button for local data.
- Draft a privacy notice for attorney review.

---

## 5. Historical market data for the crash simulator

**What I found**
- **FRED's S&P 500 series is copyrighted and short (primary).** The notice reads: "Copyright © 2016, S&P Dow Jones Indices LLC. All rights reserved. Reproduction of S&P 500 in any form is prohibited except with the prior written permission of S&P Dow Jones Indices LLC." FRED carries only "10 years of daily history" for S&P and Dow Jones series. The SP500 series runs from **2016-11-14**, so it doesn't cover 2000-02 or 2008-09. It is tagged "copyrighted: pre-approval required", and permission requests go to S&P DJI ([FRED SP500](https://fred.stlouisfed.org/series/SP500), read 2026-11-15).
- **FRED's terms (primary).**
  - Copyrighted series need the owner's permission for anything beyond personal use.
  - Public-domain and citation-required series "may be used for internal commercial uses and may be displayed in textbooks, newsletters, or reports to clients", with attribution. "Any other use ... is strictly prohibited."
  - Apps using the FRED API must show "This product uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis" and publish a privacy policy.
  - Source: [FRED legal](https://fred.stlouisfed.org/legal/).
- **S&P Dow Jones Indices (secondary, from its own pages via search).** Its site content comes under a limited, revocable license. It licenses index values "for display on television, websites, and mobile apps", and sells historical levels back to 1927 ([S&P DJI data and index licensing](https://www.spglobal.com/spdji/en/about-us/data-index-licensing)). I found no public price.
- **Shiller's dataset (primary).** Now at [shillerdata.com](https://shillerdata.com/), linked from his [Yale page](http://www.econ.yale.edu/~shiller/data.htm).
  - It gives monthly stock prices ("monthly averages of daily closing prices"), dividends and earnings since 1871. Dividends and earnings since 1926 are "computed from the S&P four-quarter totals". Earlier data comes from Cowles.
  - The site has a disclaimer, naming "Robert J. Shiller, RSBB-I, LLC", but **I found no license or permission to reuse the data**. Copies elsewhere carry their own public-domain labels, which bind no one (e.g. [datahub](https://datahub.io/core/s-and-p-500)).
- **Ken French Data Library (primary).** Its US market return comes from CRSP data ([data library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)). I found no terms of use on the page I read (**unverified**).
- **Accuracy note.** Monthly averages make crashes look shallower than daily closes do. Members should be told which one they're seeing.

**Questions for the attorney**
1. Can a paid app show S&P 500 levels from any source (S&P, FRED, Shiller) without an S&P DJI display license? Are historical index levels free-to-use facts, or protected by copyright, database terms or contract?
2. Can we use Shiller's monthly series commercially? Whose permission do we need: Shiller or RSBB-I, and also S&P?
3. Can we name "S&P 500" in the simulator (trademark), or should we call it "a broad US large-company stock index"?
4. Do FRED's terms let a paid app display public-domain series such as inflation or Treasury yields, beyond "reports to clients"?
5. If we license, what display, redistribution and attribution terms should we insist on?

**Default until answered:** build the simulator engine now with clearly labeled illustrative data. Ask S&P DJI for a quote on a small display license, write to the Shiller data site for permission, and price a licensed vendor feed as a fallback. Don't ship historical S&P figures until one of those comes through.

---

## 6. Age: 18+ only

**What I found**
- **COPPA.** It applies to services aimed at children under 13, or with actual knowledge that a user is under 13. The FTC amended the rule in 2025, with a compliance date I recall as April 2026 (**unverified** this session).
- **Contracts (secondary).** The age of majority is 19 in Alabama and Nebraska and 21 in Mississippi. Minors' contracts are generally voidable, though Alabama and Nebraska let 18-year-olds make some binding contracts ([Cornell LII](https://www.law.cornell.edu/wex/age_of_majority); statutes cited there; **unverified** against statute text). "18+" is not the same as "an adult who can contract" everywhere.
- **App-store age laws, once we ship native apps (secondary).**
  - Texas's App Store Accountability Act (SB 2420) puts duties on developers. It was enjoined 2025-12-23, then the Fifth Circuit paused that injunction, and argument was held 2026-08-04. Current status is **unverified** ([CCIA](https://ccianet.org/news/2026/05/appeals-court-pauses-injunction-on-texas-app-store-law-that-likely-violates-first-amendment/)).
  - California's Digital Age Assurance Act (AB 1043) is operative 2027-01-01. A developer that receives an operating-system age signal is deemed to know the user's age range ([Kelley Drye](https://www.kelleydrye.com/viewpoints/blogs/ad-law-access/faq-digital-age-assurance-act-california-youth-safety-on-the-internet)).
  - Utah and Louisiana have similar laws (**unverified**).
- **Gifts.** Graduation gifts will reach some 17-year-olds.

**Questions for the attorney**
1. Is a date-of-birth gate with 18+ self-attestation enough for a paid web app? What should we do for Alabama, Nebraska and Mississippi?
2. Can an adult gift a membership to someone under 18? If not, can the gift wait until the recipient's 18th birthday?
3. What must we do on learning that a member is under 18 (close the account, refund, delete data)?
4. What will Texas, California, Utah and Louisiana require of us when we launch native apps?

**Default until answered:** collect date of birth at sign-up and require 18+. Terms say members must be adults able to contract in their state. Gift pages say "for adults 18+". Close, refund and delete if we learn a member is under 18.

---

## So what for us

In order of urgency for the attorney:
1. **AI tutor scope (section 1).** This is our biggest legal risk. A paid tutor that answers personal questions looks like the "individualized advice" *Lowe* says the publisher exclusion doesn't cover. Launch without free-form Q&A, or with concept-only answers, until counsel signs off.
2. **Crash-simulator data (section 5).** S&P 500 data needs a license. FRED doesn't have the history anyway, and Shiller's data has no stated license. Start the licensing conversation now. It may take weeks and cost money, which Finance should budget for.
3. **GLBA status (section 4).** Selling financial education is a listed "financial activity". Get a yes or no early, because it decides whether we need a formal security program and privacy notice at launch.
4. **Checkout and cancel flow (section 2).** Build to the strictest common rules from day one: express consent, records, two-click online cancel, reminders and price-change notices. It's cheap to do now and expensive to retrofit.
5. **AI labels and age gate (sections 3 and 6).** These are low effort. Our "Made with AI, reviewed by a person" label already points the right way. Make "reviewed" mean a logged human approval.

Nothing here replaces counsel. Bring this file to the first meeting.
