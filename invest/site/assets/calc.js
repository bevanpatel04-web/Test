// Patient Money calculator math. Pure functions, no DOM — the page (app.js) and the
// tests (tests/invest_calc.test.js) both use this file.
//
// Model: you add the same amount at the start of every month, and the balance grows at a
// steady hypothetical yearly rate, compounded monthly. Real markets don't move steadily;
// the optional "shock" applies a one-time drop to show what that can look like.
(function (root) {
  "use strict";

  function monthlyRate(annualRate) {
    return Math.pow(1 + annualRate, 1 / 12) - 1;
  }

  // o: { startAge, endAge, monthly, rate, delay = 0, shock = { age, drop } | null }
  // Returns yearly points ({ age, balance, contributed }) from startAge to endAge.
  function project(o) {
    var delay = o.delay || 0;
    var mr = monthlyRate(o.rate);
    var balance = 0, contributed = 0, shockInfo = null;
    var points = [{ age: o.startAge, balance: 0, contributed: 0 }];
    for (var age = o.startAge; age < o.endAge; age++) {
      for (var m = 0; m < 12; m++) {
        if (age >= o.startAge + delay) { balance += o.monthly; contributed += o.monthly; }
        balance *= 1 + mr;
      }
      if (o.shock && age + 1 === o.shock.age) {
        shockInfo = { age: o.shock.age, before: balance, after: balance * (1 - o.shock.drop) };
        balance = shockInfo.after;
      }
      points.push({ age: age + 1, balance: balance, contributed: contributed });
    }
    return { points: points, final: balance, contributed: contributed, growth: balance - contributed, shock: shockInfo };
  }

  function validate(o) {
    var errors = [];
    function isNum(v) { return typeof v === "number" && isFinite(v); }
    if (!isNum(o.startAge) || o.startAge < 16 || o.startAge > 80) errors.push("Enter an age between 16 and 80.");
    if (!isNum(o.monthly) || o.monthly < 1 || o.monthly > 100000) errors.push("Enter a monthly amount between $1 and $100,000.");
    if (!isNum(o.rate) || o.rate < 0 || o.rate > 0.15) errors.push("Pick a yearly growth rate between 0% and 15%.");
    if (!isNum(o.delay) || o.delay < 1 || o.delay > 30) errors.push("Pick a wait between 1 and 30 years.");
    if (!isNum(o.endAge) || o.endAge > 100) errors.push("Pick an end age of 100 or less.");
    else if (isNum(o.startAge) && isNum(o.delay) && o.endAge <= o.startAge + o.delay) {
      errors.push("The end age has to be after you'd start, even if you wait.");
    }
    if (o.shock) {
      if (!isNum(o.shock.drop) || o.shock.drop <= 0 || o.shock.drop >= 1) errors.push("Pick a drop between 1% and 99%.");
      if (!isNum(o.shock.age) || o.shock.age <= o.startAge || o.shock.age > o.endAge) {
        errors.push("The drop has to happen between your age now and the end age.");
      }
    }
    return errors;
  }

  // Start now vs. start after `delay` years, plus the optional "start now, with a drop" line.
  function compare(o) {
    var errors = validate(o);
    if (errors.length) return { errors: errors };
    var base = { startAge: o.startAge, endAge: o.endAge, monthly: o.monthly, rate: o.rate };
    var now = project(base);
    var later = project(Object.assign({}, base, { delay: o.delay }));
    var stressed = o.shock ? project(Object.assign({}, base, { shock: o.shock })) : null;
    return {
      errors: [],
      now: now,
      later: later,
      stressed: stressed,
      costOfWaiting: now.final - later.final,
      extraPutIn: now.contributed - later.contributed
    };
  }

  function money(n) {
    var rounded = Math.abs(n) >= 10000 ? Math.round(n / 100) * 100 : Math.round(n);
    return "$" + Math.round(rounded).toLocaleString("en-US");
  }

  function compactMoney(n) {
    var a = Math.abs(n);
    if (a >= 1e6) return "$" + trim(n / 1e6) + "M";
    if (a >= 1e3) return "$" + trim(n / 1e3) + "K";
    return "$" + Math.round(n);
  }
  function trim(x) { return (Math.round(x * 10) / 10).toString(); }

  // Clean axis ticks (1, 2, 2.5 or 5 x 10^n) covering 0..max.
  function niceTicks(max, count) {
    count = count || 4;
    if (!(max > 0)) return [0, 1];
    var raw = max / count, mag = Math.pow(10, Math.floor(Math.log10(raw)));
    var steps = [1, 2, 2.5, 5, 10], step = mag;
    for (var i = 0; i < steps.length; i++) { if (steps[i] * mag >= raw) { step = steps[i] * mag; break; } }
    var ticks = [];
    for (var t = 0; t <= max + step * 0.0001; t += step) ticks.push(t);
    if (ticks[ticks.length - 1] < max) ticks.push(ticks[ticks.length - 1] + step);
    return ticks;
  }

  root.PatientMoney = { monthlyRate: monthlyRate, project: project, validate: validate, compare: compare,
                        money: money, compactMoney: compactMoney, niceTicks: niceTicks };
  if (typeof module !== "undefined" && module.exports) module.exports = root.PatientMoney;
})(typeof window !== "undefined" ? window : globalThis);
