$ErrorActionPreference = "Stop"

# 1. Setup
$ErrorActionPreference = "Continue" # Don't stop on minor errors
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "[ToneSoul] Dashboard Launcher (Blind Mode)" -ForegroundColor Cyan
$CurrentDir = Get-Location
Write-Host "Working Dir: $CurrentDir" -ForegroundColor Gray

# 2. Define Python Path (Root Relative)
# Since we flattened the repo, .venv is in the same folder!
$VenvPython = ".\.venv\Scripts\python.exe"

Write-Host "Target Python: $VenvPython" -ForegroundColor Gray
Write-Host "Mode: Clean Root Structure" -ForegroundColor Green
Write-Host "Skipping specific path checks to avoid unicode issues (Blind Trust)" -ForegroundColor Yellow

# 3. Launch
$AppPath = "apps\dashboard\frontend\app.py"
Write-Host "Launching..." -ForegroundColor Green

# Invoke directly
& $VenvPython -m streamlit run $AppPath

if ($LastExitCode -ne 0) {
    Write-Host "Exit Code: $LastExitCode" -ForegroundColor Red
    Write-Host "If this failed, please manually run:"
    Write-Host "..\.venv\Scripts\python.exe -m streamlit run apps\dashboard\frontend\app.py"
    Read-Host "Press Enter to exit"
}
