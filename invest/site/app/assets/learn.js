// Patient Money learning-app logic. Pure functions, no DOM: the app pages and
// tests/app/learn.test.js both use this file (like ../../assets/calc.js).
//
// Covers: member progress (localStorage "pm.progress.v1", docs/app/contracts.md section 3),
// level and lesson unlocking, the 3-question check, spaced-review dates, the Money Map
// summary and the crash-simulator math.
(function (root) {
  "use strict";

  var STORAGE_KEY = "pm.progress.v1";
  var PASS_MARK = 2;                 // 2 of 3 right completes a lesson
  var REVIEW_DAYS = [3, 10, 30];     // reviews come back this many days after completion
  var BUYBACK_MONTHS = 12;           // "sell and buy back a year later"
  var SLUG = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

  function isSlug(s) { return typeof s === "string" && s.length <= 100 && SLUG.test(s); }
  function isObj(o) { return !!o && typeof o === "object" && !Array.isArray(o); }
  function each(o, fn) { if (isObj(o)) Object.keys(o).forEach(function (k) { fn(k, o[k]); }); }
  function clone(o) { return JSON.parse(JSON.stringify(o)); }

  // ---- Dates: ISO calendar days ("2026-11-15"), compared as strings ----------------------------
  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function parts(iso) { return iso.split("-").map(Number); }
  function isISODate(s) {
    if (typeof s !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(s)) return false;
    var p = parts(s), d = new Date(Date.UTC(p[0], p[1] - 1, p[2]));
    return d.getUTCMonth() === p[1] - 1 && d.getUTCDate() === p[2];
  }
  // The member's local calendar day.
  function today(now) {
    var d = now || new Date();
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
  }
  function addDays(iso, n) {
    var p = parts(iso), d = new Date(Date.UTC(p[0], p[1] - 1, p[2] + n));
    return d.getUTCFullYear() + "-" + pad(d.getUTCMonth() + 1) + "-" + pad(d.getUTCDate());
  }
  // b minus a, in days.
  function daysBetween(a, b) {
    var x = parts(a), y = parts(b);
    return Math.round((Date.UTC(y[0], y[1] - 1, y[2]) - Date.UTC(x[0], x[1] - 1, x[2])) / 864e5);
  }

  // ---- Progress ---------------------------------------------------------------------------------
  function emptyProgress() {
    return { completed: {}, quiz: {}, review_due: {}, money_map: {}, member: false };
  }

  // Whatever is in storage (old, edited by hand, half-written) comes back in the contract's shape.
  function normalizeProgress(raw) {
    var p = emptyProgress();
    if (!isObj(raw)) return p;
    each(raw.completed, function (slug, d) { if (isSlug(slug) && isISODate(d)) p.completed[slug] = d; });
    each(raw.quiz, function (slug, q) {
      if (!isSlug(slug) || !isObj(q)) return;
      var best = Math.round(+q.best), tries = Math.round(+q.tries);
      p.quiz[slug] = { best: best >= 0 && best <= 3 ? best : 0, tries: tries > 0 ? tries : 0 };
    });
    each(raw.review_due, function (slug, d) { if (p.completed[slug] && isISODate(d)) p.review_due[slug] = d; });
    if (isObj(raw.money_map)) p.money_map = normalizeMoneyMap(raw.money_map);
    p.member = raw.member === true;
    return p;
  }

  function setMember(progress, on) { var p = clone(progress); p.member = on === true; return p; }

  // Clears lessons, scores and reviews. Keeps the Money Map and the membership switch.
  function resetLearning(progress) {
    var p = clone(progress);
    p.completed = {}; p.quiz = {}; p.review_due = {};
    return p;
  }

  // ---- Curriculum, unlocking and the path ------------------------------------------------------------
  // Every lesson in learning order, with its module and level.
  function flatten(cur) {
    var out = [];
    ((cur && cur.levels) || []).forEach(function (level) {
      (level.modules || []).forEach(function (mod) {
        (mod.lessons || []).forEach(function (lesson) {
          out.push({ lesson: lesson, module: mod, level: level, index: out.length });
        });
      });
    });
    return out;
  }
  function findLesson(cur, slug) {
    var all = flatten(cur);
    for (var i = 0; i < all.length; i++) if (all[i].lesson.slug === slug) return all[i];
    return null;
  }
  function lessonAfter(cur, slug) {
    var all = flatten(cur);
    for (var i = 0; i < all.length - 1; i++) if (all[i].lesson.slug === slug) return all[i + 1];
    return null;
  }

  // Level 1 is free; the rest open with membership.
  function levelOpen(level, progress) { return !!level && (level.free === true || progress.member === true); }

  function missingPrereqs(lesson, progress) {
    return (lesson.prerequisites || []).filter(function (s) { return !progress.completed[s]; });
  }

  // "done" | "open" | "needs-prereq" | "locked" (level needs membership)
  function lessonStatus(entry, progress) {
    if (!levelOpen(entry.level, progress)) return "locked";
    if (progress.completed[entry.lesson.slug]) return "done";
    return missingPrereqs(entry.lesson, progress).length ? "needs-prereq" : "open";
  }

  // Membership is the only hard lock. Order is guided (the path points at the next lesson and a
  // lesson says what it builds on); pass { enforceOrder: true } to also lock unmet prerequisites.
  function canOpen(entry, progress, opts) {
    var s = lessonStatus(entry, progress);
    if (s === "locked") return false;
    return !(opts && opts.enforceOrder && s === "needs-prereq");
  }

  // The next lesson to do: the first unfinished lesson that's open with its prerequisites done.
  // Returns { entry, locked } (locked: it's in a members-only level) or null when everything is done.
  function nextLesson(cur, progress) {
    var all = flatten(cur), fallback = null, lockedFirst = null;
    for (var i = 0; i < all.length; i++) {
      var s = lessonStatus(all[i], progress);
      if (s === "open") return { entry: all[i], locked: false };
      if (s === "needs-prereq" && !fallback) fallback = all[i];
      if (s === "locked" && !lockedFirst) lockedFirst = all[i];
    }
    if (fallback) return { entry: fallback, locked: false };
    if (lockedFirst) return { entry: lockedFirst, locked: true };
    return null;
  }

  function levelProgress(level, progress) {
    var total = 0, done = 0;
    (level.modules || []).forEach(function (m) {
      (m.lessons || []).forEach(function (x) { total++; if (progress.completed[x.slug]) done++; });
    });
    return { done: done, total: total };
  }
  function overallProgress(cur, progress) {
    var all = flatten(cur);
    return { done: all.filter(function (e) { return progress.completed[e.lesson.slug]; }).length, total: all.length };
  }

  // ---- The 3-question check --------------------------------------------------------------------------
  // answers: the chosen choice index per question (null when unanswered).
  function scoreQuiz(quiz, answers) {
    var results = (quiz || []).map(function (q, i) {
      var chosen = answers && Number.isInteger(answers[i]) ? answers[i] : null;
      return { chosen: chosen, answer: q.answer, correct: chosen === q.answer };
    });
    var correct = results.filter(function (r) { return r.correct; }).length;
    return { correct: correct, total: results.length, passed: correct >= PASS_MARK, results: results };
  }

  // ---- Spaced review ----------------------------------------------------------------------------------
  // The first review date (completion + 3, 10 or 30 days) that falls after `after`, or null.
  function nextReviewDate(completedOn, after) {
    for (var i = 0; i < REVIEW_DAYS.length; i++) {
      var d = addDays(completedOn, REVIEW_DAYS[i]);
      if (d > after) return d;
    }
    return null;
  }
  function isReviewDue(progress, slug, day) {
    var d = progress.review_due[slug];
    return !!d && d <= day;
  }

  // Records one attempt at a lesson's check. Returns { progress, passed, event } where event is
  // "completed" (first pass), "reviewed" (passed a due review), "retake" or "failed".
  function recordQuiz(progress, slug, correct, day) {
    var p = clone(progress), passed = correct >= PASS_MARK, event = passed ? "retake" : "failed";
    var q = p.quiz[slug] || { best: 0, tries: 0 };
    p.quiz[slug] = { best: Math.max(q.best, correct), tries: q.tries + 1 };
    if (passed && !p.completed[slug]) {
      p.completed[slug] = day;
      p.review_due[slug] = nextReviewDate(day, day);
      event = "completed";
    } else if (passed && isReviewDue(p, slug, day)) {
      var next = nextReviewDate(p.completed[slug], day);
      if (next) p.review_due[slug] = next; else delete p.review_due[slug];
      event = "reviewed";
    }
    return { progress: p, passed: passed, event: event };
  }

  // Due reviews in open levels, oldest first: [{ entry, due, late }] (late = days overdue).
  function dueReviews(cur, progress, day) {
    return flatten(cur)
      .filter(function (e) { return levelOpen(e.level, progress) && isReviewDue(progress, e.lesson.slug, day); })
      .map(function (e) { var due = progress.review_due[e.lesson.slug]; return { entry: e, due: due, late: daysBetween(due, day) }; })
      .sort(function (a, b) { return a.due < b.due ? -1 : a.due > b.due ? 1 : a.entry.index - b.entry.index; });
  }
  // The soonest review that isn't due yet, or null.
  function upcomingReview(cur, progress, day) {
    var best = null;
    flatten(cur).forEach(function (e) {
      var due = progress.review_due[e.lesson.slug];
      if (levelOpen(e.level, progress) && due && due > day && (!best || due < best.due)) best = { entry: e, due: due };
    });
    return best;
  }

  // ---- Money Map ---------------------------------------------------------------------------------------
  var ACCOUNT_TYPES = [
    { key: "checking", label: "Checking account" },
    { key: "savings", label: "Savings account" },
    { key: "workplace", label: "Workplace retirement plan (401(k), 403(b) or similar)" },
    { key: "roth_ira", label: "Roth IRA" },
    { key: "traditional_ira", label: "Traditional IRA" },
    { key: "brokerage", label: "Regular brokerage account" },
    { key: "hsa", label: "Health savings account (HSA)" }
  ];
  var MAX_ROWS = 30;

  function amount(v, max) {
    var n = typeof v === "string" && v.trim() !== "" ? Number(v) : v;
    return typeof n === "number" && isFinite(n) && n >= 0 && n <= (max || 1e9) ? n : null;
  }
  function text(v, max) { return typeof v === "string" ? v.slice(0, max || 80) : ""; }
  function isMonth(s) { return typeof s === "string" && /^\d{4}-(0[1-9]|1[0-2])$/.test(s); }

  function normalizeMoneyMap(raw) {
    var r = isObj(raw) ? raw : {};
    function rows(list, fn) { return (Array.isArray(list) ? list : []).slice(0, MAX_ROWS).filter(isObj).map(fn); }
    var accounts = {};
    ACCOUNT_TYPES.forEach(function (t) { if (isObj(r.accounts) && r.accounts[t.key] === true) accounts[t.key] = true; });
    var cushion = isObj(r.cushion) ? r.cushion : {};
    var months = amount(cushion.months, 24);
    return {
      pay: amount(r.pay),
      costs: rows(r.costs, function (c) { return { name: text(c.name), amount: amount(c.amount) }; }),
      cushion: { months: months === null ? 1 : months, saved: amount(cushion.saved) },
      debts: rows(r.debts, function (d) { return { name: text(d.name), balance: amount(d.balance), rate: amount(d.rate, 100) }; }),
      accounts: accounts,
      other_accounts: text(r.other_accounts, 120),
      goals: rows(r.goals, function (g) { return { name: text(g.name), amount: amount(g.amount), by: isMonth(g.by) ? g.by : "" }; }),
      updated: typeof r.updated === "string" ? r.updated.slice(0, 40) : ""
    };
  }

  // Whole months from this month to the target month ("2027-11" from 2026-11-15 is 12).
  function monthsUntil(by, day) {
    var t = by.split("-").map(Number), n = parts(day);
    return (t[0] * 12 + t[1]) - (n[0] * 12 + n[1]);
  }

  // A structured, explain-only view of what the member typed. No judgements, no suggestions.
  function moneyMapSummary(raw, day) {
    var mm = normalizeMoneyMap(raw);
    var costs = mm.costs.filter(function (c) { return c.amount !== null && c.amount > 0; });
    var costsTotal = costs.reduce(function (s, c) { return s + c.amount; }, 0);
    var pay = mm.pay !== null && mm.pay > 0 ? mm.pay : null;
    var out = {
      pay: pay,
      costsTotal: costsTotal,
      costsCount: costs.length,
      leftover: pay !== null && costs.length ? pay - costsTotal : null,
      costShare: pay !== null && costs.length ? costsTotal / pay : null,
      cushion: null,
      debts: [],
      debtTotal: 0,
      debtMonthlyInterest: 0,
      accounts: ACCOUNT_TYPES.filter(function (t) { return mm.accounts[t.key]; }).map(function (t) { return t.label; }),
      otherAccounts: mm.other_accounts.trim(),
      goals: []
    };
    if (costs.length && mm.cushion.months > 0) {
      var target = costsTotal * mm.cushion.months, saved = mm.cushion.saved;
      out.cushion = { months: mm.cushion.months, target: target, saved: saved,
                      remaining: saved === null ? null : Math.max(0, target - saved),
                      share: saved === null ? null : Math.min(1, saved / target) };
    }
    // Sorted by the rate the member typed, highest first; debts with no rate go last.
    out.debts = mm.debts.filter(function (d) { return d.balance !== null && d.balance > 0; })
      .map(function (d, i) {
        return { name: d.name.trim() || "Debt " + (i + 1), balance: d.balance, rate: d.rate,
                 monthlyInterest: d.rate === null ? null : d.balance * d.rate / 100 / 12, order: i };
      })
      .sort(function (a, b) {
        if (a.rate === null || b.rate === null) return a.rate === null ? (b.rate === null ? a.order - b.order : 1) : -1;
        return b.rate - a.rate || a.order - b.order;
      });
    out.debtTotal = out.debts.reduce(function (s, d) { return s + d.balance; }, 0);
    out.debtMonthlyInterest = out.debts.reduce(function (s, d) { return s + (d.monthlyInterest || 0); }, 0);
    out.goals = mm.goals.filter(function (g) { return g.name.trim() || g.amount; }).map(function (g, i) {
      var months = g.by ? monthsUntil(g.by, day) : null;
      return { name: g.name.trim() || "Goal " + (i + 1), amount: g.amount, by: g.by, months: months,
               perMonth: g.amount && months && months > 0 ? g.amount / months : null, past: months !== null && months <= 0 };
    });
    out.isEmpty = pay === null && !costs.length && !out.debts.length && !out.accounts.length && !out.otherAccounts && !out.goals.length;
    return out;
  }

  // ---- Crash simulator ---------------------------------------------------------------------------------
  // Made-up scenarios, clearly labeled. Real index history goes in app/data/history.json once its
  // licensing is checked (see validHistory below); the simulator treats both the same way.
  var SCENARIOS = [
    { id: "hypothetical-35", kind: "hypothetical", name: "Hypothetical A", label: "35% drop, 4-year climb back",
      description: "A made-up index falls 35% over 1 year, then takes 4 years to climb back to where it started.",
      drop: 0.35, fall_months: 12, recover_months: 48 },
    { id: "hypothetical-50", kind: "hypothetical", name: "Hypothetical B", label: "50% drop, 6-year climb back",
      description: "A made-up index falls 50% over 18 months, then takes 6 years to climb back to where it started.",
      drop: 0.5, fall_months: 18, recover_months: 72 }
  ];
  var CHOICES = [
    { id: "hold", label: "Hold" },
    { id: "sell-bottom", label: "Sell at the bottom" },
    { id: "sell-buyback", label: "Sell, buy back a year later" }
  ];

  // Monthly index levels for a hypothetical scenario: 100 at the start, a steady fall to the bottom,
  // then a steady climb back to exactly 100.
  function scenarioPath(s) {
    var path = [], bottom = 100 * (1 - s.drop);
    for (var m = 0; m <= s.fall_months; m++) path.push(100 * Math.pow(1 - s.drop, m / s.fall_months));
    for (var k = 1; k <= s.recover_months; k++) path.push(bottom * Math.pow(100 / bottom, k / s.recover_months));
    path[path.length - 1] = 100;
    return path;
  }

  function bottomIndex(path) {
    var b = 0;
    for (var i = 1; i < path.length; i++) if (path[i] < path[b]) b = i;
    return b;
  }

  // What `amount` invested at path[0] is worth each month under one choice. Selling happens at the
  // lowest point; cash earns nothing; no taxes or fees. If the path ends before the buy-back month,
  // the money stays in cash.
  function simulate(path, amt, choice, buybackMonths) {
    var b = bottomIndex(path), start = path[0], wait = buybackMonths == null ? BUYBACK_MONTHS : buybackMonths;
    var buyAt = choice === "sell-buyback" && b + wait <= path.length - 1 ? b + wait : null;
    var cash = amt * path[b] / start;
    var values = path.map(function (lvl, m) {
      if (choice === "hold" || m <= b) return amt * lvl / start;
      if (buyAt === null || m < buyAt) return cash;
      return cash * lvl / path[buyAt];
    });
    return { choice: choice, values: values, final: values[values.length - 1],
             sellAt: choice === "hold" ? null : b, buyAt: buyAt, low: cash };
  }

  // All three choices side by side, plus the facts the result text needs.
  function compareChoices(path, amt) {
    var b = bottomIndex(path), byId = {};
    CHOICES.forEach(function (c) { byId[c.id] = simulate(path, amt, c.id); });
    var hold = byId.hold, back = null;
    for (var m = b + 1; m < path.length; m++) if (path[m] >= path[0] - 1e-9) { back = m; break; }
    var buy = byId["sell-buyback"].buyAt;
    return {
      months: path.length - 1, bottom: b, drop: 1 - path[b] / path[0], low: hold.values[b],
      backToStart: back, buyAt: buy, riseBeforeBuyback: buy === null ? null : path[buy] / path[b] - 1,
      results: byId,
      vsHold: CHOICES.reduce(function (o, c) { o[c.id] = byId[c.id].final - hold.final; return o; }, {})
    };
  }

  // history.json: { "series": [ { id, label, index_name, points: [{ date: "YYYY-MM", level }], source_name,
  // source_url, retrieved, license, verified: true } ] }. Only complete, verified, sourced series count.
  function validHistory(doc) {
    return ((doc && Array.isArray(doc.series)) ? doc.series : []).filter(function (s) {
      return isObj(s) && s.verified === true && isSlug(s.id) && typeof s.label === "string" && s.label.trim() &&
        typeof s.index_name === "string" && typeof s.source_name === "string" && s.source_name.trim() &&
        typeof s.source_url === "string" && /^https:\/\/[^\s\\@]+$/i.test(s.source_url) &&
        isISODate(s.retrieved) && typeof s.license === "string" && s.license.trim() &&
        Array.isArray(s.points) && s.points.length >= 13 && s.points.length <= 600 &&
        s.points.every(function (p) { return isObj(p) && isMonth(p.date) && typeof p.level === "number" && isFinite(p.level) && p.level > 0; });
    }).map(function (s) {
      return { id: s.id, kind: "historical", name: s.label, label: s.index_name,
               description: s.index_name + ", monthly, " + s.points[0].date + " to " + s.points[s.points.length - 1].date + ".",
               path: s.points.map(function (p) { return p.level; }), dates: s.points.map(function (p) { return p.date; }),
               source: { name: s.source_name, url: s.source_url, retrieved: s.retrieved, license: s.license } };
    });
  }
  function pathFor(scenario) { return scenario.path || scenarioPath(scenario); }

  root.PatientLearn = {
    STORAGE_KEY: STORAGE_KEY, PASS_MARK: PASS_MARK, REVIEW_DAYS: REVIEW_DAYS, BUYBACK_MONTHS: BUYBACK_MONTHS,
    isSlug: isSlug, isISODate: isISODate, today: today, addDays: addDays, daysBetween: daysBetween,
    emptyProgress: emptyProgress, normalizeProgress: normalizeProgress, setMember: setMember, resetLearning: resetLearning,
    flatten: flatten, findLesson: findLesson, lessonAfter: lessonAfter, levelOpen: levelOpen,
    missingPrereqs: missingPrereqs, lessonStatus: lessonStatus, canOpen: canOpen, nextLesson: nextLesson,
    levelProgress: levelProgress, overallProgress: overallProgress,
    scoreQuiz: scoreQuiz, recordQuiz: recordQuiz, nextReviewDate: nextReviewDate, isReviewDue: isReviewDue,
    dueReviews: dueReviews, upcomingReview: upcomingReview,
    ACCOUNT_TYPES: ACCOUNT_TYPES, normalizeMoneyMap: normalizeMoneyMap, monthsUntil: monthsUntil, moneyMapSummary: moneyMapSummary,
    SCENARIOS: SCENARIOS, CHOICES: CHOICES, scenarioPath: scenarioPath, bottomIndex: bottomIndex,
    simulate: simulate, compareChoices: compareChoices, validHistory: validHistory, pathFor: pathFor
  };
  if (typeof module !== "undefined" && module.exports) module.exports = root.PatientLearn;
})(typeof window !== "undefined" ? window : globalThis);
