# docs/visual/

> Visual references aligned with the ToneSoul thesis.
> 這裡放跟 ToneSoul 哲學同源的視覺實驗 / reference。不是 production asset、不參與 build pipeline。

## 結構

```
docs/visual/
├── README.md                       — 本檔
├── tonesoul_geometry_self_checked.html  — 主層：thesis-aligned active reference
├── _archive/                       — 歷史 artifact、不是 current direction
│   ├── README.md
│   └── landing_v8_2026-05-06.html
└── _pending_thesis_sync/           — unresolved 狀態、等 sync 後 promote/archive
    ├── README.md
    └── landing_v10_2026-05-06.html
```

**三個層次的 epistemic status 嚴格區分**：

| 路徑 | 對應狀態 | 對應 Axiom |
|---|---|---|
| 主層（`docs/visual/*.html`）| Active, thesis-aligned | 正向使用 |
| `_archive/` | Historical, thesis-misaligned, not evolving | Axiom 1 Continuity（保留 trace）|
| `_pending_thesis_sync/` | Unresolved provenance / status | Axiom 1 + Axiom 4（trace + tension）|

**規則**：cold agent 讀檔案時、**路徑前綴決定可不可以引用為 current direction** — 主層 OK、`_archive/` 必須標 historical、`_pending_thesis_sync/` 不能當 current 也不能當 rejected。

## 檔案（主層）

### `tonesoul_geometry_self_checked.html`

- **作者**：Fan-Wei 的朋友（v8/v10 landing page 同作者）
- **加入日期**：2026-05-10
- **概念對應**：thesis 的 *architectural verification* 精神 — 「self-check」這個 concept 跟 ToneSoul 同源（不是 trust-me-it-works、是 evidence-led、結構自我檢驗）
- **內容**：3 層 SVG geometry（outer/middle/inner）、scroll-driven unfold、breathe animation、console.table 跑 verts 數值 + diamond equation residual
- **原始位置**：朋友交付、原檔在 `tmp_friend_*` 系列旁邊（task-c）；本 commit 之前只在 `AppData\Local\Temp` — 為避免 Windows Temp 清空遺失而收進 repo

## 用途（候選、未決）

1. ToneSoul logo motion graphic 候選
2. 對外文件的視覺輔助（READme thesis 串接）
3. 未來 v9 landing page 的 hero background motion 候選
4. 5 perspectives council 視覺化的 starting point

詳細討論見：`tmp_friend_review_v8.md`（task-c repo）。
