# 判決書:weavai 功能結晶(P1/P2/P3)— 2026-07-04

> 協議:`.claude/skills/honest-judgment/SKILL.md` 四步全走(拆題/五視角真分身/對抗裁決/落痕)。
> 模式:判決模式(可裁決行動命題)。
> 起因:owner 在 weavai.app 跑《岔軌之城》成功(兩局導出截圖為證),但軌痕留在對方平台;
> 問「要不要把該網頁的好功能結晶進自己的 site/theater/?」
> 視角:Guardian/Analyst/Advocate/Axiomatic=fable 同模型(**correlated-blind-spot 已標**:
> 全體可能高估「零伺服器=美德」框架)+ **Critic=codex(異模型)**;裁決 agent=fable(同模型,
> 以親驗碼層補獨立錨)。五案原文:`tmp/weavai_judgment/case_*.md`(gitignored 工作檔,
> 結論以本檔為準);證據簡報:`tmp/weavai_judgment/evidence_brief.md`。

## 前提事實(裁決前親驗)

- PR #295 = OPEN / MERGEABLE / 16 checks 綠;theater 檔案 origin/master 0 個、PR 分支 8 個
  (E3:`gh pr view` + `git ls-tree`)。**另一 session「README 說謊」判定=誤診**:它把
  本機工作樹(停在 PR 分支,README 與實作同行)拿去比 origin/master。README 沒有超前
  敘述,只是 PR 未 merge。
- weavai 導出截圖(owner 提供,本 session 親讀):兩局(KANA-07、大哥哥),格式
  `時間|Location|People|Memory`,一行「當前狀態」;世界演進(信任冰點→軟化、授權額度、
  跨階級同盟)。可導出的只有壓縮摘要;完整上下文/跨世界判斷/結構化軌痕導不出。

## 判決

### P1 記憶摘要顯示層 — **REFINE(修窄後照做)**,信心 0.8

修窄命題:site/theater 加**純顯示層**——一行「當前帳面」(resources_after+最新結構後果
的模板句)+ 滾動軌痕回讀面板(`章節|地點|人物|抉擇+理由`)。資料=既有 trace record 與
已載 gamedata 的**決定性 join**(或落帳時 snapshot);時間欄=**章節(劇中時間),不新增
牆鐘 ts**;命名走正典詞彙(**軌痕回讀/當前帳面**,不叫「核心記憶庫」);memory-only 模式
純記憶體渲染;零 LLM、零伺服器。
- 關鍵事實修正(裁決調解):簡報原句「trace 欄位是 weavai 格式超集」**不精確**——
  record 無時間欄(app.js:481-498 親驗)、npcs 靠事件卡 join;精確版=「trace 單獨不是
  超集,**trace+gamedata 聯集才是**」(Analyst 案內文與主 agent 親驗共同逼出)。
- 翻案條件:實作後任一欄需要生成步驟才能填 → 回爐。

### P2 簡遺碎片交換(檔案、零伺服器)— **REFINE(開 v1 工單,不入 v0)**,信心 0.65

血統澄清(Axiomatic 案):簡遺是 owner 自家正典、早於 weavai 約半年
(`data/YuHun_v2.6_knowledgebase.json:61` @ 9e6a93ab,2026-01-10)——P2 是**實現自家
正典**,不是抄外部。修窄命題(v1 工單五要件):
1. 碎片檔格式 spec:碎片=抉擇+短理由**節選**,非全 trace;
2. **匯出先行**+獨立同意文案,明文「遞出後無法遠端撤回;撤回碼僅對未來資料集提交有效」
   (Axiom 8 語義先寫出);
3. 匯入裁決閘:埋葬/續寫/反駁事件卡 + **隔離艙**(永不併入本人 trace 主體、永不進
   dataset human lane、一律標 `provenance: unverified-import`、esc()+schema+大小上限);
4. **不宣稱防偽**(零伺服器下無機制,誠實標注);
5. 分發/配對以**真實第二玩家出現**為觸發器,之前不建。
- 翻案條件:第二玩家出現 → 分發側解鎖;Axiom 8 碎片同意語義寫不出誠實版 → 轉 BLOCK。

### P3 即時多人 LLM 世界引擎 — **BLOCK-now(advisory,選擇權在人)**,信心 0.75

- 反方最強(E3 親驗):「v0 無伺服器、無自動收集」已嵌進**每份下載軌痕檔**
  (app.js:780-781)——上伺服器=既有書面承諾成為錯誤陳述、同意契約整組重寫;
  疊加 7/7 後可能零預算。
- 正方最強:LLM 即興敘事的體驗價值(截圖 E3)——但那證明的是**價值**,不是**現在建**;
  owner 原文「想要功能」≠「接受成本」,讀成後者是投射。
- **判決只鎖「今天動工」,不鎖這條路。**翻案條件(可觀察):
  (1) owner 明文接受伺服器成本與運維責任;
  (2) 托管憲章先立(保存/刪除/撤回的伺服器端強制+熄燈計畫)過 council+owner 終審;
  (3) 中間路徑(BYO-key 客戶端 LLM 節點=正典 live 選項 + P2 非同步交換)驗證後仍
  承接不了 → P3 重開。

## 一句話

weavai 免費驗證了你的世界好玩、格式好讀、有第二個玩家想玩——把已驗證的**形狀**搬回
同意閘與撤回碼之下(P1 現在做、P2 開 v1 工單),把**托管責任**留在你親手簽下成本的
那天(P3 擋今天、不擋這條路,鑰匙在你)。

## 落痕

- 反證鏈:簡報宣稱「trace 欄位是超集」被裁決親驗修窄(outcome=narrowed,#24)。
- P1 實作與 P2 工單=owner 點頭後動工(本判決 advisory;P1 無價值承擔屬技術範圍,
  P2/P3 涉同意契約與成本=owner 終審)。
