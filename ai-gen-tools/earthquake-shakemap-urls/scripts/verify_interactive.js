// Load a generated shakemap-urls interactive page in a headless DOM, open
// every level's compare panel at DEFAULT settings, and check for:
//   - any window/script error
//   - a path with NaN/Infinity/empty "d" (broken geometry)
//   - a default link over MAX_URL_LEN or left as a MultiPolygon
// The last one is NOT necessarily a failure — with the interactive tool the
// user can just drag the buffer slider themselves (see SKILL.md
// troubleshooting) — but it should be reported so Claude can mention it
// when handing off, rather than silently shipping a level that starts out
// broken with no explanation.
//
// Usage: node verify_interactive.js <path/to/page.html>
// Requires jsdom (npm install jsdom once in this scripts/ directory).
const { JSDOM } = require("jsdom");
const fs = require("fs");
const path = require("path");

const target = process.argv[2];
if (!target) {
  console.error("Usage: node verify_interactive.js <path/to/page.html>");
  process.exit(2);
}

const html = fs.readFileSync(target, "utf8");
const errors = [];

const dom = new JSDOM(html, { runScripts: "dangerously", resources: "usable" });
dom.window.onerror = (msg, src, line) => {
  errors.push(`window error: ${msg} (line ${line})`);
};

setTimeout(() => {
  const doc = dom.window.document;
  const levels = doc.querySelectorAll(".level");
  if (levels.length === 0) {
    errors.push("no .level cards were rendered at all");
  }

  levels.forEach((lvl) => {
    lvl.querySelector(".tune-toggle").dispatchEvent(new dom.window.Event("click", { bubbles: true }));
  });

  setTimeout(() => {
    levels.forEach((lvl) => {
      const mmi = lvl.querySelector(".mmi").textContent;
      const genD = lvl.querySelector(".gen-path").getAttribute("d") || "";
      const refD = lvl.querySelector(".ref-path").getAttribute("d") || "";
      const urlMeta = lvl.querySelector(".url-meta").textContent;

      if (!genD || genD.includes("NaN") || genD.includes("Infinity")) {
        errors.push(`MMI ${mmi}: generated shape path is broken/empty`);
      }
      if (!refD || refD.includes("NaN") || refD.includes("Infinity")) {
        errors.push(`MMI ${mmi}: reference contour path is broken/empty`);
      }
      if (urlMeta.includes("too long") || urlMeta.includes("could not merge")) {
        errors.push(`MMI ${mmi}: default settings need adjustment — ${urlMeta}`);
      }
    });

    if (errors.length) {
      console.log("NOT CLEAN:");
      errors.forEach((e) => console.log(`  - ${e}`));
      process.exit(1);
    }
    console.log("CLEAN");
    process.exit(0);
  }, 800 + levels.length * 100);
}, 1500);
