param(
    [int]$Port = 8765,
    [string]$Root = ""
)

if (-not $Root) {
    $Root = (Resolve-Path (Join-Path $PSScriptRoot "..\\..")).Path
}

$env:TS_WEB_SEARCH_ENDPOINT = "http://127.0.0.1:$Port/search"
$env:TS_WEB_SEARCH_ROOT = $Root

Write-Host "Starting local search server..."
Write-Host "Root: $Root"
Write-Host "Endpoint: $env:TS_WEB_SEARCH_ENDPOINT"

python scripts/local_search_server.py --root $Root --port $Port
