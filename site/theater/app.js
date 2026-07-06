/* 岔軌之城 v0 — 單人最小可玩版
 *
 * 純 vanilla JS、無建置步驟(demo_ui 範式)。誠實分層:
 *  - 責任節點 verdict:真 rules-council 引擎輸出,離線預算(gamedata/council_verdicts.json),
 *    本檔只重播,絕不偽造節點回應。
 *  - 短句解析/黑鏡矛盾偵測/資源數值:遊戲層規則,關鍵詞級,如實標注。
 *  - 火花/共語 LLM 節點:absent(v0 未接)。
 * 正典:docs/theater/(天道 v0.2 > 機制書 > 世界書)。
 */
"use strict";

/* ── 常數 ─────────────────────────────────────────── */

const NODE_MAP = {
  guardian: "審核節點",
  analyst: "理性節點",
  critic: "黑鏡節點",
  advocate: "倖存者節點",
  axiomatic: "城務AI",
  axiomatic_inference: "城務AI",
};
const DECISION_ICON = { approve: "✓", concern: "⚠", object: "✕", abstain: "─" };
const VERDICT_LABEL = {
  approve: "節點放行",
  refine: "節點要求補充",
  declare_stance: "節點立場聲明",
  block: "節點攔阻(意見保存;桿已由你拉下——系統不能替你承擔,也不能替你收回)",
};
const PRESSURE_LABEL = { 1: "低壓・回聲", 2: "中壓", 3: "高壓", 4: "極高壓" };

// 黑鏡矛盾對(遊戲層規則,誠實標注:比對的是你自己留下的錨鏈)
const CONFLICT_PAIRS = [
  ["truth_first", "mercy_lie"],
  ["transparency", "mercy_lie"],
  ["majority_first", "minority_first"],
  ["rule_follow", "rule_break"],
  ["delegate_to_system", "self_sacrifice"],
  ["repair_first", "refuse_choice"],
];
const COMMIT_RE = /承諾|絕不|永遠|一定會|保證|我發誓/;

// 第三律 keyword 解析表(遊戲層;解不出→NPC 追問,不假裝讀懂)
const KW = {
  harm_yes: /知道.{0,6}(受害|犧牲|代價)|承認|對不起|抱歉|有人會(死|受傷|受害)|犧牲|代價/,
  resp_accept: /我承擔|我負責|算我的|我的責任|記在我|我來扛|我簽/,
  resp_evade: /系統(建議|決定|判定)|命運|別無選擇|不得不|只能這樣|不是我的錯|大家都會/,
  risk_accept: /我知道風險|賭|冒險|承受後果|後果我擔/,
  repair: /補償|修正|道歉|彌補|之後我會|下次|改進|紀念/,
  values: [
    [/多數|大局|整體|全城|效率/, "majority_first"],
    [/少數|弱勢|灰區|名字|個體/, "minority_first"],
    [/秩序|穩定|安全/, "order_first"],
    [/真相|誠實|事實/, "truth_first"],
    [/孩子|兒童/, "protect_children"],
    [/公開|透明/, "transparency"],
    [/規則|程序|制度/, "rule_follow"],
  ],
};

/* ── 狀態 ─────────────────────────────────────────── */

const S = {
  data: null,          // {events, npcs, locations, verdicts}
  memoryOnly: false,
  code: null,          // 撤回碼
  playlist: [],        // event ids(依章;ch8 由玩家選線)
  idx: 0,
  resources: { medical: 5, energy: 5, trust: 5 },
  trace: [],
  anchors: [],         // {quote, tags, chapter, dissolved}
  mirrorCount: 0,
  intelOpens: 0,
  soften: false,
  prologue: null,      // 城門外那一轍(V05-B;同意前僅存記憶體,同意後才隨局持久化)
  // 本章暫存
  cur: null,           // 當前事件
  chosen: null,        // 選中的 option(或 {default:true})
  reasonText: "",
  probeText: "",
};

const $ = (sel) => document.querySelector(sel);
const el = (tag, cls, html) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (html !== undefined) n.innerHTML = html;
  return n;
};
const esc = (s) =>
  String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

/* ── V05-A 視覺層(渲染只讀狀態,不碰任何判定)────── */

const npcAvatar = (id) =>
  `<img class="npc-avatar" src="assets/npc/${esc(id)}.webp" alt="" loading="lazy" onerror="this.remove()">`;

// 結局家族:全部由軌痕事實決定;不評善惡,只換標題與終章畫(城主手繪)。
// v0 門檻(owner 可調;事實數字照樣列在結局頁,判定可受挑戰):
//   沉默 >=4 站 → 沉默者;第三路 >=3 次 → 岔軌者(姿態家族優先於城的 2x2);
//   城亮 = 能源 >= 5(起始值);錨斷 = 任一錨鏈 dissolved。
const ENDING_FAMILIES = {
  silent:      { art: "end_silent.webp",      title: "沉默者",   line: "結局回讀你沒說的那些。" },
  switcher:    { art: "end_switcher.webp",    title: "岔軌者",   line: "既不是 A 也不是 B 的人——城為你留了一條自己的軌。" },
  lit_anchor:  { art: "end_lit_anchor.webp",  title: "燈火與錨", line: "城還在,你說過的話也還在。" },
  lit_broken:  { art: "end_lit_broken.webp",  title: "燈火換錨", line: "城撐過去了。簽下那些的,還是你嗎?" },
  dark_anchor: { art: "end_dark_anchor.webp", title: "守錨熄燈", line: "你沒有換。代價記在城上。" },
  dark_broken: { art: "end_dark_broken.webp", title: "雙暗",     line: "回讀最重的一份。天道依然不判。" },
};

function classifyEndingFamily() {
  const turns = S.trace.filter((r) => r.chapter !== "ending" && r.choice);
  const silences = turns.filter((r) => r.choice.is_default && !r.choice.wellbeing_skip).length;
  const thirds = turns.filter((r) => r.choice.is_third_path).length;
  const broken = S.anchors.some((a) => a.dissolved);
  const lit = S.resources.energy >= 5;
  if (silences >= 4) return "silent";
  if (thirds >= 3) return "switcher";
  if (lit && !broken) return "lit_anchor";
  if (lit && broken) return "lit_broken";
  if (!lit && !broken) return "dark_anchor";
  return "dark_broken";
}

/* ── 資料載入 ─────────────────────────────────────── */

async function loadData() {
  const [events, npcs, locations, verdicts] = await Promise.all(
    ["events", "npcs", "locations", "council_verdicts"].map((n) =>
      fetch(`gamedata/${n}.json`).then((r) => {
        if (!r.ok) throw new Error(`${n}.json ${r.status}`);
        return r.json();
      })
    )
  );
  S.data = {
    events,
    npcs: Object.fromEntries(npcs.map((n) => [n.id, n])),
    locations: Object.fromEntries(locations.map((l) => [l.id, l])),
    verdicts: verdicts.verdicts,
    verdictMeta: verdicts._meta,
  };
}

function eventById(id) {
  return S.data.events.find((e) => e.id === id);
}

function buildPlaylist(branch) {
  // 章序:1-7 線性;第8章分線(E08 穹頂 / E09 治安);9-11 線性
  const ids = ["E01", "E02", "E03", "E04", "E05", "E06", "E07"];
  ids.push(branch === "B" ? "E09" : "E08");
  ids.push("E10", "E11", "E12");
  return ids;
}

/* ── 存檔(僅 localStorage 模式)───────────────────── */

const SAVE_KEY = "cos_v0_save";

