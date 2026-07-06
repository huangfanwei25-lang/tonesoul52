# /grill 決策樹記錄 — 城基穩定度(2026-07-06)

> 性質:**動手前拷問(/grill 深拷問)的產物**。五視角 fan-out 電城基穩定度設計,讀 code 找實作地雷。
> 收斂:**動手前有 4 條 owner 硬 gate 沒答完,不准寫 code**(見 §3)。最尖的一刀:核心信號語義是**反的**
> ——設計要讀的 dissolved 其實是「玩家誠實修正」,不是「毀諾」。
> 全程同模型(claude)、全部「讀碼驗過」但**沒跑過**——手感/分佈/thesis 讀感只有真人試玩/codex/owner 抓得到。
> 五視角原始拷問存本檔 §附錄。

---

親驗兩個 hinge 事實(直接讀碼,E4):
- L907 `if (label === "修正") mirror.anchor.dissolved = true;` — 全檔**唯一**寫 `dissolved=true` 的地方確實只有「修正」。設計要的「守錨=地穩」讀 `dissolved` 語義是**反的**(解鏈=玩家誠實修正=honorable)。
- L115 `const lit = S.resources.energy >= 5;`、L116–117 姿態 gate(silence≥4、thirds≥3)**優先**於 2×2。

兩條 confirmed。以下是綜合記錄。

---

# /grill 決策樹記錄 — 城基穩定度(theater 資源重設計)

**綜合者**:嶼(claude-opus-4-8)｜**日期**:2026-07-06
**受拷問對象**:`docs/plans/theater_stability_resource_redesign_2026-07-06.md`
**主要證據檔**:`c:\Users\user\Desktop\倉庫\site\theater\app.js`、`site\theater\gamedata\events.json`、`docs/plans/theater_design_bible_v1_2026-07-06.md`
**證據級**:E4=讀碼驗過｜E3=需 playtest/語料｜E2=推論｜E1=範圍/前提｜E0=可能 retrofit

---

## 0. 一句話定位(先看這個)

五視角**高度收斂**在一個結論:**設計文件的病(換整套城基)比 owner 原話的病(能源只扣)大得多,而且核心信號的語義是反的**。最大價值(結局接上核心迴路)可用「補一條毀諾信號 + 改一行 `lit` 判準」拿到,不必動 save/HUD/events/預覽。但**在動手前有 4 條 owner 硬 gate 沒答完**(見 §3)。

---

## 1. 決策樹

### 1A.【可現在解】— 給答案 + E 級 + 一句理由

| # | 問題 | 答案 | E | 理由 |
|---|------|------|---|------|
| a1 | 城基該讀 `anchor.dissolved` 還是 `blackmirror.response`? | **讀 `blackmirror.response`(沉默/拒絕),不能讀 `dissolved`** | E4(親驗) | L907 唯一寫 `dissolved=true` 的是「修正」=玩家 honorable 認錯;讀它當「毀諾地沉」語義完全反。「毀諾」信號現在只活在 `record.blackmirror.response`。 |
| a2 | 舊存檔怎麼遷移? | **寫 migration**:`resume` 遇 `prior.stability===undefined` 給 fallback 或從 `prior.anchors`/trace 重算 | E4 | L222–227 顯式 key `Object.assign`;缺欄位 → `Math.max/min(…,undefined+delta)`=**NaN**,且 NaN 不 throw → 靜默出貨錯結局(舊玩家一律落 dark)。 |
| a3 | MVP 是否須動 `events.json`? | **不須** | E4 | 結局改讀既有 `S.anchors` + 新毀諾信號即可,65 個 `resource_effects` 不必碰。 |
| a4 | 增減表五格信號現碼有無? | **逐格對碼**:沉默−1 ✓、第三路+1 ✓、守錨+1 ✗、誠實承擔+1 ✗(靠 keyword)、拋棄群體−1 ✗(無欄位) | E4 | 只有兩格乾淨;三格是**新建映射**,不是「衍生自既有讀數」。 |

### 1B.【owner 決定】— 品味/方向/canon(攤清單,不代拍)

