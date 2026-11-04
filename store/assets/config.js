// ===== STORE SETTINGS — edit this file, nothing else needs code changes =====
window.STORE_CONFIG = {
  name: "Snug & Co.",            // working name — change any time
  tagline: "Cozy winter gifts, shipped fast.",
  supportEmail: "support@example.com",   // REQUIRED before running ads
  currency: "USD",
  freeShippingNote: "Free US shipping on every order",
  shippingTime: "Ships in 1–3 days · arrives in 5–9 business days",

  // Ad tracking. Paste your IDs; leave "" to switch off.
  metaPixelId: "",     // Meta Events Manager → Data sources → Pixel ID
  tiktokPixelId: "",   // TikTok Ads Manager → Assets → Events → Web events

  // Discount shown in the top banner (create the same code in Stripe/Shopify)
  promo: { code: "COZY15", text: "15% off 2+ items with code COZY15" },
};
