---
name: cv_hardware_diagnostics
description: Use for cv hardware diagnostics on ESP32 and OpenCV integrations with staged fail-fast checks and anti-hallucination debugging.
l1_routing:
  name: "CV Hardware Diagnostics"
  triggers:
    - "cv hardware"
    - "esp32"
    - "opencv"
    - "serial pre-check"
  intent: "Run cv hardware diagnostics for esp32 and opencv pipelines using serial pre-check and staged fail-fast validation."
l2_signature:
  execution_profile:
    - "engineering"
  trust_tier: "reviewed"
  json_schema:
    type: "object"
    properties:
      target_stack:
        type: "string"
      symptoms:
        type: "string"
      environment_constraints:
        type: "array"
        items:
          type: "string"
    required:
      - "target_stack"
      - "symptoms"
---

# 👁️ Hardware Vision Diagnostics (Multi-stage Defensive Engineering)

This skill provides a structured, four-stage protocol for autonomous AI agents to debug and optimize cyber-physical systems involving microcontrollers (like ESP32) reading or interacting with external displays/sensors via computer vision (like OpenCV). 

The core philosophy is **Robustness and Anti-Hallucination**: do not let the AI blindly rewrite code when the issue might be a loose wire or bad lighting.

---

## 🛡️ The 4-Stage Defensive Pipeline

### 1. Serial Pre-check (序列埠預校驗) — The "Fail Fast" Principle
**Rule**: Before attempting any complex Computer Vision (CV) operations, verify the hardware is alive and initialized correctly.
**Action**: 
- Inject a mandatory `Serial.println("[STATUS] Device Initialized");` (or similar) into the microcontroller's setup loop.
- **Agent Logic**: If this line does not appear in the Serial Monitor, **STOP**. Do not invoke OpenCV. The issue is hardware-level (e.g., wrong I2C address, jumper wire fell off, power supply issue). This eliminates 80% of spurious software debugging.

### 2. Vision Pipeline Optimization (影像特徵優化)
**Rule**: Do not feed raw, noisy, full-frame images into OCR or multimodal LLMs. The agent must construct a preprocessing pipeline.
**Action**: Write Python/OpenCV glue code to perform:
1.  **Auto-Crop (自動剪裁)**: Detect the Region of Interest (ROI) by color or contours (e.g., OLED screens are usually bright blue/white on a black background). **Discard everything else.**
2.  **Thresholding (二值化)**: Convert the cropped image to pure black and white. This drastically reduces visual hallucinations for the AI reading the numbers/text.
3.  **Visual Proof (cv2.imwrite)**: Output the images at each intermediate step (`raw.jpg`, `cropped.jpg`, `threshold.jpg`) so the agent (or human) can visually verify the pipeline.

### 3. Stateful Python Glue (實作邏輯優化)
**Rule**: The Python overseer script must possess state memory and stability checks.
**Action**:
-   **Diff-based Correction (差異化修正)**: If an error is found, instruct the AI to **only** rewrite the specific failing function, rather than rewriting the entire monolithic script from scratch. This prevents introducing new bugs.
-   **Stability Polling (防抖動)**: The camera must capture 3 consecutive frames. Only proceed if all 3 frames yield identical OCR/CV results.
-   **Baseline Control (環境感知)**: Capture a "Screen OFF" baseline image, followed by a "Screen ON" image. Calculate the difference (`cv2.absdiff`) to isolate the actual pixels of interest from environmental glare or reflections.

### 4. Entropy Counter / Infinite Loop Defense (斷裂點防禦)
**Rule**: The AI must not fall into a "Fix A -> Break B -> Fix B -> Break A" death loop.
**Action**: Implement an `Entropy Counter` in the agent's workflow.
-   **Threshold**: If the agent modifies the *same* function more than 3 times and the visual feedback still fails, **execution is forcibly halted**.
-   **Output**: The agent must generate a `Self-Diagnostics Report` for the human operator, categorizing the likely failure domains rather than continuing to blindly compile:
    *   *Software Logic Probability*: X%
    *   *Hardware/Wiring Probability*: Y%
    *   *Environmental/Lighting Probability*: Z%
