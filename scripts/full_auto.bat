@echo off
setlocal
cd /d %~dp0..

if not exist .venv\Scripts\python.exe (
  echo 请先安装依赖: python -m venv .venv ^&^& pip install -r requirements.txt
  exit /b 1
)

echo [1/2] 自动生成今日方案...
.venv\Scripts\python.exe scripts\generate_daily.py
if errorlevel 1 (
  echo 生成失败，已中止推送。
  exit /b 1
)

echo [2/2] 推送草稿 + 微信通知...
.venv\Scripts\python.exe scripts\daily_run.py
endlocal
