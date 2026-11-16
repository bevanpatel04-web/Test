# Team brief: the Patient Money learning app (consumer, paid by members)

Read this first. Every agent works from it. It replaces the employer pilot direction (`docs/pilot/`), which is **shelved**: keep its files, but don't build on them or link to them.

## The product

People buy Patient Money **for themselves**, to get structure and real knowledge about money, from beginner to advanced. Core audience: 18-30 year olds starting to earn. Positioning: **"Paid by you, not by banks."** Free money apps earn by selling you cards, loans and brokerage accounts. We earn only from members, so we never push products.

**What makes it different (the bets we're testing):**
1. **A path, not a pile of content.** Five levels from beginner to advanced. Short lessons unlock in order. Each ends with a 3-question check, and you need 2 of 3 right to complete it. Spaced review brings old ideas back.
2. **AI-made video lessons.** Every lesson has a 2-4 minute video: narrated motion graphics with real charts. No fake human avatars. Each is labeled "Made with AI, reviewed by a person". The same videos are cut into short clips for TikTok/Reels, so marketing is free.
3. **Try it with your numbers.** Lessons end with a private worksheet or calculator using the member's own numbers, stored on their device. Over time it builds their **Money Map**. That's structure without advice: they fill it in, we explain.
4. **Crash simulator.** Members live through market crashes with a hypothetical index portfolio and see what holding or selling would have done. It trains behavior, the thing that actually costs beginners money. Never real money or picks. *(Update Nov 16: S&P index history needs a license, per `docs/app-research/rules.md`, so the simulator ships with clearly labeled hypothetical crashes until licensed data is in place.)*
5. **Honest by design.** It keeps everything the product already has: the claims filter, the fact registry, human approval, no stock picks and no promised returns.

**Business model (draft, to validate):** free = calculator + Level 1. Membership unlocks Levels 2-5, the simulator and the Money Map. The prices to test are about $8/month or $60/year, plus gift memberships (e.g. for graduates). Web app first (installable, Stripe checkout); native apps later. Mobile app stores take 15-30%.

## What already exists (reuse it)
- `invest/site/`: calculator, "Our rules", lessons index, shared `assets/style.css` (design tokens, light/dark).
- `invest/`: the content AI team (CEO, Facts, Lessons, Social agents), `invest/claims.py` claims filter, `invest/data/facts.json` verified facts (official sources only), `invest/data/lessons.json` (old 11-lesson list; the new curriculum replaces it).
- `company/llm.py`: the Claude client (`ClaudeLLM`, and `FakeLLM` for free dry runs and tests).
- Tests: `python -m pytest -q tests`, `node --test tests/*.test.js tests/qa/*.test.js`.

## Rules for every agent
1. **Education, not advice.** Never recommend a security, fund, coin, broker or app. Never promise or predict returns. Show risk beside any return. Advanced topics (options, leverage, crypto) are explained with their risks, never as strategies to use. All consumer copy must pass `python3 -c "from invest.claims import find_violations as f; import sys; print(f(open(sys.argv[1]).read()))" FILE` with `[]`.
2. **Facts need sources.** Use a URL and a date, from government or regulator sources first. Mark anything unverified.
3. **Stay in your lane.** Only create or edit what your task assigns you. Never touch `company/`, `site/`, `.github/`, `rewards/` or another agent's files.
4. **No git commands** that change anything. The lead integrates and commits.
5. **Privacy.** Never put the founder's name or email in a web request or in content. Member data stays on the member's device in the prototype.
6. **Plain English** for anything the founder reads. Legal-looking drafts say "DRAFT for attorney review".
7. **Keep it lean.** Usage limits are real: prefer a few high-quality files over many, and don't paste huge outputs.
8. **Finish with a short report:** file paths, what you verified and how, open questions, and anything unfinished. Don't write separate report or summary files; put it in your final message.

## Who owns what
| Agent | Owns |
|---|---|
| Research | `docs/app-research/` |
| Curriculum | `invest/data/curriculum.json`, `docs/app/curriculum.md`, `tests/test_curriculum.py` |
| Video studio | `studio/`, `invest/site/media/`, `tests/test_studio.py` |
| App builder | `invest/site/app/`, the nav in `invest/site/index.html` and `invest/site/rules.html`, the page template in `invest/publish.py`, `tests/app/` |
| Marketing | `docs/marketing-app/`, `invest/site/pricing.html` |
| Finance | `docs/finance-app/` |

Shared formats: `docs/app/contracts.md`.
