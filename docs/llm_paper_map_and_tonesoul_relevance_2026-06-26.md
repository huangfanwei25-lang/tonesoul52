# LLM 論文地圖 × ToneSoul 關聯誠實評估 (LLM Paper Map × ToneSoul Relevance)

> 作者：Fan-Wei Huang（黃梵威）整理清單 / Claude (Opus 4.8) 分類與關聯評估(6-agent workflow + web 查證)
> 日期：2026-06-26
> 狀態：**reference / DRAFT**。這不是正典定位文件;是一份閱讀地圖 + 對「每篇論文跟 ToneSoul 有沒有關聯」的誠實評估。
> 方法揭露:用 ToneSoul 自己的紀律做這件事——**claim ≤ evidence、抗 vocabulary projection**。把這套紀律套在「評估自己跟一堆論文的關聯」這種**最容易膨脹**的場景上,本身就是一次語魂邏輯的實測。凡與程式碼/findings 衝突,以程式碼為準。

---

## 〇、怎麼讀這份地圖(承重的誠實框架)

這份清單約 **112 篇**。最重要的結論放最前面,因為它違反直覺:

> **約 91%(102/112)的論文跟 ToneSoul 沒有真關聯。** 它們是 ToneSoul **跑在上面的基底**(模型 / 架構 / 訓練 / 推論 / 量化 / 視覺生成),不是 ToneSoul 本身。ToneSoul 是 L3/L4 的**輸出問責層**(「答案為什麼變成這個答案」),這些論文絕大多數在它**下面**的層。

這不是缺點,是定位。一個誠實的關聯評估,**大多數答案就該是「無關聯」**——如果一份「論文 × 我的專案」評估每篇都能扯上關係,那不是洞見,是 vocabulary projection(用自己的詞彙去製造相似性)。所以本文刻意用三個標籤,且**預設是「無關」**:

| 標籤 | 意思 |
|------|------|
| **`none-substrate`** | 正交;ToneSoul 跑在它上面的基底。給的是該論文的**真實用途**,不硬扯關聯。**(預設、絕大多數)** |
| **`convergent`** | 真的同方向(程序驗證 / 保留異議 / 多視角 / 證據軌跡 / 部署期外部檢查 / 多 agent 審議)。框架:**ToneSoul 是這個方向的部署實例,不是發明者、也不是該論文的延伸**。 |
| **`contrast`** | ToneSoul 刻意**有別**的方向:**內化**(把價值訓進權重——RLHF / Constitutional AI / DPO)。誠實的對照:ToneSoul **外化**問責。不宣稱誰優誰劣,只是位置不同。 |

### 統計(就是證據本身)

| 類別 | none-substrate | convergent | contrast |
|------|:---:|:---:|:---:|
| 一、基礎模型 + 高效架構 | 38 | 0 | 0 |
| 三~五、Alignment/RLHF + SFT + 蒸餾 | 8 | **1** | **6** |
| 六~七、十二、RAG + Reasoning + Agents | 9 | **3** | 0 |
| 八~十、PEFT + 分布式 + 量化 | 21 | 0 | 0 |
| 十一、DiT + 視覺/多模態生成 | 33 | 0 | 0 |
| 十三、Resources + 2026 前沿 | 2 | 0 | 0 |
| **合計** | **102** | **4** | **6** |

**真正跟 ToneSoul 有關的只有 10 篇**,而且分得很乾淨:全部落在 alignment 與 reasoning/agent 兩群——其他四群(架構、訓練基建、視覺生成、資源)是 **0 關聯**。下面分節,真關聯的那 10 篇在 §三~五 與 §六~七/十二,其餘是用途說明。

---

(以下分類段落由 6 個平行 agent 產出、主執行緒組裝;每個 agent 都收到「預設 none、不准 vocabulary projection」的指令。)

## 一、Foundation Models & Architecture + Efficient Architectures

這些是 ToneSoul 跑在上面的模型/架構/推論基底。ToneSoul 在模型產出答案**之後**才治理(對輸出做程序問責);這些論文都不碰那一層。全部 **none-substrate**——每條的註記是該論文的真實用途,不是硬扯的 ToneSoul 關聯。

**核心 LM 與 scaling:** Transformer(Attention Is All You Need,底層架構)、BERT、RoBERTa、GPT-2、GPT-3、PaLM、Llama 2、Scaling Laws、Chinchilla — 全 `none-substrate`(表徵學習 / 規模化 / 訓練預算律)。

