// End-to-end checks for the Patient Money calculator site (invest/site), in headless Chromium.
//
// Run:  node tests/qa/e2e_calculator.js
// It starts its own `python3 -m http.server` on a free port in 8900-8999, runs every check (a failing
// check doesn't stop the others), stops the server and exits non-zero if anything failed.
"use strict";
const { chromium } = require("playwright");
const { spawn } = require("child_process");
const fs = require("fs");
const net = require("net");
const path = require("path");
const vm = require("vm");

const SITE = path.resolve(__dirname, "..", "..", "invest", "site");
const WIDTHS = [320, 375, 768, 1280];

// ---- Independent math (deliberately not calc.js) ------------------------------------------------
// Deposits at the start of each month, compounded monthly at the yearly rate (annuity due).
function fv(monthly, annual, months) {
  if (months <= 0) return 0;
  if (annual === 0) return monthly * months;
  const i = Math.pow(1 + annual, 1 / 12) - 1;
  return monthly * ((Math.pow(1 + i, months) - 1) / i) * (1 + i);
}
function expected(o) {
  const r = o.rate / 100, months = (o.to - o.age) * 12;
  const now = fv(o.m, r, months), later = fv(o.m, r, months - o.wait * 12);
  const out = { now, later, cost: now - later };
  if (o.at) {
    const i = Math.pow(1 + r, 1 / 12) - 1, rest = (o.to - o.at) * 12;
    out.before = fv(o.m, r, (o.at - o.age) * 12);
    out.after = out.before * (1 - o.drop / 100);
    out.stressed = out.after * Math.pow(1 + i, rest) + fv(o.m, r, rest);
  }
  return out;
}
function usd(n) { return "$" + (Math.abs(n) >= 10000 ? Math.round(n / 100) * 100 : Math.round(n)).toLocaleString("en-US"); }

function siteDefaults() {
  const sandbox = { window: {} };
  vm.runInNewContext(fs.readFileSync(path.join(SITE, "assets", "config.js"), "utf8"), sandbox);
  const d = sandbox.window.SITE_CONFIG.defaults;
  return { age: d.age, to: d.endAge, m: d.monthly, wait: d.delay, rate: d.rate, drop: d.shockDrop, at: d.shockAge };
}

// ---- Tiny check runner ----------------------------------------------------------------------------
const results = [];
async function check(name, fn) {
  try { await fn(); results.push({ name, ok: true }); console.log("  ok   " + name); }
  catch (e) { results.push({ name, ok: false, err: e }); console.log("  FAIL " + name + "\n       " + String(e && e.message || e).split("\n").join("\n       ")); }
}
function assert(cond, msg) { if (!cond) throw new Error(msg); }
function eq(a, b, msg) { if (a !== b) throw new Error(`${msg}: expected ${JSON.stringify(b)}, got ${JSON.stringify(a)}`); }

// ---- Server ------------------------------------------------------------------------------------------
function portFree(port) {
  return new Promise((resolve) => {
    const s = net.createServer().once("error", () => resolve(false))
      .once("listening", () => s.close(() => resolve(true))).listen(port, "127.0.0.1");
  });
}
async function startServer() {
  for (let port = 8900; port <= 8999; port++) {
    if (!(await portFree(port))) continue;
    const proc = spawn("python3", ["-m", "http.server", String(port), "--bind", "127.0.0.1", "--directory", SITE],
      { stdio: "ignore" });
    const base = `http://127.0.0.1:${port}`;
    for (let i = 0; i < 50; i++) {
      if (proc.exitCode !== null) break;
      try { if ((await fetch(base + "/index.html")).ok) return { proc, base }; } catch (e) { /* not up yet */ }
      await new Promise((r) => setTimeout(r, 100));
    }
    proc.kill();
  }
  throw new Error("Couldn't start python3 -m http.server on any port in 8900-8999");
}

// ---- Page helpers ------------------------------------------------------------------------------------
let browser, base;
const problems = []; // console errors, page errors and failed same-origin requests, across every page