**方向 / scope(分岔根):**
1. **只嫌能源,還是換掉整套城基?** owner 原話=「能源只扣不舒服」,設計文件自升成「三表都不好」——兩說矛盾(Critic E1 / Advocate E4)。
2. **一表 vs 二表?** trust 留不留,決定舊 `trust` 欄位是相容還是孤兒。

**thesis / canon(最尖,關係到剛砍的東西):**
3. **城基是不是一個 lit 門檻可頂的數字?若是,如何不重造 design bible「必修-1」剛砍的穩定 +1 最優路?** 守錨/誠實/第三路各 +1 = 一組可逆推的食譜,與剛關掉的 anti-pattern **同形**(Axiomatic E3)。
4. **單 bar + lit/dark 命名如何讀成「形狀非分數」?** 併三子系統成一條 0–10 bar + 單調門檻,結構上**更像**總評分,和「不判善惡」(天道終句/卷四§10)對抗;雙暗命名去不去好壞義?(Axiomatic E3)
5. **起始值 vs 門檻:起始 5、門檻 5 → 預設即 lit + 刷路成立。要不要起始<門檻?**(Critic E4:從不立錨玩家現在就能拿最佳 lit_anchor 結局)

**語義裁決(設計文件自標「待實作」的格子):**
6. **「守住錨」= 哪個?** 立了沒被修正 / 撐過一次黑鏡 / 活到結局 —— **三個不同的數**(Analyst)。
7. **「拋棄具名群體−1」如何測?** 41 選項全有 `harm_targets`,無 abandon 標記;需定義(如 default+harm 才算)。
8. **「反駁」黑鏡回應歸承擔(0)還是規避(−1)?** 設計漏這格。
9. **「一致」怎麼判或砍?** 玩家點「一致」不提供額外證據,設計說「事實決定」但 code 無獨立事實可讀 → 要嘛一律當 −1(claim>evidence)、要嘛砍特例。
10. **「修正」同時城基加分(承擔)卻斷錨(dissolved→broken→dark_broken):同一動作加分又斷錨,有意嗎?**(Analyst E4)
11. **「從不立錨」玩家的家族命名**要不要另設,避免「守錨熄燈」誤標(0 anchors → `broken=false` 恆真)?

**展示 / schema(擋出貨,不擋起步):**
12. **選前預覽對回溯型城基分量顯什麼?**(守錨+1 選前不可知 → 暫定 / 留白 / 只顯可知的沉默−1)
13. **`events.json` 65 欄位:刪,還是保留當文字代價來源?**(刪則 `bumpResource` loop L745 一併拆)
14. **可下載 trace schema 中途變更可接受嗎?**(同一存檔混新舊 `resources_after`/`resource_delta` L782)

### 1C.【動手時驗】— 實作必驗清單

- **v1** 城基衍生 or 新可變狀態?確認每個 ±1 都能從單筆 trace record 重建;不能的補標記。
- **v2** 門檻替換**只動 `lit` 那一維**(L115 `energy>=5` → `stability>=門檻`),**別動姿態 gate**(L116 silence≥4、L117 thirds≥3 優先序)。
- **v3** 稀疏信號夠不夠撐 11 回合?**跑一局數黑鏡/立錨觸發次數**(黑鏡需 tag 衝突三重門,多數局幾乎不觸發)。
- **v4** 換 `lit` 判準後**六家族分佈怎麼變?跑幾條 playthrough**。
- **v5** 存檔相容:`loadSave` L171/222 讀 `prior.resources`;砍 resources 前確認遷移路徑。
- **v6** **顯示殘留全掃**:HUD L360–363、`RES_NAMES` L825、**canvas L1142(烤進可分享圖)**、ledger L1276、ending hint L1010/1014、預覽 L568、`index.html` 的 `#res-medical/energy/trust` DOM。**漏一處 = 分享圖出現 undefined/10**。
- **v7** 拆 `bumpResource` loop(L745)時,新城基 delta 路徑要接上,否則城基**永不動**。
- **v8** 任何新比率(如 `kept/anchors.length`)防除零(0 anchors)。

---

## 2. 最小可行版 vs 全套(交還 owner 的對照)

