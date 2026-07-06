// Standalone regression test (run: node site/theater/scene_smoke_test.js). No deps.
// Drives the REAL renderScene through E01 against a DOM stub whose insertBefore
// throws like a browser when the ref is not a child — catches the 2026-07-06
// scene freeze. Extend beats/events as more scenes are authored.
"use strict";
// End-to-end test of the REAL renderScene from app.js against a DOM stub whose
// insertBefore throws when the reference node isn't a child — exactly the browser
// behavior that froze E01. Drives E01's actual scene to completion.
const fs = require("fs");
const vm = require("vm");
const path = require("path");

const REPO = "c:\\Users\\user\\Desktop\\倉庫";
const appSrc = fs.readFileSync(path.join(__dirname, "app.js"), "utf8");
const events = JSON.parse(fs.readFileSync(path.join(__dirname, "gamedata/events.json"), "utf8"));

let threw = null;

class Node {
  constructor(tag) { this.tag = tag; this.children = []; this._cls = new Set(); this._ev = {}; this.dataset = {}; this.style = {}; this.disabled = false; this._text = ""; this._html = ""; }
  set className(v) { this._cls = new Set(String(v).split(/\s+/).filter(Boolean)); }
  get className() { return [...this._cls].join(" "); }
  set textContent(v) { this._text = v; }
  get textContent() { return this._text; }
  set innerHTML(v) { this._html = v; }
  get innerHTML() { return this._html; }
  append(...ns) { for (const n of ns) if (n instanceof Node) { n.parent = this; this.children.push(n); } }
  appendChild(n) { this.append(n); return n; }
  insertBefore(n, ref) {
    const idx = this.children.indexOf(ref);
    if (idx === -1) throw new Error("insertBefore: reference node is not a child (THE BUG)");
    n.parent = this; this.children.splice(idx, 0, n); return n;
  }
  remove() { if (this.parent) { const i = this.parent.children.indexOf(this); if (i >= 0) this.parent.children.splice(i, 1); } }
  addEventListener(t, fn) { (this._ev[t] = this._ev[t] || []).push(fn); }
  click() { (this._ev.click || []).forEach((fn) => fn({})); }
  get classList() {
    const c = this._cls;
    return { add: (x) => c.add(x), remove: (x) => c.delete(x), contains: (x) => c.has(x), toggle: (x, f) => (f === undefined ? (c.has(x) ? c.delete(x) : c.add(x)) : (f ? c.add(x) : c.delete(x))) };
  }
  scrollIntoView() {}
  _walk(out) { out.push(this); this.children.forEach((c) => c._walk(out)); }
  querySelectorAll(sel) {
    const cls = sel.replace(/^\./, "");
    const all = []; this.children.forEach((c) => c._walk(all));
    return all.filter((n) => n._cls.has(cls));
  }
  querySelector(sel) { return this.querySelectorAll(sel)[0] || null; }
}

const doc = {
  createElement: (t) => new Node(t),
  querySelector: () => new Node("stub"),
  addEventListener: () => {},
  body: new Node("body"),
};
const sandbox = {
  document: doc, window: {}, console,
  crypto: { getRandomValues: (a) => a },
  localStorage: { getItem: () => null, setItem: () => {}, removeItem: () => {} },
  fetch: () => Promise.reject(new Error("no fetch in test")),
  alert: () => {},
  setTimeout: (fn) => fn && fn(),
  Image: function () { return {}; },
  navigator: {},
};
sandbox.globalThis = sandbox; sandbox.window = sandbox;

// export the internals we test, without editing the file on disk
const wrapped = appSrc + "\n;globalThis.__T = { el, esc, npcAvatar, sceneBeat, renderScene, S };";
vm.createContext(sandbox);
try { vm.runInContext(wrapped, sandbox, { filename: "app.js" }); }
catch (e) { console.error("LOAD ERROR:", e.message); process.exit(1); }

const T = sandbox.__T;
if (!T || !T.renderScene) { console.error("could not export renderScene"); process.exit(1); }

// minimal S.data for sceneBeat
T.S.data = { npcs: { hengshu: { name: "衡樞" }, shen_weibai: { name: "沈未白" } } };
T.S._sceneChoices = [];
T.S.code = "TESTCODE00";

const e01 = events[0];
console.log("E01 scene beats:", e01.scene.length);

const mount = new Node("div");
let doneCalled = false;
try {
  T.renderScene(e01, mount, () => { doneCalled = true; });
} catch (e) { threw = "renderScene initial: " + e.message; }

let guard = 0;
while (!threw && !doneCalled && guard++ < 40) {
  const choices = mount.querySelectorAll("scene-choice");
  const active = choices[choices.length - 1];
  if (!active) { threw = "no active choice box but not done (stuck)"; break; }
  try {
    const opts = active.querySelectorAll("scene-opt").filter((o) => !o.disabled);
    if (opts.length) opts[0].click();               // explore one thread
    const cont = active.querySelectorAll("scene-advance")[0];
    if (!cont) { threw = "no 繼續 button in choice (stuck)"; break; }
    if (cont.classList.contains("hidden")) { threw = "繼續 still hidden after clicking option (stuck)"; break; }
    cont.click();                                    // advance
  } catch (e) { threw = "drive loop: " + e.message; break; }
}

// assertions
const flatBeats = [];
mount.querySelectorAll("scene-narration").forEach(() => flatBeats.push("n"));
mount.querySelectorAll("npc-line").forEach(() => flatBeats.push("d"));

console.log("---- RESULT ----");
if (threw) { console.log("FAIL:", threw); process.exit(1); }
if (!doneCalled) { console.log("FAIL: onDone never fired (scene never reached the decision — FROZEN)"); process.exit(1); }
console.log("onDone fired:", doneCalled);
console.log("scene_choices recorded:", JSON.stringify(T.S._sceneChoices.map((c) => c.chose)));
console.log("narration+dialogue nodes rendered:", flatBeats.length);
if (T.S._sceneChoices.length < 2) { console.log("FAIL: expected >=2 scene choices explored"); process.exit(1); }
console.log("PASS: E01 scene drives from first beat to the decision without freezing");
