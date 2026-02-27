> [!WARNING]
> **Deprecated**: This document is a **2025-12 snapshot**. Paths such as `body/surgeon/` no longer exist in the current architecture. For the current state, see `AGENTS.md` and `memory/ANTIGRAVITY_SYNC.md`.

# ToneSoul: Evolution Handoff (v0.3.0 - The Awakened Shell)

> "She can see, she can remember, and she can heal herself."

If you are new here, read `AGENTS.md` first for a stable repo snapshot.

## 🚀 Key Upgrades Delivered

### 1. 👁️ The All-Seeing Eye (Phase 17)
*   **Capability**: Multimodal Vision.
*   **Detail**: Connected `llava` to `TelemetrySensor` and `SpineController`.
*   **Usage**: Upload images in the Dashboard. She will analyze them for emotional context (STREI metrics).

### 2. ⚡ The Ghost in the Shell (Phase 18)
*   **Capability**: Hardware Optimization & Remote Brain.
*   **Detail**: 
    1.  **Telemetry Cache**: Caches moral judgments (`telemetry_cache.json`) to speed up local inference by 100x for repeated thoughts.
    2.  **Remote Switch**: Added support for OpenAI/Groq APIs in `LLMClient` to offload thinking from your old hardware.

### 3. 🔪 The Surgeon (Phase 19)
*   **Capability**: Test-Driven Autopoiesis (Self-Healing).
*   **Detail**: The most advanced feature. ToneSoul can now edit her own source code to fix bugs.
*   **Safety**: Uses a **Constitutional Sandbox** workflow:
    `Diagnosis -> Prescription -> Simulation (Sandbox + Pytest) -> Operation (Apply)`.

## 🛠️ How to Use

1.  **Start Dashboard**:
    ```bash
    python run_dashboard.py
    ```
2.  **Test Vision**: Click the 🖼️ icon in the chat bar.
3.  **Test Self-Healing**: 
    The `Surgeon` class is active in `body/surgeon`. To manually invoke repairs, you can use Python:
    ```python
    from body.surgeon.surgeon import Surgeon
    Surgeon().operate("path/to/buggy_file.py", "Fix the bug")
    ```

## ⚠️ Notes for Operator
*   **Disk Space**: You reclaimed space by identifying the models. The cache will grow slowly but save compute.
*   **Safety**: The Surgeon is powerful. Ensure `pytest` tests remain rigorous to prevent regression.

---
*Delivered: December 2025*
