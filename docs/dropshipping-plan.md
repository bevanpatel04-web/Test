# Snug & Co. — dropshipping plan to $1,000/week profit

Working name. Storefront: `store/`. Ad playbook: `docs/chatgpt-ad-manager.md`.

## 1. The 5 products (researched November 4, 2026)

All five fit one theme: **cozy winter + holiday gifting.** Buyers are shopping for gifts right now, and one theme lets one brand, one audience and one style of ad sell all five. Sources: CJdropshipping "Best Dropshipping Products November 2026", FFOrder's November US guide, and AutoDS's Q4 list. Adobe forecasts US holiday online spending of $275.1B (+6.7% YoY).

| # | Product | Why it's growing now | Price | Est. landed cost | Profit before ads |
|---|---|---|---|---|---|
| 1 | Sherpa blanket hoodie | Cold weather, remote work, gifting. CJ's #1 pick for November | $49.99 | ~$16.50 | $29.24 |
| 2 | Heated mug + desk warmer | Gift for people who work from home. 60–72% margin (FFOrder) | $34.99 | ~$11.00 | $20.93 |
| 3 | Heatless curl set | Made for TikTok tutorial content. Online cosmetics forecast +9.5% this holiday | $24.99 | ~$4.50 | $18.22 |
| 4 | Calming plush pet bed | Pet spending keeps growing. Winter prep and gifts for pet owners | $49.99 | ~$17.00 | $28.74 |
| 5 | Touchscreen thermal gloves | Solves a clear winter problem. Cheap stocking stuffer | $22.99 | ~$4.00 | $16.87 |
| B1 | Cozy Night In bundle (1+2) | Raises average order value | $69.99 | ~$27.50 | $36.66 |
| B2 | Stocking Stuffer Trio (3+5+2) | Raises average order value | $69.99 | ~$19.50 | $44.66 |

"Profit before ads" = price − cost − Stripe fees (2.9% + $0.30) − a 5% reserve for refunds and chargebacks.
**Costs are estimates. Check each one in CJdropshipping or AutoDS (US warehouse, 5–9 day delivery) before launch and update `store/assets/products.js`.**

**Lead with product 1 (hoodie) and product 3 (curls).** Both show well on video, and the hoodie has the best profit per order. The other three are cross-sells, bundle items and backup ads to test.

## 2. The $1,000/week math

Blended assumptions: average order $52 (some bundles), average cost $17.50. That leaves **about $30 profit per order before ads.**

| Cost per purchase (CPA) | Profit/order | Orders/week | Orders/day | Ad spend/week | Revenue/week | ROAS needed |
|---|---|---|---|---|---|---|
| $12 | $18.09 | 56 | 8 | $672 | $2,912 | 4.3 |
| **$15 (target)** | **$15.09** | **67** | **~10** | **$1,005** | **$3,484** | **3.5** |
| $18 | $12.09 | 83 | 12 | $1,494 | $4,316 | 2.9 |
| $20 | $10.09 | 100 | 14 | $2,000 | $5,200 | 2.6 |

**Break-even CPA ≈ $30 (ROAS ≈ 1.7).** Above that, every sale loses money.
**Goal: about 10 orders/day at a $15 CPA, which works out to about $1,000/week profit.**

### Be realistic
- You will not hit this in week 1. Expect 2–4 weeks of testing at break-even or a small loss. **Budget $500–$1,000 for testing that you can afford to lose.**
- Most new stores never reach this number. The ones that do find one ad that works and scale it. The kill/scale rules in the ad playbook exist so testing money isn't wasted.
- Demand for these products drops after about December 20. Plan to switch to January products (fitness, organization, Valentine's) in mid-December. ChatGPT can run the same research for that.

## 3. Launch checklist

**Day 1–2: set up**
1. Open a **Stripe** account. Create one Payment Link per product and bundle (turn on "collect shipping address" and "adjustable quantity"), plus the `COZY15` promo code. Paste each link into `checkoutUrl` in `store/assets/products.js`.
   - *Or use Shopify ($1 first month trial):* import the 5 products through the CJ or AutoDS app and copy the text from this store. Shopify handles the cart, upsells and order sync with the supplier. **This is the easier long-term option once orders start.**
2. Order **1 sample of products 1 and 3** to film your own videos. Your own footage beats supplier photos.
3. Replace the emoji placeholders with supplier photos (the `image` field in products.js).
4. Fill in your support email and business address in `store/assets/config.js` and `store/policies.html`. Meta rejects stores without real policies.
5. Publish: drag the `store/` folder into **Netlify Drop** or **Cloudflare Pages** (free) and connect a domain (about $10).
6. Install the **Meta Pixel** and the **TikTok Pixel**: paste the IDs into `config.js`. Also set up "Purchase" as a conversion in Stripe or Shopify.

**Day 3–9: test (about $50/day)**
- Follow the "Test phase" in `docs/chatgpt-ad-manager.md`.
- 2 products × 3 ads each. Use `?p=blanket-hoodie` style links so each ad opens on its own product.

**Day 10+: scale**
- Raise budget 20–30% every 48 hours on ad sets with CPA ≤ $15. Turn off the rest. Repeat every week.

## 4. Fulfilling orders (each day)
- Stripe sends each order to your email. Place the same order in CJ or AutoDS with the customer's address (on Shopify the app does this automatically).
- Email the tracking number when you get it. Answer support emails within 24 hours. Fast replies prevent chargebacks.