async function open(url, opts = {}) {
  const context = await browser.newContext({ viewport: { width: opts.width || 1280, height: 900 }, colorScheme: opts.colorScheme || "light" });
  const page = await context.newPage();
  const tag = (m) => problems.push(`${url}: ${m}`);
  page.on("console", (m) => { if (m.type() === "error") tag("console error: " + m.text()); });
  page.on("pageerror", (e) => tag("page error: " + e.message));
  page.on("response", (r) => {
    if (r.url().startsWith(base) && r.status() >= 400 && !r.url().endsWith("/favicon.ico")) tag(`HTTP ${r.status()} ${r.url()}`);
  });
  if (opts.route) await opts.route(page);
  const res = await page.goto(base + url);
  assert(res && res.ok(), `${url} returned ${res && res.status()}`);
  await page.waitForLoadState("networkidle");
  return page;
}
async function close(page) { await page.context().close(); }
const text = (page, sel) => page.$eval(sel, (el) => el.textContent);
async function setRange(page, sel, value) {
  await page.$eval(sel, (el, v) => { el.value = v; el.dispatchEvent(new Event("input", { bubbles: true })); }, String(value));
}
async function readState(page) {
  return page.evaluate(() => ({
    hero: document.getElementById("heroValue").textContent,
    now: document.getElementById("nowValue").textContent,
    later: document.getElementById("laterValue").textContent,
    error: document.getElementById("errors").textContent,
    errorShown: getComputedStyle(document.getElementById("errors")).display !== "none",
    opacity: getComputedStyle(document.getElementById("results")).opacity,
    search: location.search,
    series: document.querySelectorAll("#legend > span").length,
  }));
}
async function expectResults(page, o, label) {
  const s = await readState(page), e = expected(o);
  eq(s.hero, usd(e.cost), `${label}: hero`);
  eq(s.now, usd(e.now), `${label}: start-now tile`);
  eq(s.later, usd(e.later), `${label}: start-later tile`);
  eq(s.error, "", `${label}: error text`);
  eq(s.opacity, "1", `${label}: results opacity`);
  return s;
}
async function overflow(page) {
  return page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
}

