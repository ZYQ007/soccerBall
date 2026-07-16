@echo off
setlocal
cd /d %~dp0..

if not exist .venv\Scripts\python.exe (
  echo 请先执行: python -m venv .venv
  echo 然后执行: .venv\Scripts\activate ^&^& pip install -r requirements.txt
  exit /b 1
)

if "%~1"=="" (
  echo 用法: publish.bat articles\2026-07-16.json
  exit /b 1
)

.venv\Scripts\python.exe scripts\publish.py --file %1
endlocal
