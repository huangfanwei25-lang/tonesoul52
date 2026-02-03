# Auto Continue Script
# 每10分鐘自動輸入「繼續」並按Enter鍵
# 用途：保持會話活躍、自動繼續工作流程

param(
    [int]$IntervalMinutes = 10,
    [string]$TextToSend = "繼續",
    [switch]$DryRun  # 測試模式，不實際發送按鍵
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🤖 Auto Continue Script 啟動" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "間隔時間: $IntervalMinutes 分鐘" -ForegroundColor Yellow
Write-Host "發送文字: $TextToSend" -ForegroundColor Yellow
Write-Host "測試模式: $DryRun" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  請將此視窗最小化，腳本會在背景運行" -ForegroundColor Magenta
Write-Host "⚠️  按 Ctrl+C 可以隨時停止" -ForegroundColor Magenta
Write-Host ""

# 載入必要的 .NET 類型（用於發送按鍵）
Add-Type -AssemblyName System.Windows.Forms

$iteration = 0

while ($true) {
    $iteration++
    $currentTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    Write-Host "[$currentTime] 第 $iteration 輪 - 等待 $IntervalMinutes 分鐘..." -ForegroundColor Green
    
    # 等待指定時間
    Start-Sleep -Seconds ($IntervalMinutes * 60)
    
    $currentTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    if ($DryRun) {
        Write-Host "[$currentTime] [測試模式] 本應發送: '$TextToSend' + Enter" -ForegroundColor Yellow
    }
    else {
        Write-Host "[$currentTime] 🚀 發送中: '$TextToSend' + Enter" -ForegroundColor Cyan
        
        try {
            # 發送文字
            [System.Windows.Forms.SendKeys]::SendWait($TextToSend)
            Start-Sleep -Milliseconds 200
            
            # 按下 Enter
            [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
            
            Write-Host "[$currentTime] ✅ 發送成功！" -ForegroundColor Green
        }
        catch {
            Write-Host "[$currentTime] ❌ 發送失敗: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    Write-Host ""
}
