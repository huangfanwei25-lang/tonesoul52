# NLnet Grant Proposal Draft: ToneSoul (NGI0 Commons Fund)

> Purpose: draft the NLnet grant narrative for positioning ToneSoul as a local-first public-good governance engine.
> Last Updated: 2026-03-23

> **📝 申請建議策略 (Strategy Note)**
> NLnet 偏好「具體、開源、保護隱私、去中心化且不依賴特定大廠」的基礎建設專案。我們應該主打 ToneSoul 作為一個 **「Local-First 的 AI 治理與認知分歧引擎 (Local-First Cognitive Divergence Engine for AI Governance)」**，強調我們藉由本地模型 (Ollama + Qwen3) 建立三視角議會，打破專有大語言模型 (Proprietary LLMs) 的同溫層與價值觀壟斷，把真正的決策思考權（Meaningful Divergence）還給開源社群與使用者。
> 
> 以下是針對 NLnet 申請表單各大題的撰寫草稿（英文，符合審查委員閱讀習慣）：

---

### 1. Abstract: Can you explain the whole project and its expected outcome(s)?
**[Draft Answer]**
**ToneSoul is an open-source, local-first Responsible AI Governance Engine** designed to solve the critical "echo chamber" problem inherent in autonomous LLM agents. As AI systems increasingly execute real-world tasks (agentic workflows), current safety paradigms (e.g., simplistic content moderation walls) are insufficient. They struggle to handle complex, multi-step reasoning failures and suffer from centralized, proprietary API dependencies.

ToneSoul introduces a deterministic **"Meaningful Divergence" framework for AI Alignment.** It intercepts autonomous agent workflows and spawns a local, multi-agent debate council (Philosopher, Engineer, Guardian) using open-weights SLMs (e.g., Qwen3 via Ollama). Instead of a basic "allow/deny" filter, ToneSoul calculates a mathematical "Tension Tensor" and generates structured, auditable evidence traces. When cognitive divergence exceeds safety thresholds, the system triggers a **Human-in-the-Loop (HITL)** fallback, ensuring humans retain ultimate oversight over critical decisions without being overwhelmed by routine logs.

**Expected Outcomes:**
1. A fully open-source, modular TypeScript/Python runtime library for the ToneSoul Council, enabling local AI Governance.
2. The *Progressive-Disclosure Skill Registry* format, establishing strict security boundaries against Agentic Prompt Injections.
3. Standardized telemetry for "divergence quality" and "tension metrics" that other open-source agents (e.g., LangChain, AutoGen) can adopt.
4. Democratization of AI Alignment by achieving zero dependency on proprietary APIs for the core governance loop.

### 2. Have you been involved with projects or organisations relevant to this project before?
**[Draft Answer]**
Yes. We have been actively developing autonomous agent pipelines (the Elisa/Codex architecture). During our research, we recognized the escalating risks of autonomous agents executing tasks without internal friction or robust oversight. In response, we iteratively designed and open-sourced the "7D Audit Framework" (a comprehensive Red Teaming methodology for agents) and the initial prototype of the ToneSoul governance council. This grant will catalyze our effort to decouple ToneSoul from our internal agent implementation, transforming it into a universal, standalone public good for the broader NGI ecosystem.

### 3. Requested support (Budget & Tasks)
**[Draft Answer]**
We request funding to mature the ToneSoul architecture, decouple it into a standalone library, and achieve production-ready adversarial robustness. 

**Main Tasks Breakdown (Estimated 6 months, €30,000 - €40,000 total):**
1. **Engine Decoupling & Tooling (€10,000):** Extracting the CouncilRuntime and TensionGate into generic, framework-agnostic NPM/PyPI packages for the open-source community.
2. **Local Model Optimization for Governance (€8,000):** Fine-tuning the Ollama integration to ensure the 3-persona council can execute complex alignment reasoning efficiently on consumer hardware (e.g., 8GB VRAM), eliminating centralized API costs.
3. **Progressive-Disclosure Security Contracts (€7,000):** Implementing a 3-layer security boundary (Routing -> Signature -> Payload) to mitigate Prompt Injections and Jailbreaks in agent tool registries.
4. **Adversarial Audits & 7D Framework Expansion (€5,000):** Comprehensive security testing (RDD/DDD) to ensure the governance layer itself is resilient against manipulation by malicious agent outputs.
5. **Documentation & Ecosystem Integration (€5,000):** Writing integration guides and building connector abstractions for mainstream open-source agent frameworks (e.g., MCP connectors).

### 4. Compare your own project with existing or historical efforts.
**[Draft Answer]**
Existing AI safety tools (like Meta's Llama Guard or OpenAI's Moderation API) function primarily as **Content Censors**—they check if an input/output violates a static policy and block it. Moreover, they heavily rely on centralized, proprietary APIs, which limits transparency and creates vendor lock-in.

ToneSoul operates as a **Dynamical Alignment Synthesizer**. It doesn’t just look for surface-level policy violations; it looks for *logical blind spots* and *value misalignment* by forcing a local SLM to argue with the proposed action from multiple predefined philosophical and engineering standpoints. Furthermore, while typical "Multi-Agent Debates" (e.g., ChatDev, MetaGPT) are too resource-intensive and unpredictable for runtime governance, ToneSoul is highly optimized to run locally. It acts as a lightweight, deterministic **"Cognitive Escape Valve"** that quantifies tension and only interrupts the user's workflow when the disagreement is meaningful.

### 5. What are significant technical challenges you expect to solve?
**[Draft Answer]**
1. **Context Window Pollution in Local SLMs:** Running three distinct alignment personas locally can quickly overflow the context window of small models (like 4B/8B parameters), leading to instruction amnesia. We are solving this via the "Progressive-Disclosure Security Contract," ensuring only the absolute minimum required metadata (L1 Routing) is loaded initially, strictly isolating the heavy governance prompts.
2. **Quantifying "Meaningful Divergence" for HITL:** Parsing raw LLM debate text into a deterministic, programmatic True/False gate is notoriously flaky. We are engineering a "Tension Tensor" mathematical model that uses semantic embeddings to calculate the cosine distance between the personas' stances. This turns natural language disagreements into strict, auditable floating-point values for the routing system, preventing decision fatigue for human operators.

### 6. Describe the ecosystem of the project, and how you will engage with relevant actors?
**[Draft Answer]**
The project sits at the intersection of Local AI (Ollama/Llama.cpp), Autonomous Agents, and the Responsible AI (RAI) Alignment community. 
To engage the ecosystem:
1. All code licensed under AGPLv3/MIT to guarantee freedom and prevent proprietary enclosure of alignment techniques.
2. We will provide reference implementations integrating ToneSoul into heavily used open-source visual programming blocks (e.g., Blockly-based agent builders) and orchestration frameworks.
3. We will actively publish our "Divergence Architecture RFCs" on platforms like GitHub, Hugging Face, and HackerNews to invite academic AI safety researchers and open-source developers to contribute to the Tension metrics and Red Teaming (7D) frameworks.
