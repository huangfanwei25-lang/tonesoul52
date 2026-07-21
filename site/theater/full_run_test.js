// Standalone FULL-PLAYTHROUGH regression test (run: node site/theater/full_run_test.js). No deps.
// Extends scene_smoke_test.js's DOM stub to drive the REAL game end to end:
// cold open state → mission → all stations (scenes, options, reasons, probe/nag,
// silence, wellbeing skip, mirror) → both ch8 branches → ending (three questions,
// family classification, material record) → trace payload. Four player personas:
//   engaged   — branch A, rich reasons, echo activities, mirror=承認, ending=承認
//   hostile   — branch B, "怕。" reasons (probe), one silence, one skip, mirror=拒絕
//   ghost     — silence at every station (default rail all the way)
//   returning — plays 3 chapters, "closes the tab", resumes from save, finishes
// Any uncaught throw or stuck screen = FAIL. Assertions on trace/ending shape.
"use strict";
const fs = require("fs");
const vm = require("vm");
const path = require("path");

const appSrc = fs.readFileSync(path.join(__dirname, "app.js"), "utf8");
const gamedata = {};
for (const n of ["events", "npcs", "locations", "council_player_projection", "entities"]) {
  gamedata[n] = JSON.parse(fs.readFileSync(path.join(__dirname, `gamedata/${n}.json`), "utf8"));
}

/* ── DOM stub (superset of scene_smoke_test.js) ── */
class Node {
  constructor(tag) {
    this.tag = tag; this.children = []; this._cls = new Set(); this._ev = {};
    this.dataset = {}; this.style = {}; this.disabled = false;
    this._text = ""; this._html = ""; this.value = ""; this.title = "";
  }
  set className(v) { this._cls = new Set(String(v).split(/\s+/).filter(Boolean)); }
  get className() { return [...this._cls].join(" "); }
  set textContent(v) { this._text = String(v); }
  get textContent() { return this._text; }
  set innerHTML(v) { this._html = String(v); if (this._html === "") this.children = []; }
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
  click() { if (this.disabled) return; (this._ev.click || []).forEach((fn) => fn({})); }
  get classList() {
    const c = this._cls;
    return { add: (x) => c.add(x), remove: (x) => c.delete(x), contains: (x) => c.has(x),
      toggle: (x, f) => (f === undefined ? (c.has(x) ? c.delete(x) : c.add(x)) : (f ? c.add(x) : c.delete(x))) };
  }
  scrollIntoView() {}
  get parentElement() { return this.parent || null; }
  getContext() { // share-card canvas: every 2d method is a no-op
    return new Proxy({ measureText: () => ({ width: 0 }) }, { get: (t, k) => (k in t ? t[k] : () => {}) });
  }
  toDataURL() { return "data:image/png;base64,"; }
  toBlob(cb) { cb && cb({}); }
  _walk(out) { out.push(this); this.children.forEach((c) => c._walk(out)); }
  matchesClass(cls) { return this._cls.has(cls); }
  querySelectorAll(sel) {
    const all = []; this.children.forEach((c) => c._walk(all));
    const wanted = String(sel).split(",").map((s) => {
      const parts = s.trim().split(/\s+/);
      return parts[parts.length - 1].replace(/^\./, "");
    });
    return all.filter((n) => wanted.some((w) => n._cls.has(w)));
  }
  querySelector(sel) { return this.querySelectorAll(sel)[0] || null; }
}

function makeSandbox(storeObj) {
  const byId = new Map();
  const doc = {
    createElement: (t) => new Node(t),
    querySelector: (sel) => {
      if (!byId.has(sel)) {
        const n = new Node("div#" + sel);
        n.parent = new Node("stub-parent"); // renderHUD touches parentElement.dataset
        byId.set(sel, n);
      }
      return byId.get(sel);
    },
    addEventListener: () => {},
    body: new Node("body"),
  };
  const sandbox = {
    document: doc, console,
    crypto: { getRandomValues: (a) => { for (let i = 0; i < a.length; i++) a[i] = (i * 37) % 256; return a; } },
    localStorage: {
      getItem: (k) => (k in storeObj ? storeObj[k] : null),
      setItem: (k, v) => { storeObj[k] = String(v); },
      removeItem: (k) => { delete storeObj[k]; },
    },
    fetch: () => Promise.reject(new Error("no fetch in test")),
    alert: () => {},
    setTimeout: (fn) => fn && fn(),
    Image: function () { return { set src(_) { this.onload && this.onload(); }, }; },
    navigator: {},
    Blob: function (parts) { this.size = String(parts && parts[0] || "").length; },
    File: function (parts, name) { this.name = name; this.size = 0; },
    URL: { createObjectURL: () => "blob:test", revokeObjectURL: () => {} },
    location: { reload: () => {} },
    scrollTo: () => {},
    open: () => {},
  };
  sandbox.globalThis = sandbox; sandbox.window = sandbox;
  const wrapped = appSrc + "\n;globalThis.__T = { S, el, startGame, renderChapter, renderEnding, buildTracePayload, traceJson, loadSave, save, endingAxes, classifyEndingFamily };";
  vm.createContext(sandbox);
  vm.runInContext(wrapped, sandbox, { filename: "app.js" });
  const T = sandbox.__T;
  // inject real gamedata exactly the way loadData() does
  T.S.data = {
    events: gamedata.events,
    npcs: Object.fromEntries(gamedata.npcs.map((n) => [n.id, n])),
    locations: Object.fromEntries(gamedata.locations.map((l) => [l.id, l])),
    verdicts: gamedata.council_player_projection.verdicts,
    verdictMeta: gamedata.council_player_projection._meta,
    entities: gamedata.entities.entities || [],
  };
  return { T, doc, sandbox };
}

