@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "start_dashboard.ps1"
pause
