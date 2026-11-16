// End-to-end smoke test for the learning app (invest/site/app), in headless Chromium.
//
// Run:  node tests/app/e2e_app.js [--shots DIR]
// It starts `python3 -m http.server` on a free port in 8820-8849 serving invest/site, walks
// path -> lesson -> quiz -> complete -> locked level -> demo checkout -> unlocked, checks the
// Money Map, crash simulator and video player, looks for horizontal overflow at 320px and
// 1280px, runs the rendered copy through the claims filter and fails on any console error.
// --shots DIR also saves light and dark, phone and desktop screenshots of every page.
"use strict";
const { chromium } = require("playwright");
const { spawn, execFileSync } = require("child_process");
const fs = require("fs");
const net = require("net");
const path = require("path");

const REPO = path.resolve(__dirname, "..", "..");
const SITE = path.join(REPO, "invest", "site");
const CUR = JSON.parse(fs.readFileSync(path.join(SITE, "app", "data", "curriculum.json"), "utf8"));
const MANIFEST_FILE = path.join(SITE, "media", "videos", "manifest.json");
const ALL = CUR.levels.flatMap((l) => l.modules.flatMap((m) => m.lessons.map((x) => ({ ...x, level: l, module: m }))));
const L1 = ALL.filter((x) => x.level.number === 1);
const L2 = ALL.filter((x) => x.level.number === 2);
const shotsArg = process.argv.indexOf("--shots");
const SHOTS = shotsArg > 0 ? path.resolve(process.argv[shotsArg + 1]) : null;
const KEY = "pm.progress.v1";

// ---- Tiny check runner --------------------------------------------------------------------------------
const results = [];
async function check(name, fn) {
  try { await fn(); results.push({ name, ok: true }); console.log("  ok   " + name); }
  catch (e) { results.push({ name, ok: false, err: e }); console.log("  FAIL " + name + "\n       " + String(e && e.message || e).split("\n").join("\n       ")); }
}
function assert(cond, msg) { if (!cond) throw new Error(msg); }
function eq(a, b, msg) { if (a !== b) throw new Error(`${msg}: expected ${JSON.stringify(b)}, got ${JSON.stringify(a)}`); }