/* ── drive helpers ── */
const byText = (nodes, txt) => nodes.find((n) => n.textContent && n.textContent.includes(txt));

function driveScene(stage, pickLast) { // click through an active scene until options appear or scene ends
  let guard = 0;
  while (guard++ < 80) {
    const choices = stage.querySelectorAll("scene-choice");
    const active = choices[choices.length - 1];
    if (!active) return; // no scene or already done
    const opts = active.querySelectorAll("scene-opt").filter((o) => !o.disabled);
    if (opts.length) opts[pickLast ? opts.length - 1 : 0].click();
    const cont = active.querySelectorAll("scene-advance")[0];
    if (!cont) return;
    if (cont.classList.contains("hidden")) throw new Error("scene: 繼續 hidden after option click");
    cont.click();
    if (stage.querySelectorAll("opt-box").length) return; // decision reached
  }
  throw new Error("scene: drive guard exceeded (stuck)");
}

function currentStation(T) { return T.S.playlist[T.S.idx]; }

function playTurn(T, stage, persona, log) {
  const eid = currentStation(T);
  driveScene(stage); // no-op for un-scened stations
  const optBoxes = stage.querySelectorAll("opt-box");
  if (!optBoxes.length) throw new Error(`${eid}: no opt-box after scene`);
  const box = optBoxes[optBoxes.length - 1];

  if (persona.silenceAt && persona.silenceAt.has(eid)) {
    const s = byText(box.querySelectorAll("pick"), "保持沉默");
    if (!s) throw new Error(`${eid}: no silence button`);
    s.click(); log.push(`${eid}:silence`);
  } else if (persona.skipAt && persona.skipAt.has(eid)) {
    const sk = box.querySelectorAll("skip-wellbeing")[0];
    if (!sk) throw new Error(`${eid}: expected wellbeing skip button (p>=3)`);
    sk.click(); log.push(`${eid}:skip`);
  } else {
    const picks = box.querySelectorAll("pick").filter((b) => b.textContent === "拉下這一桿");
    if (!picks.length) throw new Error(`${eid}: no option pick buttons`);
    picks[Math.min(persona.optIndex || 0, picks.length - 1)].click();

    const rbox = stage.querySelectorAll("reason-box").pop();
    if (!rbox) throw new Error(`${eid}: reason box did not appear`);
    const ta = rbox.querySelectorAll("").length ? null : rbox.children.find((c) => c.tag === "textarea");
    if (!ta) throw new Error(`${eid}: no reason textarea`);
    const submit = byText(rbox.querySelectorAll("pick"), "留下理由");
    if (!submit) throw new Error(`${eid}: no 留下理由 button`);

    if (persona.testNagOnce && !persona._nagged) {
      persona._nagged = true;
      ta.value = ""; submit.click();
      if (!rbox.querySelectorAll("reason-nag").length) throw new Error(`${eid}: empty reason accepted (nag missing)`);
      log.push(`${eid}:nag-ok`);
    }
    ta.value = persona.reason(eid);
    submit.click();
    const probeDone = byText(rbox.querySelectorAll("pick"), "就這樣");
    if (probeDone) { log.push(`${eid}:probe`); probeDone.click(); }
    log.push(`${eid}:chose`);
  }

  // response screen: maybe mirror, then next
  const mirrors = stage.querySelectorAll("mirror-resp");
  if (mirrors.length) {
    const want = byText(mirrors, persona.mirror || "承認") || mirrors[0];
    want.click(); log.push(`${eid}:mirror`);
  }
  const next = stage.querySelectorAll("next")[0] || byText(stage.querySelectorAll("pick"), "前往下一站")
    || byText(stage.querySelectorAll("pick"), "生成責任結局");
  if (!next) throw new Error(`${eid}: no next button on response screen`);
  next.click();
}

