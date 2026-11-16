// One lesson (app/lesson.html#<slug>): video (or "coming soon"), objectives, key points, the risk
// note, "Try it", the 3-question check and the next lesson. Members-only lessons stay closed.
(function () {
  "use strict";
  var A = window.PMApp, L = A.L, el = A.el;
  var root = document.getElementById("lessonRoot");
  var data = { cur: null, manifest: { videos: {} }, facts: {} };
  var TOOLS = {
    calculator: { href: "../index.html", label: "Open the calculator", title: "Try it with your numbers" },
    "money-map": { href: "money-map.html", label: "Open your Money Map", title: "Try it with your numbers", from: true },
    "crash-sim": { href: "crash-sim.html", label: "Open the crash simulator", title: "Try it", from: true }
  };

  function currentSlug() {
    var raw = location.hash.replace(/^#/, "");
    try { raw = decodeURIComponent(raw); } catch (e) { return null; }
    return L.isSlug(raw) ? raw : null;
  }

  // ---- Pieces ---------------------------------------------------------------------------------------
  function crumbs(entry) {
    return el("nav", { class: "crumbs", "aria-label": "Breadcrumb" }, [
      el("a", { class: "back", href: "index.html" }, ["← Your path"]),
      el("span", { class: "meta", text: "Level " + entry.level.number + " · " + entry.module.title })
    ]);
  }

  function metaLine(entry, progress) {
    var p = el("p", { class: "meta done-note", id: "lessonMeta" }, [entry.lesson.minutes + " min lesson"]);
    var done = progress.completed[entry.lesson.slug], q = progress.quiz[entry.lesson.slug];
    if (done) {
      p.appendChild(el("span", { class: "badge done" }, [A.icon("check"),
        "Completed " + A.niceDate(done) + (q ? " · best " + q.best + " of 3" : "")]));
    }
    return p;
  }

  function soon() {
    return el("div", { class: "video-soon", id: "video", "data-state": "soon" }, [
      A.icon("play"),
      el("strong", { text: "Video coming soon" }),
      el("span", { text: "Every lesson gets a short video made with AI and checked by a person. The key points below cover the same ideas." })
    ]);
  }

  function videoBlock(entry) {
    var v = data.manifest.videos[entry.lesson.slug];
    var mp4 = v && typeof v === "object" ? A.mediaUrl(v.mp4) : null;
    if (!mp4) return soon();
    var fig = el("figure", { class: "video", id: "video", "data-state": "video" });
    var video = el("video", { controls: true, preload: "metadata", playsinline: true, poster: A.mediaUrl(v.poster),
                              "aria-label": "Video: " + entry.lesson.title });
    var source = el("source", { src: mp4, type: "video/mp4" });
    video.appendChild(source);
    var cc = A.mediaUrl(v.captions);
    if (cc) video.appendChild(el("track", { kind: "captions", src: cc, srclang: "en", label: "English", default: true }));
    // A manifest entry whose file isn't there yet falls back to "coming soon".
    function fallback() { if (fig.parentNode) fig.parentNode.replaceChild(soon(), fig); }
    source.addEventListener("error", fallback);
    video.addEventListener("error", fallback);

    var cap = el("figcaption", {});
    var approved = v.approved === true;
    if (!approved) cap.appendChild(el("span", { class: "badge draft" }, [A.icon("alert"), "Draft"]));
    var label = typeof v.ai_label === "string" && v.ai_label.trim() ? v.ai_label.trim() : "Made with AI, reviewed by a person";
    // Until it's approved, nobody has signed off on it, so the label says so.
    cap.appendChild(el("span", { class: "ai-label", text: approved ? label : "Made with AI. Not yet approved by a person." }));
    if (v.narration === "none") cap.appendChild(el("span", { text: "\u00b7 Captions only, no voice" }));
    fig.appendChild(el("div", { class: "video-frame" }, video));
    fig.appendChild(cap);
    return fig;
  }

  function list(items) {
    var ul = el("ul", {});
    (items || []).forEach(function (t) { ul.appendChild(el("li", { text: t })); });
    return ul;
  }

  function learnCard(lesson) {
    return el("section", { class: "card", id: "learnCard", "aria-label": "What this lesson covers" }, [
      el("h2", { text: "What you'll learn" }), list(lesson.objectives),
      el("h2", { text: "Key points" }), list(lesson.key_points)
    ]);
  }

  function riskCallout(lesson) {
    if (typeof lesson.risk_note !== "string" || !lesson.risk_note.trim()) return null;
    return el("aside", { class: "callout risk", id: "riskNote", "aria-labelledby": "riskTitle" }, [
      el("h2", { id: "riskTitle" }, [A.icon("alert"), "Risk to know"]),
      el("p", { text: lesson.risk_note })
    ]);
  }

  function tryIt(lesson) {
    var t = lesson.try_it, tool = t && TOOLS[t.tool];
    if (!tool) return null;
    return el("section", { class: "card try-it", id: "tryIt", "aria-labelledby": "tryTitle" }, [
      el("h2", { id: "tryTitle", text: tool.title }),
      el("p", { text: t.prompt || "" }),
      el("a", { class: "btn", href: tool.href + (tool.from ? "?from=" + lesson.slug : ""), "data-tool": t.tool }, [tool.label, " ", A.icon("arrow")])
    ]);
  }

  function prereqNote(entry, progress) {
    var missing = L.missingPrereqs(entry.lesson, progress).map(function (s) { return L.findLesson(data.cur, s); }).filter(Boolean);
    if (!missing.length) return null;
    var p = el("p", { class: "notice", id: "prereqNote" }, ["This lesson builds on "]);
    missing.forEach(function (m, i) {
      if (i) p.appendChild(document.createTextNode(i === missing.length - 1 ? " and " : ", "));
      p.appendChild(el("a", { href: A.lessonHref(m.lesson.slug), text: m.lesson.title }));
    });
    p.appendChild(document.createTextNode(". You can read it now, or start there first."));
    return p;
  }

  function reviewNote(entry, progress, quizSection) {
    if (!L.isReviewDue(progress, entry.lesson.slug, L.today())) return null;
    var go = el("button", { type: "button", class: "small", text: "Go to the check" });
    go.addEventListener("click", function () {
      quizSection.scrollIntoView({ behavior: "smooth", block: "start" });
      var first = quizSection.querySelector("input");
      if (first) first.focus({ preventScroll: true });
    });
    return el("div", { class: "notice", id: "reviewNote" }, [
      el("p", { class: "done-note" }, [A.icon("review"), el("strong", { text: "Review due." }),
        "Retake the quick check below. It brings the idea back so it sticks."]),
      go
    ]);
  }

  function sourcesCard(lesson) {
    var items = (lesson.needs_facts || []).map(function (k) { return data.facts[k]; }).filter(function (f) {
      return f && A.safeHttpUrl((f.sources || [])[0]);
    });
    if (!items.length) return null;
    var ul = el("ul", {});
    items.forEach(function (f) {
      ul.appendChild(el("li", {}, [f.label + " (" + f.as_of + "): ",
        el("a", { href: A.safeHttpUrl(f.sources[0]), rel: "noopener", text: f.source_name })]));
    });
    return el("section", { class: "card fine sources", id: "sources" }, [el("h2", { text: "Sources" }), ul]);
  }

  function nextBlock(entry, progress) {
    var after = L.lessonAfter(data.cur, entry.lesson.slug);
    var box = el("section", { class: "card", id: "nextLesson", "aria-labelledby": "nextLessonTitle" });
    if (!after) {
      box.appendChild(el("h2", { id: "nextLessonTitle", text: "That's the last lesson on the path" }));
      box.appendChild(el("a", { class: "btn", href: "index.html", text: "Back to your path" }));
      return box;
    }
    box.appendChild(el("p", { class: "kicker", text: "Next lesson" }));
    box.appendChild(el("h2", { id: "nextLessonTitle", text: after.lesson.title }));
    box.appendChild(el("p", { class: "meta", text: (after.level !== entry.level ? "Starts " + A.levelName(after.level) : after.module.title) +
      " · " + after.lesson.minutes + " min" }));
    if (L.canOpen(after, progress)) {
      box.appendChild(el("div", { class: "row-actions" }, [
        el("a", { class: "btn", href: A.lessonHref(after.lesson.slug), id: "nextBtn" }, ["Next lesson ", A.icon("arrow")]),
        el("a", { href: "index.html", text: "Back to your path" })
      ]));
    } else {
      box.appendChild(el("p", { text: "Level " + after.level.number + " is part of membership." }));
      box.appendChild(el("div", { class: "row-actions" }, [
        el("a", { class: "btn", href: A.PRICING, id: "nextUnlock", text: "Unlock all levels" }),
        el("a", { href: "account.html", text: "Try the demo membership" })
      ]));
    }
    return box;
  }

  function lockedPanel(entry) {
    return el("section", { class: "card locked-panel", id: "lockedPanel" }, [
      A.icon("lock"),
      el("h2", { text: "This lesson is for members" }),
      el("p", { text: "It's part of " + A.levelName(entry.level) + ". Membership unlocks Levels 2 to 5, " +
        "and Level 1 stays free." }),
      el("div", { class: "row-actions" }, [
        el("a", { class: "btn", href: A.PRICING, text: "Unlock all levels" }),
        el("a", { class: "btn ghost-btn", href: "account.html", text: "Try the demo membership" })
      ]),
      el("p", {}, el("a", { href: "index.html", text: "Back to your path" }))
    ]);
  }

  // ---- The 3-question check ---------------------------------------------------------------------
  function quizBlock(entry, onRecorded) {
    var lesson = entry.lesson, quiz = lesson.quiz || [];
    var sec = el("section", { class: "card quiz", id: "quiz", "aria-labelledby": "quizTitle" });
    sec.appendChild(el("h2", { id: "quizTitle", text: "Quick check" }));
    sec.appendChild(el("p", { class: "fine", text: "Get " + L.PASS_MARK + " of " + quiz.length +
      " right to complete the lesson. You can try as many times as you like." }));
    var form = el("form", { id: "quizForm", novalidate: true });
    quiz.forEach(function (q, i) {
      var fs = el("fieldset", { "data-q": i }, el("legend", { text: (i + 1) + ". " + q.q }));
      (q.choices || []).forEach(function (c, j) {
        var id = "q" + i + "c" + j;
        fs.appendChild(el("label", { class: "choice", for: id, "data-choice": j }, [
          el("input", { type: "radio", name: "q" + i, id: id, value: j }),
          el("span", { text: c }),
          el("span", { class: "mark" })
        ]));
      });
      fs.appendChild(el("p", { class: "why hidden", id: "why" + i }));
      form.appendChild(fs);
    });
    var err = el("p", { class: "error", id: "quizError", role: "alert" });
    var result = el("div", { class: "result", id: "quizResult", role: "status", tabindex: "-1" });
    var check = el("button", { type: "submit", class: "primary", id: "checkBtn", text: "Check answers" });
    var retry = el("button", { type: "button", class: "ghost hidden", id: "retryBtn", text: "Try again" });
    form.appendChild(err);
    form.appendChild(result);
    form.appendChild(el("div", { class: "row-actions" }, [check, retry]));
    sec.appendChild(form);

    function inputs() { return Array.prototype.slice.call(form.querySelectorAll("input[type=radio]")); }

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var answers = quiz.map(function (q, i) {
        var c = form.querySelector('input[name="q' + i + '"]:checked');
        return c ? parseInt(c.value, 10) : null;
      });
      var empty = answers.indexOf(null);
      if (empty >= 0) {
        err.textContent = "Answer all " + quiz.length + " questions first.";
        form.querySelector('input[name="q' + empty + '"]').focus();
        return;
      }
      err.textContent = "";
      var score = L.scoreQuiz(quiz, answers);
      var day = L.today();
      var rec = L.recordQuiz(A.loadProgress(), lesson.slug, score.correct, day);
      A.saveProgress(rec.progress);

      quiz.forEach(function (q, i) {
        var r = score.results[i];
        Array.prototype.forEach.call(form.querySelectorAll('[data-q="' + i + '"] .choice'), function (label) {
          var j = +label.getAttribute("data-choice"), mark = label.querySelector(".mark");
          A.clear(mark);
          if (j === q.answer) { label.classList.add("is-answer"); A.append(mark, [A.icon("check"), "Correct"]); }
          else if (j === r.chosen) { label.classList.add("is-wrong"); A.append(mark, [A.icon("cross"), "Your answer"]); }
        });
        var why = document.getElementById("why" + i);
        A.clear(why);
        A.append(why, [el("b", { text: r.correct ? "Right." : "Not quite." }), q.why || ""]);
        why.classList.remove("hidden");
      });
      inputs().forEach(function (x) { x.disabled = true; });
      sec.classList.add("checked");

      A.clear(result);
      result.className = "result " + (score.passed ? "pass" : "fail");
      var head = score.correct + " of " + score.total + " right. ";
      var p = rec.progress, next = p.review_due[lesson.slug];
      if (rec.event === "completed") {
        A.append(result, [el("p", { text: head + "Lesson complete." }),
          el("p", { text: next ? "It comes back for a quick review on " + A.niceDate(next) + "." : "" })]);
      } else if (rec.event === "reviewed") {
        A.append(result, [el("p", { text: head + "Review done." }),
          el("p", { text: next ? "Next review: " + A.niceDate(next) + "." : "That was its last scheduled review." })]);
      } else if (rec.event === "retake") {
        A.append(result, el("p", { text: head + "You've already completed this lesson." }));
      } else {
        A.append(result, [el("p", { text: head + "You need " + L.PASS_MARK + " of " + score.total + " to complete this lesson." }),
          el("p", { text: "Read why under each question, then try again." })]);
      }
      check.classList.add("hidden");
      retry.classList.remove("hidden");
      result.focus();
      onRecorded(rec.progress);
    });

    retry.addEventListener("click", function () {
      inputs().forEach(function (x) { x.disabled = false; x.checked = false; });
      Array.prototype.forEach.call(form.querySelectorAll(".choice"), function (c) {
        c.classList.remove("is-answer", "is-wrong"); A.clear(c.querySelector(".mark"));
      });
      Array.prototype.forEach.call(form.querySelectorAll(".why"), function (w) { w.classList.add("hidden"); A.clear(w); });
      A.clear(result); result.className = "result";
      sec.classList.remove("checked");
      check.classList.remove("hidden");
      retry.classList.add("hidden");
      var first = inputs()[0];
      if (first) first.focus();
    });
    return sec;
  }

  // ---- Page ---------------------------------------------------------------------------------------
  function message(title, text) {
    A.clear(root);
    document.title = title + " | Patient Money";
    var h1 = el("h1", { tabindex: "-1", text: title });
    root.appendChild(h1);
    root.appendChild(el("p", { class: "lede", text: text }));
    root.appendChild(el("p", {}, el("a", { class: "btn", href: "index.html", text: "Go to your path" })));
    return h1;
  }

  function render() {
    var slug = currentSlug();
    var entry = slug && L.findLesson(data.cur, slug);
    if (!entry) {
      return location.hash
        ? message("We couldn't find that lesson", "It may have moved. Your path lists every lesson.")
        : message("Pick a lesson", "Your path shows every lesson in order, with the next one to do at the top.");
    }
    var progress = A.loadProgress();
    A.clear(root);
    document.title = entry.lesson.title + " | Patient Money";
    root.appendChild(crumbs(entry));
    var h1 = el("h1", { tabindex: "-1", id: "lessonTitle", text: entry.lesson.title });
    root.appendChild(h1);
    if (!L.canOpen(entry, progress)) {
      root.appendChild(lockedPanel(entry));
      return h1;
    }
    var meta = metaLine(entry, progress);
    root.appendChild(meta);
    var nextBox = nextBlock(entry, progress);
    var quiz = quizBlock(entry, function (p) {
      var fresh = metaLine(entry, p);
      meta.parentNode.replaceChild(fresh, meta); meta = fresh;
      var rn = document.getElementById("reviewNote");
      if (rn && !L.isReviewDue(p, entry.lesson.slug, L.today())) rn.remove();
    });
    [reviewNote(entry, progress, quiz), prereqNote(entry, progress), videoBlock(entry), learnCard(entry.lesson),
     riskCallout(entry.lesson), tryIt(entry.lesson), quiz, sourcesCard(entry.lesson), nextBox]
      .forEach(function (n) { if (n) root.appendChild(n); });
    return h1;
  }

  function show(moveFocus) {
    var h1 = render();
    root.removeAttribute("aria-busy");
    if (moveFocus) { window.scrollTo(0, 0); if (h1) h1.focus({ preventScroll: true }); }
  }

  Promise.all([A.loadCurriculum(), A.loadManifest(), A.loadFacts()]).then(function (r) {
    data.cur = r[0]; data.manifest = r[1]; data.facts = r[2];
    show(false);
    window.addEventListener("hashchange", function () { show(true); });
    window.addEventListener("pageshow", function (e) { if (e.persisted) show(false); });
  }).catch(function () {
    root.removeAttribute("aria-busy");
    A.showError(root, "We couldn't load the lessons. Check your connection and reload the page.");
  });
})();
