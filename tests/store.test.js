const test = require("node:test");
const assert = require("node:assert");
globalThis.window = {};
const { PRODUCTS, BUNDLES } = require("../store/assets/products.js");

const contribution = (x) => x.price - x.cost - (x.price * 0.029 + 0.3) - x.price * 0.05;

test("there are 5 products with unique ids and required fields", () => {
  assert.strictEqual(PRODUCTS.length, 5);
  assert.strictEqual(new Set(PRODUCTS.map((p) => p.id)).size, 5);
  for (const p of PRODUCTS) {
    for (const k of ["name", "hook", "price", "compareAt", "cost", "bullets"]) assert.ok(p[k], `${p.id} missing ${k}`);
    assert.ok(p.compareAt > p.price, `${p.id} compareAt must exceed price`);
  }
});

test("every item keeps at least $15 profit before ads (room for a ~$15 CPA)", () => {
  for (const x of [...PRODUCTS, ...BUNDLES]) assert.ok(contribution(x) >= 15, `${x.id}: ${contribution(x).toFixed(2)}`);
});

test("bundles reference real products and cost less than buying separately", () => {
  const byId = Object.fromEntries(PRODUCTS.map((p) => [p.id, p]));
  for (const b of BUNDLES) {
    const parts = b.includes.map((id) => byId[id]);
    assert.ok(parts.every(Boolean), `${b.id} has unknown product`);
    assert.ok(b.price < parts.reduce((s, p) => s + p.price, 0), `${b.id} is not a discount`);
  }
});

test("checkout links, when set, are https", () => {
  for (const x of [...PRODUCTS, ...BUNDLES]) if (x.checkoutUrl) assert.match(x.checkoutUrl, /^https:\/\//);
});
