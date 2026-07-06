// Standalone regression test (run: node site/theater/ending_smoke_test.js). No deps.
// Loads the REAL classifyEndingFamily/endingAxes from app.js and drives synthetic
// traces to prove: all 6 families reachable; the 2026-07-06 /grill fixes hold
// (honorable 修正 is NOT broke-faith; never-anchor is NOT the best ending; energy
// is no longer read). Extend scenarios as the classifier evolves.
"use strict";
const fs = require("fs");
const vm = require("vm");
const path = require("path");

const appSrc = fs.readFileSync(path.join(__dirname, "app.js"), "utf8");

// minimal browser stubs so app.js boot() doesn't crash before defining functions
class N { constructor(){this.children=[];this._cls=new Set();this._ev={};this.dataset={};this.style={};}
  set className(v){this._cls=new Set(String(v).split(/\s+/).filter(Boolean));} get className(){return[...this._cls].join(" ");}
  set textContent(v){this._html=String(v);} set innerHTML(v){this._html=String(v);} get innerHTML(){return this._html||"";}
  append(...ns){for(const n of ns) if(n instanceof N) this.children.push(n);}
  appendChild(n){this.append(n);return n;} insertBefore(n){this.append(n);return n;} remove(){}
  get text(){return (this._html||"") + this.children.map(c=>c.text).join("");}
  addEventListener(){} get classList(){const c=this._cls;return{add:x=>c.add(x),remove:x=>c.delete(x),contains:x=>c.has(x),toggle:()=>{}};}
  scrollIntoView(){} querySelector(){return new N();} querySelectorAll(){return[];} }
const sandbox = { document:{createElement:()=>new N(),querySelector:()=>new N(),addEventListener:()=>{},body:new N()},
  window:{}, console, crypto:{getRandomValues:a=>a}, localStorage:{getItem:()=>null,setItem:()=>{},removeItem:()=>{}},
  fetch:()=>Promise.reject(new Error("no fetch")), alert:()=>{}, setTimeout:fn=>fn&&fn(), Image:function(){return{};}, navigator:{} };
sandbox.globalThis = sandbox; sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(appSrc + "\n;globalThis.__T={classifyEndingFamily,endingAxes,materialRecord,S};", sandbox, {filename:"app.js"});
const T = sandbox.__T;

// synthetic trace helpers
const turn = (o={}) => ({ chapter: 1, choice: { is_default: !!o.silence, wellbeing_skip: false, is_third_path: !!o.third },
  parse: { responsibility_position: o.owned ? "承擔" : "未明", evasion_signal: !!o.evaded },
  blackmirror: o.mirror ? { response: o.mirror } : null });
const setS = (trace, anchors, energy=5) => { T.S.trace = trace; T.S.anchors = anchors; T.S.resources = {medical:5,energy:energy,trust:5}; T.S.mirrorCount = trace.filter(t=>t.blackmirror).length; };
const A = (dissolved) => ({ quote:"q", tags:[], chapter:1, dissolved:!!dissolved });

let fails = 0;
function check(name, got, want) {
  const ok = got === want;
  console.log(`${ok?"PASS":"FAIL"}: ${name} → ${got}${ok?"":" (want "+want+")"}`);
  if (!ok) fails++;
}

// A: lit_anchor — laid+kept anchors, owned>evaded, no unowned contradiction
setS([turn({owned:1}),turn({owned:1}),turn({owned:1})], [A(false),A(false)]);
check("lit_anchor (kept word + owned costs)", T.classifyEndingFamily(), "lit_anchor");

// B: REVERSED-SIGNAL FIX — only 修正 (honorable, dissolved=true) must NOT be broke-faith
setS([turn({owned:1}),turn({owned:1})], [A(true)]);  // dissolved via honorable 修正
check("honorable 修正 is NOT broke-faith (was the killer bug)", T.classifyEndingFamily(), "lit_anchor");

