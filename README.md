# Mildwell — an AI-run water and skin business

**Mildwell** (working name) helps people with eczema and sensitive skin understand their tap water and choose gentler showers. This repo holds the whole company:

| Part | Folder | What it does |
|---|---|---|
| **Water Skin Check** website | `site/` | Free ZIP-code tool showing water hardness, chlorine or chloramine, and what to do about them. Collects emails and shows affiliate picks |
| **AI team** | `company/` | A CEO agent plans each day. Water Data, Content and Marketing agents do the work. You approve everything before it goes live |
| **Water data** | `data/` | City and state water data that the agents verify against official utility reports |
| **Company memory** | `ops/` | Task queue, daily briefs, and marketing packs ready to post |
| **Plan and brand** | `docs/` | Business plan and brand name shortlist |

## How a day works

```
6:23am  CEO agent reads the company status and plans up to 4 tasks
        ├─ Water Data agent  → verifies a city's water from the utility's own report (uses web search)
        ├─ Content agent     → writes a city guide, then a separate claims check reviews it
        └─ Marketing agent   → writes Pinterest pins, video scripts and the newsletter, with a claims check
        CEO agent writes your daily brief → it arrives as a GitHub issue (email or app notification)
You     approve or reject each item (about 5 minutes) → approved work goes live automatically
```

**Built-in guardrails**
- Nothing is published without your approval.
- Content is only written for cities whose data has been verified with sources.
- Every piece of copy goes through a rule-based **medical claims filter** (blocks words like "cures", "treats", "clinically proven") plus an AI compliance review. A failed draft is rewritten once, then dropped.
- A daily task cap (default 4) limits AI spending.

## One-time setup (about 20 minutes)

1. **Get a Claude API key** at console.anthropic.com → API Keys. Add a monthly spend limit there (start around $30).
2. **Add it to GitHub:** this repo → Settings → Secrets and variables → Actions → **New repository secret**, name `ANTHROPIC_API_KEY`.
3. *(Optional)* Under **Variables**, add `COMPANY_SITE_URL` (your domain) and `COMPANY_MAX_TASKS`.
4. **Publish the website:** Settings → Pages → Source: **GitHub Actions**. The site deploys from the `main` branch. (GitHub Pages on a *private* repo needs a paid GitHub plan. Otherwise drag the `site/` folder into Netlify or Cloudflare Pages for free.)
5. **Connect email sign-ups:** create a free MailerLite or Kit account, make a form, and paste its form URL into `site/assets/config.js` → `signupEndpoint`.
6. **Test it free:** Actions → **Daily agent run** → Run workflow → tick **Dry run**.

After that the team runs every morning by itself.

## Approving work (from your phone)

The daily brief lists numbered items. Open the GitHub app → this repo → **Actions** → **Approve agent work** → **Run workflow**, then type the numbers to approve (e.g. `3 4`) or reject.

When you approve:
- **Water data** → updates `data/cities.json` and the ZIP tool
- **City guides** → published to `site/cities/`
- **Marketing packs** → saved to `ops/outbox/`, ready to copy into Pinterest, TikTok/Reels and your newsletter

## Running it on a computer (optional)

```bash
pip install -r requirements.txt
python -m company run-daily --dry-run   # free test, no AI calls
export ANTHROPIC_API_KEY=...            # then for real:
python -m company run-daily
python -m company status
python -m company approve 3 4
python -m company build-site            # rebuild the ZIP tool data
cd site && python -m http.server        # preview the site at http://localhost:8000
```

Tests: `pip install pytest && python -m pytest tests` and `node --test tests/water_check.test.js`.

## Porchlight Puzzle Press (Amazon KDP books)

`kdp/` builds print-ready large-print puzzle books for Amazon KDP: interior PDF, wrap-around cover PDF, and a `listing.md` with the title, description, keywords, categories and price to paste into KDP. 34 books are already built in `kdp/books/`: 15 different top-selling product types (`--season top`), a 15-book Christmas collection (`--season christmas`) and 4 starter puzzle books. Start with [docs/kdp-playbook.md](docs/kdp-playbook.md).

```bash
python -m kdp list
python -m kdp build --all --out kdp/books
```

## Important

- The starter water numbers in `data/cities.json` are **estimates** (marked `verified: false`). The Water Data agent checks each city against the utility's Consumer Confidence Report and records sources. The website labels unverified data as an estimate.
- The site and all marketing are general water information, not medical advice. Keep it that way. See `company/claims.py`.