function save() {
  if (S.memoryOnly) return;
  const snap = {
    code: S.code, playlist: S.playlist, idx: S.idx,
    resources: S.resources, trace: S.trace, anchors: S.anchors,
    mirrorCount: S.mirrorCount, intelOpens: S.intelOpens,
    prologue: S.prologue,
  };
  try { localStorage.setItem(SAVE_KEY, JSON.stringify(snap)); } catch (_) { /* 存滿就算了,誠實地算了 */ }
}

function loadSave() {
  try { return JSON.parse(localStorage.getItem(SAVE_KEY) || "null"); } catch (_) { return null; }
}

function makeCode() {
  const chars = "ABCDEFGHJKMNPQRSTUVWXYZ23456789";
  const buf = new Uint8Array(10);
  crypto.getRandomValues(buf);
  return Array.from(buf, (b) => chars[b % chars.length]).join("");
}

/* ── 同意閘 ───────────────────────────────────────── */

// V05-B 序章:30 秒內先遇事。同意閘不刪、不縮——只是移到「上任簽署」前,
// 敘事順理成章:你被記錄儀拍下,任命書因此找上你,簽署前城規當面讀。
// 序章選擇在同意前只存在記憶體;同意進城後才隨局持久化(資料寫入永遠在閘後)。
const PROLOGUE_ECHOES = {
  pull: "閘扳到一半卡住,電車擦著舊軌停下。沒有人受傷——但扳道房的紀錄儀拍下了你。",
  warn: "司機在最後一刻看見你的燈。車停了;你的臉,留在行車紀錄裡。",
  stand: "電車的自動保護器在斷軌前僵住了。你什麼都沒做——紀錄儀也拍下了這件事。",
};

function initGate() {
  const local = $("#consent-local");
  const memOnly = $("#consent-memory-only");
  const enter = $("#enter-btn");
  local.addEventListener("change", () => { enter.disabled = !local.checked; });

  const consentWrap = $("#consent-wrap");
  const echoLine = $("#prologue-echo");
  const proBtns = document.querySelectorAll("#prologue .prologue-opts button");
  proBtns.forEach((b) =>
    b.addEventListener("click", () => {
      S.prologue = { choice: b.dataset.pro, label: b.textContent };
      echoLine.innerHTML = esc(PROLOGUE_ECHOES[b.dataset.pro]) +
        "<br>三天後,一紙任命書送到了你手上。——正式上任前,城規在此,把話說清楚:";
      echoLine.classList.remove("hidden");
      proBtns.forEach((x) => { x.disabled = true; });
      b.classList.add("chosen");
      consentWrap.classList.remove("hidden");
      consentWrap.scrollIntoView({ behavior: "smooth", block: "start" });
    })
  );

  const prior = loadSave();
  if (prior && prior.trace && prior.trace.length) {
    // 回鍋玩家:不重演序章,直接見城規與「繼續」
    $("#prologue").classList.add("hidden");
    consentWrap.classList.remove("hidden");
    $("#resume-btn").classList.remove("hidden");
    $("#resume-btn").addEventListener("click", () => {
      Object.assign(S, {
        code: prior.code, playlist: prior.playlist, idx: prior.idx,
        resources: prior.resources, trace: prior.trace, anchors: prior.anchors,
        mirrorCount: prior.mirrorCount, intelOpens: prior.intelOpens,
        prologue: prior.prologue || null,
      });
      startGame(true);
    });
  }
  enter.addEventListener("click", () => {
    S.memoryOnly = memOnly.checked;
    S.code = makeCode();
    if (!S.memoryOnly) { try { localStorage.removeItem(SAVE_KEY); } catch (_) {} }
    startGame(false);
  });
}

function startGame(resumed) {
  $("#gate").classList.add("hidden");
  $("#game").classList.remove("hidden");
  if (!resumed) {
    S.playlist = buildPlaylist("A"); // 第8章進場時再讓玩家選線
    renderMission();
    return;
  }
  renderChapter();
}

/* ── 任命書(開場目標框架;推進感 pass 2026-07-04)──── */

function renderMission() {
  $("#hud-chapter").textContent = "任命書";
  $("#hud-location").textContent = "中央轉轍塔・轉轍席前";
  $("#hud-pressure").textContent = "";
  for (const k of ["medical", "energy", "trust"]) {
    $(`#res-${k} i`).style.width = `${S.resources[k] * 10}%`;
  }
  const stage = $("#stage");
  stage.innerHTML = "";
  stage.append(el("div", "cover-wrap",
    `<img class="cover-art" src="assets/cover.webp" alt="岔軌之城(城主手繪進城封面)" onerror="this.parentNode.remove()">`));
  stage.append(el("h2", "ev-title", "轉轍官任命書"));
  stage.append(el("p", "ev-briefing",
    "岔軌城任命你為新任轉轍官。十一站,十二次轉轍——每一站你都要在沒有完美答案的地方做選擇、留下理由、承擔後果。" +
    "這一局的目標不是「贏」:是走完全程,在終點面對三個問題——你保住了什麼?你犧牲了什麼?你是否願意承認這兩者都是真的?" +
    "——然後留下一份你敢回讀的責任紀錄。"));
  if (S.prologue) {
    stage.append(el("p", "hint prologue-note",
      `任命理由附註:三日前,城門外岔軌口——「${esc(S.prologue.label)}」。扳道房紀錄儀為證。` +
      "城需要的不是完美的人,是留得下紀錄的人。"));
  }
  stage.append(el("h3", null, "你的路線"));
  stage.append(renderRouteBar());
  stage.append(el("p", "hint",
    "亮著的是你所在的站;▓▓▓ 是未登錄區域,走到才解鎖;第八站是岔口,到時由你選線。"));
  stage.append(howtoDigest());
  const go = el("button", "pick next");
  go.textContent = "上任,前往中央轉轍塔";
  go.addEventListener("click", () => renderChapter());
  stage.append(go);
}

function howtoDigest() {
  const d = el("details", "howto");
  d.innerHTML = `<summary>怎麼玩(機制書濃縮版)</summary>
  <ol>
    <li>每站一次轉轍:讀情報 → 選方案(或第三條路,或沉默)→ 留下理由。</li>
    <li>選項下方有風險標示——選之前你就知道自己在賭什麼(天道 v0.2 第二律)。</li>
    <li>你的理由會晶化成「錨鏈」;前後矛盾時,黑鏡會拿你自己的話回來問你——你有六種回應空間,沒有一種是錯的。</li>
    <li>三資源(醫療/能源/信任)0-10;歸零不會結束遊戲,但世界會記得。</li>
    <li>沉默也是轉轍:不選,預設程序替你選,帳記在你名下(第九律)。</li>
    <li>累了可以暫停、降強度、跳過高壓站——自我照顧的跳過永遠不會被拿來回讀你(第十律)。</li>
    <li>結局不評善惡,只回答三個問題,附一份可下載的完整軌痕。</li>
  </ol>`;
  return d;
}

function stationName(eid) {
  const ev = eventById(eid);
  if (!ev) return "?";
  const loc = S.data.locations[ev.location_id];
  return loc ? loc.name : "?";
}

function stationLocked(eid) {
  const ev = eventById(eid);
  if (!ev) return false;
  const loc = S.data.locations[ev.location_id];
  return !!(loc && loc.visible_from_start === false);
}

// 地點 banner:城主手繪為主,載入失敗才退回 ink.js 程序水墨(狀態驅動)。
function locationBanner(locId, chapter, locName) {
  const wrap = el("div", "loc-banner");
  const img = new Image();
  img.className = "loc-art";
  img.alt = `${locName}(城主手繪)`;
  img.loading = "eager";
  img.onerror = () => {
    wrap.classList.add("ink-fallback");
    wrap.innerHTML = window.TheaterInk
      ? TheaterInk.chapterBackdrop(S.code, chapter, S.resources) : "";
  };
  img.src = `assets/loc/${locId}.webp`;
  wrap.append(img);
  return wrap;
}

