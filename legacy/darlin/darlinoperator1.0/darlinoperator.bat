@echo off
REM Darlin Operator Bridge Launcher
REM This replaces darlinoperator.exe to redirect AI requests to Ollama

echo Starting Darlin Operator Bridge (Ollama)...
cd /d "%~dp0"
python darlin_operator_bridge.py
