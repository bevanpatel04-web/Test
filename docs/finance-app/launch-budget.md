# Launch budget: the first 6 months

*Finance, 2026-11-16. Cash only, US dollars. The totals come from `docs/finance-app/model.py` (section 9). The video-library line is calculated from the content-cost section. Edit `launch_budget` in the model's INPUTS to change any line. The budget doesn't include the founder's pay or living costs.*

## The short version

| | Lean | Fuller |
|---|---|---|
| **Total, first 6 months** | **about $3,000** ($2,984) | **about $15,000** ($15,016) |
| Video library (45 lessons, cash) | $150 | $610 |
| Legal | $1,100 (3-hour review) | $3,250 (8-hour review + trademark) |
| Creator and ad tests | $900 | $6,000 |
| Founder time to review the library | about 41 hours | about 41-80 hours, plus an outside expert |
| What it buys | a working launch, a legal check, one small acquisition test | a more polished, better-protected launch and real channel tests |

**Plain English:** making the videos costs almost nothing in cash. The real costs are founder time, a lawyer, and testing whether anyone outside your own audience will sign up. The lean budget is enough to launch and learn. The fuller budget mostly buys more marketing tests and more protection (expert review, trademark, insurance), not a better product.

```
9. LAUNCH BUDGET, FIRST 6 MONTHS (cash; see launch-budget.md for notes)
                                                                    Lean    Fuller
----------------------------------------------------------------------------------
Video library: Claude + voice, 45 lessons (x2 for retakes)          $150      $610
Voice (TTS) plan while producing                                     $44      $198
Expert fact review of all lessons                                     $0    $1,500
Music, fonts, design assets                                           $0      $300
Domain (.com, 1 year)                                                $11       $11
Hosting + video, 6 months                                            $60      $150
Email tool, 6 months                                                  $0      $198
Legal review (terms, privacy, refunds, disclaimers)               $1,100    $2,900
Trademark filing (1 class)                                            $0      $350
Company formation (if not done)                                     $150      $300
Insurance, 6 months                                                   $0      $530
Creator tests                                                       $600    $4,000
Paid ads test                                                       $300    $2,000
Claude API for the app, support and social, 6 months                $180      $360
Bookkeeping tool, 6 months                                            $0      $120
App store accounts (for later native apps)                            $0      $124

Subtotal                                                          $2,595   $13,651
Contingency (15% / 10%)                                             $389    $1,365
TOTAL, FIRST 6 MONTHS                                             $2,984   $15,016
Founder review hours for the library (base / conservative)            41        80
```

## Line by line

