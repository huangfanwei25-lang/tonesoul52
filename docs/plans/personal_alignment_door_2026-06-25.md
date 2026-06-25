# 個人對齊 spec(「門」)— Phase 0 設計草案 / DRAFT

> 作者：Claude (Opus 4.8),依 Fan-Wei「開始打造?一步一步把整個門做出來?」的提問
> 日期：2026-06-25
> 狀態：**設計 spec / DRAFT — design only, build is GATED**(見 §6)。供 Fan-Wei × Codex 對接審。

---

## 【治理決策記錄】

- **決策**:不在現在 build「門」的 code;先寫這份 Phase 0 設計 spec,build 進入 **gated** 狀態。
- **為什麼**:門的概念連貫(使用者端缺一份**可攜帶、有序、可校正、使用者掌握**的價值/目標 spec)。
  但現在 build 撞:四個未 merge PR(#187–#190)、預算有限、倉庫已太大、即將與 Codex 對接、
  且「門先於房子」(核心 Auditor 尚未 merge/被真實使用)。
- **張力來源**:Fan-Wei「一步一步把整個門做出來」的動能 **vs** measure-don't-build / restraint /
  預算 / 佇列壅塞。這是真張力——擺出來,不靜默配合,也不否定。
- **可逆性**:寫 spec 全可逆(只是文件);不寫 code,所以不留難撤回的承諾。Gate 打開後再 build。

---

## §1 它是什麼(一句)

一份**使用者親手寫的、短的、有排序的、可被後續互動校正的、可攜帶的**對齊 spec——
**個人版語魂 Tag**。模型**參照**它(overlay),不是被它**抽換**價值(沿用既有 §語魂 Tag 邊界:
overlay + 稽核,不是 substrate swap)。

它**不是**一個 100 題心理測驗引擎;100 題只是**一種** elicitation 手段,**產物**才是重點。

---

## §2 Schema(Fan-Wei 自己已設計好的六欄 + 排序)

```yaml
# alignment.yaml  (個人版語魂 Tag — 短、有序、可攜帶)
goal:            # 這個目標/工作流要達成什麼
not_wanted:      # 明確不要什麼(紅線)
success:         # 成功條件(可檢查)
failure_risks:   # 失敗風險 / 要避免的錯位
monitor:         # 要監控的副作用
boundaries:      # 你/我/它(user / AI / 第三方)的責任邊界
value_order:     # 衝突時的價值排序(最重要的一條:給壓縮/取捨一個方向)
```

`value_order` 是承重欄——它回答 Fan-Wei 第 3 段的問題(資料太多時,壓縮要把**什麼**當重要)。
**沒有它,六欄只是一疊平的規則;有它,模型有了取捨方向。**

---

## §3 可校正的 prior 紀律(承重)

使用者的答案是**自我報告**,而自我報告會飄(stated ≠ revealed preference:嘴上要「會頂嘴的
誠實 AI」,真到那刻接不接受是另一回事)。所以:

- `alignment.yaml` 是**可校正的 prior,不是定論**。
- 後續真實互動發現的偏差,寫進一個**可見的 corrections log**(append-only),**不偷偷重 fit**。
- 這就是「別信自我報告、用結構 surface 證據」那條——**套到使用者自己身上**。

---

## §4 Non-goals(守住,否則它變成它要解決的問題)

- **不是** 100 題心理測驗引擎、不是偏好預測 ML 模型。
- **不是**安靜地 model 使用者(揣測可以多,但必須**可見、可反駁、不替使用者決定、不擴散**——
  軸是**透明度**,不是「開放多少」)。
- **不是**價值抽換(模型仍跑既有訓練價值,這只是它**參照**的明確 overlay)。
- 產物**短且有序**——不准長成另一個「太多→不知道什麼重要」的大 md。

---

## §5 MVP 最小切片(build 開始時,從這裡)

最小可出貨,**不是引擎**:

1. `alignment.schema`(六欄 + value_order 的 schema 定義 + 驗證器)。
2. 一份**結構化模板**(使用者填,或 AI 用幾個問題協助壓成有序原則——elicitation 是薄的)。
3. corrections log 的 append-only 格式 + 一個「顯示目前 effective spec + 它被改過幾次」的讀取面。
4. 釘測試:schema 驗證、value_order 必填、corrections log append-only 不可重寫。

**不做**(留待後續、且要各自過 gate):花俏 UI、100 題、偏好學習、自動套用到 runtime。

---

## §6 開始 build 的 GATE(此 spec 的重點)

code **不**現在開始。打開 gate 的條件(全中):

1. #187–#190 佇列清掉(merge 或收斂),管線不壅塞;
2. Fan-Wei × Codex 對接同意這份 spec 的 scope 與 non-goals;
3. 核心(Auditor)已 merge / 有真實使用——**房子在,才裝門**;
4. 確認這條不撞當前預算約束(budget 容許一條新 build)。

達成前,本文是**設計**,不是施工許可。

---

## §7 誠實邊界

- 這份 spec 自己也是 intent;真實能力以日後 code + 測試為準,衝突以 code 為準。
- 「門」降低「從零猜使用者」的成本,但**不**保證對齊(自我報告 + overlay 的雙重限制,見 §3 / §語魂 Tag)。
- 它讓對齊**可被使用者檢視與修正**——價值在那裡,不在「讓 AI 更懂你」的浪漫版。

---

*個人對齊「門」Phase 0 v0.1（design only, build gated）*
