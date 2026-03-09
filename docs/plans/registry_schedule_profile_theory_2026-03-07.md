# Registry Schedule Profile Theory

Date: 2026-03-07
Scope: ToneSoul Phase 132+ theoretical framing for registry-driven autonomous scheduling

## 1. Problem Statement

ToneSoul 已經具備三件事：

1. `source_registry` 能判斷哪些外部來源值得信任。
2. `AutonomousDreamCycleRunner` 能把 URL 轉成 stimulus、寫入 `soul.db`、再交給治理與觀測層。
3. `AutonomousRegistrySchedule` 能在多次 host-triggered 執行之間保存 cursor，輪流抽樣 approved sources。

真正還沒被形式化的，是「應該用什麼節奏去碰撞世界」。

這不是單純的 cron 問題，而是認識論問題：

- 如果只吃同一類來源，系統會過擬合單一世界觀。
- 如果來源輪替過快，記憶還來不及沉澱就被新刺激覆寫。
- 如果來源輪替沒有風險節制，高摩擦來源會把自治 loop 變成噪音放大器。

因此我們需要一個 **Schedule Profile**。  
它不是新的治理器，而是自治節奏的外層憲法。

## 2. Core Thesis

Schedule Profile 的角色不是決定「什麼是真的」，而是決定「下一輪應該讓哪一種張力先被看見」。

所以它的本質是：

- **節奏治理**，不是內容治理
- **抽樣治理**，不是記憶治理
- **時間編排**，不是價值判決

ToneSoul 的治理判斷仍然屬於：

- `source_registry`: 來源是否准入
- `StimulusProcessor`: 刺激如何被評分
- `GovernanceKernel`: 摩擦、阻力、circuit breaker 如何判斷
- `DreamObservability`: 如何閱讀結果

Schedule Profile 只能做一件事：

> 在已批准的來源集合中，按某個可解釋的節奏去選擇「下一批要碰撞的世界切片」。

## 3. Boundary Model

為了避免 schedule layer 膨脹成第二個大腦，邊界必須固定：

### A. 它不能做的事

- 不能修改 allowlist / blocked host policy
- 不能直接改寫 `soul.db` 的語義
- 不能根據內容本身重新做 truth ranking
- 不能繞過 `GovernanceKernel`
- 不能把 schedule state 偷藏進 identity memory

### B. 它可以做的事

- 決定來源輪替順序
- 決定每輪抽幾個 entry / 幾個 URL
- 在高失敗率時降低某類來源的嘗試頻率
- 為不同類別指定 cadence / revisit interval / backoff
- 把這些選擇顯式寫成 artifact，供人類和 dashboard 檢查

## 4. Why Profile Exists

如果沒有 profile，registry-driven scheduling 只有「公平輪替」。

公平輪替雖然簡單，但對 ToneSoul 不夠，因為：

1. **來源類型不對稱**
   - `vulnerability-intel` 的更新頻率和 `research-archive` 不同
   - `open-datasets` 的認知價值和 `artifact-signing` 的 operational value 不同

2. **系統承受能力不對稱**
   - 某些來源在 crawling、parsing、governance friction 上都比較重
   - 若無節流，高成本來源會壓縮其他來源的可見性

3. **記憶沉澱需要間隔**
   - ToneSoul 不是 RSS reader
   - 它需要讓刺激進入 working layer、碰撞 durable rules、再透過 observability 看收斂

所以 profile 的存在，是為了在「新奇性、風險、沉澱時間」之間建立時間秩序。

## 5. Proposed Profile Axes

一個成熟的 Schedule Profile，至少應包含五個軸：

### A. Category Cadence

每個 category 的基礎喚醒頻率。

例：

- `vulnerability-intel`: 高頻
- `supply-chain-risk`: 中高頻
- `research-archive`: 中頻
- `open-datasets`: 低頻

### B. Entry Weight

在同 category 內，不同 source 的抽樣權重。

用途：

- 讓核心來源常回訪
- 保留少量 exploration，不讓系統卡死在固定 feed

### C. Revisit Interval

同一 entry 被再次抽中的最小間隔。

目的是避免：

- 對單一來源產生注意力霸權
- working-layer 還未消化時就重複灌入相同刺激

### D. Failure Backoff

對高失敗率來源增加退避時間。

這是 operational policy，不是 trust policy。  
它回答的是：

> 「這個來源暫時不穩，是否應該降低嘗試頻率？」

而不是：

> 「這個來源是否不再可信？」

### Operational Memory Note

`revisit interval` 與 `failure backoff` 都屬於 **operational memory**。

它們記錄的是：

- scheduler 最近做了什麼
- 某個來源暫時是否該冷卻

它們不是：

- ToneSoul 的價值觀
- ToneSoul 的長期自我敘事
- ToneSoul 的 durable memory

因此這些狀態必須留在 schedule artifact/state 裡，而不能滲進 `soul.db` 或 `self_journal.jsonl`。

### E. Tension Budget

每一輪允許注入的外部張力上限。

不是直接限制 `friction_score`，而是限制：

- 本輪抽樣量
- 高風險 category 的佔比
- 是否允許多個高摩擦來源連續進場

## 6. Cartesian Decomposition

如果用笛卡爾的方法論來拆這件事，可以分成四步：

1. **只接受可確知的邊界**
   - 哪些來源可碰，由 registry 決定
   - 哪些決策屬於 schedule，哪些不屬於，先切清楚

2. **把問題拆到最小**
   - source trust
   - cycle execution
   - schedule cadence
   - observability
   每一層各自單一職責

3. **從簡單到複雜建立秩序**
   - 先有 round-robin
   - 再加 state persistence
   - 再加 profile cadence / revisit / backoff
   - 最後才考慮 adaptive policy

4. **做完整枚舉與回看**
   - 每次 schedule 決策都要留下 artifact
   - 讓人類能回答：
     - 為什麼這一輪抽到這個 source？
     - 為什麼另一個 source 沒被抽到？
     - 是 trust policy、cadence policy，還是 runtime failure 造成的？

## 7. Implementation Consequence

因此下一步的實作不應該是把更多 if/else 塞進 scheduler。  
正確方向是新增一個顯式的 **Schedule Profile Contract**，例如：

- profile name
- category cadence
- entry weight
- revisit interval
- failure backoff policy
- urls per cycle budget

然後讓 `AutonomousRegistrySchedule` 去讀這個 contract，而不是自己發明策略。

## 8. Design Law

可以把這條理論收斂成一句設計律：

> Source registry 決定「可被看見的世界」；  
> schedule profile 決定「世界以什麼節奏被看見」；  
> governance kernel 決定「被看見後如何承受張力」。

這三者不能混層。  
一旦混層，ToneSoul 就會失去可驗證性。
