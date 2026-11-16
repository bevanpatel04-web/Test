// Crash simulator (app/crash-sim.html). The member lives through a drop with a pretend portfolio,
// picks hold / sell at the bottom / sell and buy back a year later, and sees all three over time:
// SVG chart with hover and keyboard, a table view and plain-language result text.
//
// Scenarios: the hypothetical ones in learn.js, plus any verified, sourced series in
// data/history.json (format in learn.js validHistory). Until licensing is checked that file is empty.
(function () {
  "use strict";
  var A = window.PMApp, L = A.L, el = A.el, PM = window.PatientMoney;
  var SVG = "http://www.w3.org/2000/svg";
  function $(id) { return document.getElementById(id); }

  var SLOT = { hold: 1, "sell-bottom": 2, "sell-buyback": 3 };
  var state = { scenarios: L.SCENARIOS.slice(), id: L.SCENARIOS[0].id, amount: 10000, pick: null };
  var last = null; // last chart model, for resize

  function scenario() { return state.scenarios.filter(function (s) { return s.id === state.id; })[0] || state.scenarios[0]; }
  function choiceLabel(id) { return L.CHOICES.filter(function (c) { return c.id === id; })[0].label; }
  function span(months) {
    var y = Math.floor(months / 12), m = months % 12, out = [];
    if (y) out.push(A.plural(y, "year"));
    if (m) out.push(A.plural(m, "month"));
    return out.join(" ") || "0 months";
  }
  function when(s, m) { return s.dates ? s.dates[m] : (m === 0 ? "Start" : "Month " + m); }
  function signed(n) { return (n >= 0 ? "+" : "−") + PM.money(Math.abs(n)); }
  function pct(x) { return Math.round(x * 100) + "%"; }

  // ---- Controls ----------------------------------------------------------------------------------------
  function renderScenarioChips() {
    var box = A.clear($("scenarioChips"));
    state.scenarios.forEach(function (s) {
      var b = el("button", { type: "button", class: "chip", "data-id": s.id, "aria-pressed": String(s.id === state.id) },
        [s.name, " ", el("small", { text: s.label })]);
      b.addEventListener("click", function () { state.id = s.id; state.pick = null; update(); });
      box.appendChild(b);
    });
  }

  function renderChoices() {
    var box = A.clear($("choices"));
    L.CHOICES.forEach(function (c) {
      var b = el("button", { type: "button", "data-choice": c.id, "aria-pressed": String(state.pick === c.id) },
        [el("span", { class: "key s" + SLOT[c.id], "aria-hidden": "true" }), c.label]);
      b.addEventListener("click", function () { state.pick = c.id; update(); });
      box.appendChild(b);
    });
  }

  // ---- Main update -------------------------------------------------------------------------------------
  function update() {
    var s = scenario(), path = L.pathFor(s);
    Array.prototype.forEach.call($("scenarioChips").querySelectorAll("button"), function (b) {
      b.setAttribute("aria-pressed", String(b.getAttribute("data-id") === s.id));
    });
    Array.prototype.forEach.call($("choices").querySelectorAll("button"), function (b) {
      b.setAttribute("aria-pressed", String(b.getAttribute("data-choice") === state.pick));
    });
    $("kindPill").textContent = s.kind === "historical"
      ? "Real index history · Past performance doesn't guarantee future results"
      : "Hypothetical scenario · Not real market history · Not a forecast";
    $("scenarioText").textContent = s.description;
    renderSource(s);

    var ok = state.amount >= 100 && state.amount <= 1000000;
    $("amountError").textContent = ok ? "" : "Pick an amount between $100 and $1,000,000.";
    $("simCard").style.opacity = ok ? "1" : "0.45";
    if (!ok) return;

    var r = L.compareChoices(path, state.amount);
    var drop = pct(r.drop);
    $("momentTitle").textContent = state.pick ? "2. What each choice would have done" : "2. The drop";
    $("momentText").textContent = (s.dates ? s.dates[r.bottom] : span(r.bottom) + " in") + ": your pretend " +
      PM.money(state.amount) + " is down " + drop + ", to " + PM.money(r.low) + ". Nobody knows if it falls further. What do you do?";

    var series = L.CHOICES.map(function (c) {
      return { id: c.id, name: c.label, slot: SLOT[c.id], values: r.results[c.id].values,
               pick: state.pick === c.id, dim: !!state.pick && state.pick !== c.id };
    });
    var model;
    if (!state.pick) {
      model = { scenario: s, months: r.months, bottom: r.bottom, upto: r.bottom,
                series: [{ id: "so-far", name: "Your pretend portfolio", slot: 1, values: r.results.hold.values }],
                events: [{ m: r.bottom, label: "Bottom", anchor: "end" }] };
    } else {
      var shown = series.slice().sort(function (a, b) { return (a.pick ? 1 : 0) - (b.pick ? 1 : 0); }); // pick drawn on top
      model = { scenario: s, months: r.months, bottom: r.bottom, upto: r.months, series: shown, order: series,
                events: [{ m: r.bottom, label: "Bottom", anchor: "end" }].concat(r.buyAt !== null ? [{ m: r.buyAt, label: "Buy back", anchor: "start" }] : []) };
    }
    renderLegend(model);
    renderChart(model);
    renderTable(model, r);
    renderResult(s, r);
  }

  function renderSource(s) {
    var box = A.clear($("scenarioSource"));
    if (s.kind !== "historical") {
      box.textContent = "Made-up numbers for practice, not real index history. Real crash data is coming once its licensing is checked.";
      return;
    }
    var url = A.safeHttpUrl(s.source.url);
    A.append(box, ["Source: ", url ? el("a", { href: url, rel: "noopener", text: s.source.name }) : s.source.name,
      ", retrieved " + s.source.retrieved + ". " + s.source.license]);
  }

  function renderResult(s, r) {
    var box = A.clear($("result")), tiles = A.clear($("tiles"));
    $("tiles").classList.toggle("hidden", !state.pick);
    $("againRow").classList.toggle("hidden", !state.pick);
    if (!state.pick) return;
    var res = r.results, hold = res.hold.final, sb = res["sell-bottom"].final, bb = res["sell-buyback"].final;
    var end = "by the end (" + span(r.months) + ")";
    var lines = [];
    if (state.pick === "hold") {
      lines.push("You held. Your pretend " + PM.money(state.amount) + " fell as low as " + PM.money(r.low) +
        (r.backToStart !== null ? ", then took " + span(r.backToStart - r.bottom) + " from the bottom to get back to " + PM.money(state.amount) + "." : "."));
      lines.push("Holding meant watching it fall without knowing when the drop would end.");
    } else if (state.pick === "sell-bottom") {
      lines.push("You sold at the bottom and kept " + PM.money(sb) + " in cash. Holding would have been worth " + PM.money(hold) + " " + end +
        ", which is " + PM.money(hold - sb) + " more.");
      lines.push("Selling turned a drop on paper into a loss you kept.");
    } else {
      lines.push(res["sell-buyback"].buyAt === null
        ? "You sold at the bottom. The data ends before a year had passed, so the money stayed in cash: " + PM.money(bb) + "."
        : "You sold at the bottom, then bought back a year later, after prices had already climbed " + pct(r.riseBeforeBuyback) +
          " from the low. You ended with " + PM.money(bb) + ", " + PM.money(Math.abs(hold - bb)) + (bb <= hold ? " less" : " more") + " than holding.");
      lines.push("The gap is the climb you missed while waiting in cash.");
    }
    lines.push(s.kind === "historical"
      ? "This is one past period. Other crashes went differently, and past results don't guarantee future ones."
      : "This is a made-up example. A real crash can be deeper or last longer, and an investment that falls doesn't have to come back.");
    lines.forEach(function (t, i) { box.appendChild(el("p", { class: i === 0 ? "moment" : "", text: t })); });

    L.CHOICES.forEach(function (c) {
      var v = res[c.id].final, diff = v - hold, pick = state.pick === c.id;
      tiles.appendChild(el("div", { class: "tile" + (pick ? " pick" : ""), "data-choice": c.id }, [
        pick ? el("div", { class: "tag", text: "Your pick" }) : null,
        el("div", { class: "k" }, [el("span", { class: "key s" + SLOT[c.id] }), c.label]),
        el("div", { class: "v", text: PM.money(v) }),
        el("div", { class: "sub", text: c.id === "hold" ? "at the end" : signed(diff) + " vs holding" })
      ]));
    });
  }

  // ---- Legend and table -------------------------------------------------------------------------------
  function renderLegend(model) {
    var box = A.clear($("legend"));
    if (model.series.length < 2) return; // one line: the heading names it
    (model.order || model.series).forEach(function (s) {
      box.appendChild(el("span", {}, [el("span", { class: "key s" + s.slot }), s.name + (s.pick ? " (your pick)" : "")]));
    });
  }

  function renderTable(model, r) {
    var t = A.clear($("table")), s = model.scenario, cols = model.order || model.series;
    var head = t.createTHead().insertRow();
    [s.dates ? "Month" : "When"].concat(cols.map(function (c) { return c.name + (c.pick ? " (your pick)" : ""); })).forEach(function (h, i) {
      head.appendChild(el("th", { scope: "col", class: i && cols[i - 1].pick ? "pick" : null, text: h }));
    });
    var rows = {};
    for (var m = 0; m <= model.upto; m += 12) rows[m] = true;
    rows[model.bottom] = true; rows[model.upto] = true;
    if (r.buyAt !== null && model.upto >= r.buyAt) rows[r.buyAt] = true;
    var body = t.createTBody();
    Object.keys(rows).map(Number).sort(function (a, b) { return a - b; }).forEach(function (m) {
      var row = body.insertRow();
      var note = m === model.bottom ? " (bottom)" : m === r.buyAt && model.upto >= r.buyAt ? " (buy back)" : "";
      row.appendChild(el("th", { scope: "row", text: when(s, m) + note }));
      cols.forEach(function (c) { row.appendChild(el("td", { class: c.pick ? "pick" : null, text: PM.money(c.values[m]) })); });
    });
  }

  // ---- Chart ------------------------------------------------------------------------------------------
  function svgEl(name, attrs) {
    var n = document.createElementNS(SVG, name);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    return n;
  }

  function renderChart(model) {
    last = model;
    var box = $("chart"), s = model.scenario;
    var W = Math.max(280, Math.round(box.clientWidth || 640)), H = 280;
    var mg = { t: 28, r: 58, b: 28, l: 52 };
    var N = model.months, upto = model.upto;
    var maxY = 0;
    model.series.forEach(function (sr) { for (var i = 0; i <= upto; i++) maxY = Math.max(maxY, sr.values[i]); });
    var ticks = PM.niceTicks(maxY, 4), yMax = ticks[ticks.length - 1];
    function x(m) { return mg.l + m / N * (W - mg.l - mg.r); }
    function y(v) { return mg.t + (1 - v / yMax) * (H - mg.t - mg.b); }

    var desc = model.series.length > 1
      ? model.series.map(function (sr) { return sr.name + " ends at " + PM.money(sr.values[N]); }).join("; ")
      : "Your pretend portfolio falls from " + PM.money(model.series[0].values[0]) + " to " + PM.money(model.series[0].values[upto]) + " at the bottom";
    var svg = svgEl("svg", { viewBox: "0 0 " + W + " " + H, width: W, height: H, role: "img", tabindex: "0",
      "aria-label": desc + ". Use the left and right arrow keys to read each month." });

    ticks.forEach(function (t) {
      if (t > 0) svg.appendChild(svgEl("line", { "class": "grid", x1: mg.l, x2: W - mg.r, y1: y(t), y2: y(t) }));
      var lab = svgEl("text", { "class": "tick", x: mg.l - 8, y: y(t) + 4, "text-anchor": "end" });
      lab.textContent = PM.compactMoney(t);
      svg.appendChild(lab);
    });
    svg.appendChild(svgEl("line", { "class": "baseline", x1: mg.l, x2: W - mg.r, y1: y(0), y2: y(0) }));

    // X axis: years (or dates for a real series). Thin out labels when space is short.
    var years = Math.floor(N / 12), per = (W - mg.l - mg.r) / Math.max(1, N / 12), stepY = per < 34 ? 2 : 1;
    var x0 = svgEl("text", { "class": "tick", x: x(0), y: H - 8, "text-anchor": "start" });
    x0.textContent = s.dates ? s.dates[0].slice(0, 4) : "Start";
    svg.appendChild(x0);
    for (var yr = stepY; yr <= years; yr += stepY) {
      var m = yr * 12;
      if (x(m) - x(0) < 44 || (m !== N && x(N) - x(m) < 30)) continue;
      var tx = svgEl("text", { "class": "tick", x: x(m), y: H - 8, "text-anchor": m === N ? "end" : "middle" });
      tx.textContent = s.dates ? s.dates[m].slice(0, 4) : (m === N || yr === years && x(N) - x(m) < 60 ? "Year " + yr : String(yr));
      svg.appendChild(tx);
    }

    if (upto < N) { // the unknown future, before the member decides
      svg.appendChild(svgEl("rect", { "class": "future", x: x(upto), y: mg.t, width: x(N) - x(upto), height: y(0) - mg.t }));
      var q = svgEl("text", { "class": "event-label", x: (x(upto) + x(N)) / 2, y: (mg.t + y(0)) / 2, "text-anchor": "middle" });
      q.textContent = "What happens next?";
      svg.appendChild(q);
    }
    model.events.forEach(function (e) {
      svg.appendChild(svgEl("line", { "class": "event", x1: x(e.m), x2: x(e.m), y1: mg.t - 12, y2: y(0) }));
      var t = svgEl("text", { "class": "event-label", x: x(e.m) + (e.anchor === "end" ? -4 : 4), y: mg.t - 10, "text-anchor": e.anchor });
      t.textContent = e.label;
      svg.appendChild(t);
    });

    model.series.forEach(function (sr) {
      var d = "";
      for (var i = 0; i <= upto; i++) d += (i ? "L" : "M") + x(i).toFixed(1) + " " + y(sr.values[i]).toFixed(1) + " ";
      svg.appendChild(svgEl("path", { "class": "line c" + sr.slot + (sr.pick ? " pick" : "") + (sr.dim ? " dim" : ""), d: d }));
    });

    // End dots and selective end labels (skip one that would collide with a label already placed).
    var placed = [];
    model.series.slice().reverse().forEach(function (sr) {
      var v = sr.values[upto], ex = x(upto), ey = y(v);
      svg.appendChild(svgEl("circle", { "class": "dot f" + sr.slot, cx: ex, cy: ey, r: 4 }));
      var ly = ey + 4;
      if (placed.some(function (p) { return Math.abs(p - ly) < 14; })) return;
      placed.push(ly);
      var t = svgEl("text", { "class": "end-label", x: ex + 8, y: ly, "text-anchor": "start" });
      t.textContent = PM.compactMoney(v);
      svg.appendChild(t);
    });

    // Hover / focus: crosshair snaps to the nearest month; one tooltip lists every line.
    var cross = svgEl("line", { "class": "crosshair hidden", y1: mg.t - 8, y2: y(0) });
    var dots = svgEl("g", { "class": "hidden" });
    model.series.forEach(function (sr) { dots.appendChild(svgEl("circle", { "class": "dot f" + sr.slot, r: 4 })); });
    var overlay = svgEl("rect", { x: mg.l, y: 0, width: W - mg.l - mg.r, height: H - mg.b, fill: "transparent" });
    svg.appendChild(cross); svg.appendChild(dots); svg.appendChild(overlay);

    var tip = el("div", { class: "tooltip hidden", "aria-hidden": "true" });
    var current = upto;
    var ordered = model.order || model.series;

    function show(i, announce) {
      current = Math.max(0, Math.min(upto, i));
      var cx = x(current);
      cross.setAttribute("x1", cx); cross.setAttribute("x2", cx); cross.classList.remove("hidden");
      dots.classList.remove("hidden");
      Array.prototype.forEach.call(dots.childNodes, function (c, k) { c.setAttribute("cx", cx); c.setAttribute("cy", y(model.series[k].values[current])); });
      A.clear(tip);
      var label = when(s, current) + (current === model.bottom ? " (bottom)" : "");
      tip.appendChild(el("div", { class: "t-head", text: label }));
      ordered.forEach(function (sr) {
        tip.appendChild(el("div", { class: "t-row" }, [el("span", { class: "key s" + sr.slot }),
          el("b", { text: PM.money(sr.values[current]) }), el("span", { text: sr.name + (sr.pick ? " (your pick)" : "") })]));
      });
      tip.classList.remove("hidden");
      if (announce) {
        $("chartReadout").textContent = label + ": " + ordered.map(function (sr) { return sr.name + " " + PM.money(sr.values[current]); }).join(", ") + ".";
      }
      var scale = (svg.getBoundingClientRect().width || W) / W, px = cx * scale;
      var left = px + 12 + tip.offsetWidth > box.clientWidth ? px - 12 - tip.offsetWidth : px + 12;
      tip.style.left = Math.max(0, left) + "px";
      tip.style.top = (mg.t * scale) + "px";
    }
    function hide() { cross.classList.add("hidden"); dots.classList.add("hidden"); tip.classList.add("hidden"); }
    function indexAt(clientX) {
      var rect = svg.getBoundingClientRect(), px = (clientX - rect.left) * (W / rect.width);
      return Math.round((px - mg.l) / (W - mg.l - mg.r) * N);
    }
    overlay.addEventListener("pointermove", function (e) { show(indexAt(e.clientX)); });
    overlay.addEventListener("pointerdown", function (e) { show(indexAt(e.clientX)); });
    overlay.addEventListener("pointerleave", hide);
    svg.addEventListener("focus", function () { show(current, true); });
    svg.addEventListener("blur", hide);
    svg.addEventListener("keydown", function (e) {
      var moves = { ArrowLeft: -1, ArrowRight: 1, ArrowDown: -12, ArrowUp: 12, PageDown: -12, PageUp: 12 };
      if (e.key in moves) { e.preventDefault(); show(current + moves[e.key], true); }
      else if (e.key === "Home") { e.preventDefault(); show(0, true); }
      else if (e.key === "End") { e.preventDefault(); show(upto, true); }
      else if (e.key === "Escape") hide();
    });

    A.clear(box);
    box.appendChild(svg);
    box.appendChild(tip);
  }

  var resizeTimer;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () { if (last) renderChart(last); }, 120);
  });

  // ---- Wire up -------------------------------------------------------------------------------------------
  $("amount").value = state.amount;
  $("amount").addEventListener("input", function () {
    var v = this.value.trim() === "" ? NaN : Number(this.value);
    state.amount = isFinite(v) ? v : NaN;
    update();
  });
  $("againBtn").addEventListener("click", function () {
    state.pick = null;
    update();
    var first = $("choices").querySelector("button");
    if (first) first.focus();
  });
  var from = new URLSearchParams(location.search).get("from");
  if (L.isSlug(from)) {
    $("fromLesson").querySelector("a").setAttribute("href", A.lessonHref(from));
    $("fromLesson").classList.remove("hidden");
  }
  if (!A.loadProgress().member) $("memberNote").classList.remove("hidden");

  renderScenarioChips();
  renderChoices();
  update();

  // Verified historical series, when there are any, join the list after the made-up ones.
  fetch("data/history.json", { cache: "no-cache" })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (doc) {
      var real = L.validHistory(doc);
      if (!real.length) return;
      state.scenarios = L.SCENARIOS.concat(real);
      renderScenarioChips();
      update();
    })
    .catch(function () { /* no history yet: hypothetical scenarios only */ });
})();
