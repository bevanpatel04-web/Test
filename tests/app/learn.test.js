// Unit tests for the learning-app logic (invest/site/app/assets/learn.js).
// Run with: node --test tests/app/learn.test.js
const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const L = require("../../invest/site/app/assets/learn.js");

const REPO = path.join(__dirname, "..", "..");

// A small curriculum in the contract's shape: free level 1 (3 lessons), members-only level 2 (2 lessons).
function lesson(slug, prereqs = []) {
  return { slug, title: slug, minutes: 3, objectives: ["o"], key_points: ["k"], prerequisites: prereqs, needs_facts: [],
           risk_note: null, try_it: { tool: "none", prompt: "" },
           quiz: [0, 1, 2].map((i) => ({ q: "Q" + i, choices: ["a", "b", "c"], answer: i, why: "w" })) };
}
const CUR = {
  levels: [
    { id: "L1", number: 1, title: "One", free: true, modules: [
      { id: "L1-M1", title: "M1", lessons: [lesson("a"), lesson("b", ["a"])] },
      { id: "L1-M2", title: "M2", lessons: [lesson("c", ["b"])] }] },
    { id: "L2", number: 2, title: "Two", free: false, modules: [
      { id: "L2-M1", title: "M3", lessons: [lesson("d", ["c"]), lesson("e", ["d"])] }] }
  ]
};
const fresh = () => L.emptyProgress();
const done = (...slugs) => { const p = fresh(); slugs.forEach((s) => { p.completed[s] = "2026-11-01"; }); return p; };

test("dates: calendar arithmetic across month and year ends", () => {
  assert.equal(L.addDays("2026-11-15", 3), "2026-11-18");
  assert.equal(L.addDays("2026-12-30", 3), "2027-01-02");
  assert.equal(L.addDays("2028-02-28", 1), "2028-02-29");
  assert.equal(L.daysBetween("2026-11-15", "2026-12-15"), 30);
  assert.equal(L.today(new Date(2026, 0, 5, 23, 59)), "2026-01-05");
  assert.ok(L.isISODate("2026-02-28"));
  assert.ok(!L.isISODate("2026-02-30") && !L.isISODate("2026-2-3") && !L.isISODate(null));
});

test("progress: anything in storage comes back in the contract's shape", () => {
  assert.deepEqual(L.normalizeProgress(null), fresh());
  assert.deepEqual(L.normalizeProgress([1, 2]), fresh());
  const p = L.normalizeProgress({
    completed: { a: "2026-11-01", "Bad Slug": "2026-11-01", b: "yesterday" },
    quiz: { a: { best: 9, tries: -2 }, b: { best: 2, tries: 1 } },
    review_due: { a: "2026-11-04", c: "2026-11-04" }, // c isn't completed
    member: "true", money_map: { pay: "2500", costs: "nope" }
  });
  assert.deepEqual(p.completed, { a: "2026-11-01" });
  assert.deepEqual(p.quiz, { a: { best: 0, tries: 0 }, b: { best: 2, tries: 1 } });
  assert.deepEqual(p.review_due, { a: "2026-11-04" });
  assert.equal(p.member, false, "only true counts");
  assert.equal(p.money_map.pay, 2500);
  assert.deepEqual(p.money_map.costs, []);
});

test("unlocking: level 1 is free, levels 2+ need membership", () => {
  const d = L.findLesson(CUR, "d");
  assert.equal(L.lessonStatus(d, done("a", "b", "c")), "locked");
  assert.equal(L.canOpen(d, done("a", "b", "c")), false);
  const member = L.setMember(done("a", "b", "c"), true);
  assert.equal(L.lessonStatus(d, member), "open");
  assert.equal(L.canOpen(d, member), true);
  // Order is guided, not enforced, unless asked.
  const b = L.findLesson(CUR, "b");
  assert.equal(L.lessonStatus(b, fresh()), "needs-prereq");
  assert.equal(L.canOpen(b, fresh()), true);
  assert.equal(L.canOpen(b, fresh(), { enforceOrder: true }), false);
  assert.deepEqual(L.missingPrereqs(b.lesson, fresh()), ["a"]);
  assert.equal(L.lessonStatus(L.findLesson(CUR, "a"), done("a")), "done");
});