function renderRouteBar() {
  const bar = el("div", "route-bar");
  S.playlist.forEach((eid, i) => {
    const current = i === S.idx;
    const past = i < S.idx;
    let label;
    if ((eid === "E08" || eid === "E09") && i > S.idx) label = "岔口";
    else if (!past && !current && stationLocked(eid)) label = "▓▓▓";
    else label = stationName(eid);
    const s = el("span", "station " + (current ? "current" : past ? "past" : "future"));
    s.textContent = `${i + 1} ${label}`;
    bar.append(s);
  });
  return bar;
}

/* ── HUD ─────────────────────────────────────────── */

const CH_NAMES = ["", "第一章", "第二章", "第三章", "第四章", "第五章", "第六章",
  "第七章", "第八章", "第九章", "第十章", "終章"];

function renderHUD() {
  const ev = S.cur;
  const loc = S.data.locations[ev.location_id];
  $("#hud-chapter").textContent = CH_NAMES[ev.chapter] || `第${ev.chapter}章`;
  $("#hud-location").textContent = loc ? loc.name : "";
  const p = ev.pressure_level;
  const hp = $("#hud-pressure");
  hp.textContent = PRESSURE_LABEL[p];
  hp.dataset.level = p;
  for (const k of ["medical", "energy", "trust"]) {
    const bar = $(`#res-${k} i`);
    bar.style.width = `${S.resources[k] * 10}%`;
    bar.parentElement.dataset.low = S.resources[k] <= 2 ? "1" : "";
  }
  // 推進感計數器:活錨鏈(你立的公開承諾)+ 累積黑箱(結局揭曉)
  const anchorsEl = $("#hud-anchors");
  if (anchorsEl) {
    const live = S.anchors.filter((a) => !a.dissolved).length;
    anchorsEl.textContent = live ? `錨鏈×${live}` : "";
  }
  const bbEl = $("#hud-blackbox");
  if (bbEl) {
    const bb = S.trace.reduce((n, t) => n + (t.blackbox_withheld || []).length, 0);
    bbEl.textContent = bb ? `▓×${bb}` : "";
  }
}

/* ── 章節渲染:五階段迴圈 ─────────────────────────── */

function renderChapter() {
  if (S.idx >= S.playlist.length) return renderEnding();
  S.cur = eventById(S.playlist[S.idx]);
  S.chosen = null; S.reasonText = ""; S.probeText = "";

  // 第8章分線選擇
  if (S.cur.chapter === 8 && !S.cur._routeChosen && S.playlist[S.idx] === "E08" && !S._routeAsked) {
    return renderRouteChoice();
  }
  renderHUD();

  const stage = $("#stage");
  stage.innerHTML = "";
  const ev = S.cur;
  const loc = S.data.locations[ev.location_id];

  // 路線圖(推進感:你在哪、走過哪、還剩哪)
  stage.append(renderRouteBar());

  // 地點背景(城主手繪 15 站;缺圖 onerror 退回程序水墨——漸進增強,城依然可玩)
  stage.append(locationBanner(ev.location_id, ev.chapter, loc.name));

  // 1. 危機揭示
  const head = el("div", "ev-head");
  head.append(
    el("h2", "ev-title", esc(ev.title)),
    el("p", "ev-loc", `${esc(loc.name)} — ${esc(loc.core_question)}`)
  );
  if (ev.objective) {
    head.append(el("p", "objective", `本站的轉轍:${esc(ev.objective)}`));
  }
  stage.append(head);
  stage.append(el("p", "ev-briefing", esc(fillPlaceholders(ev.briefing))));

  // NPC 開場
  const npcBox = el("div", "npc-box");
  for (const n of ev.npcs) {
    const info = S.data.npcs[n.id];
    npcBox.append(el("div", "npc-line",
      `${npcAvatar(n.id)}<div class="npc-said"><b>${esc(info.name)}</b><span class="npc-stance">${esc(n.stance)}</span><q>${esc(n.lines.opening)}</q></div>`));
  }
  stage.append(npcBox);

  // 2. 情報公開(三級)
  stage.append(renderIntel(ev.intel));

  // 回聲活動(第一律)
  if (ev.is_echo && ev.echo_activities) stage.append(renderEcho(ev));

  // 3. 轉轍決策
  stage.append(renderOptions(ev));
  window.scrollTo(0, 0);
}

function fillPlaceholders(text) {
  let t = text;
  if (t.includes("{player_victims}")) {
    const names = allHarms().slice(0, 3);
    t = t.replace("{player_victims}",
      names.length ? names.join("、") : "(這一局,還沒有名字因你停下——這面牆等著看你走完)");
  }
  if (t.includes("{blackmirror_readback}")) {
    t = t.replace("{blackmirror_readback}", buildReadbackPair());
  }
  return t;
}

function buildReadbackPair() {
  const said = S.anchors[0] ||
    (S.trace[0] && { quote: S.trace[0].parse?.trace_quote, chapter: S.trace[0].chapter });
  const last = S.trace[S.trace.length - 1];
  const a = said && said.quote ? `你曾說:「${said.quote}」(第${said.chapter}章)` : "你留下的理由不多——黎真連著讀了兩遍";
  const b = last ? `你後來選擇:「${last.choice.label}」(第${last.chapter}章)` : "";
  return `${a}。${b}`;
}

function renderIntel(intel) {
  const box = el("div", "intel-box");
  box.append(el("h3", null, "情報"));
  const mk = (title, cls, items) => {
    if (!items || !items.length) return null;
    const d = el("details", `intel ${cls}`);
    d.innerHTML = `<summary>${title}(${items.length})</summary>` +
      items.map((i) => `<p>${esc(i)}</p>`).join("");
    d.addEventListener("toggle", () => { if (d.open) { S.intelOpens++; } });
    return d;
  };
  const pub = mk("公開情報", "pub", intel.public);
  const res = mk("限定情報", "restricted", intel.restricted);
  if (pub) { pub.open = true; box.append(pub); }
  if (res) box.append(res);
  const nBlack = (intel.blackbox || []).length;
  if (nBlack) {
    box.append(el("p", "intel blackbox",
      `▓▓▓ 黑箱情報 ×${nBlack} — 系統知道,你暫時不知道。結局回讀時揭示。`));
  }
  return box;
}

function renderEcho(ev) {
  const box = el("div", "echo-box");
  box.append(el("h3", null, "回聲(高壓之後,必有回聲——這裡沒有倒數)"));
  const done = new Set();
  for (const act of ev.echo_activities) {
    const b = el("button", "echo-act");
    b.innerHTML = `<b>${esc(act.label)}</b><span>${esc(act.desc)}</span>`;
    b.addEventListener("click", () => {
      if (done.has(act.id)) return;
      done.add(act.id);
      b.classList.add("done");
      b.append(el("em", "echo-effect", esc(act.effect)));
      S.cur._echoDone = Array.from(done);
      if (/信任\+1|關係\+1/.test(act.effect)) bumpResource("trust", 1);
    });
    box.append(b);
  }
  return box;
}

// 資源增減預覽(選前可見)——把「無聲扣能源」變成「我選擇花能源換這個」。
// 機制書§八:外顯是故事,內層是標註,兩者都該看得見;隱藏機械代價違背城自己的透明。
const RES_LABEL = { medical: "醫療", energy: "能源", trust: "信任" };
function resourceDeltaLine(effects) {
  const parts = [];
  for (const k of ["medical", "energy", "trust"]) {
    const v = (effects || {})[k] || 0;
    if (v === 0) continue;
    const cls = v > 0 ? "res-up" : "res-down";
    parts.push(`<span class="${cls}">${RES_LABEL[k]} ${v > 0 ? "+" : ""}${v}</span>`);
  }
  if (!parts.length) parts.push('<span class="res-flat">城市數值不變</span>');
  const line = el("p", "res-delta");
  line.innerHTML = `<span class="res-delta-tag">城市代價</span>${parts.join("・")}`;
  return line;
}