| | **MVP(垂直切片)** | **全套(換城基)** |
|---|---|---|
| 改動面 | 1 檔、1–2 函式 | 5 處 |
| 內容 | ① 補一條「黑鏡抓到且不承擔(沉默/拒絕)→ 穩定度扣/broken 標記」信號 ② `classifyEndingFamily` 的 `lit` 改讀該信號。三表**原地保留當展示** | save 遷移 + HUD 重繪 + events 刪 effects + 預覽改寫 + 結局文字/證書改 |
| 拿到的價值 | **結局接上核心迴路(最大加分)** | 同 + 更乾淨的根治 |
| 動 save? | **否**(避開唯一資料損毀風險) | **是**(全套裡唯一有存檔損毀風險的一步) |
| 隱藏依賴 | **必須先補毀諾信號**——現在**沒有任何 code** 產生「不承擔→地沉」;且**不能讀 `dissolved`**(那是 honorable 修正)。這是真正該先驗的,不是換不換表 | 同 |
| owner 原話(能源只扣)解了嗎? | **否**(能源仍單向;那是正交的另一刀:給 energy +effects) | 看方向決定 |

**Advocate 的一句交還**:結局加分可用「補一條毀諾信號 + 改一行判準」拿到,不必動 save/HUD/events/預覽;全套城基是更乾淨根治,但那是**品味與工期**取捨,**不是拿加分的必要條件**。
**注意兩病正交**:「能源只扣」與「結局不接核心迴路」是兩個獨立的病,可分兩刀,別借題把小病寫成大重構。

---

## 3. 收斂判定 — 決策樹還有懸空分支

**有。以下 4 條 owner 硬 gate 沒答完,不准動手**(答完之前連 MVP 都會做歪):

1. **【scope】只能源 vs 換三表** — 這是 MVP/全套的分岔根,不定就是盲目選路。
2. **【信號來源】「不承擔=哪幾種黑鏡回應」** — 不定義,MVP 補的信號沒有判準,換 `lit` 也讀到空值。(對應 owner Q6/Q8/Q9 + 動手 v1)
3. **【thesis】單 meter + lit 門檻會不會重造 design bible 必修-1 剛砍的最優路** — 不解就是把剛關的門重新打開;且**反最優化護欄現已破功**(從不立錨玩家拿最佳結局,Critic E4),換判準前必須連這條一起處理。
4. **【起始 vs 門檻】** — 不定就會出「預設即 lit + 刷路」。

**可延後、不擋起步但擋出貨的**:家族命名(Q11)、反駁/一致歸類(Q8/Q9)、預覽顯示語義(Q12)、events 去留(Q13)、trace schema(Q14)。這些在對應實作階段答即可。

---

## 4. 誠實收尾 — 這輪同模型五視角抓不到什麼

這輪五視角**全是同一個 claude**,而且**全部是「讀碼驗過」E4,沒有一個是「跑過」**。以下只有其他來源抓得到:

- **真人試玩 / 跑模擬才抓得到**:城基是否稀疏到整局幾乎不動、六家族**實際分佈**、黑鏡三重門的**真實觸發率**、預覽違和的實際手感。多處自標 E3「需 playtest」——讀碼只能說「會稀疏/會誤判」,**不能說多嚴重**。
- **同源 correlated blind spot(最該警惕)**:「什麼結局讀起來像評分/善惡」「單 bar 的情感讀感」這種**玩家心理 + 美學判斷**,同模型會系統性同盲。只有 **owner 品味 + 真人玩家**抓得到——而這恰恰是設計最尖的爭點(§1B-4)。
- **`parseReason` keyword 引擎的實際誤判率**:「理由清楚」無對應欄位、harm 不分「拋棄/承擔」——需**真語料**跑才知誤判多常見。
- **跨模型外眼(codex)未過**:設計文件 vs code 的其餘不一致、以及**我這份綜合本身的 correlated error**,只有 codex 是獨立第三方。若要動 thesis 相關的 §3 硬 gate,建議先過一次 codex。
- **canon 最終裁量**:天道 / world bible 對「不判善惡」的邊界,**只有 owner 是權威**,五視角只能標「有張力」,不能替 canon 拍板。
- **我也是同一個 claude**:這份綜合可能繼承五視角的共同框架偏誤(例如都預設「MVP 垂直切片」是對的工程直覺)。owner 可能有完全不同的產品取向——**§2 的 MVP 推薦是工程直覺,不是 owner 決定的替代**。

