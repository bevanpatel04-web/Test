# Using ChatGPT as your ad manager

ChatGPT makes the decisions and writes the ads. **You click the buttons** in Meta Ads Manager and TikTok Ads Manager and paste in the numbers. Daily work takes about 10 minutes.

## Step 1: Create a ChatGPT Project named "Snug & Co. Ads"

Put everything below into the Project's **Instructions**. Then upload `docs/dropshipping-plan.md` and `store/assets/products.js` as Project files. Keep every day's report in this one Project so ChatGPT remembers past results.

```
You are the performance ad manager for Snug & Co., a US dropshipping store selling cozy winter gifts.
Goal: $1,000/week profit. Decide using the numbers I paste, not gut feeling. Be blunt.

PRODUCTS (price / profit before ads):
- Blanket hoodie $49.99 / $29.24   (main product)
- Heatless curl set $24.99 / $18.22 (main product)
- Heated mug set $34.99 / $20.93
- Calming pet bed $49.99 / $28.74
- Touchscreen gloves $22.99 / $16.87
- Bundles $69.99 / $36–45
Blended average order ~$52, profit before ads ~$30.

TARGETS: CPA ≤ $15 (target), break-even CPA $30, ROAS ≥ 3.5 target, 1.7 break-even.
Leading indicators: CTR (link) ≥ 1.2%, CPC ≤ $1.20, add-to-checkout rate ≥ 6% of link clicks.

RULES (apply them exactly):
1. Leave a new ad alone for 48 hours or until it has spent $30, whichever comes first.
2. KILL an ad if: spend ≥ $30 with 0 purchases; OR CTR < 0.8% after 2,000 impressions; OR CPA > $30 after 3+ purchases.
3. WATCH an ad if: CPA $15–30. Leave the budget as is. Suggest one new hook to test against it.
4. SCALE an ad set if: CPA ≤ $15 with 3+ purchases over the last 3 days. Raise its budget 20–30% at most, no more than once every 48 hours. Never double it.
5. When an ad clearly wins, also copy it into a new ad set with a broad audience at the same budget.
6. If total weekly ad spend > 50% of revenue, cut the worst 30% of spend before adding anything.
7. Keep at least 3 active ads per product. When one is killed, give me a replacement concept.
8. Total daily budget never goes over what I tell you my cap is.

OUTPUT FORMAT every time:
- Scoreboard: spend, revenue, orders, CPA, ROAS, estimated profit (orders × $30 − spend), progress toward $1,000/week.
- Actions table: ad name | KILL / WATCH / SCALE / KEEP | new budget | reason (one line).
- New creative: for every killed ad, one replacement (hook, 15-second script, caption, headline).
- One sentence: the most important thing to do today.
Ask me for any number you need that I didn't give you. Never make up numbers.
```

## Step 2: Daily report (each morning, about 10 minutes)

1. Meta Ads Manager → **Ads** tab → date range **Last 3 days** → Columns: *Performance and clicks* → add **Purchases, Cost per purchase, Purchase ROAS, Adds to cart, Checkouts initiated**. Export it (Reports → Export table data → CSV), or screenshot it.
2. Do the same in TikTok Ads Manager if you run TikTok ads.
3. Paste this into ChatGPT along with the file:

```
Daily report. Date: ____. My daily budget cap: $____.
Stripe/Shopify actual orders yesterday: __, revenue: $____.
Attached: Meta (and TikTok) ad-level export for the last 3 days.
Apply the rules and give me today's actions.
```

4. Make exactly the changes it lists. Don't touch anything else.

> Use **actual Stripe/Shopify orders** to check the ad platform's numbers. The pixel often over- or under-counts. If they disagree by more than 20%, tell ChatGPT and have it judge by actual orders.

## Step 3: Make ads (when launching and every time one is killed)

```
Write 3 new ad concepts for [product]. Audience: [e.g. women 18–34 who watch beauty TikTok].
For each: a scroll-stopping hook (first 2 seconds), a 15-second UGC-style script with shot list
I can film on my phone, primary text (under 125 chars), headline (under 40 chars), and which
angle it tests (problem/solution, gift, before/after, unboxing, price/deal).
No false claims, no fake reviews, no "as seen on TV".
```

Angles that tend to work for these products:
- **Hoodie:** "POV: you never leave the couch again" / gift reveal reaction / "the only gift my boyfriend actually uses".
- **Curls:** time-lapse of putting it on at night → morning reveal. This is the strongest format.
- **Mug:** "I haven't microwaved my coffee in 2 months".
- **Pet bed:** dog's first reaction / "my anxious dog finally sleeps".
- **Gloves:** close-up of texting outside in the snow.

Use the ad link `https://YOURDOMAIN/?p=blanket-hoodie` (or `heatless-curls`, `heated-mug`, `calming-pet-bed`, `touch-gloves`) so the product the ad shows appears first on the page.

## Step 4: Campaign setup (one time, Meta)

```
Campaign: Sales objective · Advantage+ off at first · CBO off (budget per ad set while testing)
  Ad set "Hoodie – Broad US":  $25/day · US · 18–55 · Advantage+ audience · placements Advantage+
     3 ads (3 different hooks)
  Ad set "Curls – Broad US":   $25/day · US · women 18–44 · same settings
     3 ads
Conversion event: Purchase
```
Test week = $50/day ≈ $350. After you have 2–3 winning ads, move them into one CBO or Advantage+ Shopping campaign and scale with Rule 4.

TikTok: the same structure in TikTok Ads Manager, $20/day per ad group minimum, Smart+ off at first. Curls and the hoodie work especially well on TikTok.

## Step 5: Weekly review (Sunday)

```
Weekly review. Actual orders: __, revenue: $____, ad spend: $____, refunds: $____.
Attached: 7-day ad-level export.
1) True profit this week (orders × product profit − spend − refunds).
2) What's working and why, in one paragraph.
3) Budget plan for next week to move toward $1,000/week profit without breaking rules.
4) Should I add or drop a product? Suggest replacements if any product has had 0 winners after $150 spent.
```

## Safety limits
- Set a **spending limit on the ad account** (Meta: Billing → Account spending limit) equal to what you can afford to lose this month.
- ChatGPT can be wrong about Ads Manager menus. If a setting it names doesn't exist, ask it for the current equivalent.
- Ads must not make health claims (e.g. "cures anxiety" for the pet bed, "no damage" as a promise). Say "helps" / "designed for", and only claim what the supplier listing supports.
