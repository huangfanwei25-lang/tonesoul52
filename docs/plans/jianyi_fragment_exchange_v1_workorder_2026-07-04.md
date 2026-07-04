# 簡遺碎片交換 v1 — 工單(規格封存,未排程)

> Status: **SPEC-FILED, NOT SCHEDULED**(2026-07-04)。依判決書
> `docs/plans/weavai_crystallization_decision_2026-07-04.md` P2(REFINE,信心 0.65)開單;
> 動工=owner 排程決定。**分發側有明確觸發器:真實第二玩家出現——之前只建匯出/匯入,
> 不建配對。**
> 格式:`docs/engineering/work_order_template.md` 八欄。
> 血統:簡遺律=owner 自家正典(`data/YuHun_v2.6_knowledgebase.json:61` @ 9e6a93ab,
> 2026-01-10;世界書 :61 標「漂流分發=待建」)——本單是實現正典,不是抄 weavai。

## 1. Framing

「多人世界」的零伺服器版本:玩家 A 的抉擇碎成簡遺,以**檔案**漂到玩家 B 的城區;
B 必須裁決(埋葬/續寫/反駁),裁決成為 B 自己的軌痕。世界書簡遺律的第一次落地。
owner 在 weavai 親證了「別人的世界線滾動」的體驗價值(截圖 E3),本單把該價值搬回
同意閘+撤回碼主權之下。

## 2. Ground truth(已驗,2026-07-04)

- trace 下載管線已存在:`site/theater/app.js` downloadTrace()(格式
  `tonesoul-theater-trace-v0`,含 withdrawal_code、consent 欄)。
- 匯入面=零:目前頁面無任何檔案讀入口(攻擊面現況乾淨,是本單要新開的東西)。
- 判決書 P2 反方最強:零伺服器下防偽**無機制**(結構事實)——工單全文繼承此前提。

## 3. Scope(exact edit list;動工時再細化)

- `site/theater/app.js`:
  (a) exportFragment():從本局 trace 選一則抉擇 → 碎片檔
      `cos-jianyi-<code>.json`(**節選**:章節/地點/抉擇 label/理由 trace_quote/
      harm_targets 摘要;**不含**完整 parse、不含 blackbox、不含 resources);
  (b) importFragment():檔案選擇器 → schema 驗證 → 裁決事件卡(埋葬/續寫/反駁
      三選,各自落一筆**本人**軌痕)。
- `site/theater/index.html` + `style.css`:結局頁「遞出簡遺」按鈕;同意閘加簡遺段;
  匯入口放同意閘後的獨立入口(不混入章節流程)。
- 本檔(動工時更新 Status)。

## 4. 禁區(本單額外;預設禁區照常繼承)

- **不宣稱防偽**——UI 文案禁用「已驗證」「防偽」字樣;碎片一律顯示
  `provenance: unverified-import`(判決書要件 4)。
- 匯入內容**永不**併入本人 trace 主體、**永不**進 dataset human lane、**永不**改
  資源數值以外的世界狀態(隔離艙;裁決本身作為本人軌痕除外,且標明 source)。
- 匯入=esc() 全轉義 + schema 白名單 + 大小上限(≤32KB)+ 不執行任何動態內容。
- 不建伺服器、不建配對/分發(觸發器未到);不動 tonesoul/。
- 匯出同意文案必含:「**遞出後無法遠端撤回**;撤回碼僅對未來資料集提交有效」
  (Axiom 8 語義,判決書要件 2)——寫不出誠實版本=整案轉 BLOCK(翻案條件)。

## 5. 驗收條件(動工時必跑)

1. `node --check site/theater/app.js` 綠
2. 匯出碎片 → `python -m json.tool` 過,且欄位=白名單完全相等(多一欄即 fail)
3. 惡意碎片測試:含 `<script>`/超大檔/未知欄位/假 schema 四種樣本,匯入全部被擋
   或全轉義呈現(頁面無腳本執行、無樣式破壞)
4. 匯入裁決後:本人 trace 增加的紀錄帶 `source: "jianyi-import"` +
   `provenance: "unverified-import"`;下載檔可見
5. `python -m http.server` 起 site/,匯出/匯入全流程手動走通一輪

## 6. 回報格式

結論進對話;碎片 schema 定稿寫回本檔 §3;惡意樣本與測試結果留 `tmp/jianyi_test/`。

## 7. 升級條款

(a) Axiom 8 同意文案寫不出誠實版 → 停,整案回裁決(翻案條件觸發);
(b) 隔離艙做不到「裁決不污染世界狀態」→ 停,回報張力;
(c) 同一子任務敗 2 次升級,第 3 次停(vow-003)。

## 8. Lane

- 實作:主 agent 或 bounded ticket 派 codex(工單已可直接轉派);
- 驗收:主 agent 實跑 §5;安全面(惡意碎片測試)建議加 codex 異模型審;
- **排程與敢不敢開匯入口:owner 決定**(本單只封存規格)。

## §9 Coda

這張單最誠實的一句話:零伺服器的多人,信任鏈只有一環——「你親手把檔案遞給了誰」。
系統不假裝能替你驗真偽;它只保證你裁決的那一刻,有紀錄、有隔離、有名字。