function iso(d) { return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0"); }
function daysFromToday(n) { const d = new Date(); d.setDate(d.getDate() + n); return iso(d); }
const TODAY = iso(new Date());
function usd(n) { return "$" + (Math.abs(n) >= 10000 ? Math.round(n / 100) * 100 : Math.round(n)).toLocaleString("en-US"); }

// ---- Server -----------------------------------------------------------------------------------------------
function portFree(port) {
  return new Promise((resolve) => {
    const s = net.createServer().once("error", () => resolve(false))
      .once("listening", () => s.close(() => resolve(true))).listen(port, "127.0.0.1");
  });
}
async function startServer() {
  for (let port = 8820; port <= 8849; port++) {
    if (!(await portFree(port))) continue;
    const proc = spawn("python3", ["-m", "http.server", String(port), "--bind", "127.0.0.1", "--directory", SITE], { stdio: "ignore" });
    const base = `http://127.0.0.1:${port}`;
    for (let i = 0; i < 50; i++) {
      if (proc.exitCode !== null) break;
      try { if ((await fetch(base + "/app/index.html")).ok) return { proc, base }; } catch (e) { /* not up yet */ }
      await new Promise((r) => setTimeout(r, 100));
    }
    proc.kill();
  }
  throw new Error("Couldn't start python3 -m http.server on any port in 8820-8849");
}

// ---- Browser helpers ---------------------------------------------------------------------------------------
let browser, base;
const problems = [];
// A missing manifest (before the Video studio ships one) and the test's own missing video are expected 404s.
function expected404(url) {
  return (/\/media\/videos\/manifest\.json$/.test(url) && !fs.existsSync(MANIFEST_FILE)) || /__missing__/.test(url);
}
async function newContext(opts = {}) {
  const ctx = await browser.newContext({ viewport: { width: opts.width || 1280, height: opts.height || 900 },
                                         colorScheme: opts.scheme || "light", reducedMotion: "reduce" });
  if (opts.progress) {
    await ctx.addInitScript(([k, v]) => { if (!sessionStorage.getItem("seeded")) { localStorage.setItem(k, v); sessionStorage.setItem("seeded", "1"); } },
      [KEY, JSON.stringify(opts.progress)]);
  }
  return ctx;
}
async function newPage(ctx, label) {
  const page = await ctx.newPage();
  page.on("console", (m) => {
    if (m.type() !== "error") return;
    const url = (m.location() || {}).url || "";
    if (/Failed to load resource/.test(m.text()) && expected404(url)) return;
    problems.push(`${label}: console error: ${m.text()} ${url}`);
  });
  page.on("pageerror", (e) => problems.push(`${label}: page error: ${e.message}`));
  page.on("response", (r) => {
    if (r.status() >= 400 && r.url().startsWith(base) && !expected404(r.url())) problems.push(`${label}: ${r.status()} ${r.url()}`);
  });
  return page;
}
async function go(page, url) {
  await page.goto(base + url);
  await page.waitForFunction(() => !document.querySelector("[aria-busy=true]"));
}
const text = (page, sel) => page.$eval(sel, (e) => e.textContent.replace(/\s+/g, " ").trim());
const store = (page) => page.evaluate((k) => JSON.parse(localStorage.getItem(k) || "null"), KEY);
async function answerQuiz(page, lesson, correctCount) {
  for (let i = 0; i < 3; i++) {
    const q = lesson.quiz[i];
    const pick = i < correctCount ? q.answer : (q.answer + 1) % q.choices.length;
    await page.check(`#q${i}c${pick}`);
  }
  await page.click("#checkBtn");
}
async function noOverflow(page, where) {
  const r = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth,
    wide: [...document.querySelectorAll("body *")].filter((e) => e.getBoundingClientRect().right > document.documentElement.clientWidth + 1 &&
      getComputedStyle(e).position !== "fixed" && !e.closest(".table-wrap") && e.offsetParent !== null).slice(0, 3)
      .map((e) => e.tagName.toLowerCase() + (e.id ? "#" + e.id : "") + "." + e.className) }));
  assert(r.sw <= r.cw, `${where}: page is ${r.sw}px wide in a ${r.cw}px viewport (${r.wide.join(", ")})`);
}

