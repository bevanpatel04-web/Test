# Data contract: rewards backend → pilot dashboard

The backend (`rewards/`) exports these two JSON files. The dashboard (`invest/site/pilot/`) reads them. Both sides must match this exactly. Money is in US dollars as numbers; dates are ISO `YYYY-MM-DD`; ids are strings.

## 1. Employer dashboard: `invest/site/pilot/data/employer.json`

```json
{
  "as_of": "2026-11-14",
  "employer": {
    "id": "emp_demo",
    "name": "Demo Diner Group",
    "plan": "pilot",
    "pepm_usd": 4.0,
    "points_per_usd": 100,
    "pool_funded_usd": 5000.0,
    "pool_remaining_usd": 3120.5
  },
  "summary": {
    "eligible": 400,
    "enrolled": 240,
    "active_30d": 181,
    "points_issued": 214000,
    "points_redeemed": 187950,
    "points_outstanding": 26050
  },
  "retention": [
    { "month": "2026-06", "enrolled_pct": 100.0, "not_enrolled_pct": 100.0 },
    { "month": "2026-07", "enrolled_pct": 95.8, "not_enrolled_pct": 90.1 }
  ],
  "earning_by_rule": [
    { "rule": "tenure_30", "label": "30 days on the job", "points": 72000 }
  ],
  "redemptions": [
    { "type": "payroll_bonus", "label": "Payroll bonus", "count": 120, "usd": 1500.0 },
    { "type": "gift_card", "label": "Gift card", "count": 45, "usd": 379.5 }
  ],
  "members": [
    { "id": "m_001", "display_name": "Member 001", "tenure_days": 95, "points_balance": 450, "lessons_completed": 4, "last_active": "2026-11-10" }
  ]
}
```

- `retention`: share of each starting group still employed, by month since the pilot began. The first month is 100 for both groups. `not_enrolled_pct` is the comparison group (eligible employees who didn't join).
- `members`: display names only. **No real names, emails or other personal data** in exports.

## 2. Member view: `invest/site/pilot/data/member.json`

```json
{
  "as_of": "2026-11-14",
  "member": { "id": "m_001", "display_name": "Member 001", "employer_name": "Demo Diner Group", "tenure_days": 95 },
  "points_balance": 450,
  "points_per_usd": 100,
  "history": [
    { "date": "2026-10-12", "kind": "earn", "rule": "tenure_90", "label": "90 days on the job", "points": 300 },
    { "date": "2026-10-20", "kind": "redeem", "rule": "gift_card", "label": "Gift card", "points": -500 }
  ],
  "next_milestones": [
    { "rule": "tenure_180", "label": "180 days on the job", "points": 600, "progress_pct": 52.8 }
  ],
  "catalog": [
    { "type": "payroll_bonus", "label": "Payroll bonus", "min_points": 500, "note": "Paid by your employer in your next paycheck. Taxed like regular pay." },
    { "type": "gift_card", "label": "Gift card", "min_points": 500, "note": "Delivered by email within 5 business days." }
  ]
}
```

## Earning rules and reward schedules

Every employer uses the same seven rules. How many points each rule pays depends on the employer's **reward schedule** (`rewards/rules.py` `SCHEDULES`). Pilots use **boosted** (decided Nov 14, 2026; see `docs/pilot/decisions.md`). `standard` is the original table, kept for comparison. The exports don't name the schedule; they simply carry the points.

| rule | label | standard | boosted (pilots) |
|---|---|---|---|
| `tenure_30` | 30 days on the job | 300 | 3,000 |
| `tenure_90` | 90 days on the job | 300 | 4,000 |
| `tenure_180` | 180 days on the job | 600 | 3,000 |
| `tenure_365` | One year on the job | 1,000 | 3,000 |
| `lesson_completed` | Finished a lesson | 50 each, max 10 lessons | 100 each, max 10 lessons |
| `checklist_completed` | Finished the "before you invest" checklist | 200, once | 500, once |
| `savings_setup` | Set up direct deposit to savings | 300, once | 500, once |
| | **Most one person can earn in a first year** | **3,200 ($32)** | **15,000 ($150)** |

A schedule change only affects points earned from then on. Past ledger rows never change.

Rules that reward trading, trade counts or account balances are **not allowed**, and the backend must reject them.