test("path: next lesson, then the members-only wall, then done", () => {
  assert.equal(L.nextLesson(CUR, fresh()).entry.lesson.slug, "a");
  assert.equal(L.nextLesson(CUR, done("a")).entry.lesson.slug, "b");
  // Skipped ahead: the first open lesson with its prerequisites done still comes first.
  assert.equal(L.nextLesson(CUR, done("b")).entry.lesson.slug, "a");
  const wall = L.nextLesson(CUR, done("a", "b", "c"));
  assert.equal(wall.entry.lesson.slug, "d");
  assert.equal(wall.locked, true);
  const member = L.setMember(done("a", "b", "c"), true);
  assert.equal(L.nextLesson(CUR, member).entry.lesson.slug, "d");
  assert.equal(L.nextLesson(CUR, member).locked, false);
  assert.equal(L.nextLesson(CUR, L.setMember(done("a", "b", "c", "d", "e"), true)), null);
  assert.deepEqual(L.levelProgress(CUR.levels[0], done("a", "c")), { done: 2, total: 3 });
  assert.deepEqual(L.overallProgress(CUR, done("a", "d")), { done: 2, total: 5 });
  assert.equal(L.lessonAfter(CUR, "c").lesson.slug, "d", "crosses into the next level");
  assert.equal(L.lessonAfter(CUR, "e"), null);
  assert.equal(L.flatten(CUR).map((e) => e.index).join(), "0,1,2,3,4");
});

test("quiz: 2 of 3 right completes; unanswered questions count as wrong", () => {
  const quiz = lesson("x").quiz; // answers 0, 1, 2
  assert.deepEqual([L.scoreQuiz(quiz, [0, 1, 2]).correct, L.scoreQuiz(quiz, [0, 1, 2]).passed], [3, true]);
  assert.deepEqual([L.scoreQuiz(quiz, [0, 1, 0]).correct, L.scoreQuiz(quiz, [0, 1, 0]).passed], [2, true]);
  assert.deepEqual([L.scoreQuiz(quiz, [0, 0, 0]).correct, L.scoreQuiz(quiz, [0, 0, 0]).passed], [1, false]);
  const partial = L.scoreQuiz(quiz, [0, null]);
  assert.equal(partial.correct, 1);
  assert.equal(partial.results[1].chosen, null);
  assert.equal(L.scoreQuiz(quiz, ["0", 1.5, 2]).correct, 1, "only whole-number indexes count");
});

test("recording attempts: tries, best score, completion and the first review", () => {
  let r = L.recordQuiz(fresh(), "a", 1, "2026-11-15");
  assert.equal(r.event, "failed");
  assert.deepEqual(r.progress.quiz.a, { best: 1, tries: 1 });
  assert.equal(r.progress.completed.a, undefined);
  r = L.recordQuiz(r.progress, "a", 2, "2026-11-15");
  assert.equal(r.event, "completed");
  assert.equal(r.progress.completed.a, "2026-11-15");
  assert.equal(r.progress.review_due.a, "2026-11-18", "first review 3 days later");
  assert.deepEqual(r.progress.quiz.a, { best: 2, tries: 2 });
  const before = JSON.stringify(r.progress);
  const again = L.recordQuiz(r.progress, "a", 3, "2026-11-16");
  assert.equal(again.event, "retake", "passing before a review is due changes nothing but the score");
  assert.equal(again.progress.review_due.a, "2026-11-18");
  assert.equal(JSON.stringify(r.progress), before, "recordQuiz doesn't change its input");
  const low = L.recordQuiz(again.progress, "a", 0, "2026-11-16");
  assert.equal(low.progress.quiz.a.best, 3, "best never goes down");
  assert.equal(low.progress.completed.a, "2026-11-15", "a later fail doesn't undo completion");
});