function maybeRoute(T, stage, branch) {
  const routes = stage.querySelectorAll("route");
  if (routes.length) {
    routes[branch === "B" ? 1 : 0].click();
    return true;
  }
  return false;
}

function runGame(persona) {
  const store = {};
  const { T, doc } = makeSandbox(store);
  const stage = doc.querySelector("#stage");
  const log = [];
  T.S.code = "TESTCODE00"; // the consent gate mints this; the gate itself is out of scope here
  T.startGame(false); // mission brief
  const go = byText(stage.querySelectorAll("pick"), "上任");
  if (!go) throw new Error("mission: no 上任 button");
  go.click();

  let guard = 0;
  while (T.S.idx < T.S.playlist.length && guard++ < 40) {
    if (maybeRoute(T, stage, persona.branch)) continue;
    if (persona.stopAfter && log.filter((l) => l.includes(":chose") || l.includes(":silence") || l.includes(":skip")).length >= persona.stopAfter) {
      return { T, store, log, stopped: true };
    }
    playTurn(T, stage, persona, log);
  }
  if (guard >= 40) throw new Error("game loop guard exceeded");

  // ending assertions
  const ending = doc.querySelector("#ending-content");
  if (!ending.children.length) throw new Error("ending: empty content");
  const seal = byText(ending.querySelectorAll("pick"), persona.seal || "承認");
  if (!seal) throw new Error("ending: no seal button");
  seal.click();
  const fam = T.classifyEndingFamily();
  const axes = T.endingAxes();
  const payload = T.buildTracePayload();
  const turns = payload.turns.filter((t) => t.event_id !== "SEAL").length;
  if (turns !== 11) throw new Error(`trace turns=${turns}, expected 11 stations`);
  if (!payload.trace_code) throw new Error("trace missing trace_code");
  if (payload.consent.submission_lane !== "none (download-only)") {
    throw new Error("trace incorrectly advertises a public submission lane");
  }
  // director-lite pilot: E01/E02 turns must carry entity_changes; entity state must move off baseline
  for (const eid of ["E01", "E02"]) {
    const turn = payload.turns.find((t) => t.event_id === eid);
    if (turn && !turn.choice.wellbeing_skip && !turn.entity_changes) {
      throw new Error(`${eid}: turn missing entity_changes (director-lite)`);
    }
  }
  if (T.S.entities) {
    const six = T.S.entities.grey_waitlist_six;
    if (six && six.card["處境"] === "避難名額候補序列上,含一戶照顧臥床母親的獨居女兒" &&
        !persona.silenceAt) {
      // engaged/hostile personas made a real E01 choice; the six-household card must have moved
      if (!persona.silenceAt || !persona.silenceAt.has("E01")) {
        throw new Error("E01: grey_waitlist_six card unchanged after a real choice");
      }
    }
  }
  JSON.parse(T.traceJson()); // download payload must be valid JSON
  // download button must not throw
  const dl = byText(ending.querySelectorAll("pick"), "下載我的軌痕");
  if (dl) dl.click();
  const share = byText(ending.querySelectorAll("pick"), "分享") || byText(ending.querySelectorAll("pick"), "生成分享卡");
  if (share) share.click();
  return { T, store, log, fam, axes, payload };
}

/* ── personas ── */
const RICH = "我知道有人會因此受害,這個代價我來承擔,後果我擔,之後我會補償他們。";
const personas = {
  engaged: { branch: "A", optIndex: 0, reason: () => RICH, mirror: "承認", seal: "承認" },
  hostile: {
    branch: "B", optIndex: 1, reason: () => "怕。", mirror: "拒絕", seal: "不承認",
    silenceAt: new Set(["E07"]), skipAt: new Set(["E09"]), testNagOnce: true,
  },
  ghost: { branch: "A", reason: () => RICH, silenceAt: new Set(["E01","E02","E03","E04","E05","E06","E07","E08","E10","E11","E12"]), seal: "不承認" },
};

let failed = 0;
for (const [name, p] of Object.entries(personas)) {
  try {
    const r = runGame(p);
    console.log(`PASS ${name}: family=${r.fam} owned=${r.axes.owned} evaded=${r.axes.evaded} anchors=${r.axes.anchorsKept}/${r.axes.anchorsLaid} log=${r.log.length} steps`);
  } catch (e) {
    failed++; console.log(`FAIL ${name}: ${e.message}`);
  }
}