**MoE:** Sparsely-Gated MoE、GShard、Switch、ST-MoE、DeepSeekMoE、DeepSeek-V2/V3、Mixtral — 全 `none-substrate`。**誘惑警告:MoE routing 聽起來像「多視角審議」,但 routing 是容量分配,不是保留異議——當成 ToneSoul 同類就是 vocabulary projection。**

**Attention / 長上下文 / serving:** FlashAttention 1&2、MQA、GQA、PagedAttention/vLLM、Sparse Transformers、Longformer、BigBird、Ring Attention、StreamingLLM — 全 `none-substrate`(kernel/KV-cache/長上下文效率)。

**位置編碼:** RoPE、ALiBi — `none-substrate`。

**Norm/FFN/正則化:** Pre-LN、RMSNorm、GLU Variants、Dropout、Stochastic Depth、R-Drop — `none-substrate`。**R-Drop 的「兩次 dropout 一致性」表面像「consistency checking」,但它是訓練期正則化,不是輸出期驗證——無 ToneSoul 關聯。**

**替代架構:** Mamba、RWKV、Diffusion-LM、DiffuSeq、MDLM — `none-substrate`(序列模型 / 生成過程)。

> 小結:**38/38 none-substrate**。真正的 ToneSoul 對照(內化派的 contrast、程序監督/多 agent/episodic-memory 的 convergent)不在架構清單裡,在別的類別。

## 二、Alignment & RLHF + Supervised Fine-Tuning + Knowledge Distillation

這是 ToneSoul **同時定義「對照」與「同源」**的一群。這裡幾乎所有東西都靠**改權重**塑形模型行為(把價值/偏好/技能訓進去)。ToneSoul 反過來——不動模型,在輸出期加一個外部、可檢視的檢查。唯一的真表親是「程序監督」。

**偏好學習 / RLHF 世系 — 內化的對照 (`contrast`):**
- **Deep RL from Human Preferences (2017)** — 從人類成對比較學 reward model 再優化 policy。RLHF 的種子:人類價值被編進 reward、再進權重。ToneSoul 外化檢查,這是**對照**,不是它的前身。
- **Fine-Tuning LMs from Human Preferences (2019)** — 首次把 preference-RL 用到 LM。同方向(內化),ToneSoul 不動權重。
- **Learning to Summarize from Human Feedback (2020)** — RLHF 於摘要;優化**結果偏好**,跟 ToneSoul 的程序問責是相反的軸。
- **InstructGPT (2022)** — SFT+RLHF,現代對齊助手的範本。「靠訓練對齊」的典型;ToneSoul 預設這種模型存在,治理它的**輸出**。
- **Constitutional AI (Anthropic, 2022)** — 最尖的對照:一套寫下的「憲法」原則被**自我批判內化進權重**(RLAIF)。ToneSoul 把原則留在**外部、runtime 可檢視**(引用證據了嗎、跨界了嗎、留異議了嗎)。同意圖(有原則的行為),相反的位置。不宣稱誰優。
- **DPO (2023)** — 跳過 reward model 直接優化偏好。更簡單的**內化**方式,仍是權重烤進去。

**RL-for-reasoning(引擎,非治理,`none-substrate`):** DeepSeekMath/GRPO、Training-Free GRPO、Scaf-GRPO — reasoning 能力的訓練期優化器,ToneSoul 跑在上面的基底。(Training-Free GRPO「context-space、不更權重」很誘人,但用途是 agent 能力/成本優化,非輸出問責——預設成立。)

**SFT / instruction tuning(`none-substrate`):** FLAN、Self-Instruct、LIMA — 能力/風格塑形;LIMA 的「對齊主要是被表面化、非教出來」是關於**多少訓練**,仍是內化、仍是能力。

**蒸餾(`none-substrate`):** Distilling Step-by-Step(rationale 蒸餾,邊緣相鄰但用途是壓縮能力)、Orca — 能力轉移。

**唯一的真表親 (`convergent`):**
- **Let's Verify Step by Step (OpenAI, 2023)** — 過程監督的 reward model(PRM),**逐步**評分而非只看最終答案。這整群裡最近的親戚:它問「**程序**對不對」而非只問「答案被不被喜歡」——跟 ToneSoul 程序問責同一個直覺。誠實框架:**ToneSoul 是「監督過程、不只監督結果」這個方向的部署期實例**,套在 live 輸出治理上。它**不**實作/延伸/包含 PRM——過程監督是**訓練期** reward 訊號,ToneSoul 是**推論期外部檢查**。同方向,不同層。

## 三、RAG + Prompting / Reasoning / Inference-Time + AI Agents