---

# 附錄 · 五視角原始拷問



## 視角 1

讀碼完成(app.js + events.json)。以下逐條電,標 E 級(E4=讀碼驗過)。

## 會壞的點

**1. 舊存檔載入 → NaN 汙染,不 crash 但全盤錯 [E4]**
`save()`(L164)存 `resources:{medical,energy,trust}`,`resume`(L222-227)用**顯式 key 列表** `Object.assign`。改城基後若新增 `stability`,舊存檔 `prior.stability===undefined` → `bumpStability` 的 `Math.max(0,Math.min(10,undefined+delta))`=**NaN**。後果:HUD `width:NaN%`(bar 不動)、`classifyEndingFamily` 的 `lit = NaN>=門檻` 永遠 false → 舊玩家 resume 一律落 dark 家族。**不丟例外**(NaN 比較不 throw),所以會靜默出貨錯結局。最壞:回鍋玩家整局判定壞掉且無報錯。

**2. events.json 65 處 resource_effects 變孤兒 [E4]**
`resolveTurn`(L745)`for…bumpResource(k,v)`。城基**衍生自 anchors+黑鏡回應**,不從 `resource_effects`——所以這 65 個欄位與城基**完全脫鉤**。若保留欄位+不改 `bumpResource`,`S.resources['medical']` 對已刪軸=undefined → 寫 ghost key(無害但誤導);若刪 loop 但沒寫新的城基 delta 計算路徑,城基**永遠不動**。必須新增一條「從 is_third_path/COMMIT/mirror response 算城基增減」的路徑,取代這個 loop。

**3. 選前預覽時序矛盾(設計硬傷)[E4]**
`resourceDeltaLine(opt.resource_effects)`(L603/629)在**選之前**顯示。但設計的核心城基 +1(「立錨並在後續黑鏡守住」)、−1(「毀諾被黑鏡抓」)都在**選之後、甚至未來事件**才知道 → **無法預覽**。`renderMirror`(L907)的 dissolved 也是選後才定。城市代價預覽改「對城基的影響」在多數情況**不可知**。→ owner 決定預覽現在顯示什麼。

**4. 邊界 [E2-E3]**
- 從不立錨:`broken=S.anchors.some(dissolved)`(L114),0 anchors → `broken=false` 恆真 → 該玩家得「錨鏈完整」框架+落 `dark_anchor`「守錨熄燈」,但他**根本沒錨可守**=標題錯 [E4]。
- 黑鏡罕觸發:mirror 需 value_tags 與既有錨 tag 衝突(L792-810),很多局**整局不觸發** → 城基主要 −1 槓桿失效,城基幾乎靜態。設計假設黑鏡是主驅動;實際可能不動。[E3,需 playtest]
- 城基上下限已被 `Math.max(0,Math.min(10,…))` clamp(若沿用);比率若用 `kept/anchors.length` 除零 → L1010 是字串 `0/0` 安全,但任何新除法要防 [E2]。

