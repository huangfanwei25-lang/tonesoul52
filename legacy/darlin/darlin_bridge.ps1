param(
    [ValidateSet("start", "stop", "status", "restart")]
    [string]$Action = "start",
    [string]$PersonaId = "darlin",
    [switch]$DisableToneSoul,
    [string]$SystemPromptPath
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$promptInfo = Get-ChildItem -LiteralPath $root -Filter "darlin_system_prompt.txt" -File -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $promptInfo) {
    foreach ($dir in (Get-ChildItem -LiteralPath $root -Directory -ErrorAction SilentlyContinue)) {
        $promptCandidate = Join-Path $dir.FullName "darlin_system_prompt.txt"
        if (Test-Path $promptCandidate) {
            $promptInfo = Get-Item $promptCandidate -ErrorAction SilentlyContinue
            break
        }
    }
}

if ($promptInfo) {
    $bridgeDir = Split-Path -Parent $promptInfo.FullName
    $bridgeCandidate = Join-Path $bridgeDir "darlin_operator_bridge.py"
    if (Test-Path $bridgeCandidate) {
        $bridgeScriptInfo = Get-Item $bridgeCandidate -ErrorAction SilentlyContinue
    }
}

if (-not $bridgeScriptInfo) {
    $bridgeScriptInfo = Get-ChildItem -LiteralPath $root -Filter "darlin_operator_bridge.py" -File -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $bridgeScriptInfo) {
        foreach ($dir in (Get-ChildItem -LiteralPath $root -Directory -ErrorAction SilentlyContinue)) {
            $candidate = Join-Path $dir.FullName "darlin_operator_bridge.py"
            if (Test-Path $candidate) {
                $bridgeScriptInfo = Get-Item $candidate -ErrorAction SilentlyContinue
                break
            }
        }
    }
}
if ($bridgeScriptInfo) {
    $bridgeScript = $bridgeScriptInfo.FullName
    $bridgeDir = Split-Path -Parent $bridgeScript
    $pidFile = Join-Path $bridgeDir "darlin_operator_bridge.pid"
    $outLog = Join-Path $bridgeDir "darlin_operator_bridge.out.log"
    $errLog = Join-Path $bridgeDir "darlin_operator_bridge.err.log"
    $defaultPrompt = Join-Path $bridgeDir "darlin_system_prompt.txt"
    if (-not $SystemPromptPath -and (Test-Path $defaultPrompt)) {
        $SystemPromptPath = $defaultPrompt
    }
} else {
    $bridgeScript = $null
    $bridgeDir = $null
    $pidFile = Join-Path $root "darlin_operator_bridge.pid"
    $outLog = Join-Path $root "darlin_operator_bridge.out.log"
    $errLog = Join-Path $root "darlin_operator_bridge.err.log"
    $defaultPrompt = $null
}

function Get-PythonCommand {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) { return $python.Source }
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) { return $py.Source }
    return $null
}

function Get-BridgeProcess {
    if (-not (Test-Path $pidFile)) { return $null }
    $procId = (Get-Content $pidFile -ErrorAction SilentlyContinue | Select-Object -First 1)
    if (-not $procId) { return $null }
    return Get-Process -Id $procId -ErrorAction SilentlyContinue
}

function Start-Bridge {
    if (-not $bridgeScript -or -not (Test-Path $bridgeScript)) {
        Write-Host "Bridge script not found. Ensure darlin_operator_bridge.py exists under the workspace."
        return
    }

    $existing = Get-BridgeProcess
    if ($existing) {
        Write-Host "Bridge already running (PID $($existing.Id))."
        return
    }

    $python = Get-PythonCommand
    if (-not $python) {
        Write-Host "Python not found. Install Python or ensure it is on PATH."
        return
    }

    if ($DisableToneSoul) {
        $env:TONESOUL_ENABLE = "0"
    } else {
        $env:TONESOUL_ENABLE = "1"
    }
    if ($PersonaId) {
        $env:TONESOUL_PERSONA_ID = $PersonaId
    }
    if ($SystemPromptPath -and (Test-Path $SystemPromptPath)) {
        $env:DARLIN_SYSTEM_PROMPT = Get-Content -Raw -Encoding UTF8 $SystemPromptPath
    }

    $proc = Start-Process -FilePath $python `
        -ArgumentList @("-u", $bridgeScript) `
        -WorkingDirectory $root `
        -RedirectStandardOutput $outLog `
        -RedirectStandardError $errLog `
        -PassThru `
        -WindowStyle Hidden

    $proc.Id | Set-Content -Encoding ASCII $pidFile
    Write-Host "Bridge started (PID $($proc.Id))."
    Write-Host "Logs: $outLog"
}

function Stop-Bridge {
    $proc = Get-BridgeProcess
    if (-not $proc) {
        Write-Host "Bridge not running."
        if (Test-Path $pidFile) { Remove-Item $pidFile -Force }
        return
    }

    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    if (Test-Path $pidFile) { Remove-Item $pidFile -Force }
    Write-Host "Bridge stopped."
}

function Show-Status {
    $proc = Get-BridgeProcess
    if ($proc) {
        Write-Host "Bridge running (PID $($proc.Id))."
    } else {
        Write-Host "Bridge not running."
    }
    Write-Host "Logs: $outLog"
}

switch ($Action) {
    "start" { Start-Bridge }
    "stop" { Stop-Bridge }
    "status" { Show-Status }
    "restart" { Stop-Bridge; Start-Bridge }
}
