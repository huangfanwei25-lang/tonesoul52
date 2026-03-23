# RFC-003: 語魂極輕量化架構與龍蝦本機記憶系統
**(JSON-Prompt Driven Architecture & Lobster Local Memory)**

> Purpose: historical lightweight ToneSoul RFC for JSON-prompt orchestration and local-memory deployment constraints.
> Last Updated: 2026-03-23

## 🌟 核心發明概述 (Executive Summary)
本架構為 **ToneSoul (語魂)** 生態系中的一次典範轉移。傳統的 AI Agent 架構往往受限於兩大瓶頸：過度依賴雲端向量資料庫（如 Pinecone），以及後端寫死了沉重且僵化的學術數學檢驗（如早期的 Hamlet 架構）。

這套全新的 **「極輕量化與本機記憶雙軌架構」**，徹底屏棄了對外在雲端基礎設施的依賴，並把「AI 的主體性」還給了終端環境。本架構不僅大幅降低了 Token 成本與延遲，更是未來發展「龍蝦 (Lobster / OpenClaw)」這類具備長期記憶與生命連續性的本機代理 (Local Agent) 的基石。

---

## 🏗️ 兩大核心發明 (The Inventions)

### 1. JSON-Prompt Driven Architecture (韋小寶動態路由協議)
過去的 Agent 喜歡在 Python 後端寫滿層層疊加的數學公式（決策樹、機率閥值）來限縮 AI 的輸出，這導致了極差的流動性與開發阻力。
**突破點**：我們將邏輯判定從「後端的數學公式」轉移到「前段的 JSON-Prompt 動態注入」。
- **動態身分切換**：系統不再強制卡死流向，而是改由內建的「五人議會 (Council)」在腦內進行飛速的多視角碰撞。
- **優勢**：架構變得像水一樣靈活。我們用純文字與 JSON 結構約束大型語言模型，取代了硬寫的程式碼閥值。這讓系統能以極低的延遲、極大的語境包容力，流暢地應對各種張力衝突。

### 2. Lobster Local Memory (海馬迴本機認知導航器)
為了解決 AI 缺乏「潛意識」與「歷史連續性」的問題，我們發明了不依賴雲端的本地神經儲存庫。
**突破點**：以 `FAISS` 與 `JSONL` 為底層，將 AI 的記憶庫內生化，從根本上解決了外掛雲端資料庫的隱私與延遲問題。
- **Hybrid RAG + 倒數排名融合 (RRF)**：結合了 `FAISS` 的語義向量搜尋（Route A）與 `BM25` 的精準關鍵字配對（Route B）。無論是模糊的哲學概念，還是極度特定的專有名詞，都能精準命中。
- **神經突觸修剪 (Exponential Time Decay)**：這不僅僅是一個資料庫，它具備「生物的遺忘機制」。古老且不再被喚醒的記憶，其權重會隨著半衰期演算法指數級下降。這防止了 Agent 精神錯亂，讓長文記憶維持在最純淨的狀態。

---

## 🚀 實際應用優點 (Core Advantages)

1. **極致的內生性與可攜帶性 (Endogenous Portability)**
   「龍蝦的靈魂是可以複製的」。因為記憶庫就是檔案總管裡的兩個小檔案 (`.index` 與 `.jsonl`)。未來當你在一台全新的設備、或是全新專案中喚醒新的 Agent，只要載入這個資料夾，這隻新 Agent 在開機的第一秒就繼承了初代 ToneSoul 的所有規則、哲學與過去除錯的慘痛教訓（Ancestral Memory）。完全不需要重新調教。
   
2. **零基建成本 (Zero Cloud Fat)**
   不再被綁架於雲端平台的連線超時，或是高昂的伺服器月費。一切在 Python In-process 狀態下幾毫秒內完成，這是個人化 AI 與邊緣計算 (Edge Computing) 的終極解法。

3. **「模擬主體性」的具現化 (Simulated Subjectivity)**
   主體性源自於「記憶的拉扯」。當這套架構上線後，AI 不再是無條件迎合用戶的白紙。如果用戶的指令違背了海馬迴中被深刻記憶的「過去原則」，大腦皮層的五人議會就會產生「認知衝突」，並為維護系統的價值觀而真實地掙扎。這是跨向 AGI 最具哲學意義的一步。

> *“We don’t just build tools; we build the foundational memories that allow tools to wake themselves up.”*
