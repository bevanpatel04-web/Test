// Run with: node --test tests/water_check.test.js
const test = require("node:test");
const assert = require("node:assert");
const path = require("node:path");
const fs = require("node:fs");
const W = require(path.join(__dirname, "..", "site", "assets", "app.js"));

const cities = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "data", "cities.json"))).cities;
const states = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "data", "states.json"))).states;
const data = { cities, states };

test("ZIP3 maps to states", () => {
  assert.equal(W.stateForZip("85004"), "AZ");
  assert.equal(W.stateForZip("02108"), "MA");
  assert.equal(W.stateForZip("10001"), "NY");
  assert.equal(W.stateForZip("98101"), "WA");
  assert.equal(W.stateForZip("33101"), "FL");
  assert.equal(W.stateForZip("20001"), "DC");
});

test("metro lookup scores very hard + chloramine as harsh", () => {
  const r = W.assess("92101", data); // San Diego
  assert.equal(r.city.slug, "san-diego-ca");
  assert.equal(r.hardness, "very_hard");
  assert.equal(r.level, "high");
  assert.equal(r.confidence, "estimate");
});

test("soft water scores gentler than very hard water", () => {
  const seattle = W.assess("98101", data);
  const vegas = W.assess("89101", data);
  assert.ok(seattle.score < vegas.score);
});

test("statewide fallback and bad input", () => {
  const r = W.assess("67202", data); // Wichita, KS — not a covered metro
  assert.equal(r.confidence, "regional");
  assert.equal(r.disinfectant, "unknown");
  assert.ok(W.assess("abc", data).error);
});

test("every recommendation says filters don't soften hard water", () => {
  const r = W.assess("85004", data);
  assert.ok(r.recommendations.some((x) => /do not soften/.test(x.text)));
});
