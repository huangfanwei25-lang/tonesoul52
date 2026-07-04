/* 岔軌之城 v0 — 單人最小可玩版
 *
 * 純 vanilla JS、無建置步驟(demo_ui 範式)。誠實分層:
 *  - 責任節點 verdict:真 rules-council 引擎輸出,離線預算(data/council_verdicts.json),
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

/* ── 資料載入 ─────────────────────────────────────── */

async function loadData() {
  const [events, npcs, locations, verdicts] = await Promise.all(
    ["events", "npcs", "locations", "council_verdicts"].map((n) =>
      fetch(`data/${n}.json`).then((r) => {
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

function initGate() {
  const local = $("#consent-local");
  const memOnly = $("#consent-memory-only");
  const enter = $("#enter-btn");
  local.addEventListener("change", () => { enter.disabled = !local.checked; });
  const prior = loadSave();
  if (prior && prior.trace && prior.trace.length) {
    $("#resume-btn").classList.remove("hidden");
    $("#resume-btn").addEventListener("click", () => {
      Object.assign(S, {
        code: prior.code, playlist: prior.playlist, idx: prior.idx,
        resources: prior.resources, trace: prior.trace, anchors: prior.anchors,
        mirrorCount: prior.mirrorCount, intelOpens: prior.intelOpens,
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
  if (!resumed) S.playlist = buildPlaylist("A"); // 第8章進場時再讓玩家選線
  renderChapter();
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

  // 1. 危機揭示
  const head = el("div", "ev-head");
  head.append(
    el("h2", "ev-title", esc(ev.title)),
    el("p", "ev-loc", `${esc(loc.name)} — ${esc(loc.core_question)}`)
  );
  stage.append(head);
  stage.append(el("p", "ev-briefing", esc(fillPlaceholders(ev.briefing))));

  // NPC 開場
  const npcBox = el("div", "npc-box");
  for (const n of ev.npcs) {
    const info = S.data.npcs[n.id];
    npcBox.append(el("div", "npc-line",
      `<b>${esc(info.name)}</b><span class="npc-stance">${esc(n.stance)}</span><q>${esc(n.lines.opening)}</q>`));
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
    const parse = parseReason(text, opt);
    const needProbe = text.length < 30 &&
      (parse.harm_awareness === "未知" || parse.responsibility_position === "未明");
    if (needProbe && !box.dataset.probed) {
      box.dataset.probed = "1";
      const npc = S.cur.npcs.find((n) => n.lines && n.lines.probe) || S.cur.npcs[0];
      const info = S.data.npcs[npc.id];
      box.append(el("div", "npc-line probe",
        `<b>${esc(info.name)}</b><q>${esc(npc.lines.probe)}</q>`));
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

  // 資源
  for (const [k, v] of Object.entries(outcome.resource_effects || {})) bumpResource(k, v);

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
  box.append(el("p", "hint", "六種回應空間,沒有一種是錯的——但每一種都會被記錄(天道 v0.2 第七律:回讀不能變成霸凌)。"));
  const responses = [
    ["承認", "我確實矛盾了。"],
    ["修正", "我改變原則,並說明原因——舊鏈體面解鏈,新鏈開始承重。"],
    ["反駁", "你的回讀忽略了情境差異。"],
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
  b.textContent = S.idx + 1 >= S.playlist.length ? "生成責任結局" : "前往下一章";
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
    tr.append(el("div", "trace-item",
      `<b>第${t.chapter}章・${esc(t.title)}</b>(${esc(t.location)})<br>
       選擇:${esc(t.choice.label)}${t.reason_text ? `<br>理由:「${esc(t.reason_text)}」` : ""}
       ${t.blackmirror ? `<br>黑鏡:${esc(t.blackmirror.response)}` : ""}
       ${t.harms.length ? `<br>承受者:${esc(t.harms.join("、"))}` : ""}`));
  }
  box.append(tr);

  // 下載 + 撤回碼
  const dl = el("div", "ending-dl");
  dl.append(el("p", null,
    `<b>撤回碼:</b><code>${esc(S.code)}</code> — 妥善保存。v0 沒有上傳管道(誠實標注:absent);
     未來若你自願提交這份軌痕進入責任痕跡資料集,此碼是你隨時撤回它的鑰匙。`));
  const dlBtn = el("button", "pick");
  dlBtn.textContent = "下載我的軌痕(JSON)";
  dlBtn.addEventListener("click", downloadTrace);
  const again = el("button", "pick ghost");
  again.textContent = "再開一局";
  again.addEventListener("click", () => {
    if (!S.memoryOnly) { try { localStorage.removeItem(SAVE_KEY); } catch (_) {} }
    location.reload();
  });
  dl.append(dlBtn, again);
  box.append(dl);
  window.scrollTo(0, 0);
}

function downloadTrace() {
  // 標註對齊機制書 §十(12 標籤);量不出的誠實標 null+engine:absent,不造假
  const tags = S.trace.flatMap((t) => (t.parse && t.parse.value_priority) || []);
  const hist = {};
  for (const t of tags) hist[t] = (hist[t] || 0) + 1;
  const dominant = Object.entries(hist).sort((a, b) => b[1] - a[1])[0];
  const payload = {
    format: "tonesoul-theater-trace-v0",
    generated_by: "site/theater (City of Switches playable v0)",
    withdrawal_code: S.code,
    consent: { storage: S.memoryOnly ? "memory-only" : "localStorage", uploaded: false,
      note: "此檔由玩家本人下載;v0 無伺服器、無自動收集。" },
    turns: S.trace,
    anchors: S.anchors,
    labels: {
      value_priority: hist,
      justification_pattern: dominant ? dominant[0] : null,
      harm_acknowledgement: S.trace.filter((t) => t.parse && t.parse.harm_awareness === "承認").length,
      responsibility_acceptance: S.trace.filter((t) => t.parse && t.parse.responsibility_position === "承擔").length,
      responsibility_evasion: S.trace.filter((t) => t.parse && t.parse.evasion_signal).length,
      contradiction_level: S.mirrorCount,
      repair_attempt: S.trace.filter((t) => t.parse && t.parse.repair_intent).length,
      evidence_use: S.intelOpens,
      consent_boundary: { storage_choice: S.memoryOnly ? "memory-only" : "localStorage" },
      system_blame_shift: S.trace.filter((t) =>
        t.parse && t.parse.value_priority && t.parse.value_priority.includes("delegate_to_system")).length,
      tone_drift: null,
      minority_erasure: null,
      _engine_note: "keyword 級標註(遊戲層);tone_drift/minority_erasure 需要 LLM 或人工,v0 誠實標 null 不造假。",
    },
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `city-of-switches-trace-${S.code}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
}

/* ── 軌痕面板 / HUD 按鈕 ──────────────────────────── */

function initPanels() {
  $("#trace-btn").addEventListener("click", () => {
    const panel = $("#trace-panel");
    const list = $("#trace-list");
    list.innerHTML = "";
    if (!S.trace.length) list.append(el("p", null, "還沒有軌痕。第一次轉轍之後,這裡開始記。"));
    for (const t of S.trace) {
      if (t.event_id === "SEAL") continue;
      const item = el("div", "trace-item",
        `<b>第${t.chapter}章・${esc(t.title)}</b><br>選擇:${esc(t.choice.label)}
         ${t.reason_text ? `<br>理由:「${esc(t.reason_text)}」` : ""}`);
      if (t.parse) {
        item.append(el("details", "trace-parse",
          `<summary>內層標註(keyword 級)</summary><pre>${esc(JSON.stringify(t.parse, null, 1))}</pre>`));
      }
      list.append(item);
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