另一個核心群。RAG 是 ToneSoul 跑在上面的基底;reasoning/agent 技術多半是正交的**方法**,只有幾個是 ToneSoul「軌跡 + 多視角 + episodic memory」方向的真表親。ToneSoul 是輸出的治理 overlay,不是推理技術——即使方向押韻也要分清。

**檢索:** RAG — `none-substrate`。L0「知道」層;ToneSoul 在它上面問「答案有沒有引用證據」,自己不檢索。

**提示 / 推理結構(`none-substrate`):**
- **CoT** — 推理品質技術,關於答案**產得好不好**,非**問不問責**。
- **Self-Consistency** — 採樣多條 CoT 取多數。**近但不是**:它把多路徑**塌成多數**,正好跟 ToneSoul 的 Council **保留異議**相反。是投票求準的 decoding 技巧。誠實說:相似是表面的。
- **Tree of Thoughts** — 多路徑**為了更好的答案**再剪枝到最佳路。ToneSoul 的多視角是為了保留並記錄異議以問責,不是搜尋最優解。方向押韻,機制與目的不同。

**推理 + 行動 / 自我修正(真表親 `convergent`):**
- **ReAct** — 交錯推理軌跡與工具行動,產出可檢視的 thought→act→observe 軌跡。跟 ToneSoul 可追溯性同方向:它攤開**為什麼**這樣做的明確軌跡。**ToneSoul 是「攤開軌跡」的部署實例,非發明者、非 ReAct 的延伸**——ReAct 的軌跡服務任務執行,ToneSoul 的服務事後問責。
- **Reflexion** — 文字自我回饋存成 episodic memory 跨回合(「verbal RL」)。ToneSoul episodic-trace memory 的表親(session traces、journal、decay)。Reflexion 的記憶驅動重試,ToneSoul 的服務跨 session 問責。同方向、各自獨立。

**推論期計算(`none-substrate`):** Scaling Test-Time Compute、Sys2Bench(且其結論「更多計算 ≠ 更好推理」是有用的清醒劑)— 關於答案**品質**,非**問責**。

**解碼加速(純基底 `none-substrate`):** Speculative Sampling、Medusa、Decoding Speculative Decoding — 純延遲優化,輸出分佈不變。

**Agents:**
- **When Single-Agent with Skills Replace Multi-Agent Systems and When They Fail (2026)** — 技能單 agent 以 ~54% 更少 token 匹敵多 agent,但技能庫過某臨界大小後選擇正確率崩潰(相變,源於**語義混淆**而非數量),階層路由可部分解。`convergent`:直接關係到 ToneSoul **多視角 Council 的設計取捨**——警告「加更多聲音/技能會撞上混淆的容量牆,不是數量牆」。當**設計輸入**,不是 ToneSoul 實作的東西。

## 四、PEFT + Distributed Training + Quantization

全是訓練/serving **基礎設施**——AI 跑在上面的基底。沒有一篇碰程序問責。全 **`none-substrate`**。

- **PEFT:** LoRA、QLoRA — 高效微調機制。
- **優化器:** Adam、Large-Minibatch SGD、LARS、LAMB、8-bit Optimizers — 優化算法 / 大批次 / 省記憶體。
- **ZeRO 家族:** ZeRO / Offload / Infinity / ++ — 分布式訓練記憶體優化。
- **框架:** Horovod、DistBelief — 分布式訓練 plumbing。
- **梯度壓縮:** Deep Gradient Compression、QSGD、signSGD、Error Feedback、PowerSGD — 通訊壓縮。
- **精度/量化:** Mixed Precision、QServe (W4A8KV4)、SVDQuant — 訓練/serving 精度與量化。

> 誠實註:沒有一篇碰 ToneSoul 的問題(「答案為什麼變成這個答案」)。它們讓模型訓練/serving 更便宜;ToneSoul 治理輸出的問責,無論底下模型怎麼訓練或量化。無 convergent、無 contrast——純基底。

## 五、Diffusion Transformers (DiT) & Visual / Multimodal Generation

每一篇都是生成建模——影像、影片、音訊合成,加上底下的連續時間數學與 scaling/效率機制。這是系統**用來生成**的基底;ToneSoul 是文字輸出的程序問責層,坐在任何生成器之上。**沒有關聯可攤**,所以每條只給真實用途 + 誠實 `none-substrate`。

