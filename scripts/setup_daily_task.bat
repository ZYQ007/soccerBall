@echo off
setlocal
cd /d %~dp0..

if "%~1"=="" (
  echo 用法: setup_daily_task.bat HH:MM
  echo 示例: setup_daily_task.bat 14:30
  exit /b 1
)

set TASK_TIME=%~1
set TASK_NAME=SoccerBallDailyRun

schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>nul
schtasks /Delete /TN "SoccerBallWechatPublish" /F >nul 2>nul

schtasks /Create ^
  /SC DAILY ^
  /TN "%TASK_NAME%" ^
  /TR "\"%CD%\\scripts\\full_auto.bat\"" ^
  /ST %TASK_TIME% ^
  /F

if errorlevel 1 (
  echo 创建计划任务失败，请以管理员身份运行终端重试。
  exit /b 1
)

echo 已创建计划任务: %TASK_NAME%
echo 执行时间: %TASK_TIME%
echo 任务内容: 自动生成方案 + 推草稿 + 微信推送
echo.
echo 请确保 .env 已配置:
echo   PUSHPLUS_TOKEN  (微信推送)
echo   LLM_API_KEY     (自动生成分析)
endlocal
