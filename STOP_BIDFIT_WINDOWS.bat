@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
title Stop BidFit - keep your local demo data
where docker >nul 2>&1
if errorlevel 1 (
  echo Docker Desktop was not found. There is no running local app to stop here.
  pause
  exit /b 1
)
if not exist .env (
  echo This copy of BidFit has not been started yet.
  pause
  exit /b 0
)
docker compose --env-file .env -f compose.local.yml down
if errorlevel 1 (
  echo The stop command failed. Check that Docker Desktop is running.
  pause
  exit /b 1
)
echo BidFit has stopped. Your example projects and original documents are kept.
echo Start again by double-clicking START_BIDFIT_WINDOWS.bat.
pause