test("spaced review: 3, 10 and 30 days after completion, then no more", () => {
  assert.deepEqual(L.REVIEW_DAYS, [3, 10, 30]);
  assert.equal(L.nextReviewDate("2026-11-01", "2026-11-01"), "2026-11-04");
  assert.equal(L.nextReviewDate("2026-11-01", "2026-11-04"), "2026-11-11");
  assert.equal(L.nextReviewDate("2026-11-01", "2026-11-12"), "2026-12-01", "a late review skips a step that's already past");
  assert.equal(L.nextReviewDate("2026-11-01", "2026-12-01"), null);

  let p = L.recordQuiz(fresh(), "a", 3, "2026-11-01").progress;
  assert.equal(L.isReviewDue(p, "a", "2026-11-03"), false);
  assert.equal(L.isReviewDue(p, "a", "2026-11-04"), true);
  let r = L.recordQuiz(p, "a", 1, "2026-11-04");
  assert.equal(r.event, "failed");
  assert.equal(r.progress.review_due.a, "2026-11-04", "a failed review stays due");
  r = L.recordQuiz(r.progress, "a", 2, "2026-11-04");
  assert.equal(r.event, "reviewed");
  assert.equal(r.progress.review_due.a, "2026-11-11");
  r = L.recordQuiz(r.progress, "a", 3, "2026-11-11");
  assert.equal(r.progress.review_due.a, "2026-12-01");
  r = L.recordQuiz(r.progress, "a", 3, "2026-12-03");
  assert.equal(r.event, "reviewed");
  assert.equal("a" in r.progress.review_due, false, "all three reviews done");
});

test("due reviews: oldest first, only in open levels; the next upcoming one", () => {
  const p = done("a", "b", "d");
  p.review_due = { a: "2026-11-10", b: "2026-11-04", d: "2026-11-01" };
  const due = L.dueReviews(CUR, p, "2026-11-10");
  assert.deepEqual(due.map((x) => x.entry.lesson.slug), ["b", "a"], "d is in a locked level");
  assert.deepEqual(due.map((x) => x.late), [6, 0]);
  assert.deepEqual(L.dueReviews(CUR, L.setMember(p, true), "2026-11-10").map((x) => x.entry.lesson.slug), ["d", "b", "a"]);
  assert.equal(L.upcomingReview(CUR, p, "2026-11-05").entry.lesson.slug, "a");
  assert.equal(L.upcomingReview(CUR, p, "2026-11-10"), null);
});

test("reset and membership keep what they should", () => {
  const p = done("a");
  p.quiz.a = { best: 3, tries: 1 }; p.review_due.a = "2026-11-04"; p.money_map = { pay: 100 }; p.member = true;
  const r = L.resetLearning(p);
  assert.deepEqual([r.completed, r.quiz, r.review_due], [{}, {}, {}]);
  assert.deepEqual(r.money_map, { pay: 100 });
  assert.equal(r.member, true);
  assert.equal(L.setMember(p, false).member, false);
  assert.equal(p.member, true, "inputs aren't changed");
});

test("Money Map summary: totals, cushion target and debts sorted by the rate typed", () => {
  const s = L.moneyMapSummary({
    pay: 3000,
    costs: [{ name: "Rent", amount: 1200 }, { name: "Food", amount: "400" }, { name: "", amount: null }, { name: "Phone", amount: 100 }],
    cushion: { months: 1, saved: 500 },
    debts: [{ name: "Car", balance: 6000, rate: 7.5 }, { name: "Card", balance: 2000, rate: 24 },
            { name: "", balance: 900, rate: null }, { name: "Store card", balance: 300, rate: 29.99 }, { name: "Paid off", balance: 0, rate: 30 }],
    accounts: { checking: true, roth_ira: true, nope: true },
    goals: [{ name: "Trip", amount: 1200, by: "2027-11" }, { name: "Laptop", amount: 900, by: "2026-01" }, { name: "Someday", amount: 50, by: "" }]
  }, "2026-11-15");
  assert.equal(s.costsTotal, 1700);
  assert.equal(s.costsCount, 3);
  assert.equal(s.leftover, 1300);
  assert.ok(Math.abs(s.costShare - 1700 / 3000) < 1e-12);
  assert.deepEqual(s.cushion, { months: 1, target: 1700, saved: 500, remaining: 1200, share: 500 / 1700 });
  assert.deepEqual(s.debts.map((d) => d.name), ["Store card", "Card", "Car", "Debt 3"], "highest rate first, no rate last");
  assert.equal(s.debts[1].monthlyInterest, 40);
  assert.equal(s.debtTotal, 9200);
  assert.deepEqual(s.accounts, ["Checking account", "Roth IRA"]);
  assert.deepEqual(s.goals.map((g) => [g.name, g.months, g.past]), [["Trip", 12, false], ["Laptop", -10, true], ["Someday", null, false]]);
  assert.equal(s.goals[0].perMonth, 100);
  assert.equal(s.goals[1].perMonth, null);
  assert.equal(s.isEmpty, false);
});