// ---- Checks -----------------------------------------------------------------------------------------------
async function run() {
  const first = ALL[0], second = ALL[1];
  const visitor = await newContext();
  const page = await newPage(visitor, "visitor");

  await check("path: a new visitor starts at lesson 1; level 1 is free, levels 2-5 are locked", async () => {
    await go(page, "/app/index.html");
    eq(await text(page, "#nextTitle"), first.title, "next lesson");
    eq(await text(page, "#nextCard .kicker"), "Start here", "first-visit label");
    eq(await page.$$eval(".level", (els) => els.length), CUR.levels.length, "one card per level");
    eq(await page.$$eval("#level-1 .lock-pill", (e) => e.length), 0, "level 1 has no lock");
    for (const l of CUR.levels.slice(1)) {
      const id = `#level-${l.number}`;
      eq(await text(page, `${id} .lock-pill`), "Members", `level ${l.number} lock`);
      eq(await page.$eval(`${id} .unlock a.btn`, (a) => [a.getAttribute("href"), a.textContent].join("|")), "../pricing.html|Unlock all levels", `level ${l.number} unlock link`);
      eq(await page.$$eval(`${id} .rows a`, (a) => a.length), 0, `level ${l.number} lessons aren't links`);
    }
    eq(await page.$eval("#level-1 details", (d) => d.open), true, "current level is open");
    eq(await page.$$eval("#level-1 .rows li", (li) => li.length), L1.length, "level 1 rows");
    eq(await text(page, "#level-1 .progress .meta"), `0 of ${L1.length} done`, "level 1 progress");
    eq(await page.$eval(`#level-1 li[data-slug="${first.slug}"]`, (li) => li.dataset.status), "next", "first lesson marked next");
  });

  await check("lesson: opens from the path with objectives, key points, risk note, try it and the check", async () => {
    await page.click("#startNext");
    await page.waitForSelector("#quiz");
    eq(new URL(page.url()).hash, "#" + first.slug, "lesson URL");
    eq(await text(page, "h1"), first.title, "lesson title");
    eq(await page.$$eval("#learnCard li", (li) => li.length), first.objectives.length + first.key_points.length, "objectives + key points");
    eq(await page.$$eval("#riskNote", (e) => e.length), first.risk_note ? 1 : 0, "risk note shown only when present");
    const tool = first.try_it.tool;
    const href = { calculator: "../index.html", "money-map": "money-map.html?from=" + first.slug, "crash-sim": "crash-sim.html?from=" + first.slug }[tool];
    eq(await page.$$eval("#tryIt a", (a) => a.map((x) => x.getAttribute("href"))[0] || null), href || null, "try it link");
    const manifest = fs.existsSync(MANIFEST_FILE) ? JSON.parse(fs.readFileSync(MANIFEST_FILE, "utf8")) : { videos: {} };
    const v = manifest.videos[first.slug];
    if (!v) {
      eq(await page.$eval("#video", (x) => x.dataset.state), "soon", "no video yet");
      assert((await text(page, "#video")).includes("Video coming soon"), "coming-soon text");
    } else if (fs.existsSync(path.join(SITE, v.mp4))) {
      eq(await page.$eval("#video", (x) => x.dataset.state), "video", "the Video studio's video plays here");
      eq(await page.$$eval("#video .badge.draft", (e) => e.length), v.approved ? 0 : 1, "Draft badge matches approved");
      eq(await page.$$eval("#video track[kind=captions]", (e) => e.length), v.captions ? 1 : 0, "captions track");
    }
    eq(await page.$$eval("#quiz fieldset", (f) => f.length), 3, "three questions");
    eq(await page.$$eval("#quiz input[type=radio]", (f) => f.length), 9, "three choices each");
  });

  await check("quiz: 0 of 3 fails and shows why; retry; 2 of 3 completes and schedules a review in 3 days", async () => {
    await page.click("#checkBtn");
    eq(await text(page, "#quizError"), "Answer all 3 questions first.", "unanswered warning");
    await answerQuiz(page, first, 0);
    const r = await text(page, "#quizResult");
    assert(r.startsWith("0 of 3 right.") && r.includes("You need 2 of 3"), "fail message: " + r);
    for (let i = 0; i < 3; i++) {
      assert(await page.isVisible(`#why${i}`), `why ${i} visible`);
      assert((await text(page, `#why${i}`)).includes(first.quiz[i].why), `why ${i} text`);
      eq(await page.$$eval(`[data-q="${i}"] .choice.is-answer`, (e) => e.length), 1, `correct answer ${i} marked`);
    }
    assert(await page.isVisible("#retryBtn"), "retry shown");
    let s = await store(page);
    eq(JSON.stringify(s.quiz[first.slug]), JSON.stringify({ best: 0, tries: 1 }), "attempt recorded");
    eq(s.completed[first.slug], undefined, "not completed");
    await page.click("#retryBtn");
    eq(await page.$$eval("#quiz input:checked, #quiz input:disabled", (e) => e.length), 0, "retry clears answers");
    await answerQuiz(page, first, 2);
    assert((await text(page, "#quizResult")).startsWith("2 of 3 right. Lesson complete."), "pass message");
    s = await store(page);
    eq(s.completed[first.slug], TODAY, "completed today");
    eq(s.review_due[first.slug], daysFromToday(3), "first review in 3 days");
    eq(JSON.stringify(s.quiz[first.slug]), JSON.stringify({ best: 2, tries: 2 }), "best and tries");
    assert((await text(page, "#lessonMeta")).includes("Completed"), "completed badge");
  });

  await check("next lesson: the button at the end opens the next lesson", async () => {
    await page.click("#nextBtn");
    await page.waitForFunction((t) => document.querySelector("h1").textContent === t, second.title);
    eq(new URL(page.url()).hash, "#" + second.slug, "next lesson URL");
    eq(await page.evaluate(() => document.activeElement.tagName), "H1", "focus moves to the new title");
    eq(await page.$$eval("#quizResult", (e) => e[0].textContent), "", "fresh check");
  });

  await check("path: progress and the next lesson update after completing one", async () => {
    await go(page, "/app/index.html");
    eq(await text(page, "#level-1 .progress .meta"), `1 of ${L1.length} done`, "level 1 progress");
    eq(await page.$eval(`#level-1 li[data-slug="${first.slug}"]`, (li) => li.dataset.status), "done", "done mark");
    eq(await text(page, "#nextTitle"), second.title, "next lesson");
    assert((await text(page, "#reviewNote")).includes(first.title), "upcoming review note");
  });

  await check("locked level: a level 2 lesson can't be opened without membership", async () => {
    await go(page, "/app/lesson.html#" + L2[0].slug);
    assert(await page.isVisible("#lockedPanel"), "locked panel");
    eq(await page.$$eval("#quiz, #learnCard, #video", (e) => e.length), 0, "no lesson content");
    eq(await page.$eval("#lockedPanel a.btn", (a) => a.getAttribute("href")), "../pricing.html", "unlock link");
    await go(page, "/app/lesson.html#" + L1[L1.length - 1].slug);
    eq(await page.$eval("#nextUnlock", (a) => a.getAttribute("href")), "../pricing.html", "end of level 1 points to membership");
    await go(page, "/app/lesson.html#not-a-real-lesson");
    eq(await text(page, "h1"), "We couldn't find that lesson", "unknown slug");
  });

  await check("demo checkout: turns membership on and unlocks levels 2-5", async () => {
    await go(page, "/app/account.html");
    eq(await text(page, "#memberStatus"), "Demo membership: off.", "starts off");
    assert((await text(page, "#demoCheckout")).includes("no payment"), "labeled as a demo");
    await page.click("#demoCheckout");
    eq(await text(page, "#memberStatus"), "Demo membership: on.", "now on");
    eq((await store(page)).member, true, "member saved");
    await go(page, "/app/index.html");
    eq(await page.$$eval(".lock-pill", (e) => e.length), 0, "no locks left");
    assert((await page.$$eval("#level-2 .rows a", (a) => a.length)) === L2.length, "level 2 lessons are links");
    await go(page, "/app/lesson.html#" + L2[0].slug);
    eq(await page.$$eval("#lockedPanel", (e) => e.length), 0, "not locked");
    assert(await page.isVisible("#quiz"), "check shown");
    if (L2[0].risk_note) assert(await page.isVisible("#riskNote"), "risk note callout visible");
  });

  await check("review: a due review shows on the path and the lesson; passing moves it to day 10", async () => {
    await page.evaluate(([k, slug, done, due]) => {
      const p = JSON.parse(localStorage.getItem(k)); p.completed[slug] = done; p.review_due[slug] = due; localStorage.setItem(k, JSON.stringify(p));
    }, [KEY, first.slug, daysFromToday(-3), TODAY]);
    await go(page, "/app/index.html");
    assert((await text(page, "#reviewCard")).includes(first.title) && (await text(page, "#reviewCard")).includes("due today"), "review card");
    eq(await text(page, `#level-1 li[data-slug="${first.slug}"] .meta`), "Review due", "row flag");
    await page.click(`#reviewCard a[href="lesson.html#${first.slug}"]`);
    await page.waitForSelector("#reviewNote");
    await answerQuiz(page, first, 3);
    assert((await text(page, "#quizResult")).includes("Review done."), "review message");
    eq((await store(page)).review_due[first.slug], daysFromToday(7), "next review 10 days after completion");
    eq(await page.$$eval("#reviewNote", (e) => e.length), 0, "review note removed");
  });

  await check("account: reset progress keeps the Money Map and membership", async () => {
    await page.evaluate((k) => { const p = JSON.parse(localStorage.getItem(k)); p.money_map = { pay: 2000 }; localStorage.setItem(k, JSON.stringify(p)); }, KEY);
    await go(page, "/app/account.html");
    assert((await text(page, "#progressSummary")).includes("completed"), "progress summary");
    await page.click("#resetBtn");
    await page.click("#resetYes");
    const s = await store(page);
    eq(JSON.stringify([s.completed, s.quiz, s.review_due]), "[{},{},{}]", "learning cleared");
    eq(s.member, true, "membership kept");
    eq(s.money_map.pay, 2000, "Money Map kept");
    await page.click("#endDemo");
    eq((await store(page)).member, false, "demo membership can be ended");
  });
  await visitor.close();

  await check("Money Map: everyone can fill it in, it's saved on the device, the summary is for members", async () => {
    const ctx = await newContext();
    const p = await newPage(ctx, "money-map");
    await go(p, "/app/money-map.html?from=" + first.slug);
    eq(await p.$eval("#fromLesson a", (a) => a.getAttribute("href")), "lesson.html#" + first.slug, "back to lesson");
    assert((await text(p, "#privacy")).includes("It stays on this device"), "privacy note");
    await p.fill("#pay", "3000");
    await p.fill("#gross", "3800");
    await p.fill("#costs-0-name", "Rent");
    await p.fill("#costs-0-amount", "1200");
    await p.fill("#costs-1-name", "Groceries");
    await p.fill("#costs-1-amount", "400");
    await p.click('#monthsChips button[data-value="3"]');
    await p.fill("#saved", "1000");
    await p.fill("#debts-0-name", "Car loan");
    await p.fill("#debts-0-balance", "6000");
    await p.fill("#debts-0-rate", "7.5");
    await p.click("#addDebt");
    eq(await p.evaluate(() => document.activeElement.id), "debts-1-name", "new row focused");
    await p.fill("#debts-1-name", "Card");
    await p.fill("#debts-1-balance", "2000");
    await p.fill("#debts-1-rate", "24");
    await p.check("#acct-checking");
    await p.fill("#goals-0-name", "Trip");
    await p.fill("#goals-0-amount", "1200");
    assert(await p.isVisible("#summaryLocked"), "summary locked for free visitors");
    eq(await p.isVisible("#summaryOpen"), false, "summary hidden");
    await p.reload();
    eq(await p.inputValue("#pay"), "3000", "pay kept after reload");
    eq(await p.inputValue("#debts-1-rate"), "24", "debt kept after reload");
    const mm = (await store(p)).money_map;
    eq(mm.pay, 3000, "saved under pm.progress.v1.money_map");
    eq(mm.cushion.months, 3, "cushion months saved");
    // Turn on membership: the summary explains, sorted by rate.
    await p.evaluate((k) => { const s = JSON.parse(localStorage.getItem(k)); s.member = true; localStorage.setItem(k, JSON.stringify(s)); }, KEY);
    await p.reload();
    assert(await p.isVisible("#summaryOpen"), "summary open for members");
    assert((await text(p, "#sumCushion")).includes("Your cushion target is 3 months of the costs you entered: $4,800."), "cushion target");
    eq(JSON.stringify(await p.$$eval("#debtOrder li", (li) => li.map((x) => x.textContent.split(":")[0]))), JSON.stringify(["Card", "Car loan"]), "debts by rate");
    assert((await text(p, "#sumMonth")).includes("leaving $1,400 a month"), "leftover");
    await p.click('#monthsChips button[data-value="1"]');
    assert((await text(p, "#sumCushion")).includes("1 month of the costs you entered: $1,600."), "1-month wording");
    await p.click('#debtsList [aria-label="Remove debt 1"]');
    eq(await p.$$eval("#debtOrder li", (li) => li.length), 1, "removing a debt updates the summary");
    await p.click("#clearBtn");
    await p.click("#clearYes");
    eq(await p.inputValue("#pay"), "", "cleared");
    assert(await p.isVisible("#summaryEmpty"), "empty summary");
    await ctx.close();
  });

  await check("crash sim: hypothetical scenarios; free visitors see the drop, members make the call", async () => {
    const ctx = await newContext();
    const p = await newPage(ctx, "crash-sim");
    await go(p, "/app/crash-sim.html");
    assert((await text(p, "#kindPill")).startsWith("Hypothetical scenario"), "labeled hypothetical");
    assert((await text(p, "#scenarioChips")).includes("Hypothetical A"), "scenario names");
    assert((await text(p, "#momentText")).includes("down 35%, to $6,500"), "the drop");
    assert(await p.isVisible("#simLocked"), "choices locked for free visitors");
    eq(await p.isVisible("#choices"), false, "no choices");
    await p.evaluate((k) => localStorage.setItem(k, JSON.stringify({ member: true })), KEY);
    await p.reload();
    assert(await p.isVisible("#choices"), "choices for members");
    eq(await p.$$eval("#chart path.line", (e) => e.length), 1, "before the call: one line to the bottom");
    await p.click('#choices button[data-choice="sell-bottom"]');
    eq(await p.$$eval("#chart path.line", (e) => e.length), 3, "after: three lines");
    eq(await text(p, '#tiles [data-choice="sell-bottom"] .v'), "$6,500", "sell-at-bottom result");
    eq(await text(p, '#tiles [data-choice="hold"] .v'), "$10,000", "hold result");
    const lvl24 = 65 * Math.pow(100 / 65, 12 / 48), buyback = 6500 * 100 / lvl24;
    eq(await text(p, '#tiles [data-choice="sell-buyback"] .v'), usd(buyback), "buy-back result");
    assert((await text(p, "#result")).includes("which is $3,500 more"), "result text: " + await text(p, "#result"));
    assert((await text(p, "#table thead")).includes("Sell at the bottom (your pick)"), "table marks the pick");
    assert((await p.$$eval("#table tbody tr", (r) => r.length)) >= 6, "table rows");
    await p.click('#choices button[data-choice="sell-buyback"]');
    assert((await text(p, "#result")).includes(usd(10000 - buyback) + " less than holding"), "buy-back text");
    await p.focus("#chart svg");
    await p.keyboard.press("Home");
    assert((await text(p, "#chartReadout")).startsWith("Start: Hold $10,000"), "keyboard Home: " + await text(p, "#chartReadout"));
    await p.keyboard.press("ArrowRight");
    assert((await text(p, "#chartReadout")).startsWith("Month 1:"), "keyboard ArrowRight");
    await p.keyboard.press("End");
    assert((await text(p, "#chartReadout")).startsWith("Month 60:"), "keyboard End");
    assert(await p.isVisible("#chart .tooltip"), "tooltip follows focus");
    await p.click('#scenarioChips button[data-id="hypothetical-50"]');
    assert((await text(p, "#momentText")).includes("down 50%"), "second scenario");
    eq(await p.$$eval("#tiles:not(.hidden)", (e) => e.length), 0, "new scenario starts at the decision");
    await p.fill("#amount", "5");
    assert((await text(p, "#amountError")).length > 0, "amount validation");
    await ctx.close();
  });

  await check("video: player with captions, Draft badge and AI label; missing or unsafe files fall back", async () => {
    const ctx = await newContext({ progress: { member: true } });
    const entry = { mp4: "media/videos/__missing__.mp4", captions: "media/videos/__missing__.vtt", poster: "media/videos/__missing__.jpg",
                    duration_s: 154, narration: "none", ai_label: "Made with AI, reviewed by a person", approved: false };
    const serve = (videos) => (route) => route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ videos }) });
    // 1. A draft whose file is still loading: the player shows.
    let p = await newPage(ctx, "video-draft");
    await p.route("**/media/videos/manifest.json", serve({ [first.slug]: entry }));
    await p.route("**/__missing__.mp4", () => { /* never answers: still loading */ });
    await p.route("**/__missing__.{vtt,jpg}", (r) => r.fulfill({ status: 200, contentType: "text/vtt", body: "WEBVTT\n" }));
    await go(p, "/app/lesson.html#" + first.slug);
    eq(await p.$eval("#video", (v) => v.dataset.state), "video", "player shown");
    eq(await p.$eval("#video video source", (s) => s.getAttribute("src")), "../media/videos/__missing__.mp4", "mp4 path relative to site/");
    eq(await p.$eval("#video track", (t) => [t.kind, t.getAttribute("src"), t.default].join("|")), "captions|../media/videos/__missing__.vtt|true", "captions track");
    eq(await text(p, "#video .badge.draft"), "Draft", "draft badge");
    assert((await text(p, "#video .ai-label")).startsWith("Made with AI"), "AI label");
    assert((await text(p, "#video figcaption")).includes("Captions only"), "captions-only note");
    await p.close();
    // 2. Approved: the manifest's label, no Draft badge.
    p = await newPage(ctx, "video-approved");
    await p.route("**/media/videos/manifest.json", serve({ [first.slug]: { ...entry, approved: true } }));
    await p.route("**/__missing__.mp4", () => {});
    await p.route("**/__missing__.{vtt,jpg}", (r) => r.fulfill({ status: 200, contentType: "text/vtt", body: "WEBVTT\n" }));
    await go(p, "/app/lesson.html#" + first.slug);
    eq(await p.$$eval("#video .badge.draft", (e) => e.length), 0, "no draft badge");
    eq(await text(p, "#video .ai-label"), "Made with AI, reviewed by a person", "approved label");
    await p.close();
    // 3. The file isn't there: "coming soon". 4. An unsafe path is never loaded.
    p = await newPage(ctx, "video-missing");
    await p.route("**/media/videos/manifest.json", serve({ [first.slug]: entry, [second.slug]: { ...entry, mp4: "javascript:alert(1)" } }));
    await go(p, "/app/lesson.html#" + first.slug);
    await p.waitForSelector('#video[data-state="soon"]', { timeout: 5000 });
    await go(p, "/app/lesson.html#" + second.slug);
    eq(await p.$eval("#video", (v) => v.dataset.state), "soon", "unsafe path ignored");
    await p.close();
    // 5. A broken manifest file.
    p = await newPage(ctx, "video-broken");
    await p.route("**/media/videos/manifest.json", (r) => r.fulfill({ status: 200, contentType: "application/json", body: "{not json" }));
    await go(p, "/app/lesson.html#" + first.slug);
    eq(await p.$eval("#video", (v) => v.dataset.state), "soon", "broken manifest");
    await ctx.close();
  });

  await check("layout: no horizontal overflow at 320px and 1280px", async () => {
    const urls = ["/app/index.html", "/app/lesson.html#" + first.slug, "/app/lesson.html#" + L2[0].slug,
                  "/app/money-map.html?from=" + first.slug, "/app/crash-sim.html", "/app/account.html", "/index.html", "/rules.html", "/learn/"];
    for (const member of [false, true]) {
      for (const width of [320, 1280]) {
        const ctx = await newContext({ width, progress: { member } });
        const p = await newPage(ctx, `layout-${width}`);
        for (const u of urls) {
          await go(p, u);
          if (u.startsWith("/app/lesson.html") && member) { await answerQuiz(p, first, 1); }
          if (u === "/app/crash-sim.html" && member) await p.click('#choices button[data-choice="hold"]');
          await noOverflow(p, `${u} at ${width}px${member ? " (member)" : ""}`);
        }
        await ctx.close();
      }
    }
  });

  await check("copy: every page's rendered text passes the claims filter", async () => {
    const ctx = await newContext({ progress: { member: true } });
    const p = await newPage(ctx, "copy");
    const chunks = [];
    const grab = async (label) => chunks.push(`\n\n[${label}]\n` + await p.evaluate(() => document.body.innerText));
    await go(p, "/app/index.html"); await grab("path");
    await go(p, "/app/lesson.html#" + ALL[0].slug);
    for (const l of ALL) {
      await p.evaluate((s) => { location.hash = s; }, l.slug);
      await p.waitForFunction((t) => document.querySelector("h1").textContent === t, l.title);
      await answerQuiz(p, l, 1);
      await grab("lesson " + l.slug);
    }
    await go(p, "/app/crash-sim.html");
    for (const c of ["hold", "sell-bottom", "sell-buyback"]) { await p.click(`#choices button[data-choice="${c}"]`); await grab("crash " + c); }
    await go(p, "/app/money-map.html");
    await p.fill("#pay", "3000"); await p.fill("#costs-0-amount", "1000"); await p.fill("#debts-0-balance", "500"); await p.fill("#debts-0-rate", "20");
    await grab("money map");
    await go(p, "/app/account.html"); await grab("account");
    await p.evaluate((k) => localStorage.setItem(k, "{}"), KEY);
    await go(p, "/app/index.html"); await grab("path, visitor");
    await go(p, "/app/lesson.html#" + L2[0].slug); await grab("locked lesson");
    await go(p, "/app/crash-sim.html"); await grab("crash, visitor");
    const out = execFileSync("python3", ["-c", "import json, sys; from invest.claims import find_violations as f; print(json.dumps(f(sys.stdin.read())))"],
      { cwd: REPO, input: chunks.join("") }).toString();
    eq(out.trim(), "[]", "claims filter hits");
    await ctx.close();
  });

  await check("accessibility: keyboard focus is visible on the path and lesson pages", async () => {
    const ctx = await newContext();
    const p = await newPage(ctx, "focus");
    for (const u of ["/app/index.html", "/app/lesson.html#" + first.slug]) {
      await go(p, u);
      const missing = [];
      for (let i = 0; i < 40; i++) {
        await p.keyboard.press("Tab");
        const s = await p.evaluate(() => {
          const e = document.activeElement;
          if (!e || e === document.body) return null;
          const target = e.matches("input[type=radio]") ? e.closest(".choice") : e;
          const c = getComputedStyle(target);
          return { id: e.tagName + (e.id ? "#" + e.id : "") + " " + (e.textContent || "").trim().slice(0, 20), ring: c.outlineStyle !== "none" && parseFloat(c.outlineWidth) >= 2 };
        });
        if (s && !s.ring) missing.push(s.id);
      }
      eq(missing.join(", "), "", `${u}: focused elements without a visible ring`);
    }
    await ctx.close();
  });

  await check("no console errors, page errors or failed requests anywhere", async () => {
    eq(problems.join("\n"), "", "problems seen while testing");
  });

  if (SHOTS) await screenshots();
}

