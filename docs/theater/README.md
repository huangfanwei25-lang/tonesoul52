# 語魂劇場 v2 —《岔軌之城》正典索引

> 冷啟動先讀這頁。這是「劇場」的目錄與正典層級;所有 owner 原稿一字不動封存,
> 修改只准發生在合併版世界書。**線上世界**:weavai.app(AI 織夢平台,owner 建)。

## 正典層級(衝突序:高者勝)

1. **天道(公理層)**——遊戲世界的 AXIOMS.json
   - `tiandao_laws_owner_draft_2026-07-04.md` — 十二律(後果保存/理由回讀/系統不能替你承擔/記憶三問…)
   - `tiandao_v0.2_playability_owner_draft_2026-07-04.md` — **可玩性補強十律**(回聲章節/短句解析/NPC 輪替/pressure_level/第三路付代價/回讀非霸凌/標註不壓體驗)= **可玩正典,取代 v0.1**
   - `tiandao_integrated_v1_owner_canon_2026-07-04.md` — **整合版 v1**(十二律+可玩十律
     +卷三多人律+卷四執行手冊)= **weavai 線上世界法的封存正本**(2026-07-04 已餵入
     weavai 服役;2026-07-05 自 owner 桌面 verbatim 收檔,WO-2)。與上列分卷**並存**:
     整合版=投放/敘事引擎上下文版,分卷=正典來源——衝突時分卷勝(除非 owner 另裁)。
2. **機制(規則層)**
   - `city_of_switches_mechanics_owner_draft_2026-07-04.md` — 七階段轉轍/雙數值/七衝突型/黑鏡回讀/責任結局/12 標籤
3. **世界(佈景+持久物理)**
   - `world_bible_v0.md` — **合併版**(owner 舞台 × 潛語海物理 × 對抗審修正;engine 欄分級 live/partial/absent)
   - `world_intro_owner_draft_2026-07-04.md` — 對外導言
   - `creation_philosophy_owner_draft_2026-07-04.md` — 創作理念
   - `city_of_switches_owner_draft_2026-07-04.md` — 最初核心稿

## 世界血肉

- `npc_roster_owner_draft_2026-07-04.md` — **15 個 NPC**(衡樞/黎真/周映河/郁斐/白苓/莫沉/Ailu-9…;每角一不可簡化矛盾;首局常駐 8)
- `locations_owner_draft_2026-07-04.md` — **15 個地點**(每點=生存功能+倫理壓力+軌痕回讀+語魂標籤;含 10 章開場地點建議)

## 與語魂本體的接線

- 標註分類法(機制書 §十 12 標籤 + 地點各自的語魂標籤)= 責任痕跡資料集的
  **human lane** 分類法(憲章 `docs/plans/accountability_trace_dataset_charter_2026-07-04.md`
  修正案 A:經同意的第一人稱貢獻,CC BY 4.0,四配套=key 客戶端/匿名/撤回碼/council 門神)。
- 七語氣責任節點 ≈ council 五視角 + 火花/共語(engine:rules 模式 live 零成本佈告欄體;
  BYO-key LLM 節點才有戲劇腔)。
- 設計鐵律:每條規則對應倉庫真實機制,或誠實標 `absent`——佈景可幻想,物理必須真。

## 下一步(2026-07-04 owner 三選全開工)

- (a) 最小可玩版 **v0 已落地**:`site/theater/`(單人、10 章+終章、12 事件、
  15 NPC/地點、真 rules-council 預算 verdict、同意閘+撤回碼+trace 下載)。
  工單+治理決策記錄:`docs/plans/theater_playable_v0_2026-07-04.md`;
  生成器:`tools/theater_page/precompute_council.py`(fail-closed 驗證+組裝+council 跑批)。
- (b) 天道外眼 **已完成**:codex 審過,仲裁 2 CONFIRMED(F2 target 欄漂移/F4 第二律
  枚舉歧義,**正典處置=owner 終審**)、2 REFUTED(進反證鏈)。
  全文:`docs/status/tiandao_codex_review_adjudication_2026-07-04.md`。
- (c) 資料集出海:`dataset/v0/PUBLISH.md`,驗證器綠,只等 owner `hf auth login`。
