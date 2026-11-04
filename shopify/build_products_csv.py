"""Builds shopify/products.csv (Shopify product import format). Run: python shopify/build_products_csv.py"""
import csv
from pathlib import Path

COLUMNS = [
    "Handle", "Title", "Body (HTML)", "Vendor", "Type", "Tags", "Published",
    "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value",
    "Variant SKU", "Variant Grams", "Variant Inventory Tracker", "Variant Inventory Policy",
    "Variant Fulfillment Service", "Variant Price", "Variant Compare At Price",
    "Variant Requires Shipping", "Variant Taxable", "Variant Weight Unit", "Cost per item",
    "Image Src", "Image Position", "Image Alt Text", "Gift Card", "SEO Title", "SEO Description", "Status",
]

VENDOR = "Snug & Co."


def body(intro, bullets, specs, care):
    li = "".join(f"<li>{b}</li>" for b in bullets)
    sp = "".join(f"<li><strong>{k}:</strong> {v}</li>" for k, v in specs)
    return f"<p>{intro}</p><ul>{li}</ul><h4>Specs</h4><ul>{sp}</ul><h4>Care</h4><p>{care}</p>"


# Each product: options, and variants as (option values, sku, grams, price, compare_at, cost)
PRODUCTS = [
    {
        "handle": "cloud-sherpa-blanket-hoodie",
        "title": "Cloud Sherpa Blanket Hoodie",
        "type": "Loungewear",
        "tags": "bestseller, gift, for-her, for-him, homebody, winter",
        "seo_title": "Cloud Sherpa Blanket Hoodie | Oversized Wearable Blanket",
        "seo_desc": "The oversized sherpa blanket hoodie you'll live in all winter. Double-layer fleece, giant pocket, one size fits most. Free US shipping.",
        "body": body(
            "Part blanket, part hoodie, fully the coziest thing you'll own. The Cloud is cut extra-oversized with a plush sherpa lining, so it feels like being wrapped in your favorite throw while you work, read, game or nap.",
            ["Double-layer flannel fleece outside, sherpa inside", "Oversized one-size fit, made to drape", "Deep front pocket for hands, phone and snacks",
             "Roomy hood with soft lining", "Ribbed cuffs keep sleeves in place"],
            [("Fit", "One size fits most adults, approx. 37\" long"), ("Material", "100% polyester fleece and sherpa")],
            "Machine wash cold on gentle, tumble dry low. Gets softer with every wash.",
        ),
        "options": ["Color"],
        "variants": [
            (["Oatmeal"], "SNUG-HOOD-OAT", 1200, 49.99, 79.99, 16.50),
            (["Charcoal"], "SNUG-HOOD-CHR", 1200, 49.99, 79.99, 16.50),
            (["Sage"], "SNUG-HOOD-SAG", 1200, 49.99, 79.99, 16.50),
            (["Blush"], "SNUG-HOOD-BLU", 1200, 49.99, 79.99, 16.50),
        ],
    },
    {
        "handle": "stay-warm-mug-warmer-set",
        "title": "Stay-Warm Mug & Desk Warmer Set",
        "type": "Kitchen & Desk",
        "tags": "bestseller, gift, coffee-lover, work-from-home, winter",
        "seo_title": "Stay-Warm Mug & Desk Warmer Set | Keeps Coffee Hot",
        "seo_desc": "A ceramic mug and slim warmer plate that keeps coffee and tea hot at your desk. Auto shut-off. A perfect work-from-home gift.",
        "body": body(
            "Your coffee, still hot by the last sip. The slim warmer plate holds your drink at a cozy, sippable temperature while you work, so you'll never reheat a forgotten mug again.",
            ["Holds drinks at about 131°F (55°C)", "Auto shut-off after 4 hours for peace of mind", "Includes a 12 oz matte ceramic mug",
             "Works with flat-bottom mugs and cups", "Gift-ready box"],
            [("Mug", "12 oz ceramic"), ("Power", "USB-C, adapter not included"), ("Plate", "4\" diameter")],
            "Wipe the warmer with a dry cloth. Mug is dishwasher safe. Do not microwave the warmer.",
        ),
        "options": ["Color"],
        "variants": [
            (["Cream"], "SNUG-MUG-CRM", 650, 34.99, 54.99, 11.00),
            (["Sage"], "SNUG-MUG-SAG", 650, 34.99, 54.99, 11.00),
            (["Charcoal"], "SNUG-MUG-CHR", 650, 34.99, 54.99, 11.00),
        ],
    },
    {
        "handle": "overnight-heatless-curl-set",
        "title": "Overnight Heatless Curl Set",
        "type": "Beauty",
        "tags": "bestseller, gift, for-her, beauty, stocking-stuffer",
        "seo_title": "Overnight Heatless Curl Set | Satin Curling Rod",
        "seo_desc": "Wrap, sleep, wake up to soft curls with no hot tools. Satin curling rod plus scrunchies and clips. Free US shipping.",
        "body": body(
            "Soft, bouncy curls without a single hot tool. Wrap damp or dry hair around the satin rod before bed, sleep comfortably, and unwrap in the morning.",
            ["Smooth satin cover is gentle on hair", "Plush foam core you can sleep on", "Includes 2 satin scrunchies and 2 claw clips",
             "Works on medium to long hair", "Takes about 2 minutes to put on"],
            [("Rod length", "approx. 33\""), ("Material", "Satin cover, foam core")],
            "Hand wash the cover in cool water and air dry.",
        ),
        "options": ["Color"],
        "variants": [
            (["Champagne"], "SNUG-CURL-CHA", 120, 24.99, 39.99, 4.50),
            (["Blush"], "SNUG-CURL-BLU", 120, 24.99, 39.99, 4.50),
            (["Black"], "SNUG-CURL-BLK", 120, 24.99, 39.99, 4.50),
        ],
    },
    {
        "handle": "cloud-donut-pet-bed",
        "title": "Cloud Donut Pet Bed",
        "type": "Pet",
        "tags": "gift, pet-parent, dogs, cats, winter",
        "seo_title": "Cloud Donut Pet Bed | Plush Round Bed for Dogs & Cats",
        "seo_desc": "A plush donut bed with a raised rim pets love to curl into. Machine washable, non-slip base. Sizes for cats to large dogs.",
        "body": body(
            "The bed they'll choose over your couch. A deep, round donut shape with a raised plush rim gives pets a cozy place to curl up and rest their heads.",
            ["Raised rim supports head and neck", "Long faux-fur shag that stays soft", "Fully machine washable",
             "Non-slip, water-resistant base", "Sizes for cats, small, medium and large dogs"],
            [("Small", "20\" for cats and dogs up to 15 lb"), ("Medium", "24\" for dogs up to 35 lb"), ("Large", "32\" for dogs up to 70 lb")],
            "Machine wash cold on gentle, tumble dry low or air dry. Fluff after washing.",
        ),
        "options": ["Size", "Color"],
        "variants": [
            (["Small 20\"", "Taupe"], "SNUG-BED-S-TAU", 800, 44.99, 64.99, 13.00),
            (["Small 20\"", "Cream"], "SNUG-BED-S-CRM", 800, 44.99, 64.99, 13.00),
            (["Medium 24\"", "Taupe"], "SNUG-BED-M-TAU", 1200, 54.99, 79.99, 17.00),
            (["Medium 24\"", "Cream"], "SNUG-BED-M-CRM", 1200, 54.99, 79.99, 17.00),
            (["Large 32\"", "Taupe"], "SNUG-BED-L-TAU", 1800, 69.99, 99.99, 24.00),
            (["Large 32\"", "Cream"], "SNUG-BED-L-CRM", 1800, 69.99, 99.99, 24.00),
        ],
    },
    {
        "handle": "thermal-touchscreen-gloves",
        "title": "Thermal Touchscreen Gloves",
        "type": "Accessories",
        "tags": "gift, for-him, for-her, commuter, stocking-stuffer, winter",
        "seo_title": "Thermal Touchscreen Gloves | Fleece-Lined Winter Gloves",
        "seo_desc": "Fleece-lined winter gloves with touchscreen fingertips. Text, scroll and pay without taking them off. Unisex sizes.",
        "body": body(
            "Text, scroll and tap to pay without taking your gloves off. Fleece-lined for warmth with touchscreen-ready thumb and index fingers.",
            ["Touchscreen thumb and index finger", "Soft fleece lining", "Wind-resistant knit shell",
             "Silicone grip palm so your phone stays put", "Unisex fit"],
            [("S/M", "palm width up to 3.5\""), ("L/XL", "palm width 3.5\"–4\""), ("Material", "Polyester, spandex, fleece lining")],
            "Hand wash cold and lay flat to dry.",
        ),
        "options": ["Color", "Size"],
        "variants": [
            (["Black", "S/M"], "SNUG-GLV-BLK-SM", 80, 22.99, 34.99, 4.00),
            (["Black", "L/XL"], "SNUG-GLV-BLK-LX", 80, 22.99, 34.99, 4.00),
            (["Grey", "S/M"], "SNUG-GLV-GRY-SM", 80, 22.99, 34.99, 4.00),
            (["Grey", "L/XL"], "SNUG-GLV-GRY-LX", 80, 22.99, 34.99, 4.00),
            (["Camel", "S/M"], "SNUG-GLV-CAM-SM", 80, 22.99, 34.99, 4.00),
            (["Camel", "L/XL"], "SNUG-GLV-CAM-LX", 80, 22.99, 34.99, 4.00),
        ],
    },
]