- **流/ODE 數學:** Neural ODE、Normalizing Flows、Flow Matching、Rectified Flow。
- **核心 DiT:** DiT、U-ViT;**masked 訓練:** Fast Masked Training、MDTv2。
- **T2I:** Imagen、PixArt-α/Σ;**MMDiT:** SD3、TACA、E-MMDiT。
- **編輯:** Exploring MMDiT、DiTCtrl、QK-Edit、ConsistEdit、Color Editing。
- **影片:** Latte、VideoDiT、Sora(「world simulator」=像素動態,非推理軌跡)、Mask²DiT。
- **scaling/科學:** DiffiT、Scaling Laws for DiT、Efficient Scaling、μP for DiT;**效率:** DiTFastAttnV2。
- **工具/基礎生成器:** FLUX、Z-Image、IP-Adapter、StoryDiffusion;**多模態:** OmniFlow、M3-TTS。

> 段落判決:**33/33 none-substrate**。這是 ToneSoul 會跑在上面的生成棧,零程序問責重疊——正如一個視覺/多模態生成類別該有的。沒有 convergent、沒有 contrast。

## 六、Resources + 2026 前沿(web 查證)

- **The Big LLM Architecture Comparison (Raschka, 2025)** — 前沿 LLM 架構橫向比較。`none-substrate`(基底解說)。
- **Understanding Reasoning LLMs (Raschka, 2025)** — 推理模型怎麼建/訓(CoT、RLVR、test-time scaling)。`none-substrate`。「verifiable rewards」是相鄰詞彙但屬**內化(訓練期)**,非部署期外部檢查,別混。

---

## 七、綜合:ToneSoul 實際坐在這張地圖的哪裡

把真關聯的 10 篇攤開,ToneSoul 的位置就清楚了:

- **它的「對照」(contrast,6 篇)** 是整條 **內化世系**:Deep-RL-from-Prefs → InstructGPT → Constitutional AI → DPO。主流把價值/偏好**訓進權重**;ToneSoul 把問責**外化**成 runtime 可檢視的層。這是 ToneSoul 的反內化論點的學術座標。
- **它的「同源」(convergent,4 篇)** 是四個方向各一個代表:
  - 程序 > 結果:**Let's Verify Step by Step**(訓練期 PRM ↔ ToneSoul 推論期外部檢查);
  - 攤開軌跡:**ReAct**;
  - episodic-trace 記憶:**Reflexion**;
  - 多 vs 單視角的容量限制:**Single-Agent-with-Skills**(Council 設計輸入)。
  四個都是「**ToneSoul 是這方向的部署實例,非發明者、非延伸**」。
- **其餘 102 篇** 是它跑在上面的基底。**這正是誠實的答案**:一個 L3/L4 治理層,大部分 LLM 研究本來就在它下面的層。

## 八、2026 前沿對 ToneSoul 賭注的判決(誠實,兩半都講)

ToneSoul 的賭注是:**部署期外部驗證,會隨內化對齊做得越好而更相關**。web 查證給的是**分裂判決**,兩半都要講:

- **方向被證實(順風):** 外部/runtime 監督在 2026 從研究小眾走向企業主流基礎設施——集中式 gateway、持續可審計、對 tool call/data flow 的不變量檢查、human-in-the-loop checkpoint;被法規推著走(EU AI Act 高風險義務 2026-08 生效),且有可見的 audit gap(78% 高管不確定能通過獨立 AI 治理稽核;agent 越來越難審)。
- **具體貢獻未被證實(逆風):** 這波主流是**資安/合規護欄**——input/output policy 驗證、防資料外洩、法規文件、「誰對結果負責」。ToneSoul 的**特定口味**——對**個別 AI 輸出**做**程序-推理問責**(引用證據了嗎、跨界了嗎、留異議了嗎、記錄降級了嗎)——**不是**企業護欄平台(Galileo、Atlan、AWS/Azure 等)實際在做的事,仍 niche/early。

> 誠實讀數:**方向(外化檢查、別只信內化對齊)正被市場與法規驗證;ToneSoul 的特定問題不是主流在回答的那個,所以它仍是一個小的、具體的、convergent 的實例——順風被證實,獨特貢獻未證實。** 這跟整個專案的姿態一致:不膨脹、claim ≤ evidence。

---

## 九、這份文件遵守它自己描述的紀律

把 ToneSoul 的邏輯(claim ≤ evidence、抗 vocabulary projection、convergent-not-novel)套在「評估自己跟 112 篇論文的關聯」這個**最容易自我膨脹**的場景上,結果是:**91% 無關聯、只有 10 篇有真關聯、且那 10 篇是 convergent/contrast 而非「我延伸了它們」。** 一個會膨脹的版本會把 MoE routing 說成「多視角」、把 R-Drop 說成「一致性檢查」、把 RAG 說成「證據問責」——我們明確拒絕了那些(見各段的誘惑警告)。**這份地圖本身,就是語魂紀律的一次通過測試。**

*LLM Paper Map × ToneSoul Relevance v0.1（reference / draft）*