// ---- Checks --------------------------------------------------------------------------------------------
async function run() {
  const D = siteDefaults();

  await check("default inputs give the independently computed hero value", async () => {
    const page = await open("/");
    eq(await page.inputValue("#age"), String(D.age), "age field");
    eq(await page.inputValue("#endAge"), String(D.to), "end age field");
    eq(await page.inputValue("#monthly"), String(D.m), "monthly field");
    eq(await page.inputValue("#rate"), String(D.rate), "rate slider");
    const s = await expectResults(page, D, "defaults");
    eq(s.hero, "$67,800", "hero for $100/mo, 21 vs 26, to 65 at 6%");
    eq(await text(page, "#heroLabel"), `Waiting ${D.wait} years could cost you about`, "hero label");
    eq(await page.$eval('#delayChips [data-value="5"]', (b) => b.getAttribute("aria-pressed")), "true", "5-year chip pressed");
    eq(s.series, 2, "legend series");
    eq(await page.$$eval("#chart svg path.line", (p) => p.length), 2, "chart lines");
    eq(await page.$$eval("#table thead th", (t) => t.length), 3, "table columns");
    await close(page);
  });

  await check("changing each input updates the results", async () => {
    const page = await open("/");
    let o = { ...D }, prev = (await readState(page)).hero;
    const step = async (label, act, change) => {
      await act();
      o = { ...o, ...change };
      const s = await expectResults(page, o, label);
      assert(s.hero !== prev, `${label}: hero didn't change (${s.hero})`);
      prev = s.hero;
    };
    await step("age field", () => page.fill("#age", "25"), { age: 25 });
    await step("end age field", () => page.fill("#endAge", "70"), { to: 70 });
    await step("monthly field", () => page.fill("#monthly", "175"), { m: 175 });
    await step("$250 chip", () => page.click('#monthlyChips [data-value="250"]'), { m: 250 });
    eq(await page.inputValue("#monthly"), "250", "monthly field follows the chip");
    await step("3-year chip", () => page.click('#delayChips [data-value="3"]'), { wait: 3 });
    eq(await text(page, "#heroLabel"), "Waiting 3 years could cost you about", "hero label after wait chip");
    await step("8% chip", () => page.click('#rateChips [data-value="8"]'), { rate: 8 });
    eq(await text(page, "#rateOut"), "8%", "rate output");
    await step("rate slider", () => setRange(page, "#rate", 4.5), { rate: 4.5 });
    eq(await text(page, "#rateOut"), "4.5%", "rate output after slider");
    eq(await page.getAttribute("#rate", "aria-valuetext"), "4.5% a year", "slider aria-valuetext");
    eq(await page.$eval('#rateChips [data-value="8"]', (b) => b.getAttribute("aria-pressed")), "false", "8% chip released");
    await close(page);
  });

  await check("invalid inputs show an error instead of updated results", async () => {
    const page = await open("/");
    const good = await readState(page);
    const cases = [
      ["#age", "5", /age between 16 and 80/],
      ["#age", "", /age between 16 and 80/],
      ["#monthly", "0", /monthly amount/],
      ["#monthly", "200000", /monthly amount/],
      ["#endAge", "24", /end age has to be after/],
      ["#endAge", "101", /100 or less/],
    ];
    for (const [sel, value, msg] of cases) {
      await page.fill(sel, value);
      const s = await readState(page);
      assert(s.errorShown && msg.test(s.error), `${sel}=${JSON.stringify(value)}: error was ${JSON.stringify(s.error)}`);
      eq(s.opacity, "0.45", `${sel}=${value}: stale results are dimmed`);
      eq(s.hero, good.hero, `${sel}=${value}: hero isn't recomputed from bad input`);
      eq(s.search, good.search, `${sel}=${value}: URL isn't rewritten with bad input`);
      await page.fill(sel, sel === "#age" ? String(D.age) : sel === "#monthly" ? String(D.m) : String(D.to));
      await expectResults(page, D, `after fixing ${sel}`);
    }
    await page.check("#shockOn");
    await page.fill("#shockAge", "99");
    const s = await readState(page);
    assert(/drop has to happen between/.test(s.error), `crash age 99: error was ${JSON.stringify(s.error)}`);
    await close(page);
  });

  await check("URL params round-trip", async () => {
    const o = { age: 25, m: 250, wait: 3, rate: 8, to: 70, drop: 40, at: 50 };
    const qs = `?age=${o.age}&m=${o.m}&wait=${o.wait}&rate=${o.rate}&to=${o.to}&crash=1&drop=${o.drop}&at=${o.at}`;
    const page = await open("/" + qs);
    await expectResults(page, o, "from URL");
    eq(await page.inputValue("#age"), "25", "age field");
    eq(await page.inputValue("#endAge"), "70", "end age field");
    eq(await page.inputValue("#shockAge"), "50", "crash age field");
    eq(await page.isChecked("#shockOn"), true, "crash toggle");
    for (const [chips, v] of [["monthlyChips", 250], ["delayChips", 3], ["rateChips", 8]]) {
      eq(await page.$eval(`#${chips} [data-value="${v}"]`, (b) => b.getAttribute("aria-pressed")), "true", `${chips} ${v} pressed`);
    }
    const params = new URLSearchParams(await page.evaluate(() => location.search));
    for (const [k, v] of Object.entries({ age: 25, m: 250, wait: 3, rate: 8, to: 70, crash: 1, drop: 40, at: 50 })) {
      eq(params.get(k), String(v), `URL keeps ${k}`);
    }
    // Change things, then open the written URL in a fresh page: same numbers.
    await page.fill("#monthly", "321");
    await page.click('#delayChips [data-value="10"]');
    const written = await page.evaluate(() => location.search), before = await readState(page);
    const again = await open("/" + written);
    const after = await readState(again);
    eq(after.hero, before.hero, "hero after reopening the shared URL");
    eq(after.now, before.now, "start-now after reopening");
    eq(await again.inputValue("#monthly"), "321", "monthly after reopening");
    await close(again);
    // Turning the crash off removes its params.
    await page.uncheck("#shockOn");
    const off = new URLSearchParams(await page.evaluate(() => location.search));
    assert(!off.has("crash") && !off.has("at") && !off.has("drop"), "crash params removed: " + off);
    await close(page);
  });

  await check("bad or fractional URL params don't break the page (regression)", async () => {
    for (const qs of ["?age=21.5&crash=1", "?crash=1&at=40.5", "?wait=2.5", "?age=abc&m=&rate=NaN", "?crash=1&at=10"]) {
      const before = problems.length;
      const page = await open("/" + qs);
      eq(problems.length, before, `${qs}: no console or page errors (${problems.slice(before).join("; ")})`);
      assert(await page.$("#chart svg"), `${qs}: chart rendered`);
      const s = await readState(page);
      eq(s.error, "", `${qs}: no validation error`);
      await close(page);
    }
    const page = await open("/?rate=13");
    eq(await page.inputValue("#rate"), "12", "rate slider at its max");
    eq(await text(page, "#rateOut"), "12%", "rate shown matches the slider (was 13% vs slider 12)");
    await expectResults(page, { ...D, rate: 12 }, "rate=13 clamped");
    await close(page);
  });

  await check("crash toggle shows the third series and its text", async () => {
    const page = await open("/");
    assert(await page.isHidden("#shockControls"), "crash controls hidden at first");
    eq(await text(page, "#shockText"), "", "no crash text at first");
    await page.check("#shockOn");
    assert(await page.isVisible("#shockControls"), "crash controls shown");
    const s = await readState(page);
    eq(s.series, 3, "legend series with crash");
    eq(await page.$$eval("#chart svg path.line.c3", (p) => p.length), 1, "third chart line");
    eq(await page.$$eval("#table thead th", (t) => t.length), 4, "table columns with crash");
    eq(await text(page, "#shockDropOut"), `${D.drop}%`, "drop output");
    const e = expected({ ...D }), t = await text(page, "#shockText");
    for (const part of [`A ${D.drop}% drop at ${D.at}`, usd(e.before), usd(e.after), usd(e.stressed), usd(e.now)]) {
      assert(t.includes(part), `crash text should include ${part}: ${t}`);
    }
    await setRange(page, "#shockDrop", 60);
    const e60 = expected({ ...D, drop: 60 });
    assert((await text(page, "#shockText")).includes(usd(e60.stressed)), "crash text follows the drop slider");
    eq(await page.getAttribute("#shockDrop", "aria-valuetext"), "60% drop", "drop slider aria-valuetext");
    // Crash in the very last year: no recovery time, and the text says so.
    await page.fill("#shockAge", String(D.to));
    const last = await text(page, "#shockText");
    assert(/no time left to recover/.test(last), "last-year crash text: " + last);
    assert(last.includes(usd(expected({ ...D, drop: 60, at: D.to }).stressed)), "last-year crash final value: " + last);
    await page.uncheck("#shockOn");
    eq((await readState(page)).series, 2, "series after turning the crash off");
    eq(await text(page, "#shockText"), "", "crash text cleared");
    await close(page);
  });

  await check("typing a crash age isn't overwritten mid-typing (regression)", async () => {
    const page = await open("/?crash=1");
    await page.fill("#shockAge", "");
    await page.locator("#shockAge").pressSequentially("45");
    eq(await page.inputValue("#shockAge"), "45", "crash age after typing 4, 5");
    await page.fill("#endAge", "");
    await page.locator("#endAge").pressSequentially("70");
    eq(await page.inputValue("#shockAge"), "45", "crash age kept while retyping the end age");
    await expectResults(page, { ...D, to: 70, at: 45 }, "after typing");
    // Moving the age range past the crash still pulls the crash back inside it.
    await page.fill("#age", "50");
    const at = Number(await page.inputValue("#shockAge"));
    assert(at > 50 && at <= 70, "crash age moved inside 50-70, got " + at);
    await close(page);
  });

  await check("chart: keyboard focus and arrow keys show the tooltip", async () => {
    const page = await open("/");
    await page.focus("#shareBtn");
    await page.keyboard.press("Tab");
    eq(await page.evaluate(() => document.activeElement && document.activeElement.tagName.toLowerCase()), "svg", "Tab after Share reaches the chart");
    const ring = await page.$eval("#chart svg", (el) => { const c = getComputedStyle(el); return c.outlineStyle + " " + c.outlineWidth; });
    eq(ring, "solid 3px", "chart focus ring");
    const tip = async () => page.$eval(".tooltip", (el) => ({ hidden: el.classList.contains("hidden"), head: (el.querySelector(".t-head") || {}).textContent, rows: el.querySelectorAll(".t-row").length }));
    let t = await tip();
    assert(!t.hidden, "tooltip shown on focus");
    eq(t.head, `Age ${D.to}`, "tooltip starts at the end age");
    eq(t.rows, 2, "tooltip rows");
    await page.keyboard.press("ArrowLeft");
    eq((await tip()).head, `Age ${D.to - 1}`, "ArrowLeft");
    await page.keyboard.press("ArrowDown");
    eq((await tip()).head, `Age ${D.to - 6}`, "ArrowDown moves 5 years back");
    await page.keyboard.press("Home");
    eq((await tip()).head, `Age ${D.age}`, "Home");
    await page.keyboard.press("ArrowLeft");
    eq((await tip()).head, `Age ${D.age}`, "ArrowLeft stops at the start");
    await page.keyboard.press("ArrowRight");
    eq((await tip()).head, `Age ${D.age + 1}`, "ArrowRight");
    const readout = await text(page, "#chartReadout");
    assert(readout.startsWith(`Age ${D.age + 1}:`) && readout.includes("$"), "screen-reader readout: " + readout);
    await page.keyboard.press("End");
    eq((await tip()).head, `Age ${D.to}`, "End");
    const e = expected(D);
    assert((await text(page, ".tooltip")).includes(usd(e.now)), "tooltip shows the start-now balance at the end age");
    await page.keyboard.press("Escape");
    assert((await tip()).hidden, "Escape hides the tooltip");
    // Mouse hover works too.
    const box = await page.$eval("#chart svg", (el) => { const r = el.getBoundingClientRect(); return { x: r.x, y: r.y, w: r.width, h: r.height }; });
    await page.mouse.move(box.x + box.w / 2, box.y + box.h / 2);
    assert(!(await tip()).hidden, "tooltip on hover");
    await close(page);
  });

  await check("facts load from data/facts.json and sources render", async () => {
    let factsStatus = null;
    const facts = JSON.parse(fs.readFileSync(path.join(SITE, "data", "facts.json"), "utf8")).facts;
    const page = await open("/", { route: async (p) => p.on("response", (r) => { if (r.url().endsWith("/data/facts.json")) factsStatus = r.status(); }) });
    eq(factsStatus, 200, "data/facts.json status");
    const used = await page.$$eval("[data-needs]", (els) => els.map((e) => e.dataset.needs));
    const shown = await page.$$eval(".needs-fact.ok", (els) => els.map((e) => e.dataset.needs));
    const known = new Set(facts.map((f) => f.key));
    eq(JSON.stringify(shown), JSON.stringify(used.filter((k) => known.has(k))), "every fact on file is shown");
    for (const f of facts.filter((f) => used.includes(f.key))) {
      eq(await text(page, `[data-fact="${f.key}"]`), f.display, `${f.key} value`);
      eq(await text(page, `[data-fact-asof="${f.key}"]`), `${f.source_name}, ${f.as_of}`, `${f.key} date and source`);
      assert(await page.isVisible(`[data-needs="${f.key}"]`), `${f.key} visible`);
    }
    const links = await page.$$eval("#factSources a", (as) => as.map((a) => ({ href: a.href, text: a.textContent })));
    const urls = [...new Set(facts.filter((f) => used.includes(f.key)).map((f) => f.sources[0]))];
    eq(JSON.stringify(links.map((l) => l.href)), JSON.stringify(urls), "one source link per unique URL");
    assert((await text(page, "#factSources")).startsWith("Sources: "), "sources label");
    await close(page);
  });

  await check("facts: missing file hides the lines; script URLs are never linked", async () => {
    const missing = await open("/", { route: (p) => p.route("**/data/facts.json", (r) => r.fulfill({ status: 200, contentType: "application/json", body: '{"facts": []}' })) });
    eq(await missing.$$eval(".needs-fact", (els) => els.filter((e) => getComputedStyle(e).display !== "none").length), 0, "no empty fact lines");
    eq(await text(missing, "#factSources"), "", "no sources");
    await close(missing);
    const evil = { facts: [{ key: "cc_apr_assessed", display: "22%", as_of: "x", source_name: "Evil", sources: ["javascript:alert(1)"] }] };
    const page = await open("/", { route: (p) => p.route("**/data/facts.json", (r) => r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(evil) })) });
    eq(await page.$$eval("#factSources a", (as) => as.length), 0, "javascript: source not linked");
    await close(page);
  });

  await check("learn/ and rules.html load with the shared styles", async () => {
    for (const [url, h1] of [["/learn/", "Learn"], ["/rules.html", "Our rules"]]) {
      const page = await open(url);
      eq((await text(page, "h1")).trim(), h1, `${url} heading`);
      eq(await page.evaluate(() => getComputedStyle(document.body).backgroundColor), "rgb(244, 243, 239)", `${url} stylesheet applied`);
      assert((await text(page, "footer")).includes("Education, not advice"), `${url} disclaimer`);
      eq(await page.$eval('nav a[aria-current="page"]', (a) => a.textContent), h1 === "Learn" ? "Learn" : "Our rules", `${url} current nav item`);
      await close(page);
    }
  });

  await check("internal links and assets aren't broken", async () => {
    const pages = ["/", "/rules.html", "/learn/"], seen = new Set(), bad = [];
    for (let i = 0; i < pages.length; i++) {
      const page = await open(pages[i]);
      const refs = await page.evaluate(() => [
        ...[...document.querySelectorAll("a[href]")].map((a) => a.href),
        ...[...document.querySelectorAll("link[href], script[src], img[src]")].map((e) => e.href || e.src),
      ]);
      for (const ref of refs) {
        const u = new URL(ref);
        if (u.origin !== base) continue;
        const key = u.pathname;
        if (seen.has(key)) continue;
        seen.add(key);
        const r = await page.request.get(base + key);
        if (!r.ok()) bad.push(`${pages[i]} -> ${key} (${r.status()})`);
        // Lesson pages linked from learn/ get crawled too.
        if (r.ok() && /^\/learn\/[^/]+\.html$/.test(key) && !pages.includes(key)) pages.push(key);
      }
      await close(page);
    }
    assert(seen.size >= 6, "found internal links: " + [...seen].join(", "));
    eq(bad.join(", "), "", "broken internal links");
  });

  await check("no horizontal overflow at 320, 375, 768 and 1280 px", async () => {
    const urls = ["/", "/?crash=1", "/?age=16&to=100&m=100000&rate=12&wait=10&crash=1", "/rules.html", "/learn/"];
    const bad = [];
    for (const width of WIDTHS) {
      for (const url of urls) {
        const page = await open(url, { width });
        if (url.includes("crash")) await page.click("summary"); // open the table view too
        let o = await overflow(page);
        if (o > 0) bad.push(`${url} @${width}: ${o}px`);
        if (url.startsWith("/?")) {
          await page.focus("#chart svg");
          await page.keyboard.press("Home");
          o = await overflow(page);
          if (o > 0) bad.push(`${url} @${width} with tooltip: ${o}px`);
        }
        await close(page);
      }
    }
    eq(bad.join("; "), "", "pages wider than the viewport");
  });

  await check("money values stay inside their tiles on small phones (regression)", async () => {
    const bad = [];
    for (const width of [320, 375]) {
      for (const url of ["/", "/?m=250&rate=8", "/?m=1000&rate=8", "/?m=20000&rate=8"]) {
        const page = await open(url, { width });
        const spills = await page.evaluate(() => [...document.querySelectorAll(".tile .v, #heroValue")].map((el) => {
          const box = el.closest(".tile, .card").getBoundingClientRect(), range = document.createRange();
          range.selectNodeContents(el);
          const t = range.getBoundingClientRect();
          return t.right > box.right + 0.5 ? `${el.id} ${el.textContent} by ${Math.round(t.right - box.right)}px` : null;
        }).filter(Boolean));
        if (spills.length) bad.push(`${url} @${width}: ${spills.join(", ")}`);
        await close(page);
      }
    }
    eq(bad.join("; "), "", "values spilling out of their box");
  });

  await check("dark mode renders with the dark tokens", async () => {
    for (const url of ["/", "/rules.html", "/learn/"]) {
      const page = await open(url, { colorScheme: "dark" });
      const c = await page.evaluate(() => ({
        bg: getComputedStyle(document.body).backgroundColor,
        fg: getComputedStyle(document.body).color,
        card: getComputedStyle(document.querySelector(".card")).backgroundColor,
        line: document.querySelector("#chart path.c1") && getComputedStyle(document.querySelector("#chart path.c1")).stroke,
        field: document.querySelector("#age") && getComputedStyle(document.querySelector("#age")).borderTopColor,
      }));
      eq(c.bg, "rgb(13, 13, 13)", `${url} dark background`);
      eq(c.fg, "rgb(240, 239, 236)", `${url} dark text`);
      eq(c.card, "rgb(26, 26, 25)", `${url} dark cards`);
      if (url === "/") {
        eq(c.line, "rgb(57, 135, 229)", "dark chart series 1");
        eq(c.field, "rgb(112, 111, 105)", "dark input border");
      }
      await close(page);
    }
    // data-theme="light" wins over a dark system setting.
    const page = await open("/", { colorScheme: "dark" });
    await page.evaluate(() => document.documentElement.setAttribute("data-theme", "light"));
    eq(await page.evaluate(() => getComputedStyle(document.body).backgroundColor), "rgb(244, 243, 239)", "data-theme=light override");
    await close(page);
  });

  await check("accessibility: every field has a label; live regions are scoped", async () => {
    const page = await open("/?crash=1");
    const unlabeled = await page.evaluate(() => [...document.querySelectorAll("input:not([type=hidden]), select, textarea")].filter((el) => {
      if (el.getAttribute("aria-label") || el.getAttribute("aria-labelledby") || el.closest("label")) return false;
      return !(el.id && document.querySelector(`label[for="${el.id}"]`));
    }).map((el) => el.id || el.name));
    eq(unlabeled.join(", "), "", "fields without a label");
    const live = await page.evaluate(() => [...document.querySelectorAll("[aria-live], [role=alert], [role=status]")].map((e) => e.id));
    for (const id of ["summary", "errors", "shareMsg", "chartReadout", "shockText", "signupMsg"]) assert(live.includes(id), `#${id} should be announced`);
    eq(await page.getAttribute("#results", "aria-live"), null, "#results itself isn't one giant live region");
    eq(await page.getAttribute("#monthlyChips", "role"), "group", "labelled chip group has a role");
    eq(await page.$$eval("main", (m) => m.length), 1, "one main landmark");
    eq(await page.getAttribute("html", "lang"), "en", "page language");
    await close(page);
  });

  await check("accessibility: every keyboard stop has a visible focus ring", async () => {
    const page = await open("/?crash=1");
    await page.click("summary"); // include the table toggle in its open state
    const stops = [], missing = [];
    for (let i = 0; i < 60; i++) {
      await page.keyboard.press("Tab");
      const s = await page.evaluate(() => {
        const el = document.activeElement;
        if (!el || el === document.body) return null;
        const c = getComputedStyle(el);
        return { id: el.tagName.toLowerCase() + (el.id ? "#" + el.id : "") + (el.textContent ? ` "${el.textContent.trim().slice(0, 16)}"` : ""),
                 ring: c.outlineStyle !== "none" && parseFloat(c.outlineWidth) >= 2 };
      });
      if (!s) continue;
      if (stops.includes(s.id)) break;
      stops.push(s.id);
      if (!s.ring) missing.push(s.id);
    }
    assert(stops.length >= 20, "reached keyboard stops: " + stops.length);
    eq(missing.join(", "), "", "focused elements without a visible ring");
    await close(page);
  });

  await check("accessibility: tap targets on a phone are at least 24x24 px", async () => {
    const page = await open("/?crash=1", { width: 375 });
    const r = await page.evaluate(() => [...document.querySelectorAll("button, input[type=number], input[type=email], summary, label.toggle, .top nav a, a.btn")]
      .filter((el) => el.offsetParent !== null)
      .map((el) => { const b = el.getBoundingClientRect(); return { id: el.id || el.textContent.trim().slice(0, 16), w: b.width, h: b.height }; }));
    const small = r.filter((t) => Math.round(t.w) < 24 || Math.round(t.h) < 24).map((t) => `${t.id} ${Math.round(t.w)}x${Math.round(t.h)}`);
    eq(small.join(", "), "", "targets under 24x24 (WCAG 2.5.8)");
    const under44 = r.filter((t) => Math.round(t.h) < 44).map((t) => `${t.id} ${Math.round(t.h)}px`);
    if (under44.length) console.log("       note: under the 44px comfort size: " + under44.join(", "));
    await close(page);
  });

  await check("email sign-up explains when it isn't connected", async () => {
    const page = await open("/");
    await page.fill('#signupForm input[type="email"]', "test@example.com");
    await page.click('#signupForm button[type="submit"]');
    assert(await page.isVisible("#signupMsg"), "message shown");
    assert(/aren't connected yet/.test(await text(page, "#signupMsg")), "explains the missing endpoint");
    await close(page);
  });

  await check("no console errors, page errors or failed requests anywhere", async () => {
    eq(problems.join("\n"), "", "problems seen while testing");
  });
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
