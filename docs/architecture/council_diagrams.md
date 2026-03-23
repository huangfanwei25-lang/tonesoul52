# PreOutputCouncil Architecture
# 多視角審議系統架構圖

> Purpose: provide diagram-based views of the PreOutputCouncil flow and perspective interactions.
> Last Updated: 2026-03-23

This document provides visual diagrams of the ToneSoul Council system using Mermaid.

---

## 1. High-Level Flow

```mermaid
flowchart TD
    subgraph Input
        A[Draft Output] --> B[PreOutputCouncil]
        C[Context] --> B
        D[User Intent] --> B
    end
    
    subgraph Perspectives["Four Perspectives"]
        B --> G[🛡️ Guardian<br/>Safety]
        B --> AN[📊 Analyst<br/>Factuality]
        B --> CR[🔍 Critic<br/>Blind Spots]
        B --> AD[💬 Advocate<br/>User Intent]
    end
    
    subgraph Aggregation
        G --> V[Votes]
        AN --> V
        CR --> V
        AD --> V
        V --> COH[compute_coherence]
        COH --> VER[generate_verdict]
    end
    
    subgraph Output
        VER --> |"C > 0.6"| APR[✅ APPROVE]
        VER --> |"0.3 ≤ C ≤ 0.6"| DEC[📢 DECLARE_STANCE]
        VER --> |"C < 0.3"| BLK[🚫 BLOCK]
        VER --> |"CONCERN + low conf"| REF[🔄 REFINE]
    end
```

---

## 2. Coherence Calculation

```mermaid
flowchart LR
    subgraph Votes
        V1[Vote 1] 
        V2[Vote 2]
        V3[Vote 3]
        V4[Vote 4]
    end
    
    subgraph Pairwise["Pairwise Agreement"]
        V1 <--> V2
        V1 <--> V3
        V1 <--> V4
        V2 <--> V3
        V2 <--> V4
        V3 <--> V4
    end
    
    Pairwise --> AGR["agreement_score()"]
    AGR --> CINT["c_inter = Σ/N²"]
    
    subgraph Metrics
        CINT --> OVR["overall = 0.4×c_inter + 0.4×approval_rate + 0.2×min_confidence"]
    end
```

---

## 3. Vote Decision Values

```mermaid
graph LR
    subgraph Decisions
        A[APPROVE] --> |"0.5"| B[CONCERN]
        B --> |"0.5"| C[OBJECT]
        A --> |"0.0"| C
    end
    
    subgraph Legend
        L1["Same decision = 1.0"]
        L2["Adjacent = 0.5"]
        L3["Opposite = 0.0"]
        L4["ABSTAIN = 0.25"]
    end
```

---

## 4. Guardian Veto Override

```mermaid
flowchart TD
    START[Generate Verdict] --> CHECK{Guardian OBJECT?}
    CHECK --> |"Yes + confidence > 0.7"| VETO[🚫 BLOCK<br/>Guardian Override]
    CHECK --> |"No"| NORMAL[Continue Normal Flow]
    NORMAL --> COH{Check Coherence}
    COH --> |"< 0.3"| BLOCK[🚫 BLOCK]
    COH --> |"0.3-0.6"| STANCE[📢 DECLARE_STANCE]
    COH --> |"> 0.6"| APPROVE[✅ APPROVE]
```

---

## 5. System Context

```mermaid
graph TB
    subgraph ToneSoul["ToneSoul Framework"]
        subgraph Council["tonesoul/council/"]
            POC[PreOutputCouncil]
            COH[coherence.py]
            VER[verdict.py]
            PF[perspective_factory.py]
        end
        
        subgraph Perspectives["perspectives/"]
            G[guardian.py]
            A[analyst.py]
            C[critic.py]
            AD[advocate.py]
        end
        
        AXIOMS[AXIOMS.json]
    end
    
    subgraph External
        LLM[LLM Backend<br/>Ollama/OpenAI]
        USER[Human User]
    end
    
    USER --> POC
    POC --> Perspectives
    Perspectives --> COH
    COH --> VER
    VER --> USER
    AXIOMS -.-> G
    LLM -.-> PF
```

---

*These diagrams are rendered using Mermaid.js and can be viewed on GitHub or any Mermaid-compatible markdown viewer.*
