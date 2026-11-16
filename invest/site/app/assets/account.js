// Account (app/account.html): the demo membership switch and resetting progress. Prototype only:
// no payment, no sign-in, nothing leaves the device.
(function () {
  "use strict";
  var A = window.PMApp, L = A.L;
  function $(id) { return document.getElementById(id); }

  function render() {
    var p = A.loadProgress();
    $("memberStatus").textContent = p.member ? "Demo membership: on." : "Demo membership: off.";
    $("memberOff").classList.toggle("hidden", p.member);
    $("memberOn").classList.toggle("hidden", !p.member);
    var done = Object.keys(p.completed).length, tries = Object.keys(p.quiz).length;
    var due = Object.keys(p.review_due).filter(function (s) { return p.review_due[s] <= L.today(); }).length;
    $("progressSummary").textContent = done || tries
      ? A.plural(done, "lesson") + " completed, " + A.plural(tries, "lesson") + " with a quiz score, " + A.plural(due, "review") + " due."
      : "No progress yet on this device.";
  }

  $("demoCheckout").addEventListener("click", function () {
    A.saveProgress(L.setMember(A.loadProgress(), true));
    render();
    $("endDemo").focus();
  });
  $("endDemo").addEventListener("click", function () {
    A.saveProgress(L.setMember(A.loadProgress(), false));
    render();
    $("demoCheckout").focus();
  });
  $("resetBtn").addEventListener("click", function () { $("resetConfirm").classList.remove("hidden"); $("resetNo").focus(); });
  $("resetNo").addEventListener("click", function () { $("resetConfirm").classList.add("hidden"); $("resetBtn").focus(); });
  $("resetYes").addEventListener("click", function () {
    A.saveProgress(L.resetLearning(A.loadProgress()));
    $("resetConfirm").classList.add("hidden");
    $("resetMsg").textContent = "Progress reset on this device.";
    render();
    $("resetBtn").focus();
  });
  window.addEventListener("pageshow", function (e) { if (e.persisted) render(); });
  render();
})();