test("Money Map summary: empty and edge cases", () => {
  assert.equal(L.moneyMapSummary({}, "2026-11-15").isEmpty, true);
  assert.equal(L.moneyMapSummary(null, "2026-11-15").isEmpty, true);
  const over = L.moneyMapSummary({ pay: 1000, costs: [{ name: "Rent", amount: 1500 }] }, "2026-11-15");
  assert.equal(over.leftover, -500);
  assert.equal(over.cushion.target, 1500, "default target is 1 month");
  assert.equal(over.cushion.saved, null);
  const noPay = L.moneyMapSummary({ costs: [{ name: "Rent", amount: 900 }], cushion: { months: 3, saved: 5000 } }, "2026-11-15");
  assert.equal(noPay.costShare, null);
  assert.deepEqual([noPay.cushion.target, noPay.cushion.remaining, noPay.cushion.share], [2700, 0, 1]);
  assert.equal(L.moneyMapSummary({ costs: [{ amount: 900 }], cushion: { months: 0 } }, "2026-11-15").cushion, null);
  const mm = L.normalizeMoneyMap({ pay: -5, cushion: { months: 99 }, goals: [{ name: "x".repeat(500), by: "2027-13" }],
                                   costs: Array.from({ length: 50 }, () => ({ name: "a", amount: 1 })) });
  assert.equal(mm.pay, null);
  assert.equal(mm.cushion.months, 1);
  assert.equal(mm.goals[0].name.length, 80);
  assert.equal(mm.goals[0].by, "");
  assert.equal(mm.costs.length, 30);
});

test("crash sim: hypothetical paths fall to the stated drop and climb back to the start", () => {
  for (const s of L.SCENARIOS) {
    assert.equal(s.kind, "hypothetical");
    assert.match(s.name, /^Hypothetical/);
    const p = L.scenarioPath(s);
    assert.equal(p.length, s.fall_months + s.recover_months + 1);
    assert.equal(p[0], 100);
    assert.equal(p[p.length - 1], 100);
    assert.equal(L.bottomIndex(p), s.fall_months);
    assert.ok(Math.abs(p[s.fall_months] - 100 * (1 - s.drop)) < 1e-9);
    for (let i = 1; i <= s.fall_months; i++) assert.ok(p[i] < p[i - 1], "falls every month");
    for (let i = s.fall_months + 1; i < p.length; i++) assert.ok(p[i] > p[i - 1], "climbs every month");
  }
  assert.deepEqual(L.SCENARIOS.map((s) => [s.drop, s.recover_months / 12]), [[0.35, 4], [0.5, 6]]);
});

test("crash sim: hold, sell at the bottom, sell and buy back a year later", () => {
  const s = L.SCENARIOS[0], p = L.scenarioPath(s);
  const r = L.compareChoices(p, 10000);
  assert.equal(r.bottom, 12);
  assert.ok(Math.abs(r.low - 6500) < 1e-6);
  assert.equal(r.backToStart, 60);
  assert.ok(Math.abs(r.results.hold.final - 10000) < 1e-6);
  assert.ok(Math.abs(r.results["sell-bottom"].final - 6500) < 1e-6);
  // Buy back at month 24: level 65 * (100/65)^(12/48); 6,500 then grows with the index back to 100.
  const lvl24 = 65 * Math.pow(100 / 65, 12 / 48);
  assert.equal(r.buyAt, 24);
  assert.ok(Math.abs(r.results["sell-buyback"].final - 6500 * 100 / lvl24) < 1e-6);
  assert.ok(Math.abs(r.riseBeforeBuyback - (lvl24 / 65 - 1)) < 1e-12);
  assert.ok(r.vsHold["sell-bottom"] < r.vsHold["sell-buyback"] && r.vsHold["sell-buyback"] < 0 && r.vsHold.hold === 0);
  // Every path is identical up to the bottom; cash stays flat while out of the market.
  for (let m = 0; m <= 12; m++) assert.equal(r.results["sell-bottom"].values[m], r.results.hold.values[m]);
  for (let m = 13; m <= 24; m++) assert.equal(r.results["sell-buyback"].values[m], r.results["sell-bottom"].values[12]);
  assert.equal(r.results.hold.values.length, 61);
});

