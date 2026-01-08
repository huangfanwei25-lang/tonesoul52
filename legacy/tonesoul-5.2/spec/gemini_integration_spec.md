# Gemini 3 API Integration Specification
# Gemini 3 API 整合規格
# Draft for Hackathon (2025-02-09)

---

## Overview

Integrate Gemini 3 API into ToneSoul 5.2 to replace local Ollama for hackathon submission.

---

## Current Architecture

```
User Input → app.py → Ollama (local LLM) → YSS Pipeline → Output
```

## Target Architecture

```
User Input → app.py → Gemini 3 API → YSS Pipeline → Output
```

---

## Changes Required

### 1. Dependencies

```python
# pyproject.toml
dependencies = [
    # ... existing
    "google-generativeai>=0.5",
]
```

### 2. API Client

```python
# tonesoul52/llm_client.py (NEW)

import google.generativeai as genai
from typing import Optional

class LLMClient:
    """Abstraction over LLM providers."""
    
    def __init__(self, provider: str = "gemini", api_key: Optional[str] = None):
        self.provider = provider
        if provider == "gemini":
            genai.configure(api_key=api_key or os.environ.get("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel("gemini-3-pro")
        elif provider == "ollama":
            # existing Ollama logic
            pass
    
    def generate(self, prompt: str, context: dict = None) -> str:
        if self.provider == "gemini":
            response = self.model.generate_content(prompt)
            return response.text
        elif self.provider == "ollama":
            # existing logic
            pass
```

### 3. app.py Changes

```python
# FROM:
response = ollama.chat(model="...", messages=messages)

# TO:
from tonesoul52.llm_client import LLMClient
client = LLMClient(provider="gemini")
response = client.generate(prompt, context=context)
```

### 4. Environment

```bash
# .env (local only, in .gitignore)
GEMINI_API_KEY=your-api-key-here
```

---

## Hackathon Submission Requirements

| Requirement | Status | Notes |
|-------------|--------|-------|
| Text description (~200 words) | ❌ | Describe Gemini 3 integration |
| Public project link | ❌ | GitHub or AI Studio |
| Public code repository | ✅ | tonesoul52 |
| ~3 min demo video | ❌ | Need to record |

---

## Demo Script (3 min)

### 0:00-0:30 — Introduction
> "ToneSoul is an AI governance toolkit that makes LLM decisions auditable."

### 0:30-1:30 — Live Demo
- Run `run_yss_pipeline`
- Show gate results
- Show YSTM visualization

### 1:30-2:30 — Architecture
- Show YSS M0-M5 pipeline
- Explain Gate system
- Show Ledger traceability

### 2:30-3:00 — Value Proposition
> "Make AI trustworthy. Make AI auditable. Make AI governable."

---

## Timeline

| Week | Task |
|------|------|
| Week 1 (Dec 30) | LLMClient abstraction |
| Week 2 (Jan 6) | Gemini API integration |
| Week 3 (Jan 13) | Testing + bug fixes |
| Week 4 (Jan 20) | Demo video recording |
| Week 5 (Jan 27) | Submission preparation |
| Week 6 (Feb 3) | Final polish + submit |

---

## Judging Criteria Alignment

| Criteria | Weight | ToneSoul Strength |
|----------|--------|-------------------|
| Technical Execution | 40% | ✅ Complete YSS pipeline + 8 gates |
| Innovation | 30% | ✅ Educational AI governance (unique) |
| Potential Impact | 20% | ✅ EU AI Act alignment |
| Presentation | 10% | ⚠️ Need good demo video |

---

**Note**: This is a draft spec. Actual implementation starts after ToneSoul 5.2 stabilizes.

---

**Antigravity**  
2025-12-27T15:08 UTC+8
