// Run with: node --test tests/invest_calc.test.js
const test = require("node:test");
const assert = require("node:assert");
const path = require("node:path");
const PM = require(path.join(__dirname, "..", "invest", "site", "assets", "calc.js"));

const base = { startAge: 21, endAge: 65, monthly: 100, rate: 0.06, delay: 5, shock: null };

test("zero growth just adds up deposits", () => {
  const r = PM.project({ startAge: 20, endAge: 30, monthly: 100, rate: 0 });
  assert.equal(r.final, 12000);
  assert.equal(r.contributed, 12000);
  assert.equal(r.points.length, 11);
});

test("matches the closed-form future value of monthly deposits", () => {
  const i = Math.pow(1.06, 1 / 12) - 1, n = 12 * 44;
  const expected = 100 * ((Math.pow(1 + i, n) - 1) / i) * (1 + i);
  const r = PM.project({ startAge: 21, endAge: 65, monthly: 100, rate: 0.06 });
  assert.ok(Math.abs(r.final - expected) < 0.01, `${r.final} vs ${expected}`);
});

test("waiting costs more than the skipped deposits when growth is positive", () => {
  const r = PM.compare(base);
  assert.deepEqual(r.errors, []);
  assert.equal(r.extraPutIn, 100 * 12 * 5);
  assert.ok(r.costOfWaiting > r.extraPutIn);
  assert.equal(r.later.points[5].contributed, 0);
  assert.equal(r.stressed, null);
});

test("a market drop cuts the balance at the chosen age", () => {
  const r = PM.compare({ ...base, shock: { age: 40, drop: 0.35 } });
  const s = r.stressed.shock;
  assert.equal(s.age, 40);
  assert.ok(Math.abs(s.after - s.before * 0.65) < 1e-6);
  assert.ok(r.stressed.final < r.now.final);
  const at40 = r.stressed.points.find((p) => p.age === 40);
  assert.ok(Math.abs(at40.balance - s.after) < 1e-6);
});

test("bad inputs are explained, not computed", () => {
  assert.ok(PM.compare({ ...base, endAge: 25 }).errors.length);
  assert.ok(PM.compare({ ...base, monthly: NaN }).errors.length);
  assert.ok(PM.compare({ ...base, rate: 0.5 }).errors.length);
  assert.ok(PM.compare({ ...base, shock: { age: 70, drop: 0.3 } }).errors.length);
  assert.ok(PM.compare({ ...base, shock: { age: 40, drop: 1.2 } }).errors.length);
});

test("formatting and axis ticks", () => {
  assert.equal(PM.money(247412.3), "$247,400");
  assert.equal(PM.money(6000), "$6,000");
  assert.equal(PM.compactMoney(247400), "$247.4K");
  assert.equal(PM.compactMoney(1250000), "$1.3M");
  assert.deepEqual(PM.niceTicks(247000, 4), [0, 100000, 200000, 300000]);
  assert.deepEqual(PM.niceTicks(0), [0, 1]);
});
