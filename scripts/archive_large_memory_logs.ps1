param(
  [long]$MinSizeBytes = 1MB,
  [string[]]$IncludePatterns = @(
    "entropy_monitor_log*.jsonl",
    "*_scan*.jsonl",
    "*_search*.jsonl",
    "*_posts*.jsonl"
  )
)

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$memoryDir = Join-Path $repoRoot "memory"
$archiveDir = Join-Path $repoRoot ".archive\\logs\\memory"
$excludeNames = @("provenance_ledger.jsonl", "self_journal.jsonl")

if (!(Test-Path $memoryDir)) {
  Write-Error "memory/ directory not found: $memoryDir"
  exit 1
}

New-Item -ItemType Directory -Force $archiveDir | Out-Null

$files = Get-ChildItem -Path $memoryDir -File -Filter *.jsonl |
  Where-Object {
    if ($excludeNames -contains $_.Name) { return $false }
    if ($_.Length -le $MinSizeBytes) { return $false }
    foreach ($pattern in $IncludePatterns) {
      if ($_.Name -like $pattern) { return $true }
    }
    return $false
  }

if (-not $files) {
  Write-Host "No memory JSONL files over $MinSizeBytes bytes to archive."
  exit 0
}

foreach ($file in $files) {
  $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
  $destName = "{0}.{1}{2}" -f $file.BaseName, $timestamp, $file.Extension
  $destPath = Join-Path $archiveDir $destName
  Move-Item -LiteralPath $file.FullName -Destination $destPath
  Write-Host "Archived: $($file.Name) -> $destName"
}
