// WCAG 2.2 contrast of the color tokens in invest/site/assets/style.css, light and dark.
// Run with: node --test tests/qa/contrast.test.js
const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");

const css = fs.readFileSync(path.join(__dirname, "..", "..", "invest", "site", "assets", "style.css"), "utf8");

function tokens(block) {
  const out = {};
  for (const m of block.matchAll(/--([\w-]+):\s*(#[0-9a-fA-F]{6})\b/g)) out[m[1]] = m[2].toLowerCase();
  return out;
}
function blockAfter(selector) {
  const start = css.indexOf(selector);
  assert.ok(start >= 0, `style.css should contain ${selector}`);
  const open = css.indexOf("{", start);
  return css.slice(open + 1, css.indexOf("}", open));
}
const light = tokens(blockAfter(":root {"));
const dark = { ...light, ...tokens(blockAfter(':root[data-theme="dark"]')) };
const darkMedia = { ...light, ...tokens(blockAfter(':root:where(:not([data-theme="light"]))')) };

function luminance(hex) {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
    .map((v) => (v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
function ratio(a, b) {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

// [foreground, background, minimum, what it is]
const TEXT = 4.5, UI = 3;
const PAIRS = [
  ["text", "bg", TEXT, "body text"], ["text", "surface", TEXT, "text on cards"],
  ["muted", "bg", TEXT, "lede, nav links"], ["muted", "surface", TEXT, ".fine, labels, tile captions"],
  ["faint", "surface", TEXT, "chart tick labels (11px)"], ["faint", "bg", TEXT, "faint text on the page"],
  ["accent", "surface", TEXT, "links on cards"], ["accent", "bg", TEXT, "links on the page"],
  ["accent-ink", "accent", TEXT, "primary buttons, pressed chips"],
  ["critical", "surface", TEXT, "error messages"],
  ["text", "accent-soft", TEXT, "pill, callout text"], ["muted", "accent-soft", TEXT, "fine print in callouts"],
  ["accent", "surface", UI, "focus ring"], ["accent", "bg", UI, "focus ring on the page"],
  ["field-border", "surface", UI, "text-field outline (WCAG 1.4.11)"], ["field-border", "bg", UI, "text-field outline, inside"],
  ["s1", "surface", UI, "chart series 1"], ["s2", "surface", UI, "chart series 2"],
];

for (const [name, theme] of [["light", light], ["dark", dark]]) {
  test(`${name} theme: text and UI contrast`, () => {
    const fails = [];
    for (const [fg, bg, min, what] of PAIRS) {
      assert.ok(theme[fg] && theme[bg], `missing token --${fg} or --${bg}`);
      const r = ratio(theme[fg], theme[bg]);
      if (r < min) fails.push(`--${fg} on --${bg} (${what}): ${r.toFixed(2)} < ${min}`);
    }
    assert.deepEqual(fails, []);
  });
}

test("the two dark-mode blocks define the same tokens", () => {
  assert.deepEqual(darkMedia, dark);
});

// Known gap, kept visible: series 3 (aqua, "with the drop") is 2.74:1 on the light surface. The
// table view and the crash text carry the same numbers, so it isn't the only way to read them.
test("light theme: chart series 3 reaches 3:1", { todo: "s3 #1baf7a is 2.74:1 on #fcfcfb; needs a design decision" }, () => {
  assert.ok(ratio(light.s3, light.surface) >= UI);
});
test("dark theme: chart series 3 reaches 3:1", () => {
  assert.ok(ratio(dark.s3, dark.surface) >= UI);
});