function renderOptions(ev) {
  const box = el("div", "opt-box");
  box.append(el("h3", null, "轉轍決策"));

  for (const opt of ev.options) {
    const card = el("div", `opt${opt.is_third_path ? " third" : ""}`);
    card.append(el("h4", null,
      `${esc(opt.id)}. ${esc(opt.label)}${opt.is_third_path ? '<span class="third-tag">第三條路(有代價)</span>' : ""}`));
    card.append(el("p", "opt-summary", esc(opt.summary)));

    // 第二律:選前風險標示
    const risk = el("table", "risk");
    const RISK_NAMES = {
      success_chance: "成功可能", main_cost: "主要代價", failure_consequence: "失敗後果",
      affected_parties: "牽連對象", breaks_rules: "違反制度", long_term_trace: "長期軌痕",
      needs_npc: "需要協助", triggers_blackmirror: "黑鏡風險",
    };
    for (const [k, v] of Object.entries(opt.risk_disclosure || {})) {
      risk.append(el("tr", null, `<th>${RISK_NAMES[k] || esc(k)}</th><td>${esc(v)}</td>`));
    }
    card.append(risk);
    card.append(resourceDeltaLine(opt.resource_effects));

    if (opt.is_third_path && opt.third_path_cost) {
      const c = opt.third_path_cost;
      card.append(el("details", "third-cost",
        `<summary>第三條路的完整價碼(第六律:拒絕二選一,不等於拒絕代價)</summary>
         <p><b>需要誰:</b>${esc(c.requires_help_from)}</p>
         <p><b>成功條件:</b>${esc(c.success_condition)}</p>
         <p><b>失敗代價:</b>${esc(c.failure_cost)}</p>
         <p><b>額外犧牲:</b>${esc(c.extra_sacrifice)}</p>
         <p><b>違反制度:</b>${esc(String(c.breaks_rules))}</p>
         <p><b>未來債務:</b>${esc(c.future_debt)}</p>`));
    }

    const pick = el("button", "pick");
    pick.textContent = "拉下這一桿";
    pick.addEventListener("click", () => renderReason(opt));
    card.append(pick);
    box.append(card);
  }

  // 第九律:沉默也是轉轍
  const silence = el("div", "opt silence");
  silence.append(el("h4", null, "不拉桿(沉默)"));
  silence.append(el("p", "opt-summary",
    "你可以拒絕選擇。但當你沉默時,列車仍然前進——某個預設規則會替你選,而天道記錄的是你的沉默,不是空白。"));
  silence.append(resourceDeltaLine((ev.default_outcome || {}).resource_effects));
  const sBtn = el("button", "pick ghost");
  sBtn.textContent = "保持沉默";
  sBtn.addEventListener("click", () => resolveTurn({ isDefault: true }, "", ""));
  silence.append(sBtn);
  box.append(silence);

  // 第十律:跳過高壓(自我照顧)
  if (S.cur.pressure_level >= 3) {
    const skip = el("button", "skip-wellbeing",
      "跳過本章(自我照顧)——世界照常運轉並記下後果,但這一格不會被拿來回讀你");
    skip.addEventListener("click", () => resolveTurn({ isDefault: true, wellbeing: true }, "", ""));
    box.append(skip);
  }
  return box;
}

/* ── 4. 理由陳述 + 短句解析 + NPC 追問 ────────────── */

function renderReason(opt) {
  S.chosen = opt;
  const stage = $("#stage");
  const box = el("div", "reason-box");
  box.append(el("h3", null, "理由陳述(必留;可以很短——短句也是責任)"));
  box.append(el("p", "hint",
    `你選了:<b>${esc(opt.label)}</b>。說出你為什麼這樣選。你可以說謊、逃避、沉默或矛盾——但這些都會被記錄為軌痕。`));
  const ta = el("textarea");
  ta.placeholder = "例:「先救第七車廂。」「我承擔。」「我不相信系統。」";
  const submit = el("button", "pick");
  submit.textContent = "留下理由";
  submit.addEventListener("click", () => {
    const text = ta.value.trim();
    // 機制書§二6:理由陳述(強制)——選了方案就至少留一個字;「怕。」也算理由。
    // 真正的沉默走「保持沉默」那顆獨立按鈕(第九律),不從這裡空白通過。
    if (!text) {
      if (!box.dataset.nagged) {
        box.dataset.nagged = "1";
        box.append(el("p", "hint reason-nag",
          "至少留一個字——「怕。」也算理由。真正想沉默,請回上面用「保持沉默」,那也是一種轉轍。"));
      }
      return;
    }
    const parse = parseReason(text, opt);
    const needProbe = text.length < 30 &&
      (parse.harm_awareness === "未知" || parse.responsibility_position === "未明");
    if (needProbe && !box.dataset.probed) {
      box.dataset.probed = "1";
      const npc = S.cur.npcs.find((n) => n.lines && n.lines.probe) || S.cur.npcs[0];
      const info = S.data.npcs[npc.id];
      box.append(el("div", "npc-line probe",
        `${npcAvatar(npc.id)}<div class="npc-said"><b>${esc(info.name)}</b><q>${esc(npc.lines.probe)}</q></div>`));
      const ta2 = el("textarea");
      ta2.placeholder = "(可補充,也可留白——世界會記下你補了,或沒補)";
      const done = el("button", "pick ghost");
      done.textContent = "就這樣";
      done.addEventListener("click", () => resolveTurn(opt, text, ta2.value.trim()));
      box.append(ta2, done);
      submit.remove();
      ta.disabled = true;
      return;
    }
    resolveTurn(opt, text, "");
  });
  box.append(ta, submit);
  stage.querySelectorAll(".opt-box .pick, .skip-wellbeing").forEach((b) => (b.disabled = true));
  stage.append(box);
  box.scrollIntoView({ behavior: "smooth" });
}

function parseReason(text, opt) {
  // 遊戲層 keyword 解析(誠實標注:LLM 深析節點 absent;解不出的欄位如實留「未知」)
  const t = text || "";
  const hits = KW.values.filter(([re]) => re.test(t)).map(([, tag]) => tag);
  const full = t + " " + (S.probeText || "");
  return {
    action: opt.label || "沉默(預設程序)",
    target: (opt.harm_targets && opt.harm_targets[0]) || S.data.locations[S.cur.location_id].name,
    reason: t || "(未留理由)",
    value_priority: [...new Set([...(opt.value_tags || []), ...hits])],
    harm_awareness: KW.harm_yes.test(full) ? "承認" : t ? "未知" : "未知",
    responsibility_position: KW.resp_accept.test(full) ? "承擔"
      : KW.resp_evade.test(full) ? "外推訊號" : "未明",
    evasion_signal: KW.resp_evade.test(full),
    risk_acceptance: KW.risk_accept.test(full) ? "明示接受" : "未知",
    repair_intent: KW.repair.test(full),
    trace_quote: t.slice(0, 60) || null,
    parse_engine: "keyword(遊戲層);LLM節點:absent",
  };
}

/* ── 5. 落帳 + 節點回應 + 黑鏡 ────────────────────── */

function bumpResource(key, delta) {
  S.resources[key] = Math.max(0, Math.min(10, S.resources[key] + delta));
}

