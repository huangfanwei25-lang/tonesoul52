@echo off
setlocal
cd /d %~dp0

if not exist "tonesoul_simple_app.py" (
  echo This launcher must stay next to tonesoul_simple_app.py.
  echo Please run it from the repo folder or create a shortcut to this file.
  pause
  exit /b 1
)

where python >nul 2>nul
if %errorlevel%==0 (
  python -u tonesoul_simple_app.py
  goto :eof
)

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 -u tonesoul_simple_app.py
  goto :eof
)

echo Python not found. Please install Python or add it to PATH.
echo You can also run: py -3 -u tonesoul_simple_app.py