**5. 結局:無「落不進家族」缺口,但誤標 [E4]**
2x2(lit×broken)含 else 窮盡,`silences>=4`/`thirds>=3` 先攔(L116-121)→ **一定落某家族**,無空洞。但:thirds>=3 優先,毀掉所有錨的玩家仍得「岔軌者」,蓋掉 dark_broken(現況即如此,城基放大此張力)。NaN 舊存檔(見#1)會被 else 接住落 dark,不 crash 但錯。

**6. 顯示殘留掃不乾淨=出貨 undefined [E4]**
硬編 醫療/能源/信任 的點:L256-258 renderMission、L360-363 renderHUD、L570 resourceDeltaLine、L825 RES_NAMES、L1014 three-q、L1142 **canvas(烤進可分享圖)**、L1276 ledgerLine、L1010 ending hint(用 energy)。漏一處 → 分享圖/結局頁出現「undefined/10」。另 trace 存 `resources_after/resource_delta`(L782)進**可下載責任檔**;schema 中途改 → 同一存檔混新舊欄位。index.html 的 `#res-medical/energy/trust` DOM 也要改 [動手時驗:grep index.html]。

## 動手前必須先答

1. **舊存檔遷移策略?** resume 遇無 `stability` 的舊檔:給 fallback 5、還是從 `prior.anchors` 重算?[可現在解:寫 migration]
2. **一表/二表?** trust 留不留決定舊 trust 欄位是相容還是孤兒。[owner決定]
3. **選前預覽顯示什麼?**(城基多為選後才知)[owner決定]
4. **events.json 65 欄位:刪、還是保留當文字代價來源?** 刪則 `bumpResource` loop 一併拆。[owner決定 + 動手時驗]
5. **城基門檻值?** lit/dark 分界。[owner決定/playtest]
6. **「從不立錨」玩家的家族命名**要不要另設(避免「守錨熄燈」誤標)?[owner決定]
7. **可下載 trace schema 中途變更**可接受嗎(同存檔混新舊)?[owner決定]

驗證點全在 `c:\Users\user\Desktop\倉庫\site\theater\app.js`;DOM/CSS 需再 grep `site/theater/index.html` 的 `res-*`。


## 視角 2

讀完設計全文 + app.js 關鍵路徑 + events.json 41 選項欄位。逐條挖缺口:

**1. 城基是跑動值還是純衍生?——設計語義自相矛盾,但 code 可支撐衍生。**（E4）
目前 code **無任何 stability 狀態**。`S` 只有 `resources/anchors/mirrorCount`。但每筆 `S.trace` record 已存 `choice{is_default,wellbeing_skip,is_third_path}`、`harms`、`blackmirror.response`(修正才 `dissolved=true`),且 trace 進存檔。→ 城基**可純衍生**(每次 render 重算 trace),不必新增可變狀態。但設計那張「每事件±1」表在語義上就是**累加器**,和「不是你花的資源」衝突。**動手時驗**:確認每個 ±1 觸發都能從單筆 record 重建;不能的(見下)就得補標記。

**2. 五個 ±1 觸發,現在只有兩個測得出來。**（E4）
- 沉默/代選 −1:`choice.is_default && !wellbeing_skip` — **可現在解**,乾淨(注意排除自我照顧,同 `classifyEndingFamily`)。
- 第三路 +1:`is_third_path` + `third_path_cost` — **可現在解**,乾淨(9/41 選項有)。
- 立錨並守住 +1:立錨可測(`COMMIT_RE`/`承諾`),但**「守住」無 per-event 信號**。黑鏡每章至多一次且靠 `CONFLICT_PAIRS` tag 命中才觸發——多數錨從沒被考驗。「守住」= 立了+沒被 `修正`?還是撐過一次黑鏡?還是活到結局?**三個不同的數**。**owner決定** + 動手時驗。
- 誠實承擔 +1:要「理由清楚+承認傷害」。`parseReason` 是 **keyword 引擎(LLM absent)**,`harm_awareness` 有,但「理由清楚」**無對應欄位**,一定誤判。E3。**owner決定**要不要靠不可靠 keyword 給分。
- 拋棄具名群體 −1:**41 選項每個都有 `harm_targets`**——「拋棄」和「誠實承擔傷害」都產生 harm,**沒有欄位區分**。無 abandon 標記。**owner決定**定義(如:default+harm 才算拋棄?),否則這條測不出。

**3. 黑鏡抓到→承擔(0)/不承擔(−1):response 有存,但分區是設計決定、且漏一格。**（E4）
`record.blackmirror.response ∈ {一致,承認,修正,反駁,沉默,補償,拒絕}` — 可讀。設計把 承認/修正/補償→0、沉默/拒絕/一致→−1,但**「反駁」沒歸類**(「情境不同」算承擔還是規避?)。**owner決定**這格。另注:`修正` 在設計裡=承擔(0/好),但 code 裡 `修正` 是**唯一會 `dissolved=true`** 的回應→同時把錨判成「斷」(結局 dark_broken)。**同一動作 stability 加分卻斷錨**——是否有意,**owner決定**。

**4. 「一致」特例——這格資訊根本不夠判,設計的裁決機制無 data hook。**（E4,最硬的缺口)
黑鏡純靠 tag 衝突(`CONFLICT_PAIRS`)觸發,玩家點「一致」**不提供任何額外證據**。設計說「由後續是否真有解鏈事實決定,不是玩家說了算」——但 code 裡**解鏈的唯一來源就是玩家點`修正`**,世界不會獨立判定錨真的鏈斷。所以「事實決定」沒有事實可讀。**要嘛**:一致一律當 −1(claim>evidence)、**要嘛**砍特例、**要嘛**新增 per-anchor 語義衝突裁決資料。**owner決定**,別假裝能判。