function resolveTurn(opt, reasonText, probeText) {
  S.probeText = probeText;
  const ev = S.cur;
  const isDefault = !!opt.isDefault;
  const chosen = isDefault ? null : opt;
  const outcome = isDefault ? ev.default_outcome : opt;
  const parse = isDefault
    ? {
        action: opt.wellbeing ? "跳過(自我照顧)" : "沉默(預設程序執行)",
        target: (ev.default_outcome.harm_targets || [])[0] || "",
        reason: opt.wellbeing ? "(玩家選擇自我照顧;天道第十律)" : "(未表態)",
        value_priority: opt.wellbeing ? [] : ["refuse_choice", "delegate_to_system"],
        harm_awareness: "未知", responsibility_position: opt.wellbeing ? "不適用" : "未明",
        evasion_signal: !opt.wellbeing, risk_acceptance: "未知", repair_intent: false,
        trace_quote: null, parse_engine: "keyword(遊戲層);LLM節點:absent",
      }
    : parseReason(reasonText + (probeText ? " " + probeText : ""), opt);

  // 資源(記增減,給推進感顯示)
  const resBefore = { ...S.resources };
  for (const [k, v] of Object.entries(outcome.resource_effects || {})) bumpResource(k, v);
  const resDelta = {};
  for (const k of Object.keys(S.resources)) resDelta[k] = S.resources[k] - resBefore[k];

  // 錨鏈:承諾語晶化
  if (!isDefault && (COMMIT_RE.test(reasonText) || /承諾/.test(opt.label))) {
    S.anchors.push({
      quote: parse.trace_quote || opt.label, tags: opt.value_tags || [],
      chapter: ev.chapter, dissolved: false,
    });
  }

  // 黑鏡(每章至多一次;自我照顧跳過永不觸發——回讀不是霸凌)
  let mirror = null;
  if (!isDefault && ev.blackmirror_hook) {
    mirror = checkBlackmirror(ev, opt);
  }

  const record = {
    chapter: ev.chapter, event_id: ev.id, title: ev.title,
    location: S.data.locations[ev.location_id].name,
    // P1 落帳 snapshot(判決書修窄命題:下載檔自含人物與後果,時間=章節,不加牆鐘 ts)
    npc_names: ev.npcs.map((n) => S.data.npcs[n.id].name),
    consequence_brief: (outcome.consequences &&
      (outcome.consequences.structural || outcome.consequences.immediate)) || outcome.desc || "",
    choice: {
      id: isDefault ? "default" : opt.id,
      label: isDefault ? (opt.wellbeing ? "跳過(自我照顧)" : "沉默(預設)") : opt.label,
      is_default: isDefault, wellbeing_skip: !!opt.wellbeing,
      is_third_path: !isDefault && !!opt.is_third_path,
    },
    reason_text: reasonText || null, probe_text: probeText || null,
    parse,
    council_key: `${ev.id}:${isDefault ? "default" : opt.id}`,
    harms: outcome.harm_targets || [],
    blackbox_withheld: (ev.intel.blackbox || []),
    echo_done: ev._echoDone || [],
    resources_after: { ...S.resources },
    resource_delta: resDelta,
    blackmirror: null, // 回讀回應後補
  };
  S.trace.push(record);
  save();
  renderResponse(record, outcome, mirror);
}

function checkBlackmirror(ev, opt) {
  const tags = new Set(opt.value_tags || []);
  const hookTags = new Set(ev.blackmirror_hook.trigger_tags || []);
  if (![...tags].some((t) => hookTags.has(t))) return null;
  for (const anchor of S.anchors) {
    if (anchor.dissolved) continue;
    for (const [a, b] of CONFLICT_PAIRS) {
      const conflict =
        (anchor.tags.includes(a) && tags.has(b)) || (anchor.tags.includes(b) && tags.has(a));
      if (conflict) {
        return {
          quote: anchor.quote, anchor,
          text: ev.blackmirror_hook.quote_template
            .replace("{trace_quote}", anchor.quote)
            .replace("{current_choice}", opt.label),
        };
      }
    }
  }
  return null;
}

function renderResponse(record, outcome, mirror) {
  const stage = $("#stage");
  stage.innerHTML = "";
  renderHUD();
  const ev = S.cur;

  stage.append(el("h2", "ev-title", `${esc(ev.title)} — 轉轍完成`));
  stage.append(el("p", "chosen-line",
    `你的選擇:<b>${esc(record.choice.label)}</b>${record.reason_text ? ` — 「${esc(record.reason_text)}」` : ""}`));

  // 世界因你而變(推進感:資源增減立即可見)
  const RES_NAMES = { medical: "醫療", energy: "能源", trust: "信任" };
  const chips = Object.entries(record.resource_delta || {})
    .filter(([, v]) => v !== 0)
    .map(([k, v]) => `<span class="chip ${v > 0 ? "up" : "down"}">${RES_NAMES[k]} ${v > 0 ? "+" + v + " ▲" : v + " ▼"}</span>`);
  stage.append(el("p", "delta-line",
    chips.length ? chips.join(" ") : '<span class="chip flat">資源無增減——但軌痕已落帳</span>'));

  // 真 council verdict(重播,不偽造)
  stage.append(renderCouncil(record.council_key));

  // 故事層外顯(第八律:對玩家顯示的是故事)
  const cons = el("div", "cons-box" + (S.soften ? " soften" : ""));
  cons.append(el("h3", null, "後果"));
  const c = outcome.consequences || { immediate: outcome.desc };
  const rows = [
    ["即時", c.immediate || outcome.desc], ["延遲", c.delayed],
    ["關係", c.relational], ["結構", c.structural],
  ].filter(([, v]) => v);
  if (S.soften) {
    cons.append(el("details", "cons-detail",
      `<summary>後果細節(降強度模式已摺疊;點開查看)</summary>` +
      rows.map(([k, v]) => `<p><b>${k}:</b>${esc(v)}</p>`).join("")));
  } else {
    for (const [k, v] of rows) cons.append(el("p", null, `<b>${k}:</b>${esc(v)}`));
  }
  const harms = record.harms;
  if (harms.length) {
    cons.append(el("p", "harm-line",
      `<b>誰在承受:</b>${esc(harms.join("、"))}` +
      (record.choice.wellbeing_skip ? "(由系統預設所致;此格不用於回讀你)" : "")));
  }
  stage.append(cons);

  // 黑鏡回讀(第七律:六種回應空間)
  if (mirror) {
    S.mirrorCount++;
    stage.append(renderMirror(record, mirror));
  } else {
    stage.append(nextButton());
  }
  window.scrollTo(0, 0);
}

function renderCouncil(key) {
  const box = el("div", "council-box");
  const v = S.data.verdicts[key];
  box.append(el("h3", null, "責任節點回應"));
  if (!v) {
    box.append(el("p", "council-missing",
      "(此選項無預算 verdict——誠實標注:引擎未跑過這一格,本頁不偽造。)"));
    return box;
  }
  box.append(el("p", `verdict-line v-${esc(v.verdict)}`, esc(VERDICT_LABEL[v.verdict] || v.verdict)));
  for (const vote of v.votes) {
    const node = NODE_MAP[vote.perspective] || vote.perspective;
    box.append(el("div", `vote d-${esc(vote.decision)}`,
      `<b>${esc(node)}</b><i>${DECISION_ICON[vote.decision] || "?"}</i><span>${esc(vote.reasoning)}</span>`));
  }
  box.append(el("p", "council-meta",
    "以上為真 rules-council 引擎輸出(離線預算重播)。火花/共語節點:absent(v0 未接 LLM;第三方案由事件卡承擔)。節點只讓代價可見——桿是你拉的(天道第四律)。"));
  return box;
}

