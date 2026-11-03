// Water Skin Check — runs entirely in the browser. Data: data/water.json (built by `python -m company build-site`).
(function (root) {
  "use strict";

  // ZIP3 prefix ranges -> state (USPS). Inclusive ranges.
  var ZIP3_STATES = [
    [5, 5, "NY"], [10, 27, "MA"], [28, 29, "RI"], [30, 38, "NH"], [39, 49, "ME"],
    [50, 54, "VT"], [55, 55, "MA"], [56, 59, "VT"], [60, 69, "CT"], [70, 89, "NJ"],
    [100, 149, "NY"], [150, 196, "PA"], [197, 199, "DE"], [200, 200, "DC"], [201, 201, "VA"],
    [202, 205, "DC"], [206, 219, "MD"], [220, 246, "VA"], [247, 268, "WV"], [270, 289, "NC"],
    [290, 299, "SC"], [300, 319, "GA"], [320, 339, "FL"], [341, 349, "FL"], [350, 369, "AL"],
    [370, 385, "TN"], [386, 397, "MS"], [398, 399, "GA"], [400, 427, "KY"], [430, 459, "OH"],
    [460, 479, "IN"], [480, 499, "MI"], [500, 528, "IA"], [530, 549, "WI"], [550, 567, "MN"],
    [569, 569, "DC"], [570, 577, "SD"], [580, 588, "ND"], [590, 599, "MT"], [600, 629, "IL"],
    [630, 658, "MO"], [660, 679, "KS"], [680, 693, "NE"], [700, 714, "LA"], [716, 729, "AR"],
    [730, 749, "OK"], [750, 799, "TX"], [800, 816, "CO"], [820, 831, "WY"], [832, 838, "ID"],
    [840, 847, "UT"], [850, 865, "AZ"], [870, 884, "NM"], [885, 885, "TX"], [889, 898, "NV"],
    [900, 961, "CA"], [967, 968, "HI"], [970, 979, "OR"], [980, 994, "WA"], [995, 999, "AK"]
  ];

  var HARDNESS_LABEL = { soft: "Soft", moderate: "Moderately hard", hard: "Hard", very_hard: "Very hard" };
  var HARDNESS_POINTS = { soft: 0, moderate: 1, hard: 2, very_hard: 3 };
  var DISINFECTANT_POINTS = { chlorine: 1.5, chloramine: 2, unknown: 1 };

  function stateForZip(zip) {
    var p = parseInt(zip.slice(0, 3), 10);
    for (var i = 0; i < ZIP3_STATES.length; i++) {
      var r = ZIP3_STATES[i];
      if (p >= r[0] && p <= r[1]) return r[2];
    }
    return null;
  }

  // USGS classes, mg/L as CaCO3.
  function hardnessCategory(mgL) {
    if (mgL <= 60) return "soft";
    if (mgL <= 120) return "moderate";
    if (mgL <= 180) return "hard";
    return "very_hard";
  }

  function assess(zip, data) {
    if (!/^\d{5}$/.test(zip)) return { error: "Please enter a 5-digit US ZIP code." };
    var zip3 = zip.slice(0, 3);
    var city = null;
    for (var i = 0; i < data.cities.length; i++) {
      if (data.cities[i].zip3.indexOf(zip3) !== -1) { city = data.cities[i]; break; }
    }
    var state = city ? city.state : stateForZip(zip);
    if (!state) return { error: "We couldn't match that ZIP code to a US state." };

    var category, disinfectant, area, confidence, mgL = null;
    if (city) {
      mgL = city.hardness_mg_l;
      category = hardnessCategory(mgL);
      disinfectant = city.disinfectant;
      area = city.city + ", " + city.state + " area";
      confidence = city.verified ? "verified" : "estimate";
    } else {
      category = data.states[state];
      if (!category) return { error: "We don't have data for that area yet." };
      disinfectant = "unknown";
      area = state + " (statewide)";
      confidence = "regional";
    }

    var raw = (HARDNESS_POINTS[category] / 3) * 5 + (DISINFECTANT_POINTS[disinfectant] / 2) * 5;
    var score = Math.round(raw * 10) / 10;
    var level = score < 4 ? "low" : score < 7 ? "mid" : "high";

    return {
      zip: zip, state: state, city: city, area: area, mgL: mgL,
      hardness: category, disinfectant: disinfectant, confidence: confidence,
      score: score, level: level, recommendations: recommend(category, disinfectant)
    };
  }

  function recommend(category, disinfectant) {
    var recs = [];
    if (disinfectant === "chloramine") {
      recs.push({ text: "Your utility uses chloramine. Many basic carbon shower filters don't remove it well. Look for a vitamin C or catalytic-carbon shower filter with test results for chloramine.", link: "chloramineShowerFilter" });
    } else if (disinfectant === "chlorine") {
      recs.push({ text: "Your utility uses chlorine. A carbon or KDF shower filter with independent test results can reduce chlorine in your shower.", link: "chlorineShowerFilter" });
    } else {
      recs.push({ text: "Check whether your utility uses chlorine or chloramine (it's in your annual Consumer Confidence Report). That decides which shower filter type works.", link: null });
    }
    if (category === "hard" || category === "very_hard") {
      recs.push({ text: "Your water is hard. Shower filters reduce chlorine but generally do not soften water. Only a whole-home water softener reduces hardness.", link: "softenerGuide" });
    }
    recs.push({ text: "For baths, especially for kids, a vitamin C bath dechlorinator neutralizes chlorine and chloramine in the tub.", link: "bathDechlorinator" });
    recs.push({ text: "Gentle routine: lukewarm water, short showers, fragrance-free cleanser, pat dry, and moisturize within a few minutes.", link: null });
    return recs;
  }

  root.WaterCheck = { assess: assess, stateForZip: stateForZip, hardnessCategory: hardnessCategory };
  if (typeof module !== "undefined" && module.exports) { module.exports = root.WaterCheck; return; }

  // ---------- Browser UI ----------
  var cfg = root.SITE_CONFIG || { links: {} };
  var $ = function (id) { return document.getElementById(id); };
  var dataPromise = fetch("data/water.json").then(function (r) { return r.json(); });

  if (cfg.brand) { $("brand").textContent = cfg.brand; }

  $("zipForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var zip = $("zip").value.trim();
    dataPromise.then(function (data) { show(assess(zip, data)); })
      .catch(function () { showError("Couldn't load water data. Please try again."); });
  });

  function showError(msg) {
    $("zipError").textContent = msg;
    $("zipError").classList.remove("hidden");
    $("result").classList.add("hidden");
  }

  function show(res) {
    if (res.error) { showError(res.error); return; }
    $("zipError").classList.add("hidden");
    $("scoreNum").textContent = res.score.toFixed(1);
    $("scoreNum").className = "num lvl-" + res.level;
    $("scoreLabel").textContent = { low: "Gentle", mid: "Moderate", high: "Harsh" }[res.level];
    $("scoreLabel").className = "label lvl-" + res.level;
    $("area").textContent = res.area;
    $("hardness").textContent = HARDNESS_LABEL[res.hardness] + (res.mgL ? " (~" + res.mgL + " mg/L)" : "");
    $("disinfectant").textContent = { chlorine: "Chlorine", chloramine: "Chloramine", unknown: "Unknown" }[res.disinfectant];
    $("confidence").textContent = {
      verified: "Verified against your utility's latest water quality report.",
      estimate: "Estimate for this metro area — we're verifying it against the utility's latest report.",
      regional: "Statewide estimate only. Hardness varies a lot by town — check your utility's Consumer Confidence Report."
    }[res.confidence];

    var ul = $("recs");
    ul.innerHTML = "";
    res.recommendations.forEach(function (r) {
      var li = document.createElement("li");
      li.textContent = r.text + " ";
      var url = r.link && cfg.links && cfg.links[r.link];
      if (url) {
        var a = document.createElement("a");
        a.href = url; a.rel = "sponsored noopener"; a.target = "_blank"; a.textContent = "See our pick →";
        li.appendChild(a);
      }
      ul.appendChild(li);
    });
    $("signupZip").value = res.zip;
    $("result").classList.remove("hidden");
  }

  $("signupForm").addEventListener("submit", function (e) {
    var msg = $("signupMsg");
    msg.classList.remove("hidden");
    if (!cfg.signupEndpoint) {
      e.preventDefault();
      msg.textContent = "Sign-ups aren't connected yet. Add your email provider's form URL in assets/config.js.";
      return;
    }
    this.action = cfg.signupEndpoint;
    msg.textContent = "Thanks! Check your inbox.";
  });
})(typeof window !== "undefined" ? window : globalThis);
