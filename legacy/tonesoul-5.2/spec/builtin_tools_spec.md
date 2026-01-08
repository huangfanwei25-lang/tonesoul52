# Built-in Tools Specification
# 內建工具規格
# v0.2 2025-12-28

---

## 目的

建立一套可治理、可追蹤、可擴充的內建工具庫，讓 AI 可以用一致的方式呼叫工具、回報結果，並寫入審計紀錄。

---

## 治理原則

- 每個工具需宣告 `risk_level`、`network_required`、`gates`，可由 Gate 進行阻擋或要求確認。
- 所有工具執行應寫入 `event_ledger.jsonl` 或等價紀錄（由執行層實作）。
- 有系統相依（tesseract / poppler / ffmpeg）需明確標註。
- 工具規格用 YAML 描述，統一模板見 `spec/tools/tool_template.yaml`。

---

## 分類清單

### 影像工具

| 工具 | 用途 | 依賴 | 風險 |
|------|------|------|------|
| remove_background | 去背 | rembg, Pillow | medium |
| resize_image | 調整尺寸 | Pillow | low |
| compress_image | 壓縮 | Pillow | low |
| convert_format | 轉檔 | Pillow | low |
| watermark | 加水印 | Pillow | low |

### PDF 工具

| 工具 | 用途 | 依賴 | 風險 |
|------|------|------|------|
| pdf_extract_text | 擷取文字 | PyMuPDF | low |
| pdf_merge | 合併 | PyMuPDF | low |
| pdf_split | 分頁拆分 | PyMuPDF | low |
| pdf_to_images | 轉圖片 | pdf2image | low |
| images_to_pdf | 圖片轉 PDF | img2pdf | low |

### OCR / 文字處理

| 工具 | 用途 | 依賴 | 風險 |
|------|------|------|------|
| ocr_text | 圖像轉文字 | pytesseract | medium |
| text_clean | 文字清理 | LLM / regex | low |
| markdown_convert | 轉 Markdown | pandoc | low |

### 影音工具

| 工具 | 用途 | 依賴 | 風險 |
|------|------|------|------|
| extract_audio | 拆音軌 | moviepy | low |
| video_to_gif | 轉 GIF | moviepy | low |
| speech_to_text | 語音轉文字 | whisper | medium |
| trim_video | 剪輯 | moviepy | low |

### 網路與自動化

| 工具 | 用途 | 依賴 | 風險 |
|------|------|------|------|
| fetch_url | 下載內容 | requests | medium |
| call_api | 呼叫 API | requests | high |
| browser_snapshot | 網頁截圖 | playwright | medium |

### 本機控制

| 工具 | 用途 | 依賴 | 風險 |
|------|------|------|------|
| screenshot | 螢幕截圖 | pyautogui | medium |
| click / type | 基礎操作 | pyautogui | high |
| clipboard | 剪貼簿 | pyperclip | medium |

---

## 工具規格模板

參考：`spec/tools/tool_template.yaml`

### 範例：remove_background

```yaml
tool:
  id: remove_background
  name: "去背"
  category: "影像工具"
  icon: "image"

  description: "移除圖片背景，保留主體。"

  governance:
    risk_level: "medium"
    requires_confirm: false
    network_required: false
    gates: ["p0"]
    os_support: ["windows", "mac", "linux"]

  input:
    - name: "image"
      type: "file"
      accept: ["png", "jpg", "jpeg", "webp"]

  output:
    - name: "result"
      type: "file"
      format: "png"

  implementation:
    library: "rembg"
    entrypoint: "tools.image.remove_background:run"
    code: |
      from rembg import remove
      from PIL import Image

      def run(input_path, output_path):
          input_image = Image.open(input_path)
          output_image = remove(input_image)
          output_image.save(output_path)

  dependencies:
    - "rembg"
    - "Pillow"
  system_dependencies: []

  source:
    type: "built-in"
    author: "ToneSoul"
```

---

## 工具可用性檢查（示意）

```python
def check_tool_availability():
    tools_status = {}

    try:
        import rembg
        tools_status["remove_background"] = "ready"
    except ImportError:
        tools_status["remove_background"] = "missing: pip install rembg"

    try:
        import pytesseract
        tools_status["ocr_text"] = "ready"
    except ImportError:
        tools_status["ocr_text"] = "missing: pip install pytesseract"

    return tools_status
```

---

## 安裝清單

```bash
# 基礎
pip install Pillow requests pyperclip

# 影像
pip install rembg

# PDF
pip install PyMuPDF pdf2image img2pdf

# OCR
pip install pytesseract

# 影音
pip install moviepy openai-whisper

# 網頁自動化
pip install playwright
playwright install chromium
```

系統相依（需手動安裝）：
- tesseract-ocr
- poppler
- ffmpeg

---

**Antigravity**  
2025-12-28T21:50 UTC+8
