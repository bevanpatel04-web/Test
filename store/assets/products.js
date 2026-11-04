// ===== CATALOG =====
// cost = estimated landed cost (product + US shipping) from CJdropshipping/AutoDS, Nov 2026.
// VERIFY each cost with your supplier before launch, then paste your checkout link.
// checkoutUrl: a Stripe Payment Link (Stripe → Payment Links → New, "let customers adjust quantity",
// "collect shipping address") or a Shopify product URL. Empty = button shows "Coming soon".
window.PRODUCTS = [
  {
    id: "blanket-hoodie",
    name: "Cloud Sherpa Blanket Hoodie",
    hook: "A blanket you can wear. Warm in minutes.",
    price: 49.99, compareAt: 79.99, cost: 16.5,
    emoji: "🧸", image: "",
    bullets: ["Oversized fit for all sizes", "Double-layer sherpa fleece", "Big front pocket", "Machine washable"],
    audience: "Remote workers, students, gamers, holiday gift buyers",
    checkoutUrl: "",
  },
  {
    id: "heated-mug",
    name: "Stay-Warm Mug & Desk Warmer Set",
    hook: "Your coffee stays hot until the last sip.",
    price: 34.99, compareAt: 54.99, cost: 11,
    emoji: "☕", image: "",
    bullets: ["Keeps drinks at about 131°F", "Auto shut-off for safety", "Includes 12 oz ceramic mug", "USB powered"],
    audience: "Work-from-home office gifts, coffee and tea drinkers",
    checkoutUrl: "",
  },
  {
    id: "heatless-curls",
    name: "Overnight Heatless Curl Set",
    hook: "Wake up with curls. No heat tools needed.",
    price: 24.99, compareAt: 39.99, cost: 4.5,
    emoji: "🎀", image: "",
    bullets: ["Soft satin curling rod", "2 scrunchies + 2 clips included", "Works on long and medium hair", "Comfortable to sleep in"],
    audience: "Women 18–40, beauty TikTok, stocking stuffers",
    checkoutUrl: "",
  },
  {
    id: "calming-pet-bed",
    name: "Calming Plush Donut Pet Bed",
    hook: "The bed your dog won't want to leave.",
    price: 49.99, compareAt: 74.99, cost: 17,
    emoji: "🐶", image: "",
    bullets: ["Raised rim supports head and neck", "Faux-fur shag", "Machine washable", "Non-slip base · S / M / L"],
    audience: "Dog and cat owners, anxious pets, pet-parent gifts",
    checkoutUrl: "",
  },
  {
    id: "touch-gloves",
    name: "Thermal Touchscreen Gloves",
    hook: "Text, scroll, and pay without freezing your fingers.",
    price: 22.99, compareAt: 34.99, cost: 4,
    emoji: "🧤", image: "",
    bullets: ["Touchscreen thumb and finger", "Fleece-lined, wind resistant", "Silicone grip palm", "Unisex sizes"],
    audience: "Commuters, cold-climate states, stocking stuffers",
    checkoutUrl: "",
  },
];

// Bundles lift average order value. This is the main lever for hitting $1,000/week.
window.BUNDLES = [
  {
    id: "cozy-night-in",
    name: "Cozy Night In Bundle",
    includes: ["blanket-hoodie", "heated-mug"],
    price: 69.99, cost: 27.5,
    note: "Our best-selling gift. Save $15.",
    checkoutUrl: "",
  },
  {
    id: "stocking-stuffer-trio",
    name: "Stocking Stuffer Trio",
    includes: ["heatless-curls", "touch-gloves", "heated-mug"],
    price: 69.99, cost: 19.5,
    note: "Three gifts, one click. Save $13.",
    checkoutUrl: "",
  },
];

if (typeof module !== "undefined") module.exports = { PRODUCTS: window.PRODUCTS, BUNDLES: window.BUNDLES };