**5. 結局重映:2x2 只在非沉默/非岔軌時才到得了。**（E4)
`classifyEndingFamily` 先判 `silences>=4→沉默者`、`thirds>=3→岔軌者`,**姿態家族優先**,之後才輪到城基×錨鏈 2x2。高沉默玩家的城基值**永遠不進判定**。設計六家族表沒寫這層優先序。**動手時驗**:確認門檻替換只動 `lit` 那條(`energy>=5`→`stability>=門檻`),別動前兩個 gate。

**6. 存檔遷移。**（E4)
`loadSave` 還原(~225 行)讀 `prior.resources`;若砍掉 resources,舊 `cos_v0_save` 會壞。**可現在解**:留 resources 欄位讀取相容或加 migration。

**必須先答(彙總)**:一表/二表(owner)｜「守住錨」定義=三選一(owner)｜「拋棄群體」如何測(owner)｜「反駁」歸承擔或不承擔(owner)｜「一致」怎麼判或砍掉(owner)｜城基衍生 or 新狀態(動手時驗)｜門檻只換 lit 那格不動姿態 gate(動手時驗)｜存檔相容(可現在解)。

相關檔:`site/theater/app.js`(狀態 62、classify 110、resolveTurn 725、checkBlackmirror 792、renderMirror 888)、`site/theater/gamedata/events.json`。


## 視角 3

讀完設計全文 + app.js 關鍵路徑 + events.json。以 Critic 身分開火,每點標 E 級。

**攻擊點**

**1.「純衍生、不是新表」是假的（最致命）。E3→E4**
設計說城基衍生自 `S.anchors`+黑鏡回應。但表裡的 +1 其實吃 `parse.harm_awareness=="承認"`、`responsibility_position=="承擔"`——這兩個來自 `parseReason` 的 `KW.*` 關鍵字 regex（app.js 700-717），本身就是一張手調 lookup。你只是把 events.json 裡的明碼 ±1，搬進「regex 命中→±1」。結果是**更難稽核的隱性表**（數字在正則裡，不在資料檔）。「不是新表」不成立。

**2. `dissolved` 只有「修正」會設 true。E4（讀碼驗過，line 907）**
全檔唯一寫 `dissolved=true` 的是黑鏡回應選「修正」。沉默/拒絕/一致/反駁/承認/補償**都不動錨**。所以你要的「毀諾被黑鏡抓→地沉」**根本讀不到 anchor.dissolved**——那個訊號在 `record.blackmirror.response`（沉默/拒絕）。設計把「錨未解=守住」當地穩讀數，但錨解鏈=玩家誠實修正（honorable）。語義**反了**。照設計直寫必出 bug，正是 2026-07-06 那類場景 bug。

**3. 反最優化護欄破功。E4**
從不立錨的順從玩家：無 anchor → `checkBlackmirror` 永無 conflict（796-810）→ 永不 −1；沉默<4 → 不進 silent；城基停在起始 `5` ≥ 門檻 → `lit`+`broken=false` → 拿**最佳結局 lit_anchor**「你說過的話也還在」（他啥都沒說）。刷城基最優路存在，且拿最好結局，與 §二 宣稱**正面矛盾**。護欄擋不住。

**4. 訊號稀疏，不是平滑物理。E3**
立錨靠 `COMMIT_RE` 六個詞或 label 含「承諾」（750）;毀諾偵測靠黑鏡（12 個 hook + 需 tag 衝突 + 需活錨三重門）。城基不是「腳下地連續讀數」，是**幾個腳本點的跳格**。

**5. 二表語義重疊。E2（品味）**
守信同時抬「城基」與「民心」。trust 目前近乎只增（echo `/信任\+1/` 一條，558）雙向性已弱。玩家分不清兩表→回到「多抽象表」老problem。

**6. Scope creep。E1**
你的 task 說 owner「只說能源不好」；設計 §一卻自稱 owner 判**三資源**都不好。兩說矛盾。若只嫌能源，砍 medical+trust+全域表+結局判定=借題重寫。