| Item | Lean | Fuller | Why, and the source |
|---|---|---|---|
| Video library | $150 | $610 | Claude for scripts, compliance review and scene code, plus voice. The model's cash cost is $76 (base) or $307 (conservative) for 45 lessons; both are doubled for retakes. Rendering is local ffmpeg, so it's free. |
| Voice (TTS) plan | $44 | $198 | ElevenLabs Creator $22/month or Pro $99/month for 2 production months (https://elevenlabs.io/pricing/api). Google Chirp 3 HD at $30 per 1M characters is a cheaper option (https://cloud.google.com/text-to-speech/pricing). |
| Expert fact review | $0 | $1,500 | ASSUMPTION: about 20 minutes per lesson from a freelance financial educator at ~$100/hour. Lean relies on the founder, the claims filter and the fact registry. |
| Music, fonts, design | $0 | $300 | ASSUMPTION. Lean uses free-licensed fonts and no music. |
| Domain | $11 | $11 | .com at cost, about $10.46/year at Cloudflare (third-party listings). A taken name can cost far more. Choose one that's available. |
| Hosting + video | $60 | $150 | Cloudflare Workers $5/month + Stream $5 per 1,000 minutes stored (https://developers.cloudflare.com/workers/platform/pricing/, https://developers.cloudflare.com/stream/pricing/); fuller uses Vercel Pro $20/month (https://vercel.com/pricing). Video delivery is $1 per 1,000 minutes watched, which is in the running costs. |
| Email | $0 | $198 | Kit is free up to 10,000 subscribers; Creator is $33/month for automations (https://kit.com/pricing). |
| Legal review | $1,100 | $2,900 | 3 or 8 hours at $362/hour, the US average lawyer rate (Clio, updated Oct 2026, https://www.clio.com/resources/legal-trends/compare-lawyer-rates/). Scope: terms of service, privacy notice, refund and auto-renewal terms (California's law was tightened effective July 2025), the "education, not advice" disclaimers, AI-content labels, gift-code rules. Ask for a flat fee. |
| Trademark | $0 | $350 | USPTO base fee $350 per class since Jan 2025 (e.g. https://beancount.io/blog/2026/09/27/how-much-does-trademark-cost-2026-uspto-fees-guide). Lean: do a free search first and file later. |
| Company formation | $150 | $300 | ASSUMPTION: state filing fees vary (roughly $50-500). Skip it if the company already exists. |
| Insurance | $0 | $530 | Professional liability averages about $88/month for small businesses (Insureon, https://www.insureon.com/small-business-insurance/professional-liability/cost). Lean skips it, which is a real risk for a money-education business. Get a quote. |
| Creator tests | $600 | $4,000 | Micro creators (10K-50K followers) charge about $200-1,000 per post in 2026 guides (https://ttcalculator.net/learn/brand-deal-rates-by-followers/). Lean = 2-3 posts. Prefer per-signup or affiliate deals. |
| Paid ads test | $300 | $2,000 | Enough to measure the cost per free signup. 2026 benchmarks: Meta traffic clicks ~$0.60, education lead clicks $1.25-2.10 (vendor reports). |
| Claude API (app, support, social) | $180 | $360 | ASSUMPTION $30-60/month. Opus 5.5 $4/$20, Sonnet 5.5 $2/$10, Haiku 5.5 $0.10/$0.50 per million tokens. Set a monthly spend cap in the Claude Console. |
| Bookkeeping | $0 | $120 | ASSUMPTION. Lean: a spreadsheet plus Stripe reports. |
| App store accounts | $0 | $124 | Apple Developer $99/year + Google Play $25 once, only if a native app starts within 6 months. |
| Contingency | $389 | $1,365 | 15% lean, 10% fuller. |

**Stripe has no monthly fee.** It takes 2.9% + 30c + 0.7% (subscriptions) + 0.5% (tax) per payment, which comes out of revenue and is in the model's revenue section, not this budget.

## After launch: monthly running costs

About **$131 a month** in fixed costs (hosting, video storage, a voice plan for fixes, Claude for support and social drafts, bookkeeping, domain, email). Each paying member adds about **$0.25 a month**. In the base case gross profit covers these, and the small marketing tests, from **month 7**. The lowest point for operating cash after launch is only about **-$860**. So once the launch budget is spent, the business is cheap to keep running. What it needs is time and reach.

## Spend in this order (gates)

1. **Before any money goes out:** the founder reviews 3 finished lessons end to end and times it. If one takes over 2 hours, fix the workflow first.
2. **Build the library and the legal review** (about weeks 1-6). Spend: video, voice, domain, hosting, legal.
3. **Launch on organic short video only** (weeks 6-10). Tag every link, then measure signups, Level 1 completion and conversion.
4. **Only then spend on creators and ads**, in small tests. Keep a channel only if a free signup costs **under about $0.81** (LTV/CAC of 3 in the base case) or under $1.10 (6-month payback). Stop at $2.50 or more. Lean has room for one round of tests; fuller has room for several.
5. **Hold back the contingency** for retakes, a second legal question, or a creator who works.

## What the lean budget skips (and the risk)

- **No outside expert review:** accuracy rests on the founder, the claims filter and the fact registry. Add a review of the 9 free Level 1 lessons first (about $300) if money allows, because those reach the most people.
- **No insurance:** a complaint about financial content would be paid out of pocket.
- **No trademark:** someone could register a similar name first. A free search lowers the risk.
- **Only a few creator posts:** too few to know if creators work. Treat the result as a hint, not proof.
