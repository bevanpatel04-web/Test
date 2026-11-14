// Edge cases for the calculator math (invest/site/assets/calc.js).
// Run with: node --test tests/qa/calc_edge.test.js
const test = require("node:test");
const assert = require("node:assert");
const path = require("node:path");
const PM = require(path.join(__dirname, "..", "..", "invest", "site", "assets", "calc.js"));

const base = { startAge: 21, endAge: 65, monthly: 100, rate: 0.06, delay: 5, shock: null };

// Future value of `months` deposits made at the start of each month (annuity due), written
// independently of calc.js so the two can't share a bug.
function fv(monthly, annual, months) {
  if (annual === 0) return monthly * months;
  const i = Math.pow(1 + annual, 1 / 12) - 1;
  return monthly * ((Math.pow(1 + i, months) - 1) / i) * (1 + i);
}
const close = (a, b, rel = 1e-9) => assert.ok(Math.abs(a - b) <= Math.abs(b) * rel + 1e-6, `${a} vs ${b}`);

test("largest allowed inputs stay finite and match the closed form", () => {
  const o = { startAge: 16, endAge: 100, monthly: 100000, rate: 0.15, delay: 1, shock: null };
  const r = PM.compare(o);
  assert.deepEqual(r.errors, []);
  assert.ok(Number.isFinite(r.now.final) && r.now.final > 1e12);
  close(r.now.final, fv(100000, 0.15, 84 * 12));
  close(r.later.final, fv(100000, 0.15, 83 * 12));
  assert.equal(r.extraPutIn, 100000 * 12);
  assert.equal(r.now.points.length, 85);
  assert.equal(r.now.points[84].age, 100);
});

test("0% growth: waiting costs exactly the skipped deposits", () => {
  const r = PM.compare({ ...base, rate: 0 });
  assert.deepEqual(r.errors, []);
  assert.equal(r.now.final, 100 * 12 * 44);
  assert.equal(r.costOfWaiting, r.extraPutIn);
  assert.equal(r.now.growth, 0);
});

test("15% is the top allowed rate; anything above is an error", () => {
  assert.deepEqual(PM.compare({ ...base, rate: 0.15 }).errors, []);
  close(PM.compare({ ...base, rate: 0.15 }).now.final, fv(100, 0.15, 44 * 12));
  assert.ok(PM.compare({ ...base, rate: 0.1501 }).errors.length);
  assert.ok(PM.compare({ ...base, rate: -0.01 }).errors.length);
});

test("age bounds: 16 and 80 are allowed, 15 and 81 are not", () => {
  assert.deepEqual(PM.validate({ ...base, startAge: 16 }), []);
  assert.deepEqual(PM.validate({ ...base, startAge: 80, endAge: 100 }), []);
  assert.ok(PM.validate({ ...base, startAge: 15 }).length);
  assert.ok(PM.validate({ ...base, startAge: 81, endAge: 100 }).length);
});

test("end age 100 is allowed, 101 is not", () => {
  const r = PM.compare({ ...base, endAge: 100 });
  assert.deepEqual(r.errors, []);
  assert.equal(r.now.points[r.now.points.length - 1].age, 100);
  assert.ok(PM.validate({ ...base, endAge: 101 }).length);
});

test("the end age must come after the delayed start", () => {
  assert.ok(PM.validate({ ...base, endAge: 26 }).length); // 21 + 5 = 26: the later saver never starts
  assert.deepEqual(PM.validate({ ...base, endAge: 27 }), []);
});

test("1-year wait costs one year of deposits plus their growth", () => {
  const r = PM.compare({ ...base, delay: 1 });
  assert.deepEqual(r.errors, []);
  assert.equal(r.extraPutIn, 1200);
  close(r.costOfWaiting, fv(100, 0.06, 44 * 12) - fv(100, 0.06, 43 * 12));
  assert.equal(r.later.points[1].contributed, 0);
  assert.equal(r.later.points[2].contributed, 1200);
  assert.ok(PM.validate({ ...base, delay: 0 }).length);
  assert.ok(PM.validate({ ...base, delay: 31 }).length);
});

test("a crash at the last age cuts the final balance", () => {
  const r = PM.compare({ ...base, shock: { age: 65, drop: 0.35 } });
  assert.deepEqual(r.errors, []);
  assert.equal(r.stressed.shock.age, 65);
  close(r.stressed.final, r.now.final * 0.65);
  close(r.stressed.points[r.stressed.points.length - 1].balance, r.stressed.final);
  assert.ok(PM.validate({ ...base, shock: { age: 66, drop: 0.35 } }).length);
  assert.ok(PM.validate({ ...base, shock: { age: 21, drop: 0.35 } }).length); // must be after "now"
});

test("a crash one year in hits only the first year's deposits", () => {
  const r = PM.compare({ ...base, shock: { age: 22, drop: 0.5 } });
  assert.deepEqual(r.errors, []);
  close(r.stressed.shock.before, fv(100, 0.06, 12));
  close(r.stressed.shock.after, fv(100, 0.06, 12) * 0.5);
});