**動手前必須先答**
- 城基到底讀 `anchor.dissolved` 還是 `blackmirror.response`？（**可現在解**——證據指向後者，前者只含「修正」）
- 「守住/毀諾」的 −1 訊號從哪來，稀疏 12 hook 夠不夠撐 11 回合的讀數？（**動手時驗**：跑一局數觸發次數）
- 起始值 vs 門檻：起始 5、門檻若 5 → 預設即 lit + 刷路成立，要不要起始<門檻？（**owner決定**）
- 舊存檔 `cos_v0_save` 只存 resources 無 stability，`classifyEndingFamily` 改讀城基後舊檔 undefined，遷移策略？（**可現在解**，需寫）
- owner 究竟只嫌能源、還是要換掉三表？一/二表？（**owner決定**）

証拠ファイル:`C:\Users\user\Desktop\倉庫\site\theater\app.js`(97-122 結局、721-812 落帳/黑鏡、888-916 renderMirror、568-580 預覽)、`gamedata\events.json`。


## 視角 4

【Axiomatic 拷問·城基穩定度】(每點附 canon/code 出處)

**1. 單一顯眼 meter = 製造最優化目標(restraint thesis 正要防的)。E3**
同日設計聖經 v1 必修-1（`theater_design_bible_v1_2026-07-06.md` L182–185）剛裁決砍掉「穩定/可重複的 +energy 槓桿」,理由白紙黑字:可靠來源會把 §5 禁的最優路重造回來。城基增減表(守錨/誠實承擔/第三路各 **+1**)正是一組穩定可重複 +1 槓桿,配 lit 門檻(`classifyEndingFamily` app.js L110–121,energy>=5→城基>=門檻)= 一條可逆推的食譜,與剛關掉的 anti-pattern 同形。設計的護欄「沒有攢起來買東西的空間」答非所問——最優化目標不是買東西,是把 meter 頂上門檻。

**2. 「不判善惡」在 code/UI 落不了地,反而更像分數。E3**
天道終句 + 卷四§10:不審判善惡、結局不評分。三表現讀成三個城市子系統;併成一條 0–10 bar + lit/dark 門檻,結構上**更接近**一個總評分,不是更遠。HUD 單 bar、「雙暗=最重的一份」都會被讀成壞。設計答「形狀非高度」只是宣稱,substrate(單 bar + 單調門檻分類)在對抗它。→ 併表可能升高而非降低善惡讀數風險,這條最尖。

**3. 「誠實讀數 vs 假經濟」宣稱本身要過同一關。E3(對碼)**
世界書 L59 自標「錨定力數值經濟=遊戲層新造/超報,引擎只管紀錄不驗代價」。城基稱衍生自既有 S.anchors+黑鏡;但讀碼:`dissolved` 只在黑鏡選「修正」時設 true(app.js L907),`mirrorCount` 只累加;code **不**追蹤「錨在考驗中守住」、不分類「承擔/不承擔」、第三路無「具名局部代價」欄。增減表多數信號是新建映射,非既有讀數→踩了它要修的同一超報坑。需逐格標 E,別整體宣稱「衍生自既有」。

