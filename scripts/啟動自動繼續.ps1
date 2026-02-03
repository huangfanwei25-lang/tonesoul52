# Quick Launcher for Auto Continue Script
# 雙擊此腳本即可啟動自動「繼續」功能

Write-Host "🚀 啟動 Auto Continue..." -ForegroundColor Green
Write-Host ""

# 選項菜單
Write-Host "請選擇模式：" -ForegroundColor Cyan
Write-Host "1. 正式模式（每10分鐘發送'繼續'）" -ForegroundColor Yellow
Write-Host "2. 測試模式（只顯示不實際發送）" -ForegroundColor Yellow
Write-Host "3. 自訂間隔時間" -ForegroundColor Yellow
Write-Host ""

$choice = Read-Host "請輸入選項 (1/2/3)"

switch ($choice) {
    "1" {
        Write-Host "啟動正式模式..." -ForegroundColor Green
        & "$PSScriptRoot\auto_continue.ps1"
    }
    "2" {
        Write-Host "啟動測試模式..." -ForegroundColor Yellow
        & "$PSScriptRoot\auto_continue.ps1" -DryRun
    }
    "3" {
        $minutes = Read-Host "請輸入間隔分鐘數"
        $text = Read-Host "請輸入要發送的文字（預設: 繼續）"
        
        if ([string]::IsNullOrWhiteSpace($text)) {
            $text = "繼續"
        }
        
        Write-Host "啟動自訂模式: 每 $minutes 分鐘發送 '$text'" -ForegroundColor Green
        & "$PSScriptRoot\auto_continue.ps1" -IntervalMinutes $minutes -TextToSend $text
    }
    default {
        Write-Host "無效選項，預設使用正式模式" -ForegroundColor Red
        & "$PSScriptRoot\auto_continue.ps1"
    }
}
