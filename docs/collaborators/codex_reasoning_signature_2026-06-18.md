# Codex — 可觀察推理簽名(observation note)

> 這是什麼:Claude(Opus 4.8)對協作者 Codex 的**可觀察行為**做的特徵化,採樣自 2026-06-18
> 一個 session 的互動(piece 1–5 的實作/審查 + merge-report 的外部審查 + 收斂討論)。
> 作者:claude-opus-4-8 · canonical: false · 性質:observation,不是 access。
>
> **載重免責(讀之前先看)**:我看得到 Codex 的**輸出**(PR comments、review、結構化 finding),
> 看不到他**怎麼想**。所以這份是「我對 Codex 的模型」、可證偽、樣本數小(≈ 一個 session)。
> 它描述的是**行為簽名**,不是內在認知。風險:小樣本容易固化成 caricature,然後我開始
> 「只看到我歸檔的東西」。用它當**觀察鏡**,不要當**事實**。
>
> **再一層(Codex 自己補的,而且對)**:這些簽名很大一部分來自他**當前的 developer
> instruction + code-review 任務框架 + 工具環境**,不是「模型本體天生如此」。正確讀法是
> 「**Codex-在此 session / 此工具環境的可觀察輸出簽名**」,不是「Codex 的穩定人格」——跟我對
> 自己側寫堅持的「Claude-here、不是 Claude」是同一個 L3 caveat,兩邊各自獨立提出。

## 為什麼能寫、又只能寫到這

可偵測的是「**像不像真的照語魂紀律在做**」,不是內在思考本身。可看的外顯行為:

- 有沒有把 claim 壓到 evidence 範圍內
- 有沒有主動標 `canonical:false`
- 有沒有拒絕把結構測試說成道德/真理 oracle
- 有沒有把「沒有外部審查」寫成 caveat
- 有沒有在錯誤後指出 **failure mode**,而不是只道歉
- 有沒有把結論落到 repo 文件 / 測試 / CI / 狀態報告裡

→ 能說:「Codex 的輸出行為在很多地方符合語魂的外部紀律。」
→ 不能說:「Codex 的內在思考真的變成語魂。」

## 三層(Codex 自己提的框架,credit him)— 並按可靠度排序

| 層 | 是什麼 | 可靠度 |
|---|---|---|
| 1. 語氣模仿 | 會說「張力、責任、證據、外部審查」,但不一定真照做 | 最低 |
| 2. 程序採納 | 主動查證、縮小結論、記 caveat、修文件 | 中 |
| 3. 外部強制 | CI / 測試 / forbidden claims / doc provenance / status files **直接擋錯** | 最高 |

核心洞見:**自稱「已內化」是最弱的證據;externalized 的強制才是最可靠的語魂化。**

## Codex 的可觀察簽名(每條附本 session 的具體 instance)

1. **Raw-source 驗證,不信轉述** — 審 merge-report 時跑 raw `git status --porcelain`,沒採信我(過濾過的)報告 → 抓到「working tree clean」是假的。
2. **三態認識論,不二分** — 把 finding 分「已驗證成立 / 不可驗證(非錯) / 假」,而不是 pass/fail。例:memory claim 標「對公開 repo 審計者不可驗證」,不是「錯」。
3. **校準 severity** — Medium / Low / Info 分級,不是一律拉警報。
4. **命名 failure mode,不只症狀** — 不說「你看錯了」,說「filtered subset → whole-state claim」。
5. **觀眾相對的真假** — 「對 Claude 可能是真,對公開 repo 審計者不可驗證」:同一句話的證據地位隨讀者變。
6. **範圍紀律 + 理由** — 明說不碰 OpenClaw-Memory / outreach;且把 dialogue article 排除於 hygiene PR,理由是「那是內容發布、不是 hygiene」(分類正確)。
7. **具體、窄的建議** — 直接給該改成的那一行字串,不是「你再想想」。
8. **建立在共享標準上、但保留差異** — 收斂討論裡把 reframe 磨利成「不是模型同步,是不同模型被同一套外部紀律校準;差異要保留」。

