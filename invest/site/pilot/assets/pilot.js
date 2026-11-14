// Patient Money rewards pilot: employer dashboard (index.html) and member view (member.html).
// Reads data/employer.json or data/member.json in the format of docs/pilot/data-contract.md.
// Every value from the data goes into the page with textContent, never innerHTML.
(function () {
  "use strict";
  var SVG = "http://www.w3.org/2000/svg";
  var NF = new Intl.NumberFormat("en-US");
  var FULL_DATE = { month: "short", day: "numeric", year: "numeric" };

  // ---- Small helpers ---------------------------------------------------------------------------
  function $(id) { return document.getElementById(id); }
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined && text !== null) n.textContent = String(text);
    return n;
  }
  function svgEl(name, attrs) {
    var n = document.createElementNS(SVG, name);
    for (var k in attrs) if (Object.prototype.hasOwnProperty.call(attrs, k)) n.setAttribute(k, attrs[k]);
    return n;
  }
  function num(v) { return typeof v === "number" && isFinite(v) ? v : null; }
  function arr(v) { return Array.isArray(v) ? v : []; }
  function obj(v) { return !!v && typeof v === "object" && !Array.isArray(v); }
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
  function cap(s) { s = String(s || ""); return s.charAt(0).toUpperCase() + s.slice(1); }
  function keySpan(slot) { return el("span", "key s" + slot); }

  // ---- Formatting ------------------------------------------------------------------------------
  function count(n) { n = num(n); return n === null ? "—" : NF.format(Math.round(n)); }
  function plural(n, one, many) { return count(n) + " " + (Math.round(n) === 1 ? one : many); }
  // money(5000) -> "$5,000", money(3120.5) -> "$3,120.50"; cents=true always shows cents.
  function money(n, cents) {
    n = num(n);
    if (n === null) return "—";
    var showCents = cents || Math.round(Math.abs(n) * 100) % 100 !== 0;
    var s = Math.abs(n).toLocaleString("en-US", { minimumFractionDigits: showCents ? 2 : 0, maximumFractionDigits: 2 });
    return (n < 0 ? "−$" : "$") + s;
  }
  // pct(95.8) -> "95.8%", pct(100) -> "100%". pct1 keeps one decimal for table columns.
  function pct(n) {
    n = num(n);
    if (n === null) return "—";
    var s = n.toFixed(1);
    return (s.slice(-2) === ".0" ? s.slice(0, -2) : s) + "%";
  }
  function pct1(n) { n = num(n); return n === null ? "—" : n.toFixed(1) + "%"; }
  function share(part, whole) { part = num(part); whole = num(whole); return part === null || !whole ? null : part / whole * 100; }

  // Dates are ISO "YYYY-MM-DD" or "YYYY-MM"; build local dates so nothing shifts a day by time zone.
  function parseDate(s) {
    var m = /^(\d{4})-(\d{2})(?:-(\d{2}))?$/.exec(String(s || ""));
    return m ? new Date(+m[1], +m[2] - 1, m[3] ? +m[3] : 1) : null;
  }
  function fmtDate(s, opts) { var d = parseDate(s); return d ? d.toLocaleDateString("en-US", opts) : (s ? String(s) : "—"); }
  function shortDate(s, refYear) {
    var d = parseDate(s);
    if (!d) return s ? String(s) : "—";
    return d.toLocaleDateString("en-US", d.getFullYear() === refYear ? { month: "short", day: "numeric" } : FULL_DATE);
  }
  function monthYear(s) { return fmtDate(s, { month: "long", year: "numeric" }); }

  // ---- Loading and failure ---------------------------------------------------------------------
  function loadJSON(path) {
    if (!window.fetch) return Promise.reject(new Error("fetch unavailable"));
    return fetch(path, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    });
  }

  function showProblem(what, page, badFormat) {
    var box = $("loadStatus");
    box.textContent = "";
    box.className = "load-status card load-error";
    box.setAttribute("role", "alert");
    box.appendChild(el("h2", null, "We couldn't show the " + what + " right now"));
    if (location.protocol === "file:") {
      box.appendChild(el("p", null, "This page was opened straight from a file on your computer. Browsers don't let pages opened that way read their data files, so there's nothing to show yet."));
      var p = el("p", null, "To view it, start a small local web server from the project folder: ");
      p.appendChild(el("code", null, "python3 -m http.server 8000 --directory invest/site"));
      p.appendChild(document.createTextNode(" Then open "));
      p.appendChild(el("code", null, "http://localhost:8000/pilot/" + page));
      p.appendChild(document.createTextNode(" in your browser."));
      box.appendChild(p);
      return;
    }
    box.appendChild(el("p", null, badFormat
      ? "The data file loaded, but it isn't in the format this page expects. The latest export may be incomplete. Please try again after the next export."
      : "The data file didn't load. Check your connection and try again. If it keeps happening, the latest export may not be published yet."));
    var retry = el("button", "ghost", "Try again");
    retry.type = "button";
    retry.addEventListener("click", function () { location.reload(); });
    box.appendChild(retry);
  }

  function boot(path, what, page, isValid, render) {
    loadJSON(path).then(function (data) {
      if (!isValid(data)) { showProblem(what, page, true); return; }
      // Show the content before rendering so the chart can measure its width.
      $("app").classList.remove("hidden");
      $("loadStatus").classList.add("hidden");
      try {
        render(data);
      } catch (err) {
        $("app").classList.add("hidden");
        console.error(err);
        showProblem(what, page, true);
      }
    }, function () { showProblem(what, page, false); });
  }

  // Tooltips that stay open after a tap close when someone taps elsewhere.
  var tipClosers = {};
  document.addEventListener("pointerdown", function (e) {
    Object.keys(tipClosers).forEach(function (k) {
      var c = tipClosers[k];
      if (c && !c.root.contains(e.target)) c.hide();
    });
  });

  // ==============================================================================================
  // Employer dashboard
  // ==============================================================================================
  var RET_SERIES = [
    { key: "enrolled_pct", name: "Enrolled", slot: 1 },
    { key: "not_enrolled_pct", name: "Not enrolled", slot: 2 }
  ];
  var retention = null; // { rows, width } for re-rendering on resize

  function isEmployer(d) { return obj(d) && obj(d.employer) && obj(d.summary) && Array.isArray(d.retention); }

  function setMeter(span, p) { span.style.width = (p === null ? 0 : clamp(p, 0, 100)) + "%"; }

  function renderEmployer(d) {
    var emp = d.employer, s = d.summary, ppu = num(emp.points_per_usd);
    var asOf = parseDate(d.as_of), year = asOf ? asOf.getFullYear() : null;

    $("demoBanner").classList.toggle("hidden", emp.id !== "emp_demo");
    if (emp.name) document.title = emp.name + ": Rewards Pilot Dashboard | Patient Money";
    $("planPill").textContent = emp.plan ? cap(emp.plan) + " plan" : "Rewards plan";
    $("empName").textContent = emp.name || "Rewards pilot";
    var meta = [];
    if (d.as_of) meta.push("Data as of " + fmtDate(d.as_of, FULL_DATE));
    if (num(emp.pepm_usd) !== null) meta.push(money(emp.pepm_usd, true) + " per employee per month");
    if (ppu) meta.push(count(ppu) + " points = $1");
    $("empMeta").textContent = meta.join(" · ");

    // Stat tiles
    var enrolledShare = share(s.enrolled, s.eligible);
    $("tEnrolled").textContent = count(s.enrolled);
    $("tEnrolledSub").textContent = "of " + count(s.eligible) + " eligible" + (enrolledShare === null ? "" : " (" + Math.round(enrolledShare) + "%)");
    setMeter($("tEnrolledBar"), enrolledShare);

    var activeShare = share(s.active_30d, s.enrolled);
    $("tActive").textContent = count(s.active_30d);
    $("tActiveSub").textContent = activeShare === null ? "enrolled members" : Math.round(activeShare) + "% of enrolled members";
    setMeter($("tActiveBar"), activeShare);

    var poolShare = share(emp.pool_remaining_usd, emp.pool_funded_usd);
    $("tPool").textContent = money(emp.pool_remaining_usd);
    $("tPoolSub").textContent = "of " + money(emp.pool_funded_usd) + " funded" + (poolShare === null ? "" : " (" + Math.round(poolShare) + "% left)");
    setMeter($("tPoolBar"), poolShare);

    $("tOutstanding").textContent = count(s.points_outstanding);
    $("tOutstandingSub").textContent = ppu && num(s.points_outstanding) !== null
      ? "worth " + money(s.points_outstanding / ppu) + ", earned but not yet redeemed"
      : "earned but not yet redeemed";

    // Retention
    var rows = arr(d.retention).filter(function (r) { return obj(r) && parseDate(r.month); }).slice()
      .sort(function (a, b) { return a.month < b.month ? -1 : a.month > b.month ? 1 : 0; });
    renderLegend($("retLegend"), RET_SERIES);
    renderRetentionHeadline(rows);
    renderRetentionTable(rows);
    retention = { rows: rows, width: 0 };
    drawRetention();

    renderRuleBars(arr(d.earning_by_rule), ppu);
    renderRedemptions(arr(d.redemptions), s);
    renderMembers(arr(d.members), year);
  }

  function renderLegend(box, series) {
    box.textContent = "";
    series.forEach(function (s) {
      var item = el("span");
      item.appendChild(keySpan(s.slot));
      item.appendChild(document.createTextNode(s.name));
      box.appendChild(item);
    });
  }

  function gapText(r) {
    var a = num(r.enrolled_pct), b = num(r.not_enrolled_pct);
    if (a === null || b === null) return "";
    var g = Math.abs(a - b).toFixed(1);
    if (g === "0.0") return "No gap";
    return (a > b ? "Enrolled ahead by " : "Enrolled behind by ") + g + (g === "1.0" ? " point" : " points");
  }

  function lastComplete(rows) {
    for (var i = rows.length - 1; i >= 0; i--) {
      if (num(rows[i].enrolled_pct) !== null && num(rows[i].not_enrolled_pct) !== null) return rows[i];
    }
    return null;
  }

  function renderRetentionHeadline(rows) {
    var box = $("retHeadline"), last = lastComplete(rows);
    box.textContent = "";
    if (!last || rows.length < 2) {
      box.textContent = "The comparison starts once there are at least two months of data.";
      return;
    }
    var a = last.enrolled_pct, b = last.not_enrolled_pct, g = Math.abs(a - b).toFixed(1);
    box.appendChild(document.createTextNode("In " + monthYear(last.month) + ", "));
    box.appendChild(el("strong", null, pct(a)));
    box.appendChild(document.createTextNode(" of the enrolled group were still on staff, compared with "));
    box.appendChild(el("strong", null, pct(b)));
    box.appendChild(document.createTextNode(" of eligible staff who didn't enroll. "));
    box.appendChild(document.createTextNode(g === "0.0" ? "So far there's no gap between the groups."
      : "That's " + g + " points " + (a > b ? "higher" : "lower") + " for the enrolled group."));
  }

  function renderRetentionTable(rows) {
    var t = $("retTable");
    t.textContent = "";
    var caption = t.createCaption();
    caption.className = "sr-only";
    caption.textContent = "Share of each starting group still employed, by month";
    var head = t.createTHead().insertRow();
    ["Month", "Enrolled", "Not enrolled", "Gap (points)"].forEach(function (h) {
      var th = el("th", null, h); th.scope = "col"; head.appendChild(th);
    });
    var body = t.createTBody();
    rows.forEach(function (r) {
      var tr = body.insertRow();
      var th = el("th", null, fmtDate(r.month, { month: "short", year: "numeric" })); th.scope = "row"; tr.appendChild(th);
      tr.insertCell().textContent = pct1(r.enrolled_pct);
      tr.insertCell().textContent = pct1(r.not_enrolled_pct);
      var a = num(r.enrolled_pct), b = num(r.not_enrolled_pct);
      tr.insertCell().textContent = a === null || b === null ? "—" : (a - b > 0 ? "+" : a - b < 0 ? "−" : "") + Math.abs(a - b).toFixed(1);
    });
  }

  // Line chart: two series, one y-axis (% still employed), months on x. Crosshair snaps to the
  // nearest month; one tooltip lists both series; arrow keys move between months.
  function drawRetention() {
    var box = $("retChart"), rows = retention.rows, series = RET_SERIES, n = rows.length;
    retention.width = box.clientWidth;
    box.textContent = "";
    delete tipClosers.ret;

    var vals = [];
    rows.forEach(function (r) { series.forEach(function (s) { var v = num(r[s.key]); if (v !== null) vals.push(v); }); });
    if (!vals.length) { box.appendChild(el("p", "fine", "No retention data yet.")); return; }

    var W = Math.max(240, Math.round(box.clientWidth || 640));
    var wide = W >= 440;
    var H = wide ? Math.round(clamp(W * 0.34, 260, 340)) : 260;
    var m = { t: 16, r: wide ? 92 : 52, b: 42, l: 44 }; // right margin holds the end labels
    var plotW = W - m.l - m.r, plotH = H - m.t - m.b;

    var vMin = Math.min.apply(null, vals), vMax = Math.max.apply(null, vals), step = 10;
    var lo = Math.max(0, Math.floor((vMin - 3) / step) * step);
    var hi = Math.max(lo + step, Math.ceil(vMax / step) * step);
    if ((hi - lo) / step > 6) { step = 20; lo = Math.floor(lo / step) * step; hi = Math.ceil(hi / step) * step; }

    function x(i) { return n === 1 ? m.l + plotW / 2 : m.l + i / (n - 1) * plotW; }
    function y(v) { return m.t + (1 - (v - lo) / (hi - lo)) * plotH; }
    function val(i, s) { return num(rows[i][s.key]); }

    var first = rows[0], last = lastComplete(rows) || rows[n - 1];
    var label = "Line chart of the share of each group still employed, " + monthYear(first.month) + " to " + monthYear(rows[n - 1].month) + ". " +
      series.map(function (s) { return s.name + ": " + pct(num(first[s.key])) + " to " + pct(num(last[s.key])); }).join(". ") +
      ". Use the left and right arrow keys to read each month.";
    var svg = svgEl("svg", { viewBox: "0 0 " + W + " " + H, width: W, height: H, role: "img", tabindex: "0", "aria-label": label });

    // Y gridlines and ticks (the bottom one is the axis line)
    for (var t = lo; t <= hi + 1e-9; t += step) {
      svg.appendChild(svgEl("line", { "class": t === lo ? "baseline" : "grid", x1: m.l, x2: m.l + plotW, y1: y(t), y2: y(t) }));
      var tl = svgEl("text", { "class": "tick", x: m.l - 8, y: y(t) + 4, "text-anchor": "end" });
      tl.textContent = t + "%";
      svg.appendChild(tl);
    }

    // X ticks: month names (counted back from the latest month, so it always has a label),
    // with the year under the first labeled month of each year.
    var spacing = n > 1 ? plotW / (n - 1) : plotW, every = Math.max(1, Math.ceil(30 / spacing)), shownYear = null;
    rows.forEach(function (r, i) {
      if ((n - 1 - i) % every !== 0) return;
      var dt = parseDate(r.month);
      var mt = svgEl("text", { "class": "tick", x: x(i), y: H - m.b + 18, "text-anchor": "middle" });
      mt.textContent = dt.toLocaleDateString("en-US", { month: "short" });
      svg.appendChild(mt);
      if (dt.getFullYear() !== shownYear) {
        shownYear = dt.getFullYear();
        var yt = svgEl("text", { "class": "tick year", x: x(i), y: H - m.b + 32, "text-anchor": "middle" });
        yt.textContent = shownYear;
        svg.appendChild(yt);
      }
    });

    // Lines (a missing value breaks the line rather than inventing a point)
    series.forEach(function (s) {
      var dPath = "", pen = false;
      rows.forEach(function (r, i) {
        var v = val(i, s);
        if (v === null) { pen = false; return; }
        dPath += (pen ? "L" : "M") + x(i).toFixed(1) + " " + y(v).toFixed(1) + " ";
        pen = true;
      });
      if (dPath) svg.appendChild(svgEl("path", { "class": "line c" + s.slot, d: dPath.trim() }));
    });

    // End dots and direct end labels: value, plus the series name when there's room.
    var ends = [];
    series.forEach(function (s) {
      for (var i = n - 1; i >= 0; i--) {
        var v = val(i, s);
        if (v !== null) { ends.push({ s: s, v: v, ex: x(i), ey: y(v) }); break; }
      }
    });
    ends.forEach(function (e) { svg.appendChild(svgEl("circle", { "class": "dot f" + e.s.slot, cx: e.ex, cy: e.ey, r: 4 })); });
    var twoLine = wide && ends.every(function (a, k) {
      return ends.every(function (b, j) { return j === k || Math.abs(a.ey - b.ey) >= 32; });
    });
    var placed = [];
    ends.forEach(function (e) {
      var ly = e.ey + 4;
      if (placed.some(function (p) { return Math.abs(p - ly) < 15; })) return; // too close: legend + tooltip carry it
      placed.push(ly);
      var tv = svgEl("text", { "class": "end-label", x: e.ex + 12, y: ly });
      tv.textContent = pct(e.v);
      svg.appendChild(tv);
      if (twoLine) {
        var tn = svgEl("text", { "class": "tick", x: e.ex + 12, y: ly + 15 });
        tn.textContent = e.s.name;
        svg.appendChild(tn);
      }
    });

    // Hover / focus layer
    var cross = svgEl("line", { "class": "crosshair hidden", y1: m.t, y2: m.t + plotH });
    var hoverDots = svgEl("g", { "class": "hidden" });
    series.forEach(function (s) { hoverDots.appendChild(svgEl("circle", { "class": "dot f" + s.slot, r: 5 })); });
    // The whole chart is the hit target; the crosshair snaps to the nearest month.
    var overlay = svgEl("rect", { x: 0, y: 0, width: W, height: H, fill: "transparent" });
    svg.appendChild(cross); svg.appendChild(hoverDots); svg.appendChild(overlay);

    var tip = el("div", "tooltip hidden");
    tip.setAttribute("aria-hidden", "true");
    var current = n - 1;

    function show(i) {
      current = clamp(i, 0, n - 1);
      var cx = x(current), r = rows[current], ys = [];
      cross.setAttribute("x1", cx); cross.setAttribute("x2", cx);
      cross.classList.remove("hidden");
      hoverDots.classList.remove("hidden");
      series.forEach(function (s, k) {
        var c = hoverDots.childNodes[k], v = val(current, s);
        c.classList.toggle("hidden", v === null);
        if (v !== null) { c.setAttribute("cx", cx); c.setAttribute("cy", y(v)); ys.push(y(v)); }
      });

      tip.textContent = "";
      tip.appendChild(el("div", "t-head", monthYear(r.month)));
      series.forEach(function (s) {
        var row = el("div", "t-row");
        row.appendChild(keySpan(s.slot));
        row.appendChild(el("b", null, pct(val(current, s))));
        row.appendChild(el("span", null, s.name));
        tip.appendChild(row);
      });
      var g = gapText(r);
      if (g) tip.appendChild(el("div", "t-note", g));
      tip.classList.remove("hidden");

      var scale = (svg.getBoundingClientRect().width || W) / W, px = cx * scale;
      var maxLeft = Math.max(0, box.clientWidth - tip.offsetWidth), left, top;
      if (!wide && box.getBoundingClientRect().top > tip.offsetHeight + 8) {
        // Narrow screens: float above the plot, so the tooltip doesn't hide the lines under a finger.
        left = px - tip.offsetWidth / 2;
        top = -tip.offsetHeight - 8;
      } else {
        // Beside the crosshair, flipped near the right edge; top or bottom, away from the lines.
        left = px + 14 + tip.offsetWidth > box.clientWidth ? px - 14 - tip.offsetWidth : px + 14;
        var avgY = ys.length ? ys.reduce(function (a, b) { return a + b; }, 0) / ys.length : H;
        top = Math.max(0, avgY < m.t + plotH / 2 ? (m.t + plotH) * scale - tip.offsetHeight : m.t * scale);
      }
      tip.style.left = clamp(left, 0, maxLeft) + "px";
      tip.style.top = top + "px";
    }
    function hide() { cross.classList.add("hidden"); hoverDots.classList.add("hidden"); tip.classList.add("hidden"); }
    function announce() {
      var r = rows[current];
      $("retLive").textContent = monthYear(r.month) + ": " +
        series.map(function (s) { return s.name + " " + pct(val(current, s)); }).join(", ") + ". " + gapText(r) + ".";
    }
    function indexAt(clientX) {
      if (n === 1) return 0;
      var rect = svg.getBoundingClientRect(), px = (clientX - rect.left) * (W / rect.width);
      return Math.round((px - m.l) / plotW * (n - 1));
    }

    overlay.addEventListener("pointermove", function (e) { show(indexAt(e.clientX)); });
    overlay.addEventListener("pointerdown", function (e) { show(indexAt(e.clientX)); });
    overlay.addEventListener("pointerleave", function (e) { if (e.pointerType !== "touch") hide(); });
    svg.addEventListener("focus", function () { show(current); });
    svg.addEventListener("blur", hide);
    svg.addEventListener("keydown", function (e) {
      var next = null;
      if (e.key === "ArrowLeft" || e.key === "ArrowDown") next = current - 1;
      else if (e.key === "ArrowRight" || e.key === "ArrowUp") next = current + 1;
      else if (e.key === "Home") next = 0;
      else if (e.key === "End") next = n - 1;
      else if (e.key === "Escape") { hide(); return; }
      if (next === null) return;
      e.preventDefault();
      show(next);
      announce();
    });
    tipClosers.ret = { root: box, hide: hide };

    box.appendChild(svg);
    box.appendChild(tip);
  }

  var resizeTimer;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      if (retention && $("retChart").clientWidth !== retention.width) drawRetention();
    }, 120);
  });

  // Ranked horizontal bars, one hue, value at each bar's tip. The whole row is the hover target.
  function renderRuleBars(rules, ppu) {
    var rows = rules.filter(function (r) { return obj(r) && num(r.points) !== null; }).slice()
      .sort(function (a, b) { return b.points - a.points; });
    var list = $("ruleBars"), box = $("ruleBox");
    list.textContent = "";
    var total = rows.reduce(function (t, r) { return t + r.points; }, 0);
    var max = rows.reduce(function (mx, r) { return Math.max(mx, r.points); }, 0);
    $("ruleSub").textContent = rows.length
      ? count(total) + " points earned since the pilot began" + (ppu ? ", worth " + money(total / ppu) : "") + "."
      : "No points earned yet.";

    rows.forEach(function (r, i) {
      var li = el("li");
      li.setAttribute("data-i", i);
      li.appendChild(el("span", "bar-label", r.label || r.rule));
      var track = el("span", "bar-track");
      var bar = el("span", "bar" + (r.points > 0 ? "" : " zero"));
      bar.style.setProperty("--p", String(max > 0 ? Math.max(0, r.points) / max : 0));
      track.appendChild(bar);
      track.appendChild(el("span", "bar-value", count(r.points)));
      li.appendChild(track);
      list.appendChild(li);
    });

    // Table twin
    var t = $("ruleTable");
    t.textContent = "";
    var head = t.createTHead().insertRow();
    ["Rule", "Points", "Share", "Value"].forEach(function (h) { var th = el("th", null, h); th.scope = "col"; head.appendChild(th); });
    var body = t.createTBody();
    rows.forEach(function (r) {
      var tr = body.insertRow();
      var th = el("th", null, r.label || r.rule); th.scope = "row"; tr.appendChild(th);
      tr.insertCell().textContent = count(r.points);
      tr.insertCell().textContent = total > 0 ? pct1(r.points / total * 100) : "—";
      tr.insertCell().textContent = ppu ? money(r.points / ppu, true) : "—";
    });

    if (!rows.length) { box.removeAttribute("tabindex"); return; }

    var tip = el("div", "tooltip hidden");
    tip.setAttribute("aria-hidden", "true");
    box.appendChild(tip);
    var current = -1;

    function detail(r) {
      var parts = [count(r.points) + " points"];
      if (total > 0) parts.push(pct(r.points / total * 100) + " of all points earned");
      if (ppu) parts.push(money(r.points / ppu) + " in reward value");
      return parts;
    }
    function activate(i) {
      current = clamp(i, 0, rows.length - 1);
      list.classList.add("has-active");
      Array.prototype.forEach.call(list.children, function (li, k) { li.classList.toggle("is-active", k === current); });
      var r = rows[current], li = list.children[current], bar = li.querySelector(".bar");
      tip.textContent = "";
      tip.appendChild(el("div", "t-head", r.label || r.rule));
      detail(r).forEach(function (line, k) {
        var row = el("div", "t-row");
        if (k === 0) row.appendChild(el("b", null, line)); else row.appendChild(el("span", null, line));
        tip.appendChild(row);
      });
      tip.classList.remove("hidden");
      var boxRect = box.getBoundingClientRect(), barRect = bar.getBoundingClientRect(), liRect = li.getBoundingClientRect();
      var left = clamp(barRect.right - boxRect.left - tip.offsetWidth / 2, 0, Math.max(0, box.clientWidth - tip.offsetWidth));
      var top = liRect.top - boxRect.top - tip.offsetHeight - 4;
      if (top < 0) top = liRect.bottom - boxRect.top + 4;
      tip.style.left = left + "px";
      tip.style.top = top + "px";
    }
    function clear() {
      list.classList.remove("has-active");
      Array.prototype.forEach.call(list.children, function (li) { li.classList.remove("is-active"); });
      tip.classList.add("hidden");
    }
    function fromEvent(e) {
      var li = e.target.closest && e.target.closest("li");
      if (li && list.contains(li)) activate(+li.getAttribute("data-i"));
    }
    list.addEventListener("pointermove", fromEvent);
    list.addEventListener("pointerdown", fromEvent);
    box.addEventListener("pointerleave", function (e) { if (e.pointerType !== "touch") clear(); });
    box.addEventListener("focus", function () { activate(current < 0 ? 0 : current); });
    box.addEventListener("blur", clear);
    box.addEventListener("keydown", function (e) {
      var next = null;
      if (e.key === "ArrowUp" || e.key === "ArrowLeft") next = current - 1;
      else if (e.key === "ArrowDown" || e.key === "ArrowRight") next = current + 1;
      else if (e.key === "Home") next = 0;
      else if (e.key === "End") next = rows.length - 1;
      else if (e.key === "Escape") { clear(); return; }
      if (next === null) return;
      e.preventDefault();
      activate(next);
      var r = rows[current];
      $("ruleLive").textContent = (r.label || r.rule) + ": " + detail(r).join(", ") + ".";
    });
    tipClosers.rules = { root: box, hide: clear };
  }

  function renderRedemptions(items, s) {
    var list = $("redList");
    list.textContent = "";
    var rows = items.filter(obj), totalCount = 0, totalUsd = 0;
    rows.forEach(function (r) {
      var li = el("li");
      var name = el("span", "name", r.label || r.type);
      name.appendChild(el("span", "sub", num(r.count) === null ? "" : plural(r.count, "redemption", "redemptions")));
      li.appendChild(name);
      li.appendChild(el("span", "amt", money(r.usd, true)));
      list.appendChild(li);
      totalCount += num(r.count) || 0;
      totalUsd += num(r.usd) || 0;
    });
    if (!rows.length) {
      list.appendChild(el("li", "fine", "No redemptions yet."));
    } else if (rows.length > 1) {
      var li = el("li", "total");
      var name = el("span", "name", "Total");
      name.appendChild(el("span", "sub", plural(totalCount, "redemption", "redemptions")));
      li.appendChild(name);
      li.appendChild(el("span", "amt", money(totalUsd, true)));
      list.appendChild(li);
    }
    $("redSub").textContent = num(s.points_redeemed) !== null ? count(s.points_redeemed) + " points redeemed so far." : "";
  }

  function renderMembers(members, refYear) {
    var cols = [
      { key: "display_name", label: "Member", type: "text" },
      { key: "tenure_days", label: "Days on the job", type: "num" },
      { key: "points_balance", label: "Points", type: "num" },
      { key: "lessons_completed", label: "Lessons", type: "num" },
      { key: "last_active", label: "Last active", type: "text" } // ISO dates sort as text
    ];
    var list = members.filter(obj), state = { key: "display_name", dir: 1 };
    var table = $("memTable");
    table.textContent = "";
    var caption = table.createCaption();
    caption.className = "sr-only";
    caption.textContent = "Pilot members, display names only";
    var headRow = table.createTHead().insertRow();
    var body = table.createTBody();

    var ths = cols.map(function (c) {
      var th = el("th");
      th.scope = "col";
      var b = el("button", "sort");
      b.type = "button";
      b.appendChild(el("span", null, c.label));
      var arrow = el("span", "arrow");
      arrow.setAttribute("aria-hidden", "true");
      b.appendChild(arrow);
      b.addEventListener("click", function () {
        state.dir = state.key === c.key ? -state.dir : (c.key === "display_name" ? 1 : -1);
        state.key = c.key;
        paint();
      });
      th.appendChild(b);
      headRow.appendChild(th);
      return th;
    });

    function sortValue(mb, c) {
      var v = mb[c.key];
      if (c.type === "num") { v = num(v); return v === null ? -Infinity : v; }
      return v === undefined || v === null ? "" : String(v);
    }
    function paint() {
      var col = cols.filter(function (c) { return c.key === state.key; })[0];
      ths.forEach(function (th, k) {
        var on = cols[k].key === state.key;
        if (on) th.setAttribute("aria-sort", state.dir > 0 ? "ascending" : "descending");
        else th.removeAttribute("aria-sort");
        th.querySelector(".arrow").textContent = on ? (state.dir > 0 ? "▲" : "▼") : "";
      });
      var sorted = list.slice().sort(function (a, b) {
        var va = sortValue(a, col), vb = sortValue(b, col), r;
        r = typeof va === "number" ? va - vb : va.localeCompare(vb, "en", { numeric: true });
        return r * state.dir || String(a.display_name || "").localeCompare(String(b.display_name || ""), "en", { numeric: true });
      });
      body.textContent = "";
      if (!sorted.length) {
        var empty = body.insertRow().insertCell();
        empty.colSpan = cols.length;
        empty.textContent = "No members yet.";
        return;
      }
      sorted.forEach(function (mb) {
        var tr = body.insertRow();
        var th = el("th", null, mb.display_name || "Member");
        th.scope = "row";
        tr.appendChild(th);
        tr.insertCell().textContent = count(mb.tenure_days);
        tr.insertCell().textContent = count(mb.points_balance);
        tr.insertCell().textContent = count(mb.lessons_completed);
        tr.insertCell().textContent = shortDate(mb.last_active, refYear);
      });
    }
    paint();
    $("memSub").textContent = plural(list.length, "member", "members") +
      ". Display names only: this dashboard never shows real names, emails or other personal details. Select a column heading to sort.";
  }

  // ==============================================================================================
  // Member view
  // ==============================================================================================
  function isMember(d) { return obj(d) && obj(d.member) && num(d.points_balance) !== null; }

  function renderMember(d) {
    var mb = d.member, ppu = num(d.points_per_usd), bal = d.points_balance;
    var asOf = parseDate(d.as_of), year = asOf ? asOf.getFullYear() : null;

    $("hello").textContent = mb.display_name ? "Hi, " + mb.display_name : "Your rewards";
    var meta = [];
    if (mb.employer_name) meta.push("Rewards from " + mb.employer_name);
    if (num(mb.tenure_days) !== null) meta.push(plural(mb.tenure_days, "day", "days") + " on the job");
    if (d.as_of) meta.push("As of " + fmtDate(d.as_of, FULL_DATE));
    $("memberMeta").textContent = meta.join(" · ");

    $("balance").textContent = count(bal);
    $("balanceUnit").textContent = Math.round(bal) === 1 ? "point" : "points";
    $("balanceUsd").textContent = ppu ? "Worth " + money(bal / ppu, true) + " in rewards (" + count(ppu) + " points = $1)." : "";

    renderMilestones(arr(d.next_milestones), num(mb.tenure_days));
    renderCatalog(arr(d.catalog), bal, ppu);
    renderHistory(arr(d.history), year);
  }

  function renderMilestones(items, tenure) {
    var ul = $("milestones");
    ul.textContent = "";
    var rows = items.filter(obj);
    if (!rows.length) { ul.appendChild(el("li", "fine", "You've reached every milestone for now.")); return; }
    rows.forEach(function (ms) {
      var p = clamp(num(ms.progress_pct) || 0, 0, 100), name = ms.label || ms.rule;
      var li = el("li");
      var head = el("div", "ms-head");
      head.appendChild(el("span", "name", name));
      if (num(ms.points) !== null) head.appendChild(el("span", "pts", "+" + count(ms.points) + " pts"));
      li.appendChild(head);

      var meter = el("div", "meter lg");
      meter.setAttribute("role", "progressbar");
      meter.setAttribute("aria-label", name);
      meter.setAttribute("aria-valuemin", "0");
      meter.setAttribute("aria-valuemax", "100");
      meter.setAttribute("aria-valuenow", String(p));
      meter.setAttribute("aria-valuetext", Math.round(p) + "% of the way there");
      var fill = el("span");
      fill.style.width = p + "%";
      meter.appendChild(fill);
      li.appendChild(meter);

      var sub = el("div", "ms-sub");
      sub.appendChild(el("span", null, Math.round(p) + "% of the way there"));
      var tm = /^tenure_(\d+)$/.exec(String(ms.rule || ""));
      if (tm && tenure !== null && +tm[1] > tenure) sub.appendChild(el("span", null, plural(+tm[1] - tenure, "day", "days") + " to go"));
      li.appendChild(sub);
      ul.appendChild(li);
    });
  }

  function renderCatalog(items, bal, ppu) {
    var box = $("catalog");
    box.textContent = "";
    var rows = items.filter(obj);
    if (!rows.length) { box.appendChild(el("p", "fine", "No rewards are available right now.")); return; }
    rows.forEach(function (it) {
      var name = it.label || it.type, min = num(it.min_points);
      var card = el("div", "reward");
      card.appendChild(el("h3", null, name));
      if (it.note) card.appendChild(el("p", "fine", it.note));
      if (min !== null) card.appendChild(el("p", "cost", "From " + count(min) + " points" + (ppu ? " (" + money(min / ppu, true) + ")" : "")));

      var btn = el("button", "primary");
      btn.type = "button";
      function label(text) {
        btn.textContent = text;
        btn.appendChild(el("span", "sr-only", ": " + name));
      }
      label("Redeem");
      var status = el("p", "fine reward-status");
      status.setAttribute("role", "status");
      var short = min === null ? 0 : min - bal;
      if (short > 0) {
        btn.disabled = true;
        status.textContent = "You need " + plural(short, "more point", "more points") + " for this one.";
      }
      btn.addEventListener("click", function () {
        if (btn.disabled || btn.getAttribute("aria-disabled") === "true") return;
        label("Request sent (demo)");
        btn.setAttribute("aria-disabled", "true");
        btn.classList.add("sent");
        status.textContent = "This is a demo, so nothing was sent and your points haven't changed.";
      });
      card.appendChild(btn);
      card.appendChild(status);
      box.appendChild(card);
    });
  }

  function renderHistory(items, year) {
    var ol = $("history");
    ol.textContent = "";
    var rows = items.filter(obj).slice().sort(function (a, b) { return String(b.date || "").localeCompare(String(a.date || "")); });
    if (!rows.length) { ol.appendChild(el("li", "fine", "No activity yet.")); return; }
    rows.forEach(function (h) {
      var li = el("li");
      var main = el("div", "h-main");
      main.appendChild(el("span", "h-label", h.label || h.rule));
      var kind = h.kind === "earn" ? "Earned" : h.kind === "redeem" ? "Redeemed" : cap(h.kind);
      main.appendChild(el("span", "h-sub", (kind ? kind + " · " : "") + shortDate(h.date, year)));
      li.appendChild(main);
      var p = num(h.points);
      var pts = el("span", "h-pts" + (p !== null && p < 0 ? " neg" : ""),
        p === null ? "—" : (p > 0 ? "+" : p < 0 ? "−" : "") + count(Math.abs(p)));
      pts.appendChild(el("span", "sr-only", " points"));
      li.appendChild(pts);
      ol.appendChild(li);
    });
  }

  // ---- Start -----------------------------------------------------------------------------------
  var page = document.body.getAttribute("data-page");
  if (page === "employer") boot("data/employer.json", "dashboard", "", isEmployer, renderEmployer);
  else if (page === "member") boot("data/member.json", "member view", "member.html", isMember, renderMember);
})();
