// Regression test for the public player projection. Run with:
// node site/theater/council_projection_test.js
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const appPath = path.join(__dirname, "app.js");
const projectionPath = path.join(__dirname, "gamedata", "council_player_projection.json");
const legacyVerdictsPath = path.join(__dirname, "gamedata", "council_verdicts.json");
const appSrc = fs.readFileSync(appPath, "utf8");
const playerProjection = JSON.parse(fs.readFileSync(projectionPath, "utf8"));
const marker = "RAW_AUDIT_RATIONALE_MUST_NOT_REACH_PLAYER";

assert.equal(playerProjection._meta.audience, "player");
assert.ok(!fs.existsSync(legacyVerdictsPath), "the raw verdict payload must not ship with the game");
assert.ok(!JSON.stringify(playerProjection).includes("\"reasoning\""),
  "the player payload must not contain raw rationale fields");

for (const verdict of Object.values(playerProjection.verdicts)) {
  for (const vote of verdict.votes) {
    assert.deepEqual(Object.keys(vote).sort(), ["decision", "perspective"]);
  }
}

assert.ok(appSrc.includes("council_player_projection"));
assert.ok(!appSrc.includes("council_verdicts"), "the game must not request the raw verdict file");
assert.ok(!appSrc.includes("vote.reasoning"), "the player UI must not read raw reasoning");
assert.ok(!appSrc.includes("issues/new"), "the public game must not open an Issue submission flow");
assert.ok(!appSrc.includes("trace-submission"), "the public game must not refer to a trace template");

const document = {
  addEventListener: () => {},
  createElement: () => ({
    classList: { add: () => {}, remove: () => {}, toggle: () => {} },
    append: () => {}, appendChild: () => {}, addEventListener: () => {},
    style: {}, dataset: {},
  }),
  querySelector: () => ({
    addEventListener: () => {},
    classList: { add: () => {}, remove: () => {} },
  }),
  body: {},
};
const sandbox = {
  console, document, window: {},
  localStorage: { getItem: () => null, setItem: () => {}, removeItem: () => {} },
  fetch: () => Promise.reject(new Error("not used in projection test")),
  crypto: { getRandomValues: (a) => a },
  setTimeout: () => {}, alert: () => {}, Image: function Image() {}, navigator: {},
};
sandbox.globalThis = sandbox;
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(appSrc + "\n;globalThis.__T = { projectCouncilVoteForPlayer };", sandbox,
  { filename: appPath });

assert.equal(typeof sandbox.__T.projectCouncilVoteForPlayer, "function");
const projected = sandbox.__T.projectCouncilVoteForPlayer({
  perspective: "critic",
  decision: "object",
  reasoning: marker,
  confidence: 0.99,
});

assert.deepEqual(JSON.parse(JSON.stringify(projected)), {
  perspective: "critic",
  decision: "object",
  cue: "此路徑觸及界線；反對意見已被保留。",
});
assert.ok(!JSON.stringify(projected).includes(marker));

console.log("PASS public theater uses a lossy player council projection");
