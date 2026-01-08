# ToneSoul 5.2 雲端儲存規劃
# Cloud Storage Plan
# 2025-12-28

---

## 目標

把佔空間的資料移到 Google Drive，本地只保留代碼和必要檔案。

---

## 資料夾分類

| 本地保留 | 移到雲端 | 原因 |
|----------|----------|------|
| `tonesoul52/` | ❌ | 核心代碼，需要快速存取 |
| `spec/` | ❌ | 規格文件，需要快速存取 |
| `frontend/` | ❌ | 前端代碼 |
| `tests/` | ❌ | 測試代碼 |
| `memory/` | ✅ | **記憶資料，會持續增長** |
| `run/execution/` | ✅ | **執行記錄，會持續增長** |
| `reports/ystm_demo/` | ✅ | 視覺化輸出 |
| `runtime/screenshots/` | ✅ | 截圖會累積 |

---

## Google Drive 結構

```
我的雲端硬碟/
└── ToneSoul/
    └── 5.2/
        ├── memory/           ← 記憶資料
        │   ├── seeds/
        │   ├── skills/
        │   └── engrams/
        ├── run/
        │   └── execution/    ← 執行記錄
        ├── reports/          ← 報告和視覺化
        │   ├── ystm_demo/
        │   └── ystm_demo_math/
        └── screenshots/      ← 截圖
```

---

## 設置步驟

### 1. 安裝 Google Drive for Desktop

下載：https://www.google.com/drive/download/

### 2. 建立雲端資料夾

在 Google Drive 網頁版建立：
```
ToneSoul/5.2/memory
ToneSoul/5.2/run
ToneSoul/5.2/reports
ToneSoul/5.2/screenshots
```

### 3. 建立符號連結（Symlink）

以**管理員身份**執行 PowerShell：

```powershell
# 先備份現有資料
cd c:\Users\user\Desktop\倉庫\5.2

# 移動 memory/ 到雲端
Move-Item -Path "memory" -Destination "G:\我的雲端硬碟\ToneSoul\5.2\memory"
New-Item -ItemType SymbolicLink -Path "memory" -Target "G:\我的雲端硬碟\ToneSoul\5.2\memory"

# 移動 run/ 到雲端
Move-Item -Path "run" -Destination "G:\我的雲端硬碟\ToneSoul\5.2\run"
New-Item -ItemType SymbolicLink -Path "run" -Target "G:\我的雲端硬碟\ToneSoul\5.2\run"

# 移動 reports/ 到雲端（可選）
# Move-Item -Path "reports" -Destination "G:\我的雲端硬碟\ToneSoul\5.2\reports"
# New-Item -ItemType SymbolicLink -Path "reports" -Target "G:\我的雲端硬碟\ToneSoul\5.2\reports"

# 移動截圖到雲端
Move-Item -Path "runtime\screenshots" -Destination "G:\我的雲端硬碟\ToneSoul\5.2\screenshots"
New-Item -ItemType SymbolicLink -Path "runtime\screenshots" -Target "G:\我的雲端硬碟\ToneSoul\5.2\screenshots"
```

⚠️ 注意：`G:\我的雲端硬碟` 是 Google Drive 的預設位置，可能因系統而異。

---

## 預估空間節省

| 資料夾 | 目前大小 | 增長速度 |
|--------|----------|----------|
| memory/ | ~10 MB | 每次對話增加 |
| run/execution/ | ~50 MB | 每次執行增加 |
| screenshots/ | ~10 MB | 每次截圖增加 |
| **總計** | ~70 MB | **持續增長** |

移到雲端後，本地只佔 ~20 MB（代碼）。

---

## 注意事項

1. **符號連結對程式透明** — 代碼不需要修改
2. **離線時可能無法存取** — Google Drive 需要網路
3. **同步可能有延遲** — 大檔案上傳需要時間
4. **多台電腦共用** — 記憶可以在不同電腦間同步

---

**Antigravity**
2025-12-28T18:37 UTC+8
