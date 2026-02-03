# Auto Continue Script - README
# 自動按鍵精靈使用說明

## 🎯 功能

每10分鐘自動輸入「繼續」並按 Enter 鍵，用於：
- 保持 AI 對話活躍
- 自動繼續工作流程  
- 避免手動重複輸入

## 📦 文件說明

| 檔案 | 說明 |
|------|------|
| `auto_continue.ps1` | 主程式腳本 |
| `啟動自動繼續.ps1` | 快速啟動器（推薦使用） |
| `README_auto_continue.md` | 本說明文件 |

## 🚀 快速開始

### 方法一：使用快速啟動器（推薦）
1. 雙擊 `啟動自動繼續.ps1`
2. 選擇模式（正式/測試/自訂）
3. 將視窗最小化，腳本會在背景運行

### 方法二：命令行
```powershell
# 預設模式（10分鐘間隔）
.\auto_continue.ps1

# 測試模式（不實際發送按鍵）
.\auto_continue.ps1 -DryRun

# 自訂間隔（5分鐘）
.\auto_continue.ps1 -IntervalMinutes 5

# 自訂文字
.\auto_continue.ps1 -TextToSend "continue"
```

## ⚙️ 參數說明

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `-IntervalMinutes` | 整數 | 10 | 間隔分鐘數 |
| `-TextToSend` | 字串 | "繼續" | 要發送的文字 |
| `-DryRun` | 開關 | false | 測試模式（不實際發送） |

## ⚠️ 注意事項

1. **焦點視窗**：按鍵會發送到當前焦點視窗，請確保目標應用程式在前景
2. **停止腳本**：按 `Ctrl+C` 可隨時停止
3. **執行策略**：首次使用可能需要調整 PowerShell 執行策略：
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

## 🐛 疑難排解

### 問題：按鍵沒有發送
**原因**：目標視窗可能失去焦點  
**解決**：確保目標應用程式在前景，或使用 `-DryRun` 測試

### 問題：找不到 System.Windows.Forms
**原因**：.NET Framework 未正確載入  
**解決**：重新啟動 PowerShell 視窗

### 問題：腳本無法執行
**原因**：執行策略限制  
**解決**：執行 `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

## 💡 使用場景

### 場景1：保持 AI 對話
```powershell
# 每10分鐘發送「繼續」
.\auto_continue.ps1
```

### 場景2：自動化測試
```powershell
# 每1分鐘測試一次
.\auto_continue.ps1 -IntervalMinutes 1 -DryRun
```

### 場景3：英文環境
```powershell
# 發送英文 "continue"
.\auto_continue.ps1 -TextToSend "continue"
```

## 🔧 進階用法

### 搭配 Task Scheduler 開機自動執行
1. 打開「工作排程器」
2. 創建基本工作
3. 觸發程序：登入時
4. 動作：啟動程式
   - 程式：`powershell.exe`
   - 引數：`-File "c:\Users\user\Desktop\倉庫\scripts\auto_continue.ps1"`

### 記錄日誌
```powershell
# 將輸出重定向到日誌檔
.\auto_continue.ps1 > auto_continue.log 2>&1
```

## 📝 更新日誌

**v1.0.0** (2026-02-02)
- ✨ 初始版本
- ✨ 支援自訂間隔時間
- ✨ 支援自訂發送文字
- ✨ 測試模式
- ✨ 友善的啟動器介面

## 🦞 作者

ToneSoul Automation Tools  
為了優化你而優化 🤪

---

**贊助提醒**：如果這個工具幫到你，記得請作者喝杯咖啡！快窮死了 😂