def rows():
    for p in PRODUCTS:
        for i, (vals, sku, grams, price, compare, cost) in enumerate(p["variants"]):
            first = i == 0
            r = dict.fromkeys(COLUMNS, "")
            r.update({
                "Handle": p["handle"],
                "Option1 Value": vals[0],
                "Option2 Value": vals[1] if len(vals) > 1 else "",
                "Variant SKU": sku, "Variant Grams": grams,
                "Variant Inventory Policy": "continue", "Variant Fulfillment Service": "manual",
                "Variant Price": f"{price:.2f}", "Variant Compare At Price": f"{compare:.2f}",
                "Variant Requires Shipping": "TRUE", "Variant Taxable": "TRUE",
                "Variant Weight Unit": "g", "Cost per item": f"{cost:.2f}",
            })
            if first:
                r.update({
                    "Title": p["title"], "Body (HTML)": p["body"], "Vendor": VENDOR, "Type": p["type"],
                    "Tags": p["tags"], "Published": "TRUE",
                    "Option1 Name": p["options"][0], "Option2 Name": p["options"][1] if len(p["options"]) > 1 else "",
                    "Gift Card": "FALSE", "SEO Title": p["seo_title"], "SEO Description": p["seo_desc"], "Status": "active",
                })
            yield r


if __name__ == "__main__":
    out = Path(__file__).with_name("products.csv")
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows())
    print(f"wrote {out}")
