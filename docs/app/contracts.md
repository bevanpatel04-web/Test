# Shared data formats for the learning app

Three agents build in parallel against these formats. Don't add or rename keys without updating this file. The lead has to approve the change.

## 1. Curriculum: `invest/data/curriculum.json` (owned by the Curriculum agent)

```json
{
  "version": 1,
  "updated": "2026-11-15",
  "levels": [
    {
      "id": "L1",
      "number": 1,
      "title": "Money foundations",
      "summary": "One or two plain sentences.",
      "free": true,
      "modules": [
        {
          "id": "L1-M1",
          "title": "Where your money goes",
          "summary": "One sentence.",
          "lessons": [
            {
              "slug": "what-a-budget-is-for",
              "title": "What a budget is actually for",
              "minutes": 3,
              "objectives": ["Explain ...", "..."],
              "key_points": ["...", "...", "..."],
              "prerequisites": [],
              "needs_facts": [],
              "risk_note": null,
              "try_it": { "tool": "money-map", "prompt": "One sentence telling the member what to try." },
              "quiz": [
                { "q": "Question?", "choices": ["A", "B", "C"], "answer": 1, "why": "One-sentence explanation." }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

Rules:
- **Levels:** 5 levels, numbered 1-5. Level 1 is `free: true` and the rest are `false`.
- **Slugs:** lowercase letters, digits and hyphens, unique across the whole curriculum. They're used as file names for videos.
- **Order:** the order of lessons within a module, and of modules within a level, is the learning order.
- **`prerequisites`:** slugs only. They must point to earlier lessons.
- **`needs_facts`:** keys from `invest/data/facts.json`. A lesson that cites a statistic must list it.
- **`risk_note`:** a string, required for any lesson that touches returns, investing products, leverage, options or crypto. Otherwise `null`.
- **`try_it.tool`:** one of `calculator` (the existing start-now-vs-later tool), `crash-sim`, `money-map`, `none`.
- **`quiz`:** exactly 3 questions, each with 3 choices. `answer` is the 0-based index of the correct choice.
- All text must pass the claims filter.

## 2. Video manifest: `invest/site/media/videos/manifest.json` (owned by the Video studio agent)

```json
{
  "updated": "2026-11-15",
  "videos": {
    "what-a-budget-is-for": {
      "mp4": "media/videos/what-a-budget-is-for.mp4",
      "captions": "media/videos/what-a-budget-is-for.vtt",
      "poster": "media/videos/what-a-budget-is-for.jpg",
      "duration_s": 154,
      "narration": "none",
      "ai_label": "Made with AI, reviewed by a person",
      "approved": false
    }
  }
}
```

- **Paths:** relative to `invest/site/`.
- **`narration`:** `"none"` (captions only) or the name of the voice provider used.
- **`approved`:** stays `false` until the founder approves the video. The app shows unapproved videos only with a "Draft" badge.
- **Missing videos:** a lesson with no entry has no video yet. The app must handle that gracefully.

## 3. Member progress (browser only, owned by the App builder)

`localStorage` key `pm.progress.v1`:
`{ "completed": { "<slug>": "<ISO date>" }, "quiz": { "<slug>": {"best": 2, "tries": 1} }, "review_due": { "<slug>": "<ISO date>" }, "money_map": { ... }, "member": false }`

- **Prototype only:** this lives on the member's device and is never sent anywhere.
- **`member`:** `true` after the mock checkout, which unlocks Levels 2-5 in the prototype.
- **Dates:** calendar days (`YYYY-MM-DD`, the member's local date). `review_due` holds the next review: 3, then 10, then 30 days after `completed`. It's removed after the last one.
- **`money_map`:** written by `app/money-map.html`. Every number is a number or `null`; months are `YYYY-MM`. The worksheet is open to everyone; the combined summary is members-only.
  `{ "pay": 3000, "gross": 3800, "costs": [{"name": "Rent", "amount": 1200}], "flexible": 350,
  "cushion": {"months": 1, "saved": 500, "where": "Savings account", "rate": 3.5, "insured": true},
  "debts": [{"name": "Card", "balance": 2000, "rate": 24, "minimum": 60}], "credit_checked": "2026-03",
  "accounts": {"checking": true}, "other_accounts": "", "goals": [{"name": "Trip", "amount": 1200, "by": "2027-11"}], "updated": "<ISO time>" }`
  Account keys: `checking`, `savings`, `workplace`, `roth_ira`, `traditional_ira`, `brokerage`, `hsa`. Code: `normalizeMoneyMap()` in `invest/site/app/assets/learn.js`.
