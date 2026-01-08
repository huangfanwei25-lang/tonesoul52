@echo off
setlocal

set SCRIPT=%~dp0darlin_bridge.ps1
if not exist "%SCRIPT%" (
  echo Missing script: %SCRIPT%
  exit /b 1
)

powershell -ExecutionPolicy Bypass -File "%SCRIPT%" %*
