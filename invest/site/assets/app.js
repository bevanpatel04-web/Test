// Patient Money page logic: inputs, results, chart (SVG with hover + keyboard), table view,
// verified facts (data/facts.json, written by `python -m invest build-site`) and email sign-up.
(function () {
  "use strict";
  var PM = window.PatientMoney;
  var cfg = window.SITE_CONFIG || {};
  var d = cfg.defaults || {};
  var SVG = "http://www.w3.org/2000/svg";
  function $(id) { return document.getElementById(id); }

  // ---- State (URL params let people share their numbers) ----------------------------------
  var q = new URLSearchParams(location.search);
  function param(key, fallback) { var v = parseFloat(q.get(key)); return isFinite(v) ? v : fallback; }
  // Ages and the wait are whole years (a shared "?age=21.5&crash=1" link used to crash the page).
  function wholeParam(key, fallback) { return Math.round(param(key, fallback)); }
  var rateIn = $("rate");
  var state = {
    age: wholeParam("age", d.age || 21),
    monthly: param("m", d.monthly || 100),
    delay: wholeParam("wait", d.delay || 5),
    // Keep a linked rate inside the slider's range so the slider and the math agree.
    rate: Math.min(+rateIn.max, Math.max(+rateIn.min, param("rate", d.rate || 6))),
    endAge: wholeParam("to", d.endAge || 65),
    shockOn: q.get("crash") === "1",
    shockDrop: param("drop", d.shockDrop || 35),
    shockAge: wholeParam("at", d.shockAge || 40)
  };

  $("age").value = state.age;
  $("endAge").value = state.endAge;
  $("monthly").value = state.monthly;
  $("rate").value = state.rate;
  $("shockOn").checked = state.shockOn;
  $("shockDrop").value = state.shockDrop;
  $("shockAge").value = state.shockAge;

  // Writes a money value with optional line breaks after the commas ("$29,534,<wbr>900").
  function setMoney(el, n) {
    el.textContent = "";
    PM.money(n).split(",").forEach(function (part, i, all) {
      el.appendChild(document.createTextNode(part + (i < all.length - 1 ? "," : "")));
      if (i < all.length - 1) el.appendChild(document.createElement("wbr"));
    });
  }

  function years(n) { return n === 1 ? "1 year" : n + " years"; }
  function pct(n) { return (n % 1 === 0 ? String(n) : n.toFixed(1)) + "%"; }

  function readInputs() {
    state.age = parseInt($("age").value, 10);
    state.endAge = parseInt($("endAge").value, 10);
    state.monthly = parseFloat($("monthly").value);
    state.rate = parseFloat($("rate").value);
    state.shockOn = $("shockOn").checked;
    state.shockDrop = parseFloat($("shockDrop").value);
    state.shockAge = parseInt($("shockAge").value, 10);
  }

  // Keep the crash inside the time window when the age range changes. Skipped while the person
  // is typing the crash age itself (typing "45" used to become "43" after the first digit), and
  // while the age range is still invalid (retyping the end age used to reset the crash age).
  function clampShockAge(source) {
    if (!state.shockOn || source === "shockAge") return;
    if (PM.validate(Object.assign(calcInputs(), { shock: null })).length) return;
    if (!(state.shockAge > state.age && state.shockAge <= state.endAge)) {
      state.shockAge = Math.min(state.endAge, Math.max(state.age + 1, Math.round((state.age + state.endAge) / 2)));
      $("shockAge").value = state.shockAge;
    }
  }

  function calcInputs() {
    return {
      startAge: state.age, endAge: state.endAge, monthly: state.monthly, rate: state.rate / 100, delay: state.delay,
      shock: state.shockOn ? { age: state.shockAge, drop: state.shockDrop / 100 } : null
    };
  }

  // ---- Chips ---------------------------------------------------------------------------------
  function wireChips(id, key, after) {
    $(id).addEventListener("click", function (e) {
      var b = e.target.closest("button[data-value]");
      if (!b) return;
      state[key] = parseFloat(b.dataset.value);
      if (after) after(state[key]);
      update();
    });
  }
  wireChips("monthlyChips", "monthly", function (v) { $("monthly").value = v; });
  wireChips("delayChips", "delay");
  wireChips("rateChips", "rate", function (v) { $("rate").value = v; });
  function syncChips() {
    [["monthlyChips", "monthly"], ["delayChips", "delay"], ["rateChips", "rate"]].forEach(function (p) {
      Array.prototype.forEach.call($(p[0]).querySelectorAll("button[data-value]"), function (b) {
        b.setAttribute("aria-pressed", String(parseFloat(b.dataset.value) === state[p[1]]));
      });
    });
  }

  // ---- Main update -----------------------------------------------------------------------------
  var lastSeries = null;

  function update(source) {
    clampShockAge(source);
    syncChips();
    $("rateOut").textContent = isFinite(state.rate) ? pct(state.rate) : "";
    $("shockDropOut").textContent = state.shockDrop + "%";
    // Screen readers announce "6%" rather than a bare "6".
    if (isFinite(state.rate)) $("rate").setAttribute("aria-valuetext", pct(state.rate) + " a year");
    $("shockDrop").setAttribute("aria-valuetext", state.shockDrop + "% drop");
    $("shockControls").classList.toggle("hidden", !state.shockOn);

    var r = PM.compare(calcInputs());
    $("errors").textContent = r.errors.join(" ");
    $("results").style.opacity = r.errors.length ? "0.45" : "1";
    if (r.errors.length) return;

    var laterAge = state.age + state.delay;
    $("heroLabel").textContent = "Waiting " + years(state.delay) + " could cost you about";
    setMoney($("heroValue"), r.costOfWaiting);
    $("heroNote").textContent = "by age " + state.endAge + ", if your money grew a hypothetical " + pct(state.rate) + " a year.";
    $("nowLabel").textContent = "Start at " + state.age;
    setMoney($("nowValue"), r.now.final);
    $("nowSub").textContent = "You put in " + PM.money(r.now.contributed);
    $("laterLabel").textContent = "Start at " + laterAge;
    setMoney($("laterValue"), r.later.final);
    $("laterSub").textContent = "You put in " + PM.money(r.later.contributed);

    var insight = "Starting at " + state.age + " instead of " + laterAge + " means putting in " + PM.money(r.extraPutIn) +
      " more of your own money, but it could leave you with " + PM.money(r.costOfWaiting) + " more.";
    var growthGap = r.costOfWaiting - r.extraPutIn;
    if (growthGap >= 1) insight += " The other " + PM.money(growthGap) + " is growth on those early years.";
    $("insight").textContent = insight;

    var series = [
      { name: "Start at " + state.age, slot: 1, points: r.now.points },
      { name: "Start at " + laterAge, slot: 2, points: r.later.points }
    ];
    if (r.stressed) {
      series.push({ name: "Start at " + state.age + ", " + state.shockDrop + "% drop at " + state.shockAge, short: "With the drop",
                    slot: 3, points: r.stressed.points });
      var s = r.stressed.shock;
      var text = "A " + state.shockDrop + "% drop at " + state.shockAge + " would take the start-now balance from about " +
        PM.money(s.before) + " to " + PM.money(s.after) + ".";
      text += state.shockAge >= state.endAge
        ? " That's the end age, so there'd be no time left to recover: you'd end at about " + PM.money(r.stressed.final) +
          " instead of " + PM.money(r.now.final) + "."
        : " If growth then picked back up at " + pct(state.rate) + " a year, you'd end at about " +
          PM.money(r.stressed.final) + " instead of " + PM.money(r.now.final) + ".";
      text += r.stressed.final >= r.later.final
        ? " In this example, starting now with the crash still ends ahead of waiting " + years(state.delay) + " with no crash (" + PM.money(r.later.final) + ")."
        : " In this example, the crash costs more than waiting " + years(state.delay) + " would have (" + PM.money(r.later.final) + ").";
      $("shockText").textContent = text;
    } else {
      $("shockText").textContent = "";
    }

    lastSeries = series;
    renderLegend(series);
    renderChart(series);
    renderTable(series);
    writeUrl();
  }

  function writeUrl() {
    var p = new URLSearchParams({ age: state.age, m: state.monthly, wait: state.delay, rate: state.rate, to: state.endAge });
    if (state.shockOn) { p.set("crash", "1"); p.set("drop", state.shockDrop); p.set("at", state.shockAge); }
    try { history.replaceState(null, "", "?" + p.toString()); } catch (e) { /* file:// or sandboxed */ }
  }

  // ---- Legend & table --------------------------------------------------------------------------
  function keySpan(slot) { var k = document.createElement("span"); k.className = "key s" + slot; return k; }

  function renderLegend(series) {
    var box = $("legend");
    box.textContent = "";
    series.forEach(function (s) {
      var item = document.createElement("span");
      item.appendChild(keySpan(s.slot));
      item.appendChild(document.createTextNode(s.name));
      box.appendChild(item);
    });
  }

  function renderTable(series) {
    var table = $("table");
    table.textContent = "";
    var head = table.createTHead().insertRow();
    ["Age"].concat(series.map(function (s) { return s.name; })).forEach(function (h) {
      var th = document.createElement("th"); th.textContent = h; head.appendChild(th);
    });
    var body = table.createTBody(), pts = series[0].points, last = pts.length - 1;
    pts.forEach(function (p, i) {
      if (i !== last && (p.age - pts[0].age) % 5 !== 0) return;
      var row = body.insertRow();
      row.insertCell().textContent = p.age;
      series.forEach(function (s) { row.insertCell().textContent = PM.money(s.points[i].balance); });
    });
  }

  // ---- Chart -----------------------------------------------------------------------------------
  function svgEl(name, attrs) {
    var n = document.createElementNS(SVG, name);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    return n;
  }

  function renderChart(series) {
    var box = $("chart");
    var W = Math.max(280, Math.round(box.clientWidth || 640)), H = 280;
    var m = { t: 24, r: 58, b: 28, l: 48 }; // right margin holds the end-value labels
    var pts0 = series[0].points, a0 = pts0[0].age, a1 = pts0[pts0.length - 1].age;
    var maxY = 0;
    series.forEach(function (s) { s.points.forEach(function (p) { if (p.balance > maxY) maxY = p.balance; }); });
    var ticks = PM.niceTicks(maxY, 4), yMax = ticks[ticks.length - 1];
    function x(age) { return m.l + (age - a0) / (a1 - a0) * (W - m.l - m.r); }
    function y(v) { return m.t + (1 - v / yMax) * (H - m.t - m.b); }

    var svg = svgEl("svg", { viewBox: "0 0 " + W + " " + H, width: W, height: H, role: "img", tabindex: "0",
      "aria-label": series.map(function (s) { return s.name + ": " + PM.money(s.points[s.points.length - 1].balance) + " at " + a1; }).join("; ") +
        ". Use the left and right arrow keys to read each age." });

    ticks.forEach(function (t) {
      if (t > 0) svg.appendChild(svgEl("line", { "class": "grid", x1: m.l, x2: W - m.r, y1: y(t), y2: y(t) }));
      var label = svgEl("text", { "class": "tick", x: m.l - 8, y: y(t) + 4, "text-anchor": "end" });
      label.textContent = PM.compactMoney(t);
      svg.appendChild(label);
    });
    svg.appendChild(svgEl("line", { "class": "baseline", x1: m.l, x2: W - m.r, y1: y(0), y2: y(0) }));

    var span = a1 - a0, step = span > 30 ? 10 : 5;
    var startLabelEnd = x(a0) + 50; // "Age 21" sits at the left end of the axis
    for (var a = Math.ceil(a0 / step) * step; a <= a1; a += step) {
      if (x(a) - 10 < startLabelEnd) continue;
      if (a !== a1 && x(a1) - x(a) < 28) continue; // leave room for the end age label
      var xt = svgEl("text", { "class": "tick", x: x(a), y: H - 8, "text-anchor": "middle" });
      xt.textContent = a; svg.appendChild(xt);
    }
    if (a1 % step !== 0) { var xe = svgEl("text", { "class": "tick", x: x(a1), y: H - 8, "text-anchor": "end" }); xe.textContent = a1; svg.appendChild(xe); }
    var xs = svgEl("text", { "class": "tick", x: x(a0), y: H - 8, "text-anchor": "start" });
    xs.textContent = "Age " + a0; svg.appendChild(xs);

    series.forEach(function (s) {
      var dPath = s.points.map(function (p, i) { return (i ? "L" : "M") + x(p.age).toFixed(1) + " " + y(p.balance).toFixed(1); }).join(" ");
      svg.appendChild(svgEl("path", { "class": "line c" + s.slot, d: dPath }));
    });

    // End dots, then selective end labels (skip a label that would collide with one already placed).
    var placed = [];
    series.forEach(function (s) {
      var p = s.points[s.points.length - 1], ex = x(p.age), ey = y(p.balance);
      svg.appendChild(svgEl("circle", { "class": "dot f" + s.slot, cx: ex, cy: ey, r: 4 }));
      var ly = ey + 4;
      if (placed.some(function (v) { return Math.abs(v - ly) < 14; })) return;
      placed.push(ly);
      var t = svgEl("text", { "class": "end-label", x: ex + 8, y: ly, "text-anchor": "start" });
      t.textContent = PM.compactMoney(p.balance);
      svg.appendChild(t);
    });

    // Hover / focus layer: crosshair snaps to the nearest age; one tooltip lists every series.
    var cross = svgEl("line", { "class": "crosshair hidden", y1: m.t - 8, y2: y(0) });
    var hoverDots = svgEl("g", { "class": "hidden" });
    series.forEach(function (s) { hoverDots.appendChild(svgEl("circle", { "class": "dot f" + s.slot, r: 4 })); });
    var overlay = svgEl("rect", { x: m.l, y: 0, width: W - m.l - m.r, height: H - m.b, fill: "transparent" });
    svg.appendChild(cross); svg.appendChild(hoverDots); svg.appendChild(overlay);

    var tip = document.createElement("div");
    tip.className = "tooltip hidden";
    tip.setAttribute("aria-hidden", "true");
    var current = pts0.length - 1;

    function show(i, announce) {
      current = Math.max(0, Math.min(pts0.length - 1, i));
      var age = pts0[current].age, cx = x(age);
      cross.setAttribute("x1", cx); cross.setAttribute("x2", cx); cross.classList.remove("hidden");
      hoverDots.classList.remove("hidden");
      Array.prototype.forEach.call(hoverDots.childNodes, function (c, k) {
        c.setAttribute("cx", cx); c.setAttribute("cy", y(series[k].points[current].balance));
      });
      tip.textContent = "";
      var head = document.createElement("div"); head.className = "t-head"; head.textContent = "Age " + age; tip.appendChild(head);
      series.forEach(function (s) {
        var row = document.createElement("div"); row.className = "t-row";
        var b = document.createElement("b"); b.textContent = PM.money(s.points[current].balance);
        var name = document.createElement("span"); name.textContent = s.short || s.name;
        row.appendChild(keySpan(s.slot)); row.appendChild(b); row.appendChild(name);
        tip.appendChild(row);
      });
      tip.classList.remove("hidden");
      if (announce) {
        $("chartReadout").textContent = "Age " + age + ": " + series.map(function (s) {
          return (s.short || s.name) + " " + PM.money(s.points[current].balance);
        }).join(", ") + ".";
      }
      var scale = (svg.getBoundingClientRect().width || W) / W, px = cx * scale;
      var left = px + 12 + tip.offsetWidth > box.clientWidth ? px - 12 - tip.offsetWidth : px + 12;
      tip.style.left = Math.max(0, left) + "px";
      tip.style.top = (m.t * scale) + "px";
    }
    function hide() { cross.classList.add("hidden"); hoverDots.classList.add("hidden"); tip.classList.add("hidden"); }
    function indexAt(clientX) {
      var rect = svg.getBoundingClientRect(), px = (clientX - rect.left) * (W / rect.width);
      return Math.round((px - m.l) / (W - m.l - m.r) * (a1 - a0));
    }
    overlay.addEventListener("pointermove", function (e) { show(indexAt(e.clientX)); });
    overlay.addEventListener("pointerdown", function (e) { show(indexAt(e.clientX)); });
    overlay.addEventListener("pointerleave", hide);
    svg.addEventListener("focus", function () { show(current, true); });
    svg.addEventListener("blur", hide);
    svg.addEventListener("keydown", function (e) {
      var moves = { ArrowLeft: -1, ArrowRight: 1, ArrowDown: -5, ArrowUp: 5 };
      if (e.key in moves) { e.preventDefault(); show(current + moves[e.key], true); }
      else if (e.key === "Home") { e.preventDefault(); show(0, true); }
      else if (e.key === "End") { e.preventDefault(); show(pts0.length - 1, true); }
      else if (e.key === "Escape") hide();
    });

    box.textContent = "";
    box.appendChild(svg);
    box.appendChild(tip);
  }

  var resizeTimer;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () { if (lastSeries) renderChart(lastSeries); }, 120);
  });

  // ---- Inputs ----------------------------------------------------------------------------------
  ["age", "endAge", "monthly", "rate", "shockDrop", "shockAge"].forEach(function (id) {
    $(id).addEventListener("input", function () { readInputs(); update(id); });
  });
  $("shockOn").addEventListener("change", function () { readInputs(); update(); });
  $("calcForm").addEventListener("submit", function (e) { e.preventDefault(); });

  // ---- Share -----------------------------------------------------------------------------------
  $("shareBtn").addEventListener("click", function () {
    var url = location.href, msg = $("shareMsg");
    if (navigator.share) {
      navigator.share({ title: document.title, text: "What waiting to invest could cost (hypothetical math):", url: url }).catch(function () {});
    } else if (navigator.clipboard) {
      navigator.clipboard.writeText(url).then(function () { msg.textContent = "Link copied."; },
        function () { msg.textContent = "Copy the address bar to share."; });
    } else {
      msg.textContent = "Copy the address bar to share.";
    }
  });

  // ---- Verified facts ----------------------------------------------------------------------------
  function applyFacts(doc) {
    var byKey = {}, used = [];
    (doc.facts || []).forEach(function (f) { byKey[f.key] = f; });
    Array.prototype.forEach.call(document.querySelectorAll("[data-needs]"), function (el) {
      var f = byKey[el.dataset.needs];
      if (!f) return;
      Array.prototype.forEach.call(el.querySelectorAll("[data-fact]"), function (b) {
        var g = byKey[b.dataset.fact]; b.textContent = g ? g.display : "";
      });
      Array.prototype.forEach.call(el.querySelectorAll("[data-fact-asof]"), function (s) {
        var g = byKey[s.dataset.factAsof]; s.textContent = g ? g.source_name + ", " + g.as_of : "";
      });
      el.classList.add("ok");
      if (used.indexOf(f) < 0) used.push(f);
    });
    var box = $("factSources"), seen = {};
    box.textContent = "";
    used.forEach(function (f) {
      var url = (f.sources || [])[0];
      if (!url || seen[url] || !/^https?:\/\//i.test(url)) return;
      seen[url] = true;
      box.appendChild(document.createTextNode(box.childNodes.length ? " · " : "Sources: "));
      var a = document.createElement("a");
      a.href = url; a.rel = "noopener"; a.textContent = f.source_name;
      box.appendChild(a);
    });
  }
  if (window.fetch) {
    fetch("data/facts.json").then(function (r) { return r.ok ? r.json() : { facts: [] }; }).then(applyFacts).catch(function () {});
  }

  // ---- Email sign-up ---------------------------------------------------------------------------
  $("signupForm").addEventListener("submit", function (e) {
    var msg = $("signupMsg");
    msg.classList.remove("hidden");
    if (!cfg.signupEndpoint) {
      e.preventDefault();
      msg.textContent = "Sign-ups aren't connected yet. Add your email provider's form URL in assets/config.js.";
      return;
    }
    this.action = cfg.signupEndpoint;
    msg.textContent = "Thanks! Check your inbox to confirm.";
  });

  update();
})();
