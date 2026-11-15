// The learning path (app/index.html): what's next, what's due for review, and every level with
// its modules and lessons. Levels 2-5 show a lock until membership is on.
(function () {
  "use strict";
  var A = window.PMApp, L = A.L, el = A.el;
  var root = document.getElementById("pathRoot");
  var curriculum = null;

  function statusBadge(kind) {
    var map = {
      done: ["st st-done", "check", "Done"],
      next: ["st st-next", "dot", "Up next"],
      open: ["st", "ring", "Not started"],
      locked: ["st st-locked", "lock", "Locked, for members"]
    }[kind];
    return el("span", { class: map[0] }, [A.icon(map[1]), el("span", { class: "sr-only", text: map[2] + ": " })]);
  }

  function nextCard(next, overall, progress) {
    var card = el("section", { class: "card next-card", "aria-labelledby": "nextTitle", id: "nextCard" });
    if (!next) {
      card.appendChild(el("p", { class: "kicker", text: "Path complete" }));
      card.appendChild(el("h2", { id: "nextTitle", text: "You've finished every lesson" }));
      card.appendChild(el("p", { text: "Reviews keep bringing old lessons back so the ideas stick." }));
      return card;
    }
    var e = next.entry;
    if (next.locked) {
      card.appendChild(el("p", { class: "kicker", text: "Free level complete" }));
      card.appendChild(el("h2", { id: "nextTitle", text: "Next up: " + A.levelName(e.level) }));
      card.appendChild(el("p", { text: "It starts with “" + e.lesson.title + "”. Levels 2 to 5 are part of membership." }));
      card.appendChild(el("div", { class: "row-actions" }, [
        el("a", { class: "btn", href: A.PRICING, text: "Unlock all levels" }),
        el("a", { class: "btn ghost-btn", href: "account.html", text: "Try the demo membership" })
      ]));
      return card;
    }
    card.appendChild(el("p", { class: "kicker", text: overall.done ? "Up next" : "Start here" }));
    card.appendChild(el("h2", { id: "nextTitle", text: e.lesson.title }));
    card.appendChild(el("p", { class: "meta", text: "Level " + e.level.number + " · " + e.module.title + " · " + e.lesson.minutes + " min" }));
    card.appendChild(el("div", { class: "row-actions" }, [
      el("a", { class: "btn", href: A.lessonHref(e.lesson.slug), id: "startNext" }, [overall.done ? "Continue" : "Start the first lesson", " ", A.icon("arrow")]),
      el("span", { class: "meta", text: overall.done + " of " + A.plural(overall.total, "lesson") + " done" })
    ]));
    return card;
  }

  function reviewCard(due, upcoming, day) {
    if (!due.length) {
      if (!upcoming) return null;
      return el("p", { class: "fine", id: "reviewNote" }, [
        "Nothing to review today. Next review: “" + upcoming.entry.lesson.title + "”, " + A.niceDate(upcoming.due) + "."
      ]);
    }
    var list = el("ul", { class: "review-list" });
    due.forEach(function (d) {
      list.appendChild(el("li", {}, [
        el("span", { class: "st" }, A.icon("review")),
        el("a", { href: A.lessonHref(d.entry.lesson.slug) + "", text: d.entry.lesson.title }),
        el("span", { class: "meta", text: "due " + A.relDay(d.due, day) })
      ]));
    });
    return el("section", { class: "card", id: "reviewCard", "aria-labelledby": "reviewTitle" }, [
      el("h2", { id: "reviewTitle", text: "Due for review (" + due.length + ")" }),
      el("p", { class: "fine", text: "A quick retake of the 3-question check. Bringing an idea back after a few days helps it stick." }),
      list
    ]);
  }

  function levelCard(level, progress, next, day) {
    var open = L.levelOpen(level, progress), lp = L.levelProgress(level, progress);
    var nextSlug = next && next.entry.lesson.slug;
    var count = lp.total, modules = (level.modules || []).length;
    var card = el("section", { class: "card level" + (open ? "" : " is-locked"), id: "level-" + level.number,
                               "aria-labelledby": "levelTitle" + level.number });
    var title = el("h2", { id: "levelTitle" + level.number }, [el("span", { class: "sr-only", text: "Level " + level.number + ": " }), level.title]);
    if (!open) title.appendChild(el("span", { class: "lock-pill" }, [A.icon("lock"), "Members"]));
    else if (level.free && !progress.member) title.appendChild(el("span", { class: "badge", text: "Free" }));
    card.appendChild(el("div", { class: "level-head" }, [
      el("span", { class: "level-num", "aria-hidden": "true", text: level.number }),
      title,
      el("p", { text: level.summary })
    ]));
    var pct = lp.total ? Math.round(lp.done / lp.total * 100) : 0;
    var fill = el("span");
    fill.style.width = pct + "%";
    card.appendChild(el("div", { class: "progress" }, [
      el("div", { class: "bar", "aria-hidden": "true" }, fill),
      el("span", { class: "meta", text: lp.done + " of " + lp.total + " done" })
    ]));

    var details = el("details", { open: nextSlug && next.entry.level === level });
    details.appendChild(el("summary", { text: A.plural(count, "lesson") + (modules > 1 ? " in " + modules + " modules" : "") }));
    (level.modules || []).forEach(function (mod) {
      var rows = el("ul", { class: "rows" });
      (mod.lessons || []).forEach(function (lesson) {
        var entry = { lesson: lesson, module: mod, level: level };
        var s = L.lessonStatus(entry, progress);
        var kind = s === "done" ? "done" : s === "locked" ? "locked" : lesson.slug === nextSlug ? "next" : "open";
        var meta = lesson.minutes + " min";
        if (L.isReviewDue(progress, lesson.slug, day) && open) meta = "Review due";
        rows.appendChild(el("li", { "data-slug": lesson.slug, "data-status": kind }, [
          statusBadge(kind),
          open ? el("a", { class: "title", href: A.lessonHref(lesson.slug), text: lesson.title })
               : el("span", { class: "title", text: lesson.title }),
          el("span", { class: "meta", text: meta })
        ]));
      });
      details.appendChild(el("div", { class: "module" }, [
        el("h3", { text: mod.title }),
        mod.summary ? el("p", { class: "meta", text: mod.summary }) : null,
        rows
      ]));
    });
    card.appendChild(details);
    if (!open) {
      card.appendChild(el("div", { class: "unlock" }, [
        el("a", { class: "btn", href: A.PRICING, text: "Unlock all levels" }),
        el("a", { href: "account.html", text: "Or try the demo membership" })
      ]));
    }
    return card;
  }

  function render() {
    if (!curriculum) return;
    var progress = A.loadProgress(), day = L.today();
    var next = L.nextLesson(curriculum, progress);
    var overall = L.overallProgress(curriculum, progress);
    A.clear(root);
    root.appendChild(nextCard(next, overall, progress));
    var rc = reviewCard(L.dueReviews(curriculum, progress, day), L.upcomingReview(curriculum, progress, day), day);
    if (rc) root.appendChild(rc);
    (curriculum.levels || []).forEach(function (level) { root.appendChild(levelCard(level, progress, next, day)); });
    root.removeAttribute("aria-busy");
  }

  A.loadCurriculum().then(function (c) { curriculum = c; render(); })
    .catch(function () { A.showError(root, "We couldn't load the lessons. Check your connection and reload the page."); });
  // Coming back with the Back button (page cache) or a change in another tab: redraw from storage.
  window.addEventListener("pageshow", function (e) { if (e.persisted) render(); });
  window.addEventListener("storage", function (e) { if (e.key === L.STORAGE_KEY) render(); });
})();
