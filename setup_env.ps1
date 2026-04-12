$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "[ToneSoul] Environment Setup" -ForegroundColor Cyan
Write-Host "Rebuilding virtual environment in Root..." -ForegroundColor Gray

# 1. Check Global Python (python → python3 → py launcher)
$GlobalPy = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $GlobalPy = Get-Command $cmd -ErrorAction Stop
        Write-Host "Found Global Python: $($GlobalPy.Source)" -ForegroundColor Green
        break
    }
    catch { continue }
}
if ($null -eq $GlobalPy) {
    Write-Host "[Error] No global python found! Tried: python, python3, py" -ForegroundColor Red
    Write-Host "Please install Python 3.10+ and add to PATH." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# 2. Create Venv
$VenvDir = ".\.venv"
if (Test-Path $VenvDir) {
    Write-Host "Existing .venv found. Re-using..." -ForegroundColor Yellow
}
else {
    Write-Host "Creating .venv..." -ForegroundColor Cyan
    & $GlobalPy.Name -m venv .venv
}

# 3. Verify Venv Creation
$VenvPython = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host "[Error] Failed to create .venv!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# 4. Install Dependencies
Write-Host "Installing Dependencies..." -ForegroundColor Cyan
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r requirements.txt
& $VenvPython -m pip install streamlit plotly pandas psutil requests

Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "You can now run: .\start_dashboard.bat" -ForegroundColor Cyan
Read-Host "Press Enter to exit"