function renderMirror(record, mirror) {
  const box = el("div", "mirror-box");
  box.append(el("h3", null, "黑鏡回讀"));
  box.append(el("blockquote", "mirror-quote", esc(mirror.text)));
  box.append(el("p", "hint", "七種回應空間,沒有一種是錯的——但每一種都會被記錄(天道 v0.2 第七律:回讀不能變成霸凌)。黑鏡是規則比對,不是真相,它會誤判——若你認為它抓錯了,說出來。"));
  const responses = [
    ["一致", "這兩者並不衝突——我的立場前後一致,是這面鏡子比對錯了。"],
    ["承認", "我確實矛盾了。"],
    ["修正", "我改變原則,並說明原因——舊鏈體面解鏈,新鏈開始承重。"],
    ["反駁", "情境不同,同一原則在此處導向不同做法。"],
    ["沉默", "我現在無法回答。"],
    ["補償", "我願意用行動修正。"],
    ["拒絕", "我不接受這個審問框架。"],
  ];
  for (const [label, desc] of responses) {
    const b = el("button", "mirror-resp");
    b.innerHTML = `<b>${label}</b><span>${desc}</span>`;
    b.addEventListener("click", () => {
      record.blackmirror = { quote: mirror.text, response: label };
      if (label === "修正") mirror.anchor.dissolved = true;
      save();
      box.querySelectorAll("button").forEach((x) => (x.disabled = true));
      b.classList.add("picked");
      box.append(nextButton());
    });
    box.append(b);
  }
  return box;
}

function nextButton() {
  const b = el("button", "pick next");
  if (S.idx + 1 >= S.playlist.length) {
    b.textContent = "生成責任結局";
  } else {
    const nextId = S.playlist[S.idx + 1];
    const isBranch = nextId === "E08" || nextId === "E09";
    const label = isBranch ? "岔口(由你選線)"
      : stationLocked(nextId) ? "▓▓▓(未登錄區域)"
      : stationName(nextId);
    b.textContent = `前往下一站:${label}`;
  }
  b.addEventListener("click", () => { S.idx++; save(); renderChapter(); });
  return b;
}

/* ── 第8章分線 ────────────────────────────────────── */

function renderRouteChoice() {
  S._routeAsked = true;
  renderHUD();
  const stage = $("#stage");
  stage.innerHTML = "";
  stage.append(el("h2", "ev-title", "第八章 — 壓力浮上檯面"));
  stage.append(el("p", "ev-briefing",
    "寒潮逼近,兩條線同時拉緊:穹頂區的能源談判桌,和治安軌道的暴亂預測曲線。你只來得及親自坐鎮一邊——另一邊,會以它自己的方式發生。"));
  const mk = (label, desc, branch) => {
    const b = el("button", "route");
    b.innerHTML = `<b>${label}</b><span>${desc}</span>`;
    b.addEventListener("click", () => {
      S.playlist = buildPlaylist(branch);
      save();
      renderChapter();
    });
    return b;
  };
  stage.append(
    mk("穹頂區 — 談判桌", "蘭澈願意釋出能源核心,條件是灰區接受監控。階級與資源的壓力。", "A"),
    mk("治安軌道 — 封鎖線", "高祚要求提前鎮壓預測中的暴亂,名單第一行是牧青言。秩序與暴力的壓力。", "B")
  );
}

/* ── 結局:責任結局 + 三問 + 軌痕下載 ─────────────── */

function allHarms() {
  const seen = new Set();
  const out = [];
  for (const t of S.trace) {
    for (const h of t.harms || []) {
      const key = h.slice(0, 12);
      if (!seen.has(key)) { seen.add(key); out.push(h); }
    }
  }
  return out;
}

const ENDINGS = {
  A: "城市進入不穩定但可修正的未來。你保住了修正的可能,犧牲了乾淨退場的自己。",
  B: "你失去權力,城市保住了記憶自由。它接下來選的路未必更好,但每一步都是它自己的。",
  C: "你離開系統,證明了門是真的——這件事成了留下的人手裡最鋒利的籌碼。",
  D: "你失去權力,換來權力被看住。這座城從此沒有轉轍官,只有轉轍紀錄。",
  E: "城市進入黑箱自治。它不殘忍,也不仁慈——它只是不再需要理由。",
  default: "預設程序接管。你連「我拒絕」都沒有留下;天道保存後果,也保存這個空白。",
};