// ---- Screenshots (--shots DIR) -----------------------------------------------------------------------------
async function screenshots() {
  fs.mkdirSync(SHOTS, { recursive: true });
  const demoMap = { pay: 3000, gross: 3800, costs: [{ name: "Rent", amount: 1200 }, { name: "Groceries", amount: 400 }, { name: "Phone", amount: 60 }],
    flexible: 350, cushion: { months: 3, saved: 1200, where: "Savings account", rate: 3.5, insured: true },
    debts: [{ name: "Car loan", balance: 6000, rate: 7.5, minimum: 180 }, { name: "Credit card", balance: 2000, rate: 24, minimum: 60 }],
    accounts: { checking: true, savings: true, workplace: true }, goals: [{ name: "Trip", amount: 1200, by: daysFromToday(365).slice(0, 7) }] };
  const done = {}; L1.slice(0, 3).forEach((l) => { done[l.slug] = daysFromToday(-4); });
  const review = { [L1[0].slug]: daysFromToday(-1), [L1[1].slug]: daysFromToday(2), [L1[2].slug]: daysFromToday(6) };
  const sets = [
    ["path", "/app/index.html", { completed: done, review_due: review, quiz: {} }],
    ["lesson", "/app/lesson.html#" + L1[3].slug, { completed: done, review_due: review }, async (p) => { await answerQuiz(p, L1[3], 2); }],
    ["lesson-risk-member", "/app/lesson.html#" + (ALL.find((l) => l.risk_note && l.level.number > 1) || L2[0]).slug, { member: true }],
    ["lesson-locked", "/app/lesson.html#" + L2[0].slug, {}],
    ["money-map-free", "/app/money-map.html", { money_map: demoMap }],
    ["money-map-member", "/app/money-map.html", { member: true, money_map: demoMap }],
    ["crash-sim", "/app/crash-sim.html", { member: true }, async (p) => { await p.click('#choices button[data-choice="sell-buyback"]'); }],
    ["crash-sim-free", "/app/crash-sim.html", {}],
    ["account", "/app/account.html", { member: false }],
  ];
  for (const scheme of ["light", "dark"]) {
    for (const [device, width] of [["phone", 375], ["desktop", 1280]]) {
      for (const [name, url, progress, act] of sets) {
        const ctx = await newContext({ width, height: device === "phone" ? 800 : 900, scheme, progress });
        const p = await newPage(ctx, "shot");
        await go(p, url);
        if (act) await act(p);
        await p.screenshot({ path: path.join(SHOTS, `${name}-${device}-${scheme}.png`), fullPage: true });
        await ctx.close();
      }
    }
  }
  console.log(`  screenshots saved to ${SHOTS}`);
}

(async () => {
  let server;
  const stop = () => { if (server) { server.proc.kill(); server = null; } };
  process.on("SIGINT", () => { stop(); process.exit(130); });
  try {
    server = await startServer();
    base = server.base;
    console.log(`Serving ${SITE} at ${base}`);
    browser = await chromium.launch();
    await run();
  } catch (e) {
    results.push({ name: "setup", ok: false, err: e });
    console.error(e);
  } finally {
    if (browser) await browser.close();
    stop();
  }
  const failed = results.filter((r) => !r.ok);
  console.log(`\n${results.length - failed.length} passed, ${failed.length} failed`);
  process.exit(failed.length ? 1 : 0);
})();