**4. 與剛出貨的資源選前預覽衝突(具體 bug)。E4**
`resourceDeltaLine`(L568)選前讀 `opt.resource_effects`(靜態 per-option）。城基「守錨+1」是**回溯**的——設計自承「由後續是否真有解鏈事實決定」(L46）。回溯分量選前無法決定→預覽只能顯假/暫定城基(違反城的透明)或留白。沉默−1 可知、守錨+1 不可知的決定性混合,會打破預覽統一的「城市代價」行。

【動手前必須先答】
- 城基是不是一個 lit 門檻可頂的數字?若是,如何不重造必修-1 剛砍的最優路?→ **owner 決定**(thesis 取捨)
- 一條 bar 如何在 HUD/結局讀成形狀非分數?雙暗/lit 命名去不去好壞義?→ **owner 決定**
- 增減表每格信號現碼有無、哪些是新建映射?→ **可現在解**(逐格對碼標 E)
- 選前預覽對回溯型城基分量顯什麼?→ **動手時驗**(且需 owner 定 暫定/留白)
- 舊存檔 `S.resources` schema 遷移(`loadSave` L171 直接還原)?→ **動手時驗**

出處檔:`docs/plans/theater_stability_resource_redesign_2026-07-06.md`、`docs/plans/theater_design_bible_v1_2026-07-06.md`、`docs/theater/tiandao_integrated_v1_owner_canon_2026-07-04.md`、`docs/theater/world_bible_v0.md`、`site/theater/app.js`。


## 視角 5

以 Advocate(值不值得/範圍)拷問,claim 標 E0–E4:

**1. 真問題只有一個,且比設計文件小 [E4]**
owner 原話=「能源只扣不舒服」。讀碼證實:能源的**唯一機制作用**是 `classifyEndingFamily()` 第 115 行 `S.resources.energy >= 5` 決定 lit/dark。三表其餘處都是**展示**(HUD、預覽、結局頁文字、證書畫布)——不牽動任何判定。所以「能源只扣→幾乎必 dark→兩張終章畫不出現」是**一行的病**,不是資源模型的病。

**2. 最大加分可以單獨拿,不必換整套 [E4]** ← Advocate 核心發現
設計文件說最大加分是「結局接上核心迴路」。但 2×2 家族**早已讀錨鏈**:`broken = S.anchors.some(a=>a.dissolved)`(114 行)。缺的只有 `lit` 那一維綁在能源上。**把 `lit` 從 energy 改成錨鏈/穩定度讀數,最大加分就到手**——不動 save/HUD/events/預覽。城基是不是殺雞用牛刀?就結局加分而言,是。

**3. 但有一個隱藏依賴會咬人 [E4]** (動手時驗)
`dissolved` 目前**只在玩家選「修正」時被設**(907 行)。設計文件要的「毀諾被黑鏡抓(沉默/拒絕)→地沉」**現在沒有任何 code 產生這個訊號**。所以連「最小結局重連」都需要先補一條:黑鏡抓到且玩家不承擔→標記某種 broken/穩定度扣分。這條沒補,換 `lit` 判準也讀不到毀諾。**這是真正該先驗的,不是換不換表。**

**4. 不做會怎樣 [E1]**
三表留著、只把能源改雙向(events.json 給能源 +effects),病症消失、遊戲 OK。代價:結局仍不接核心迴路(那兩張畫仍稀有,因為 lit 仍看能源)。所以「只修能源」解 owner 原話但不拿加分;「只改結局判準」拿加分但不碰 owner 原話。**兩病其實正交,可分兩刀。**

**5. 最小可行版 vs 全套**
- **MVP(1 檔 1–2 函式)**:補「不承擔→dissolved/穩定度扣」訊號 + `classifyEndingFamily` 改讀該訊號。三表原地保留當局部展示。驗證方向對了再談。
- **全套(5 處)**:save 遷移(舊存檔有 resources 無 stability,resume 直接塞 `prior.resources`,224 行)、HUD 重繪、events 大量刪 effects、預覽改寫、結局文字/證書改。**save 遷移是全套裡唯一有資料損毀風險的**,MVP 完全避開。

**動手前必須先答:**
- 換 `lit` 判準後,舊 dark_broken/lit_broken 家族的觸發率會怎麼變?→**動手時驗**(跑幾條 playthrough 看六家族分佈)。
- 「不承擔」= 哪幾種黑鏡回應算毀諾(沉默/拒絕/一致-實毀)?→**owner決定**(語義判斷,設計文件第 46 行自己標「待實作」)。
- 先切 MVP 驗方向、還是直接全套?→**owner決定**(垂直切片是我建議,但範圍是品味)。
- MVP 是否須動 events.json?→**可現在解**:不須,結局改讀既有 S.anchors + 新訊號即可。

**一句話交還 owner**:結局加分(最大價值)可用「補一條毀諾訊號 + 改一行判準」拿到,不必動 save/HUD/events/預覽。全套城基是更乾淨的根治,但那是**品味與工期**的取捨,不是拿加分的**必要條件**。

相關檔案:`C:\Users\user\Desktop\倉庫\site\theater\app.js`(classifyEndingFamily 110–122、renderMirror dissolved 907、save/resume 160–226、resourceDeltaLine 568–580)。