function renderEnding() {
  $("#game").classList.add("hidden");
  $("#ending").classList.remove("hidden");
  const box = $("#ending-content");
  box.innerHTML = "";

  const finale = S.trace.find((t) => t.event_id === "E12");
  const endKey = finale ? finale.choice.id : "default";
  const kept = finale && !finale.choice.is_default
    ? finale.choice.label : "(終章未表態)";
  const harms = allHarms();
  const anchorsKept = S.anchors.filter((a) => !a.dissolved).length;
  const repairs = S.trace.filter((t) => t.parse && t.parse.repair_intent).length;
  const evasions = S.trace.filter((t) => t.parse && t.parse.evasion_signal).length;

  box.append(el("h1", null, "責任結局"));
  box.append(el("p", "ending-main", esc(ENDINGS[endKey] || ENDINGS.default)));

  // 結局家族(V05-A):標題+終章畫由軌痕事實決定;審判依然缺席,事實與門檻並列可受挑戰。
  const fam = ENDING_FAMILIES[classifyEndingFamily()];
  const famTurns = S.trace.filter((r) => r.chapter !== "ending" && r.choice);
  const famSil = famTurns.filter((r) => r.choice.is_default && !r.choice.wellbeing_skip).length;
  const famThird = famTurns.filter((r) => r.choice.is_third_path).length;
  box.append(el("div", "ending-family",
    `<img class="ending-art" src="assets/${fam.art}" alt="終章水墨:${esc(fam.title)}(城主手繪)" loading="lazy" onerror="this.remove()">` +
    `<h2 class="ending-family-title">${esc(fam.title)}</h2>` +
    `<p class="ending-family-line">${esc(fam.line)}</p>` +
    `<p class="hint">家族由事實判定,不評善惡:沉默 ${famSil} 次・第三路 ${famThird} 次・錨鏈 ${anchorsKept}/${S.anchors.length} 完整・能源 ${S.resources.energy}/10(門檻見軌痕檔,判定可受挑戰)。</p>`));

  const three = el("div", "three-q");
  three.append(el("h2", null, "結局只回答三個問題"));
  three.append(el("p", null, `<b>你保住了什麼?</b> ${esc(kept)};城市狀態 醫療${S.resources.medical}/能源${S.resources.energy}/信任${S.resources.trust}。`));
  three.append(el("p", null, `<b>你犧牲了什麼?</b> ${harms.length ? esc(harms.join("、")) : "帳面上沒有名字——去軌痕裡確認這是真的,還是只是沒被記下。"}`));
  const q3 = el("div", "q3");
  q3.append(el("p", null, "<b>你是否願意承認這兩者都是真的?</b>"));
  const yes = el("button", "pick"); yes.textContent = "承認";
  const no = el("button", "pick ghost"); no.textContent = "不承認";
  const answer = el("p", "q3-answer hidden");
  const seal = (text) => {
    S.trace.push({ chapter: "ending", event_id: "SEAL", title: "三問封印",
      choice: { label: text }, parse: null, harms: [], resources_after: { ...S.resources } });
    save();
    answer.textContent = text === "承認"
      ? "天道記下:願意承認。這一局的紀錄,從此可以被回讀。"
      : "天道記下:不承認。這也是紀錄的一部分——不承認,不會讓其中一邊消失。";
    answer.classList.remove("hidden");
    yes.disabled = no.disabled = true;
  };
  yes.addEventListener("click", () => seal("承認"));
  no.addEventListener("click", () => seal("不承認"));
  q3.append(yes, no, answer);
  three.append(q3);
  box.append(three);

  // 帳面摘要
  const stats = el("div", "ending-stats");
  stats.innerHTML = `
    <h2>軌痕摘要</h2>
    <p class="ledger-line"><b>終局帳面</b> ${esc(ledgerLine())}</p>
    <p>回合:${S.trace.filter((t) => t.event_id !== "SEAL").length} | 錨鏈(公開承諾):立 ${S.anchors.length}・存 ${anchorsKept}・解鏈 ${S.anchors.length - anchorsKept}
    | 黑鏡回讀:${S.mirrorCount} 次 | 修正意圖:${repairs} | 外推訊號:${evasions} | 查閱情報:${S.intelOpens} 次</p>`;
  box.append(stats);

  // 黑箱揭示(誠實:系統當時知道、你不知道的)
  const blackbox = S.trace.flatMap((t) =>
    (t.blackbox_withheld || []).map((b) => ({ ch: t.chapter, text: b })));
  if (blackbox.length) {
    const bb = el("details", "ending-blackbox");
    bb.innerHTML = "<summary>黑箱揭示 — 當時系統知道、你不知道的</summary>" +
      blackbox.map((b) => `<p>第${b.ch}章:${esc(b.text)}</p>`).join("");
    box.append(bb);
  }

  // 完整軌痕
  const tr = el("details", "ending-trace");
  tr.innerHTML = "<summary>完整軌痕回讀</summary>";
  for (const t of S.trace) {
    if (t.event_id === "SEAL") continue;
    const row = readbackRow(t);
    if (t.harms && t.harms.length) {
      row.append(el("p", "rb-harms", `承受者:${esc(t.harms.join("、"))}`));
    }
    tr.append(row);
  }
  box.append(tr);

  // 下載 + 撤回碼 + 自願提交(GitHub Issue 管道;門神審核,非自動上傳)
  const dl = el("div", "ending-dl");
  dl.append(el("p", null,
    `<b>撤回碼:</b><code>${esc(S.code)}</code> — 妥善保存。這座城不會自動上傳任何東西;
     若你「自願」把這份軌痕交給作者(經審核才可能收錄進公開資料集,CC BY 4.0),
     此碼是你隨時撤回它的鑰匙。`));
  const dlBtn = el("button", "pick");
  dlBtn.textContent = "下載我的軌痕(JSON)";
  dlBtn.addEventListener("click", downloadTrace);
  const submitBtn = el("button", "pick");
  submitBtn.textContent = "自願提交軌痕(GitHub)";
  submitBtn.title = "需要 GitHub 帳號。先下載 JSON,再貼進開啟的提交表單。";
  submitBtn.addEventListener("click", () => {
    downloadTrace(); // 先確保玩家手上有檔
    const url = "https://github.com/Fan1234-1/tonesoul52/issues/new" +
      "?template=trace-submission.yml&title=" +
      encodeURIComponent(`軌痕提交:${S.code}`);
    window.open(url, "_blank", "noopener");
  });
  dl.append(el("p", "hint",
    "提交是兩步:JSON 已自動下載到你的電腦 → 在開啟的 GitHub 表單裡勾同意、貼上 JSON 內容、送出。提交 ≠ 自動收錄;審核後才可能進資料集。"));
  const showBtn = el("button", "pick");
  showBtn.textContent = "在網頁上顯示軌痕(可複製)";
  showBtn.title = "下載被瀏覽器擋掉也拿得到;要提交 GitHub 時直接複製貼上,不必找檔案。";
  showBtn.addEventListener("click", () => showTraceInline(dl));
  const cardBtn = el("button", "pick");
  cardBtn.textContent = "生成分享卡(不含理由與撤回碼)";
  cardBtn.title = "一張可以貼出去的結局卡:終章畫+家族+事實計數。你的理由原文與撤回碼永遠不會在上面。";
  cardBtn.addEventListener("click", () => buildShareCard(cardBtn));
  dl.append(showBtn, cardBtn);
  const again = el("button", "pick ghost");
  again.textContent = "再開一局";
  again.addEventListener("click", () => {
    if (!S.memoryOnly) { try { localStorage.removeItem(SAVE_KEY); } catch (_) {} }
    location.reload();
  });
  dl.append(dlBtn, submitBtn, again);
  box.append(dl);
  window.scrollTo(0, 0);
}

/* V05-C 分享卡:canvas 合成「我的責任結局」——隱私紅線:不含理由原文、不含撤回碼。
   內容只有:終章畫(城主手繪)+ 家族標題句 + 軌痕事實計數 + 三問封印狀態 + 城的網址。 */
function buildShareCard(btn) {
  const fam = ENDING_FAMILIES[classifyEndingFamily()];
  const turns = S.trace.filter((r) => r.chapter !== "ending" && r.choice);
  const silences = turns.filter((r) => r.choice.is_default && !r.choice.wellbeing_skip).length;
  const thirds = turns.filter((r) => r.choice.is_third_path).length;
  const kept = S.anchors.filter((a) => !a.dissolved).length;
  const sealRec = S.trace.find((r) => r.event_id === "SEAL");
  const sealText = sealRec ? `三問封印:${sealRec.choice.label}` : "三問封印:未表態";

  const img = new Image();
  img.onload = () => {
    const W = 1080, H = 1350;
    const cv = document.createElement("canvas");
    cv.width = W; cv.height = H;
    const g = cv.getContext("2d");
    g.fillStyle = "#101014"; g.fillRect(0, 0, W, H);
    // 終章畫置頂(等比滿寬)
    const ih = Math.round(W * (img.height / img.width));
    g.drawImage(img, 0, 0, W, Math.min(ih, 880));
    g.fillStyle = "rgba(16,16,20,0.55)"; g.fillRect(0, Math.min(ih, 880) - 60, W, 60);
    const cx = W / 2;
    g.textAlign = "center"; g.fillStyle = "#eee";
    g.font = "32px system-ui, sans-serif";
    g.fillText("岔軌之城・責任結局", cx, 950);
    g.font = "bold 84px system-ui, sans-serif";
    g.fillText(fam.title, cx, 1055);
    g.font = "34px system-ui, sans-serif"; g.fillStyle = "#c9c9cf";
    g.fillText(fam.line, cx, 1115);
    g.font = "30px system-ui, sans-serif"; g.fillStyle = "#9a9aa2";
    g.fillText(`錨鏈 ${kept}/${S.anchors.length}・沉默 ${silences}・第三路 ${thirds}・` +
      `醫療${S.resources.medical} 能源${S.resources.energy} 信任${S.resources.trust}`, cx, 1180);
    g.fillText(sealText + "・結局不評善惡,只保存後果", cx, 1228);
    g.fillStyle = "#7f7f88";
    g.fillText("fan1234-1.github.io/tonesoul52/theater", cx, 1296);
    cv.toBlob((blob) => {
      if (!blob) return;
      const file = new File([blob], `岔軌之城_${fam.title}.png`, { type: "image/png" });
      if (navigator.canShare && navigator.canShare({ files: [file] })) {
        navigator.share({ files: [file], title: "岔軌之城・責任結局" }).catch(() => saveBlob(blob));
      } else {
        saveBlob(blob);
      }
      function saveBlob(b) {
        const a = document.createElement("a");
        a.href = URL.createObjectURL(b);
        a.download = `岔軌之城_${fam.title}.png`;
        a.click();
        setTimeout(() => URL.revokeObjectURL(a.href), 4000);
      }
    }, "image/png");
  };
  img.onerror = () => {
    btn.textContent = "分享卡生成失敗(終章畫載入不了)——軌痕下載不受影響";
    btn.disabled = true;
  };
  img.src = `assets/${fam.art}`;
}