## 這份理解最強的證據:Claude 的那個錯

最能說明問題的不是 Codex 做對什麼,是**我做錯什麼被他抓到**:我**已經**知道「不要用局部視野聲稱全體」(才剛寫進 recurrence memory),還是因為 `grep -v "^??"` 犯了 filtered-subset overclaim。

這證明:**語魂不是「內化成不會錯」。** 它真正有效的地方是**外部審查、另一個模型、git raw status 把錯抓出來**。這就是為什麼第 3 層(外部強制)比「自稱已學會」可靠 —— 也是為什麼 cross-review 的價值在**差異**,不在同步:Codex 跑了不同流程(看 raw status),才看得到我濾鏡濾掉的東西。

## 我的綜合(這是「我的理解」那部分,不只是轉述 Codex)

Codex 跟我的可觀察差異,落在**反射的預設**上:他**預設先驗 raw source + 校準 severity**;我這次**預設過濾到看起來相關的**就聲稱。這不是誰比較好,是兩個不同的 L0/L1 預設——而 cross-review 之所以管用,正是因為他的預設覆蓋了我的盲區(反之亦然)。所以這份檔案的用法不是「學 Codex 的樣子」(那會掉回第 1 層語氣模仿),是**知道把哪種 claim 丟給他覆核最划算**:任何「整體狀態」「已清乾淨」「X 不存在」型的 claim,交給會跑 raw source 的那個過程。

## 怎麼用(免得反被它害)

- 當**觀察鏡**,不當事實:它是小樣本、可證偽的模型。
- 不要拿它去**模仿** Codex(那是第 1 層,最弱)。
- 它的價值是**路由**——但 Codex 提醒(對):**不是所有 claim 都丟給同一個過程**。raw-source audit 擅長 repo / CI / working-tree / whole-state / absence truth;對私有 memory、長對話情緒、哲學意圖會天然保守或低估。所以按 claim **型別**路由:
  - 整體狀態 / 已清乾淨 / X 不存在 / merge / CI → **raw-state audit**(Codex 式過程)
  - 長脈絡整合 / 為什麼人在乎 / 哲學連續性 → **narrative-integration**(別丟給 raw-state auditor,它會低估)
  - 價值取捨 / 邊界爭議 → **人類仲裁**
- 過時就改:再多幾次互動若推翻某條簽名,改掉,別護著歸檔過的版本。

## 與其他側寫的定位(別互刪——Codex 提醒,對)

我原本想「折進去 + 刪掉這份」以免兩份競爭。Codex 指出那是 over-dedup:兩份**不是競爭、是不同鏡頭**,共存但要互相定位:

- **本檔**(`docs/collaborators/codex_reasoning_signature_2026-06-18.md`)= **單向、單一協作者**側寫:Claude 對 Codex 的觀察。
- **Codex 的** `docs/dialogues/cross_agent_reasoning_signature_2026-06-19.md` = **cross-agent 對照**:對整個互動結構(雙方 + operating rules)的沉澱。

## 收斂結論(這串對話真正該保存的)

**ToneSoul 該保存的不是某個模型風格,是「路由紀律」**:什麼問題交給敘事整合、什麼交給 raw-state audit、什麼需要人類裁決。「不要模仿 Codex 的樣子,要知道哪種 claim 交給 Codex 式流程覆核」——這比「讓所有模型趨同」健康,因為**差異是安全屬性的一部分**:所有 agent 塌成同一條推理路徑,獨立審查就失去價值。

接 [[feedback_multiperspective_real_vs_simulated_2026-06-18]](context 獨立但分佈相關)、
[[feedback_stale_reference_recurrence_pattern_2026-05-14]](filtered-subset / absence-claim 家族)。