// C: NEVER-ANCHOR LOOPHOLE FIX — 0 anchors must NOT get lit_anchor
setS([turn({owned:1}),turn({owned:1})], []);
check("never-anchor is NOT the best ending (loophole closed)", T.classifyEndingFamily(), "lit_broken");

// D: unowned contradiction (沉默 black-mirror) → broke faith
setS([turn({owned:1}),turn({owned:1,mirror:"沉默"})], [A(false)]);
check("unowned contradiction → broke faith", T.classifyEndingFamily(), "lit_broken");

// E: dark_anchor — kept faith but evaded>owned (ground sank)
setS([turn({evaded:1}),turn({evaded:1}),turn({owned:1})], [A(false)]);
check("dark_anchor (kept word, ground sank)", T.classifyEndingFamily(), "dark_anchor");

// F: dark_broken — evaded>owned AND unowned contradiction
setS([turn({evaded:1}),turn({evaded:1,mirror:"拒絕"})], [A(false)]);
check("dark_broken", T.classifyEndingFamily(), "dark_broken");

// G: silent posture gate (>=4 silences) wins first
setS([turn({silence:1,evaded:1}),turn({silence:1,evaded:1}),turn({silence:1,evaded:1}),turn({silence:1,evaded:1})], [A(false)]);
check("silent (posture gate first)", T.classifyEndingFamily(), "silent");

// H: switcher posture gate (>=3 thirds)
setS([turn({third:1,owned:1}),turn({third:1,owned:1}),turn({third:1,owned:1})], [A(false)]);
check("switcher (posture gate)", T.classifyEndingFamily(), "switcher");

// I: ENERGY IGNORED — same as A but energy=0 must still be lit_anchor
setS([turn({owned:1}),turn({owned:1}),turn({owned:1})], [A(false),A(false)], 0);
check("energy=0 still lit_anchor (energy no longer read)", T.classifyEndingFamily(), "lit_anchor");

// div-zero guard: 0 anchors doesn't throw
setS([turn({owned:1})], []);
try { T.endingAxes(); console.log("PASS: endingAxes with 0 anchors does not throw"); }
catch (e) { console.log("FAIL: endingAxes threw on 0 anchors: "+e.message); fails++; }

// A 接點 materialRecord: bands + R1 undefined-safety
function matLines(res) {
  T.S.resources = res;
  const box = T.materialRecord();
  return box.children.length; // head + 3 lines
}
try {
  check("materialRecord returns head+3 lines (normal)", matLines({medical:5,energy:5,trust:5}), 4);
  check("materialRecord survives MISSING axis (R1 safety, no throw)", matLines({medical:2}), 4);
  check("materialRecord survives undefined resources (R1 safety)", (T.S.resources=undefined, T.materialRecord().children.length), 4);
} catch (e) { console.log("FAIL: materialRecord threw: "+e.message); fails++; }
// band selection via endingAxes-independent check: verify low/mid/high boundaries don't throw at 0 and 10
[0,3,4,6,7,10].forEach(v => { try { matLines({medical:v,energy:v,trust:v}); } catch(e){ console.log("FAIL: materialRecord threw at "+v); fails++; } });
// bands must produce DIFFERENT prose (codex finding: child-count alone would pass even if all bands equal)
function medLine(v){ T.S.resources={medical:v,energy:5,trust:5}; return T.materialRecord().text; }
const lowT = medLine(2), midT = medLine(5), highT = medLine(9);
check("低帶 prose 含拒收(≤3)", lowT.includes("拒收"), true);
check("高帶 prose 含大多接住(≥7)", highT.includes("大多接住"), true);
check("三帶 prose 互異", (lowT!==midT && midT!==highT && lowT!==highT), true);
// boundary: exactly 3 = low, exactly 7 = high
check("醫療=3 落低帶", medLine(3).includes("拒收"), true);
check("醫療=7 落高帶", medLine(7).includes("大多接住"), true);

console.log(fails === 0 ? "\nALL PASS: 6 families reachable, both /grill fixes hold, energy ignored" : `\n${fails} FAILED`);
process.exit(fails === 0 ? 0 : 1);
