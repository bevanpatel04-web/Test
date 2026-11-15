// Shared helpers for the learning-app pages: DOM building (text only, never HTML strings),
// progress stored on this device, and loading the curriculum, video manifest and facts.
(function () {
  "use strict";
  var L = window.PatientLearn;
  var SVG = "http://www.w3.org/2000/svg";

  // el("p", { class: "fine", text: "Hi" }, [child, "more text"])
  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    for (var k in attrs || {}) {
      var v = attrs[k];
      if (v == null || v === false) continue;
      if (k === "text") n.textContent = v;
      else if (k === "class") n.className = v;
      else n.setAttribute(k, v === true ? "" : String(v));
    }
    append(n, kids);
    return n;
  }
  function append(n, kids) {
    if (kids == null) return n;
    (Array.isArray(kids) ? kids : [kids]).forEach(function (c) {
      if (c == null || c === false) return;
      n.appendChild(typeof c === "object" ? c : document.createTextNode(String(c)));
    });
    return n;
  }
  function clear(n) { n.textContent = ""; return n; }

  // Small line icons (24x24, stroke = currentColor). Always paired with a text label.
  var ICONS = {
    check: ["M5 12.5l4.5 4.5L19 7.5"],
    lock: ["M7 11V8a5 5 0 0 1 10 0v3", "M5.5 11h13v9.5h-13z"],
    dot: ["M12 8.5a3.5 3.5 0 1 1 0 7a3.5 3.5 0 1 1 0-7z"],
    ring: ["M12 5a7 7 0 1 1 0 14a7 7 0 1 1 0-14z"],
    cross: ["M7 7l10 10", "M17 7L7 17"],
    alert: ["M12 4l9 16H3z", "M12 10v4", "M12 17v.5"],
    play: ["M9 7.5v9l7.5-4.5z", "M12 2.5a9.5 9.5 0 1 1 0 19a9.5 9.5 0 1 1 0-19z"],
    review: ["M4 12a8 8 0 0 1 14-5.3", "M18 3v4h-4", "M20 12a8 8 0 0 1-14 5.3", "M6 21v-4h4"],
    arrow: ["M5 12h14", "M13 6l6 6-6 6"]
  };
  function icon(name, cls) {
    var s = document.createElementNS(SVG, "svg");
    s.setAttribute("viewBox", "0 0 24 24");
    s.setAttribute("aria-hidden", "true");
    s.setAttribute("focusable", "false");
    s.setAttribute("class", "icon" + (cls ? " " + cls : ""));
    (ICONS[name] || []).forEach(function (d) {
      var p = document.createElementNS(SVG, "path");
      p.setAttribute("d", d);
      s.appendChild(p);
    });
    return s;
  }

  // ---- Progress on this device -------------------------------------------------------------------
  var storageWorks = true;
  function loadProgress() {
    try {
      var raw = window.localStorage.getItem(L.STORAGE_KEY);
      return L.normalizeProgress(raw ? JSON.parse(raw) : null);
    } catch (e) {
      if (e && e.name !== "SyntaxError") storageBlocked();
      return L.emptyProgress();
    }
  }
  function saveProgress(p) {
    try { window.localStorage.setItem(L.STORAGE_KEY, JSON.stringify(p)); return true; }
    catch (e) { storageBlocked(); return false; }
  }
  function storageBlocked() {
    storageWorks = false;
    var box = document.getElementById("storageNote");
    if (box) {
      box.textContent = "Your browser is blocking storage for this site, so progress won't be kept after you leave.";
      box.classList.remove("hidden");
    }
  }

  // ---- Data -----------------------------------------------------------------------------------------
  function getJSON(url) {
    return fetch(url, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) throw new Error(url + " " + r.status);
      return r.json();
    });
  }
  function loadCurriculum() { return getJSON("data/curriculum.json"); }
  // No manifest yet (or a broken one) just means no videos yet.
  function loadManifest() {
    return getJSON("../media/videos/manifest.json")
      .then(function (d) { return d && typeof d.videos === "object" && d.videos ? d : { videos: {} }; })
      .catch(function () { return { videos: {} }; });
  }
  function loadFacts() {
    return getJSON("../data/facts.json").then(function (d) {
      var by = {};
      ((d && d.facts) || []).forEach(function (f) { if (f && f.key) by[f.key] = f; });
      return by;
    }).catch(function () { return {}; });
  }

  // Manifest paths are relative to invest/site/ and must stay inside media/.
  function mediaUrl(p) {
    return typeof p === "string" && /^media\/[A-Za-z0-9_\-./]+$/.test(p) && p.indexOf("..") < 0 ? "../" + p : null;
  }
  function safeHttpUrl(u) { return typeof u === "string" && /^https?:\/\/[^\s\\@]+$/i.test(u) ? u : null; }

  // ---- Formatting -------------------------------------------------------------------------------------
  function dateObj(iso) { var p = iso.split("-").map(Number); return new Date(p[0], p[1] - 1, p[2]); }
  function niceDate(iso) {
    return dateObj(iso).toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
  }
  function relDay(iso, day) {
    var n = L.daysBetween(day, iso);
    if (n === 0) return "today";
    if (n === -1) return "yesterday";
    if (n === 1) return "tomorrow";
    return n < 0 ? -n + " days ago" : "in " + n + " days";
  }
  function money(n) { return window.PatientMoney ? window.PatientMoney.money(n) : "$" + Math.round(n).toLocaleString("en-US"); }
  function plural(n, one, many) { return n + " " + (n === 1 ? one : many || one + "s"); }
  function lessonHref(slug) { return L.isSlug(slug) ? "lesson.html#" + slug : "index.html"; }
  function levelName(level) { return "Level " + level.number + ": " + level.title; }

  function showError(box, msg) {
    clear(box);
    box.appendChild(el("div", { class: "card", role: "alert" }, [
      el("h2", { text: "Something didn't load" }),
      el("p", { text: msg }),
      el("p", {}, el("a", { class: "btn", href: "index.html", text: "Back to your path" }))
    ]));
  }

  var PRICING = "../pricing.html";

  window.PMApp = {
    L: L, el: el, append: append, clear: clear, icon: icon,
    loadProgress: loadProgress, saveProgress: saveProgress, storageWorks: function () { return storageWorks; },
    loadCurriculum: loadCurriculum, loadManifest: loadManifest, loadFacts: loadFacts,
    mediaUrl: mediaUrl, safeHttpUrl: safeHttpUrl,
    niceDate: niceDate, relDay: relDay, money: money, plural: plural, lessonHref: lessonHref, levelName: levelName,
    showError: showError, PRICING: PRICING
  };
})();
