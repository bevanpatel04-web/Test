# Patient Money — investing education for 18–25 year olds, run by a small AI team

**Patient Money** (working name) helps people in their early twenties see why *time* matters in investing, and what *risk* looks like, so they can make their own decisions. It is education only: no stock picks, no promised returns, no personal advice.

| Part | Folder | What it does |
|---|---|---|
| **Start now vs. later calculator** | `invest/site/` | Free tool: what waiting 1–10 years could cost, plus an optional "market crash" stress test. Shareable links, chart with table view, email sign-up |
| **AI team** | `invest/agents/` | A CEO agent plans each day. The Facts, Lessons and Social agents do the work. You approve everything before it goes live |
| **Facts registry** | `invest/data/facts.json` | Every statistic the site or the agents may use, with official sources. Only verified facts are published |
| **Curriculum** | `invest/data/lessons.json` | The lessons to write, and the facts each one needs |
| **Company memory** | `invest/ops/` | Task queue, daily briefs, and social packs ready to post (created on first run) |
| **Plan** | `docs/patient-money-plan.md` | Research, legal guardrails, revenue path, 30-day validation plan, interview script |

## How a day works

```
7:41am  CEO agent reads the status and plans up to 3 tasks
        ├─ Facts agent    → checks one figure against an official source (IRS, Fed, SEC, ...)
        ├─ Lessons agent  → writes one 2-minute lesson, using only verified facts
        └─ Social agent   → weekly pack: 2 short-video scripts, 1 carousel, 1 newsletter
        Every draft → hard-rule claims filter → AI compliance review → one rewrite → or dropped
        CEO agent writes your daily brief → it arrives as a GitHub issue
You     approve or reject each item (about 5 minutes) → approved work goes live automatically
```

## Built-in guardrails

- **Nothing is published without your approval.**
- **Facts need an official source.** A fact only counts as verified if its source is on a government or regulator domain (or S&P Dow Jones Indices for index data). Anything else stays hidden. See `PRIMARY_SOURCE_DOMAINS` in `invest/config.py`.
- **Lessons wait for their facts.** The CEO can't assign a lesson until every fact it needs is verified, and a lesson can't cite an unverified fact.
- **Claims filter** (`invest/claims.py`) blocks promised returns ("guaranteed", "risk-free", "will grow to"), advice ("you should buy"), hype ("10x", "get rich", "act now") and cashtags like `$TSLA`. Honest negations such as "past performance doesn't guarantee future results" are allowed.
- **AI compliance review** checks every draft against the education-only policy and the verified facts.
- **Disclaimers are added in code** to every caption and newsletter, so the agents can't forget them.
- **Spending cap:** at most 3 tasks a day (`INVEST_MAX_TASKS`).

## Setup (about 20 minutes)

1. **Claude API key.** If Mildwell is already set up, you're done: both teams use the `ANTHROPIC_API_KEY` secret. Otherwise add it under repo Settings → Secrets and variables → Actions → **New repository secret**. Set a monthly spend limit in the Claude Console.
2. **Test it for free:** Actions → **Investing team daily run** → Run workflow → tick **Dry run**.
3. **Turn on the daily schedule:** Settings → Secrets and variables → Actions → **Variables** → add `INVEST_AGENTS_ENABLED` = `true`. Optional: `INVEST_SITE_URL` (your domain) and `INVEST_MAX_TASKS`.
4. **Publish the website (free):** in Cloudflare Pages (or Netlify), connect this repo, leave the build command empty and set the output directory to `invest/site`. (This repo's GitHub Pages site is already used by Mildwell.)
5. **Connect email sign-ups:** create a free Beehiiv, Kit or MailerLite form and paste its form URL into `invest/site/assets/config.js` → `signupEndpoint`.

## Approving work

The daily brief lists numbered items. Read one with `python -m invest show <id>` (or open `invest/ops/state.json` on GitHub). Then go to Actions → **Approve investing agent work** → Run workflow and type the numbers.

When you approve:
- **Facts** → `invest/data/facts.json` is updated, and the fact appears on the site if its source is official
- **Lessons** → published to `invest/site/learn/`, added to the lessons page and the sitemap
- **Social packs** → saved to `invest/ops/outbox/`, ready to film and post

## Running it on a computer

```bash
pip install -r requirements.txt
python -m invest run-daily --dry-run   # free test, no AI calls
export ANTHROPIC_API_KEY=...           # then for real:
python -m invest run-daily
python -m invest status
python -m invest show 3
python -m invest approve 3 4
python -m invest build-site            # rebuild facts data, lessons page and sitemap
cd invest/site && python -m http.server   # preview at http://localhost:8000
```

Tests: `python -m pytest tests` and `node --test tests/invest_calc.test.js`.

## Renaming the brand

"Patient Money" is a placeholder until a trademark search clears it. To rename: set `INVEST_BRAND`, update `brand` in `invest/site/assets/config.js`, and find-and-replace the name in `invest/site/index.html` and `invest/site/rules.html`.

## Important

This site is general education. It is not investment, tax or legal advice. Keep it impersonal and never recommend a specific security, provider or action for a reader. Read the legal section of `docs/patient-money-plan.md` before taking any paid partnership.