test("crash sim: works on any series, including one that ends before the buy-back", () => {
  const short = [100, 90, 70, 80, 95, 100];
  const r = L.compareChoices(short, 1000);
  assert.equal(r.bottom, 2);
  assert.equal(r.buyAt, null);
  assert.ok(Math.abs(r.results["sell-buyback"].final - 700) < 1e-9, "stays in cash");
  const shifted = L.simulate([200, 100, 150, 200], 500, "hold");
  assert.deepEqual(shifted.values, [500, 250, 375, 500], "levels are relative to the first point");
  assert.equal(L.simulate(short, 1000, "sell-buyback", 2).buyAt, 4);
});

test("history.json: only complete, verified, sourced series are used", () => {
  const points = Array.from({ length: 24 }, (_, i) => ({ date: `20${String(7 + Math.floor(i / 12)).padStart(2, "0")}-${String(i % 12 + 1).padStart(2, "0")}`, level: 100 - (i < 12 ? i * 3 : (23 - i) * 3) }));
  const good = { id: "crash-2008", label: "2008-09", index_name: "Example index", points, source_name: "Example source",
                 source_url: "https://example.gov/data", retrieved: "2026-11-20", license: "Public domain", verified: true };
  const out = L.validHistory({ series: [good, { ...good, id: "x2", verified: false }, { ...good, id: "x3", source_url: "javascript:alert(1)" },
    { ...good, id: "x4", license: "" }, { ...good, id: "x5", points: points.slice(0, 5) }, { ...good, id: "x6", points: [...points.slice(1), { date: "2009-01", level: -1 }] }] });
  assert.deepEqual(out.map((s) => s.id), ["crash-2008"]);
  assert.equal(out[0].kind, "historical");
  assert.equal(out[0].path.length, 24);
  assert.equal(out[0].dates[0], "2007-01");
  assert.equal(L.pathFor(out[0]), out[0].path);
  assert.deepEqual(L.validHistory(null), []);
  // The file shipped today is the empty placeholder.
  const shipped = JSON.parse(fs.readFileSync(path.join(REPO, "invest", "site", "app", "data", "history.json"), "utf8"));
  assert.deepEqual(L.validHistory(shipped), []);
});

test("the real curriculum works with the app logic", () => {
  const cur = JSON.parse(fs.readFileSync(path.join(REPO, "invest", "data", "curriculum.json"), "utf8"));
  const all = L.flatten(cur);
  assert.ok(all.length >= 3);
  assert.ok(all.every((e) => L.isSlug(e.lesson.slug)), "every slug is one the app accepts");
  assert.equal(new Set(all.map((e) => e.lesson.slug)).size, all.length, "slugs are unique");
  assert.equal(cur.levels[0].free, true);
  assert.ok(cur.levels.slice(1).every((l) => l.free === false));
  assert.equal(L.nextLesson(cur, fresh()).entry.lesson.slug, all[0].lesson.slug);
  // Walking the path in order, passing each check, reaches the members-only wall after level 1.
  let p = fresh();
  for (let guard = 0; guard < all.length; guard++) {
    const n = L.nextLesson(cur, p);
    if (!n || n.locked) break;
    p = L.recordQuiz(p, n.entry.lesson.slug, 3, "2026-11-15").progress;
  }
  assert.equal(L.overallProgress(cur, p).done, L.levelProgress(cur.levels[0], p).total);
  assert.equal(L.nextLesson(cur, p).locked, true);
  for (const e of all) {
    assert.equal(e.lesson.quiz.length, 3, e.lesson.slug);
    for (const q of e.lesson.quiz) assert.ok(Number.isInteger(q.answer) && q.answer >= 0 && q.answer < q.choices.length, e.lesson.slug);
  }
});

test("the app's copy of the curriculum matches the source (run `python3 -m invest build-site`)", () => {
  const src = fs.readFileSync(path.join(REPO, "invest", "data", "curriculum.json"), "utf8");
  const copy = fs.readFileSync(path.join(REPO, "invest", "site", "app", "data", "curriculum.json"), "utf8");
  assert.equal(copy, src);
});
