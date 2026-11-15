// The Money Map (app/money-map.html): a private worksheet saved on this device under
// pm.progress.v1 -> money_map. The summary explains what was entered; it never advises.
(function () {
  "use strict";
  var A = window.PMApp, L = A.L, el = A.el;
  function $(id) { return document.getElementById(id); }

  var mm = L.normalizeMoneyMap(A.loadProgress().money_map);

  var ROWS = {
    costs: { list: "costsList", add: "addCost", noun: "cost", start: 3, blank: { name: "", amount: null },
             fields: [{ key: "name", label: "What it is", type: "text", wide: true, examples: ["Rent", "Groceries", "Phone"] },
                      { key: "amount", label: "Per month ($)", type: "number" }] },
    debts: { list: "debtsList", add: "addDebt", noun: "debt", start: 1, cls: "three", blank: { name: "", balance: null, rate: null },
             fields: [{ key: "name", label: "Debt", type: "text", wide: true, examples: ["Credit card"] },
                      { key: "balance", label: "Balance ($)", type: "number" },
                      { key: "rate", label: "Interest rate (APR %)", type: "number", step: "0.01", max: 100 }] },
    goals: { list: "goalsList", add: "addGoal", noun: "goal", start: 1, cls: "three", blank: { name: "", amount: null, by: "" },
             fields: [{ key: "name", label: "Goal", type: "text", wide: true, examples: ["Trip, laptop, moving costs"] },
                      { key: "amount", label: "Amount ($)", type: "number" },
                      { key: "by", label: "By (month)", type: "month" }] }
  };

  function num(v, max) {
    if (typeof v !== "string" || v.trim() === "") return null;
    var n = Number(v);
    return isFinite(n) && n >= 0 && n <= (max || 1e9) ? n : null;
  }
  function blank(kind) { return JSON.parse(JSON.stringify(ROWS[kind].blank)); }

  // ---- Repeating rows (costs, debts, goals) ------------------------------------------------------------
  function renderRows(kind, focusIndex) {
    var cfg = ROWS[kind], list = A.clear($(cfg.list));
    if (!mm[kind].length) for (var s = 0; s < cfg.start; s++) mm[kind].push(blank(kind));
    mm[kind].forEach(function (row, i) {
      var li = el("li", { class: "entry" + (cfg.cls ? " " + cfg.cls : ""), "data-row": i });
      cfg.fields.forEach(function (f) {
        var id = kind + "-" + i + "-" + f.key;
        var input = el("input", { type: f.type, id: id, autocomplete: "off", maxlength: f.type === "text" ? 80 : null,
          min: f.type === "number" ? 0 : null, max: f.max || null, step: f.type === "number" ? (f.step || "any") : null,
          inputmode: f.type === "number" ? "decimal" : null,
          placeholder: f.examples ? f.examples[i % f.examples.length] : (f.type === "month" ? "YYYY-MM" : null) });
        var v = row[f.key];
        input.value = v == null ? "" : String(v);
        input.addEventListener("input", function () {
          row[f.key] = f.type === "number" ? num(input.value, f.max) : f.type === "month"
            ? (/^\d{4}-(0[1-9]|1[0-2])$/.test(input.value) ? input.value : "") : input.value.slice(0, 80);
          changed();
        });
        li.appendChild(el("div", { class: "field" + (f.wide ? " wide" : "") }, [el("label", { for: id, text: f.label }), input]));
      });
      var rm = el("button", { type: "button", class: "small remove", text: "Remove",
                              "aria-label": "Remove " + cfg.noun + " " + (i + 1) });
      rm.addEventListener("click", function () {
        mm[kind].splice(i, 1);
        changed();
        renderRows(kind, Math.min(i, mm[kind].length - 1));
      });
      li.appendChild(rm);
      list.appendChild(li);
    });
    if (focusIndex != null) {
      var target = list.querySelector('[data-row="' + focusIndex + '"] input') || $(cfg.add);
      target.focus();
    }
  }
  Object.keys(ROWS).forEach(function (kind) {
    $(ROWS[kind].add).addEventListener("click", function () {
      if (mm[kind].length >= 30) return;
      mm[kind].push(blank(kind));
      renderRows(kind, mm[kind].length - 1);
      changed();
    });
  });

  // ---- Single fields ---------------------------------------------------------------------------------
  function renderAccounts() {
    var box = A.clear($("accountChecks"));
    L.ACCOUNT_TYPES.forEach(function (t) {
      var input = el("input", { type: "checkbox", id: "acct-" + t.key });
      input.checked = !!mm.accounts[t.key];
      input.addEventListener("change", function () {
        if (input.checked) mm.accounts[t.key] = true; else delete mm.accounts[t.key];
        changed();
      });
      box.appendChild(el("label", { for: "acct-" + t.key }, [input, t.label]));
    });
  }

  function syncMonths() {
    Array.prototype.forEach.call($("monthsChips").querySelectorAll("button"), function (b) {
      b.setAttribute("aria-pressed", String(+b.dataset.value === mm.cushion.months));
    });
  }

  function fillForm() {
    $("pay").value = mm.pay == null ? "" : mm.pay;
    $("months").value = mm.cushion.months;
    $("saved").value = mm.cushion.saved == null ? "" : mm.cushion.saved;
    $("otherAccounts").value = mm.other_accounts;
    $("monthsError").textContent = "";
    syncMonths();
    renderAccounts();
    Object.keys(ROWS).forEach(function (k) { renderRows(k); });
  }

  $("pay").addEventListener("input", function () { mm.pay = num(this.value); changed(); });
  $("saved").addEventListener("input", function () { mm.cushion.saved = num(this.value); changed(); });
  $("otherAccounts").addEventListener("input", function () { mm.other_accounts = this.value.slice(0, 120); changed(); });
  $("months").addEventListener("input", function () {
    var n = num(this.value, 24);
    var ok = n !== null && Math.floor(n) === n;
    $("monthsError").textContent = ok || this.value === "" ? "" : "Use a whole number of months from 0 to 24.";
    if (ok) { mm.cushion.months = n; syncMonths(); changed(); }
  });
  $("monthsChips").addEventListener("click", function (e) {
    var b = e.target.closest("button[data-value]");
    if (!b) return;
    mm.cushion.months = +b.dataset.value;
    $("months").value = mm.cushion.months;
    $("monthsError").textContent = "";
    syncMonths();
    changed();
  });
  $("mapForm").addEventListener("submit", function (e) { e.preventDefault(); });

  // ---- Summary ------------------------------------------------------------------------------------------
  function pct(x) { return Math.round(x * 100) + "%"; }
  function rate(r) { return (Math.round(r * 100) / 100) + "%"; }
  function monthName(ym) {
    var p = ym.split("-").map(Number);
    return new Date(p[0], p[1] - 1, 1).toLocaleDateString("en-US", { month: "short", year: "numeric" });
  }
  function months(n) { return A.plural(n, "month"); }

  function renderSummary() {
    var s = L.moneyMapSummary(mm, L.today()), box = A.clear($("summaryBody")), $m = A.money;
    if (s.isEmpty) {
      box.appendChild(el("p", { class: "meta", id: "summaryEmpty", text: "Fill in any part above and your summary shows up here." }));
      return;
    }
    function section(title, id, kids) { box.appendChild(el("div", { id: id }, [el("h3", { text: title })].concat(kids))); }

    var month = [];
    if (s.pay !== null) month.push(el("p", {}, ["Take-home pay: ", el("strong", { text: $m(s.pay) }), " a month."]));
    if (s.costsCount) {
      month.push(el("p", {}, ["Must-pay costs: ", el("strong", { text: $m(s.costsTotal) }), " a month, across " + A.plural(s.costsCount, "item") + "."]));
      if (s.costShare !== null) {
        month.push(el("p", { text: s.leftover >= 0
          ? "That's " + pct(s.costShare) + " of your take-home pay, leaving " + $m(s.leftover) + " a month for everything else."
          : "That's " + $m(-s.leftover) + " a month more than your take-home pay." }));
      }
    }
    if (month.length) section("Each month", "sumMonth", month);

    var cushion = [];
    if (s.cushion) {
      var c = s.cushion;
      cushion.push(el("p", {}, ["Your cushion target is " + months(c.months) + " of the costs you entered: ",
        el("strong", { class: "big", text: $m(c.target) }), "."]));
      if (c.saved !== null) {
        cushion.push(el("p", { text: c.remaining > 0
          ? "You've saved " + $m(c.saved) + " of it (" + pct(c.share) + "), with " + $m(c.remaining) + " to go."
          : "What you've saved (" + $m(c.saved) + ") covers the target you set." }));
      }
    } else if (s.costsCount) {
      cushion.push(el("p", { text: "Your cushion target is set to 0 months." }));
    } else {
      cushion.push(el("p", { class: "meta", text: "Add your must-pay costs to see a cushion target." }));
    }
    section("Cash cushion", "sumCushion", cushion);

    if (s.debts.length) {
      var ol = el("ol", { id: "debtOrder" });
      s.debts.forEach(function (d) {
        ol.appendChild(el("li", { text: d.rate === null
          ? d.name + ": " + $m(d.balance) + " (no rate entered)"
          : d.name + ": " + $m(d.balance) + " at " + rate(d.rate) + " APR, about " + $m(d.monthlyInterest) + " a month in interest" }));
      });
      section("Debts, by the interest rate you typed", "sumDebts", [
        el("p", { class: "meta", text: "Highest rate first. On the same balance, a higher rate adds more interest each month." }),
        ol,
        el("p", { text: "Total owed: " + $m(s.debtTotal) + ". At these rates, that's about " + $m(s.debtMonthlyInterest) + " a month in interest." }),
        el("p", { class: "fine", text: "Monthly interest here is the balance times the rate, divided by 12. Your statement's figure can differ." })
      ]);
    }

    if (s.accounts.length || s.otherAccounts) {
      var ul = el("ul", {});
      s.accounts.forEach(function (a) { ul.appendChild(el("li", { text: a })); });
      if (s.otherAccounts) ul.appendChild(el("li", { text: s.otherAccounts }));
      section("Accounts you have", "sumAccounts", [ul]);
    }

    if (s.goals.length) {
      var gl = el("ul", {});
      s.goals.forEach(function (g) {
        var t = g.name + (g.amount ? ": " + $m(g.amount) : "");
        if (g.by) t += " by " + monthName(g.by);
        if (g.perMonth) t += ". That's " + months(g.months) + " away, or about " + $m(g.perMonth) + " a month before any interest or growth.";
        else if (g.past) t += ". That month has passed; change it to see a monthly amount.";
        else if (!g.by || !g.amount) t += ". Add an amount and a month to see what it takes each month.";
        else t += ".";
        gl.appendChild(el("li", { text: t }));
      });
      section("Goals", "sumGoals", [gl]);
    }
  }

  // ---- Save ---------------------------------------------------------------------------------------------
  function changed() {
    mm.updated = new Date().toISOString();
    var p = A.loadProgress();
    p.money_map = mm;
    var ok = A.saveProgress(p);
    $("savedNote").textContent = ok ? "Saved on this device at " +
      new Date().toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" }) + "." : "";
    renderSummary();
  }

  $("clearBtn").addEventListener("click", function () { $("clearConfirm").classList.remove("hidden"); $("clearNo").focus(); });
  $("clearNo").addEventListener("click", function () { $("clearConfirm").classList.add("hidden"); $("clearBtn").focus(); });
  $("clearYes").addEventListener("click", function () {
    mm = L.normalizeMoneyMap({});
    var p = A.loadProgress();
    p.money_map = {};
    A.saveProgress(p);
    fillForm();
    renderSummary();
    $("savedNote").textContent = "Cleared from this device.";
    $("clearConfirm").classList.add("hidden");
    $("clearBtn").focus();
  });

  // Came from a lesson's "Try it": offer the way back.
  var from = new URLSearchParams(location.search).get("from");
  if (L.isSlug(from)) {
    $("fromLesson").querySelector("a").setAttribute("href", A.lessonHref(from));
    $("fromLesson").classList.remove("hidden");
  }
  if (!A.loadProgress().member) $("memberNote").classList.remove("hidden");

  fillForm();
  renderSummary();
})();