test("drop size must be strictly between 0% and 100%", () => {
  for (const drop of [0, 1, -0.1, NaN]) {
    assert.ok(PM.validate({ ...base, shock: { age: 40, drop } }).length, String(drop));
  }
  assert.deepEqual(PM.validate({ ...base, shock: { age: 40, drop: 0.99 } }), []);
});

test("NaN, empty and non-number inputs are explained, not computed", () => {
  for (const key of ["startAge", "endAge", "monthly", "rate", "delay"]) {
    for (const bad of [NaN, undefined, null, "", "21", Infinity]) {
      const r = PM.compare({ ...base, [key]: bad });
      assert.ok(r.errors.length, `${key}=${String(bad)}`);
      assert.equal(r.now, undefined);
    }
  }
  // parseInt("") in the page gives NaN; the crash age too.
  assert.ok(PM.compare({ ...base, shock: { age: NaN, drop: 0.3 } }).errors.length);
});

test("fractional ages and waits are rejected (a fractional crash age used to crash the page)", () => {
  assert.ok(PM.validate({ ...base, startAge: 21.5 }).length);
  assert.ok(PM.validate({ ...base, endAge: 64.5 }).length);
  assert.ok(PM.validate({ ...base, delay: 2.5 }).length);
  assert.ok(PM.validate({ ...base, shock: { age: 40.5, drop: 0.3 } }).length);
  // Every valid crash age really applies the drop, so the page never sees shock === null.
  for (let age = 22; age <= 65; age++) {
    assert.ok(PM.compare({ ...base, shock: { age, drop: 0.2 } }).stressed.shock, `crash at ${age}`);
  }
});

test("monthly amount bounds: $1 and $100,000", () => {
  assert.deepEqual(PM.validate({ ...base, monthly: 1 }), []);
  assert.deepEqual(PM.validate({ ...base, monthly: 100000 }), []);
  assert.ok(PM.validate({ ...base, monthly: 0.5 }).length);
  assert.ok(PM.validate({ ...base, monthly: 100001 }).length);
  assert.ok(PM.validate({ ...base, monthly: -100 }).length);
});

test("money(): rounding, millions and negatives", () => {
  assert.equal(PM.money(0), "$0");
  assert.equal(PM.money(9999.4), "$9,999");
  assert.equal(PM.money(10049), "$10,000");
  assert.equal(PM.money(1234567.89), "$1,234,600");
  assert.equal(PM.money(98276860321), "$98,276,860,300");
  assert.equal(PM.money(-5000), "-$5,000");
  assert.equal(PM.money(-1234567), "-$1,234,600");
  assert.equal(PM.money(-0.4), "$0");          // no "$-0"
  assert.equal(PM.money(-0), "$0");
});

test("compactMoney(): units, rollover and negatives", () => {
  assert.equal(PM.compactMoney(0), "$0");
  assert.equal(PM.compactMoney(999), "$999");
  assert.equal(PM.compactMoney(1000), "$1K");
  assert.equal(PM.compactMoney(999949), "$999.9K");
  assert.equal(PM.compactMoney(999960), "$1M");  // used to be "$1000K"
  assert.equal(PM.compactMoney(2.5e9), "$2500M");
  assert.equal(PM.compactMoney(-1500000), "-$1.5M");
  assert.equal(PM.compactMoney(-250), "-$250");
});

test("niceTicks(): tiny, huge and odd maxima", () => {
  const check = (max) => {
    const t = PM.niceTicks(max, 4);
    assert.equal(t[0], 0);
    assert.ok(t[t.length - 1] >= max, `${max}: top tick ${t[t.length - 1]}`);
    assert.ok(t.length >= 2 && t.length <= 7, `${max}: ${t.length} ticks`);
    const step = t[1] - t[0];
    t.forEach((v, i) => assert.ok(Math.abs(v - i * step) <= step * 1e-9, `${max}: uneven ticks ${t}`));
    const mant = step / Math.pow(10, Math.floor(Math.log10(step)));
    assert.ok([1, 2, 2.5, 5].some((m) => Math.abs(m - mant) < 1e-9), `${max}: step ${step}`);
    return t;
  };
  for (const max of [1e-9, 0.001, 0.3, 1, 7, 99, 247000, 1e6, 123456789, 9.8e10, 1e15, 1e300]) check(max);
  assert.deepEqual(PM.niceTicks(0.3, 4), [0, 0.1, 0.2, 0.3]);     // no 0.30000000000000004
  assert.deepEqual(PM.niceTicks(0.001, 4), [0, 0.00025, 0.0005, 0.00075, 0.001]);
  assert.deepEqual(PM.niceTicks(1e9, 4), [0, 2.5e8, 5e8, 7.5e8, 1e9]);
});

test("niceTicks(): non-positive and non-finite maxima fall back instead of hanging", () => {
  for (const max of [0, -5, NaN, undefined, Infinity]) assert.deepEqual(PM.niceTicks(max), [0, 1], String(max));
  assert.deepEqual(PM.niceTicks(100, 0), PM.niceTicks(100, 4));
});
