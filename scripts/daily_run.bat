@echo off
setlocal
cd /d %~dp0..
.venv\Scripts\python.exe scripts\daily_run.py
endlocal
