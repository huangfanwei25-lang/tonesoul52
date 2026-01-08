$path = "C:\Users\user\Desktop\倉庫\.venv\Scripts\python.exe"
Write-Host "Testing Path: $path"
Write-Host "Exists? $(Test-Path $path)"

$rel = ".\.venv\Scripts\python.exe"
Write-Host "Testing Rel: $rel"
Write-Host "Exists? $(Test-Path $rel)"

Get-ChildItem .venv\Scripts\python.exe
