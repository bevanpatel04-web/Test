# Launch Snug & Co. on Shopify (about 45 minutes)

Two files do most of the work:
- **`snug-hearth-theme.zip`**: a custom premium theme ("Hearth"). It has an editorial serif and warm ivory/espresso design, a slide-out cart with a "buy 2, save 15%" progress bar, a sticky add-to-bag bar on phones, a Christmas cutoff message, and is ready for reviews apps. It passes Shopify's official Theme Check with 0 issues.
- **`products.csv`**: all 5 products with 22 variants, prices, compare-at prices, your cost per item, written descriptions, SEO titles and tags.

To download them, open each file on GitHub and click the download button (top-right of the file view).

## 1. Store basics (10 min)
1. Start a Shopify trial at shopify.com. **Settings → Store details**: store name `Snug & Co.` (or your own), support email, business address.
2. **Settings → Payments**: turn on Shopify Payments, Shop Pay, Apple Pay and Google Pay.
3. **Settings → Shipping and delivery**: one US rate, "Free shipping", $0.
4. **Settings → Policies**: click "Create from template" for Refund, Privacy, Shipping and Terms. Set returns to 30 days. Meta checks these before approving ads.

## 2. Install the theme (3 min)
**Online Store → Themes → Add theme → Upload zip file** → choose `snug-hearth-theme.zip` → **Publish**.
Click **Customize** to change any text, colors or fonts, or to upload your own logo and hero photos. The homepage uses free Unsplash photos until you upload your own.

## 3. Import the products (3 min)
**Products → Import → `products.csv`** → Upload and preview → Import.
All 5 products appear with their variants and prices. They don't have photos yet; you add those in step 4.

## 4. Connect your supplier + add photos (20 min)
1. Install the **CJdropshipping** app from the Shopify App Store (free). AutoDS also works.
2. In CJ, search each product (e.g. "sherpa wearable blanket hoodie", "heatless curling rod", "cup warmer mug set", "donut plush pet bed", "touchscreen fleece gloves").
   Pick listings with a **US warehouse** and good ratings. **Check the colors and sizes match the CSV** (rename the variants in Shopify if they differ).
3. Open each product in CJ → **Connect** → pick the matching Shopify product → map each variant. Now when an order comes in, CJ fulfils it.
4. Download each CJ listing's images (the "download images" button on the CJ product page) and drag them into the matching Shopify product under **Media**. Put a lifestyle shot second; the theme swaps to it when shoppers hover over the product.
5. **Check costs**: if CJ's price plus shipping is higher than the "Cost per item" in Shopify, update it there. Every product needs at least $15 profit before ads.

## 5. Turn on the offers (3 min)
- **Discounts → Create discount → Amount off products → Automatic discount**. Name it "Buy 2, save 15%", 15%, all products, minimum quantity **2**. The theme's cart progress bar and banners already advertise it.
- (Optional) **Discounts → Code** `WELCOME10`, 10% off, one use per customer. The footer sign-up form promises this, so email it to new subscribers with Shopify Email.

## 6. Menus (3 min)
**Online Store → Navigation**:
- **Main menu**: Shop all (`/collections/all`), Hoodie, Gifts, Pets (link to products), Contact.
- **Footer menu**: Contact, Track order, FAQ.
Create a **Contact** page under Online Store → Pages with template `page.contact`.

## 7. Reviews (5 min)
Install **Judge.me** (free plan). In Customize → Home page → "Apps (e.g. reviews)" section → **Add block** → Judge.me carousel. On the product page add the Judge.me stars and reviews blocks.
The reviews section stays hidden until a reviews app is added. Only ever show real reviews. You can ask your first buyers for photo reviews through Judge.me's automatic emails.

## 8. Tracking for ads (5 min)
- **Meta**: install the **Facebook & Instagram** app → connect your Business account → set data sharing to **Maximum** (pixel + Conversions API).
- **TikTok**: install the **TikTok** app → connect → turn on the pixel with "Advanced" data sharing.
Shopify sends Purchase events automatically. ChatGPT needs them to judge your ads (see `docs/chatgpt-ad-manager.md`).

## 9. Launch
**Online Store → Preferences → Password protection: off.** Place one real test order yourself and refund it, to check checkout and that CJ receives the order. Then start ads.

Ad links go to product pages, e.g. `https://YOURSTORE.com/products/cloud-sherpa-blanket-hoodie`.
Product links: `cloud-sherpa-blanket-hoodie`, `stay-warm-mug-warmer-set`, `overnight-heatless-curl-set`, `cloud-donut-pet-bed`, `thermal-touchscreen-gloves`.

---
*Editing the theme or products:* the source is in `shopify/theme/`. Rebuild the zip with `cd shopify/theme && zip -qr ../snug-hearth-theme.zip .`. Edit products in `shopify/build_products_csv.py`, then run `python shopify/build_products_csv.py`.