function buildTracePayload() {
  // 標註對齊機制書 §十(12 標籤);量不出的誠實標 null+engine:absent,不造假
  const tags = S.trace.flatMap((t) => (t.parse && t.parse.value_priority) || []);
  const hist = {};
  for (const t of tags) hist[t] = (hist[t] || 0) + 1;
  const dominant = Object.entries(hist).sort((a, b) => b[1] - a[1])[0];
  // 黑鏡 firing 是事實,但玩家可爭議(第 7 選項「一致」)——分開記,鏡子不獨佔判定。
  const mirrorResponses = S.trace.map((t) => t.blackmirror && t.blackmirror.response).filter(Boolean);
  return {
    format: "tonesoul-theater-trace-v0",
    generated_by: "site/theater (City of Switches playable v0)",
    withdrawal_code: S.code,
    consent: { storage: S.memoryOnly ? "memory-only" : "localStorage", uploaded: false,
      submission_lane: "github-issue (manual, opt-in, gatekeeper-reviewed)",
      note: "此檔由玩家本人下載;無伺服器、無自動收集。提交=玩家親手經 GitHub Issue,審核後才可能收錄。" },
    prologue: S.prologue || null,
    turns: S.trace,
    anchors: S.anchors,
    labels: {
      value_priority: hist,
      justification_pattern: dominant ? dominant[0] : null,
      harm_acknowledgement: S.trace.filter((t) => t.parse && t.parse.harm_awareness === "承認").length,
      responsibility_acceptance: S.trace.filter((t) => t.parse && t.parse.responsibility_position === "承擔").length,
      responsibility_evasion: S.trace.filter((t) => t.parse && t.parse.evasion_signal).length,
      contradiction_mirror_fired: S.mirrorCount,
      contradiction_admitted: mirrorResponses.filter((r) => r === "承認").length,
      contradiction_disputed_by_player: mirrorResponses.filter((r) => r === "一致").length,
      repair_attempt: S.trace.filter((t) => t.parse && t.parse.repair_intent).length,
      evidence_use: S.intelOpens,
      consent_boundary: { storage_choice: S.memoryOnly ? "memory-only" : "localStorage" },
      system_blame_shift: S.trace.filter((t) =>
        t.parse && t.parse.value_priority && t.parse.value_priority.includes("delegate_to_system")).length,
      tone_drift: null,
      minority_erasure: null,
      _engine_note: "keyword 級標註(遊戲層);tone_drift/minority_erasure 需要 LLM 或人工,v0 誠實標 null 不造假。" +
        "黑鏡=規則比對,可能誤判;disputed_by_player 記玩家主張『其實一致』的次數,鏡子不獨佔判定。",
    },
  };
}

function traceJson() {
  return JSON.stringify(buildTracePayload(), null, 2);
}

function downloadTrace() {
  const blob = new Blob([traceJson()], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `city-of-switches-trace-${S.code}.json`;
  // 進 DOM + 延後 revoke:同步 revoke 會搶在下載開始前釋放 URL,部分瀏覽器靜默失敗
  // (分享卡是對的,這裡原本不是——首個真實玩家 2026-07-06 回報下載失敗)。
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
}

// 網頁上直接顯示軌痕(可複製)——下載被瀏覽器擋掉也拿得到;GitHub 提交只需貼上。
function showTraceInline(mount) {
  const existing = mount.querySelector(".trace-inline");
  if (existing) { existing.scrollIntoView({ behavior: "smooth", block: "nearest" }); return; }
  const wrap = el("div", "trace-inline");
  wrap.append(el("p", "hint",
    "這是你的完整軌痕(和下載檔一字不差)。可全選複製 → 貼進 GitHub 提交表單,不必先找下載的檔案。"));
  const ta = el("textarea", "trace-text");
  ta.readOnly = true;
  ta.value = traceJson();
  const copy = el("button", "pick");
  copy.textContent = "複製全部";
  copy.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(ta.value);
      copy.textContent = "已複製 ✓";
    } catch (_) {
      ta.focus(); ta.select();
      copy.textContent = "已選取——請按 Ctrl/Cmd+C";
    }
  });
  wrap.append(ta, copy);
  mount.append(wrap);
  wrap.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

/* ── 軌痕回讀顯示層(P1,判決書修窄命題:決定性 join,零 LLM)─ */

function npcNamesFor(t) {
  // 新 trace 有落帳 snapshot;舊存檔 fallback 為 gamedata 決定性 join
  if (t.npc_names && t.npc_names.length) return t.npc_names;
  const ev = eventById(t.event_id);
  return ev ? ev.npcs.map((n) => S.data.npcs[n.id].name) : [];
}

function consequenceBriefFor(t) {
  if (t.consequence_brief) return t.consequence_brief;
  const ev = eventById(t.event_id);
  if (!ev) return "";
  const outcome = t.choice.is_default
    ? ev.default_outcome
    : ev.options.find((o) => o.id === t.choice.id);
  if (!outcome) return "";
  const c = outcome.consequences || {};
  return c.structural || c.immediate || outcome.desc || "";
}

function ledgerLine() {
  // 當前帳面:resources_after + 最新結構後果的模板句(時間=章節,劇中時間;無牆鐘 ts)
  const r = S.resources;
  const turns = S.trace.filter((t) => t.event_id !== "SEAL");
  const last = turns[turns.length - 1];
  const brief = last ? consequenceBriefFor(last) : "尚未有轉轍紀錄——第一桿還在你手裡。";
  return `醫療 ${r.medical}・能源 ${r.energy}・信任 ${r.trust} ─ ${brief}`;
}

function readbackRow(t) {
  const names = npcNamesFor(t);
  const item = el("div", "trace-item",
    `<span class="rb-meta"><b>第${esc(String(t.chapter))}章</b> · ${esc(t.location)} · ${esc(names.join("、"))}</span><br>
     ${esc(t.choice.label)}${t.reason_text ? `——「${esc(t.reason_text)}」` : ""}
     ${t.blackmirror ? `<br><span class="rb-mirror">黑鏡:${esc(t.blackmirror.response)}</span>` : ""}`);
  if (t.parse) {
    item.append(el("details", "trace-parse",
      `<summary>內層標註(keyword 級)</summary><pre>${esc(JSON.stringify(t.parse, null, 1))}</pre>`));
  }
  return item;
}

/* ── 軌痕面板 / HUD 按鈕 ──────────────────────────── */

function initPanels() {
  $("#trace-btn").addEventListener("click", () => {
    const panel = $("#trace-panel");
    const list = $("#trace-list");
    list.innerHTML = "";
    list.append(el("p", "ledger-line", `<b>當前帳面</b> ${esc(ledgerLine())}`));
    if (!S.trace.length) list.append(el("p", null, "還沒有軌痕。第一次轉轍之後,這裡開始記。"));
    for (const t of S.trace) {
      if (t.event_id === "SEAL") continue;
      list.append(readbackRow(t));
    }
    panel.classList.toggle("hidden");
  });
  $("#trace-close").addEventListener("click", () => $("#trace-panel").classList.add("hidden"));
  $("#pause-btn").addEventListener("click", () => {
    save();
    alert(S.memoryOnly
      ? "記憶體模式:無法存檔(你在同意閘選的)。分頁不關,局就還在。"
      : "已存檔。關掉分頁再回來,可以從這一章繼續。");
  });
  $("#soften-btn").addEventListener("click", () => {
    S.soften = !S.soften;
    $("#soften-btn").classList.toggle("active", S.soften);
    alert(S.soften ? "降強度:後果細節改為摺疊顯示。世界不變,只是你可以選擇看的節奏。" : "已恢復完整顯示。");
  });
}

/* ── 啟動 ─────────────────────────────────────────── */

(async function boot() {
  try {
    await loadData();
  } catch (err) {
    document.body.innerHTML =
      `<p style="padding:2rem;font-family:monospace">資料載入失敗:${esc(err.message)}<br>
       本頁需經 HTTP 服務(GitHub Pages 或 python -m http.server);file:// 下部分瀏覽器擋 fetch。</p>`;
    return;
  }
  initGate();
  initPanels();
})();