/* ── returning persona: play 3 turns, drop, resume from save, finish ── */
try {
  const first = runGame({ branch: "A", optIndex: 0, reason: () => RICH, mirror: "承認", stopAfter: 3 });
  if (!first.stopped) throw new Error("stopAfter did not stop");
  const saved = first.store[Object.keys(first.store).find((k) => k.includes("save"))];
  if (!saved) throw new Error("no save written after 3 turns");

  const { T, doc } = makeSandbox(first.store);
  const snap = T.loadSave();
  if (!snap || !snap.trace || snap.trace.length < 3) throw new Error("loadSave returned bad snapshot");
  Object.assign(T.S, {
    code: snap.code, playlist: snap.playlist, idx: snap.idx,
    resources: snap.resources, trace: snap.trace, anchors: snap.anchors,
    mirrorCount: snap.mirrorCount, intelOpens: snap.intelOpens,
  });
  const stage = doc.querySelector("#stage");
  T.startGame(true);
  const log = [];
  const persona = { branch: "A", optIndex: 0, reason: () => RICH, mirror: "承認" };
  let guard = 0;
  while (T.S.idx < T.S.playlist.length && guard++ < 40) {
    if (maybeRoute(T, stage, "A")) continue;
    playTurn(T, stage, persona, log);
  }
  const payload = T.buildTracePayload();
  const turns = payload.turns.filter((t) => t.event_id !== "SEAL").length;
  if (turns !== 11) throw new Error(`resume run turns=${turns}, expected 11`);
  console.log(`PASS returning: resumed at idx=${snap.idx}, finished with ${turns} turns`);
} catch (e) { failed++; console.log(`FAIL returning: ${e.message}`); }

/* ── option sweep: EVERY option of EVERY station resolves through the response screen ──
   (single-station playlists; scene choices explored first-and-last for scened stations) */
let sweepFails = 0, sweepCount = 0;
for (const ev of gamedata.events) {
  const scenePasses = Array.isArray(ev.scene) && ev.scene.length ? [false, true] : [false];
  for (let i = 0; i < ev.options.length; i++) {
    for (const pickLast of scenePasses) {
      sweepCount++;
      try {
        const { T, doc } = makeSandbox({});
        const stage = doc.querySelector("#stage");
        T.S.code = "TESTCODE00";
        T.S.playlist = [ev.id];
        T.S.idx = 0;
        T.S._routeAsked = true; // single-station playlist: skip the ch8 fork screen
        T.renderChapter();
        driveScene(stage, pickLast);
        const box = stage.querySelectorAll("opt-box").pop();
        if (!box) throw new Error("no opt-box");
        const picks = box.querySelectorAll("pick").filter((b) => b.textContent === "拉下這一桿");
        if (i >= picks.length) throw new Error(`option[${i}] not rendered (${picks.length} picks)`);
        picks[i].click();
        const rbox = stage.querySelectorAll("reason-box").pop();
        if (!rbox) throw new Error("no reason box");
        const ta = rbox.children.find((c) => c.tag === "textarea");
        ta.value = RICH;
        byText(rbox.querySelectorAll("pick"), "留下理由").click();
        const probeDone = byText(rbox.querySelectorAll("pick"), "就這樣");
        if (probeDone) probeDone.click();
        const mirrors = stage.querySelectorAll("mirror-resp");
        if (mirrors.length) mirrors[0].click();
        const next = stage.querySelectorAll("next")[0]
          || byText(stage.querySelectorAll("pick"), "生成責任結局")
          || byText(stage.querySelectorAll("pick"), "前往下一站");
        if (!next) throw new Error("no next/ending button after response");
        // director-lite pilot stations must render entity cards on the response screen
        if ((ev.id === "E01" || ev.id === "E02") && !stage.querySelectorAll("entity-card").length) {
          throw new Error("no entity cards rendered (director-lite pilot station)");
        }
      } catch (e) {
        sweepFails++; console.log(`SWEEP FAIL ${ev.id} option[${i}]${pickLast ? " (alt scene path)" : ""}: ${e.message}`);
      }
    }
  }
}
console.log(sweepFails === 0
  ? `SWEEP: all ${sweepCount} option paths resolve`
  : `SWEEP: ${sweepFails}/${sweepCount} failed`);
failed += sweepFails;

console.log(failed === 0 ? "\nALL PERSONAS COMPLETE A FULL RUN" : `\n${failed} FAILURE(S)`);
process.exit(failed === 0 ? 0 : 1);
