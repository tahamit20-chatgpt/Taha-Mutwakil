@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
title BidFit - Windows local demo

echo ============================================================
echo BidFit - synthetic demonstration on YOUR Windows computer
 echo No real AI service or paid API key is needed.
echo ============================================================
echo.
if not exist compose.local.yml goto not_extracted
if not exist .env.example goto not_extracted

echo [1/5] Checking Docker Desktop...
where docker >nul 2>&1
if errorlevel 1 goto no_docker
docker compose version >nul 2>&1
if errorlevel 1 goto old_docker
docker info >nul 2>&1
if errorlevel 1 goto docker_stopped
set "BIDFIT_DOCKER_OS="
for /f "delims=" %%P in ('docker info --format "{{.OSType}}" 2^>nul') do set "BIDFIT_DOCKER_OS=%%P"
if /i not "%BIDFIT_DOCKER_OS%"=="linux" goto windows_containers
docker compose up --help | findstr /L /C:"--wait-timeout" >nul
if errorlevel 1 goto old_docker

echo [2/5] Preparing local settings...
if exist .env goto settings_ready
copy .env.example .env >nul
if errorlevel 1 goto folder_locked
:settings_ready

echo [3/5] Building and starting the app...
echo The FIRST run downloads its files. This can take several minutes.
echo Leave this window open. Progress and any errors appear below.
echo.
docker compose --env-file .env -f compose.local.yml up --build -d --wait --wait-timeout 300
if errorlevel 1 goto startup_failed

echo.
echo [4/5] Preparing the fictional example RFQ...
docker compose --env-file .env -f compose.local.yml exec -T api python infra/seed_demo.py
if errorlevel 1 goto example_failed

set "BIDFIT_ADDRESS="
for /f "delims=" %%P in ('docker compose --env-file .env -f compose.local.yml port api 8000') do set "BIDFIT_ADDRESS=%%P"
if not defined BIDFIT_ADDRESS goto address_failed
set "BIDFIT_URL=http://%BIDFIT_ADDRESS%"
echo.
echo [5/5] Ready - opening Chrome...
echo YOUR COMPUTER'S address: %BIDFIT_URL%
echo Choose: Enter local demo as Alice (engineer).
echo Open: BidFit 2.0 - standards review required.
echo.
set "BIDFIT_CHROME="
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set "BIDFIT_CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if not defined BIDFIT_CHROME if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set "BIDFIT_CHROME=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
if not defined BIDFIT_CHROME if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" set "BIDFIT_CHROME=%LocalAppData%\Google\Chrome\Application\chrome.exe"
if not defined BIDFIT_CHROME goto no_chrome
start "" "%BIDFIT_CHROME%" "%BIDFIT_URL%"
echo You may close this black window. Keep Docker Desktop running.
echo When finished, double-click STOP_BIDFIT_WINDOWS.bat to stop the app.
pause
exit /b 0

:no_chrome
echo BidFit IS running, but Chrome was not found in its normal folders.
echo Open Chrome yourself and paste: %BIDFIT_URL%
echo Install Chrome if needed: https://www.google.com/chrome/
pause
exit /b 0

:not_extracted
echo ERROR: Project files are missing from this folder.
echo Right-click the downloaded ZIP, choose Extract All, then open
 echo the extracted folder and run START_BIDFIT_WINDOWS.bat from there.
goto help_end
:no_docker
echo ERROR: Docker Desktop was not found.
echo Install it using the official Windows instructions:
echo https://docs.docker.com/desktop/setup/install/windows-install/
echo Restart Windows if the installer requests it, then start Docker Desktop.
goto help_end
:old_docker
echo ERROR: This Docker Desktop version is missing a required feature.
echo Update Docker Desktop, then run this file again.
echo https://docs.docker.com/desktop/setup/install/windows-install/
goto help_end
:docker_stopped
echo ERROR: Docker Desktop is installed but its engine is not ready.
echo Open Docker Desktop from the Windows Start menu. Wait for Engine running.
echo If it asks for WSL or a Windows restart, follow its instructions first.
echo https://learn.microsoft.com/en-us/windows/wsl/install
goto help_end
:windows_containers
echo ERROR: Docker Desktop must use Linux containers for this app.
echo In Docker Desktop's menu choose Switch to Linux containers,
echo then wait until Docker Desktop is ready and try again.
goto help_end
:folder_locked
echo ERROR: Windows would not let BidFit create its local settings file.
echo Extract the ZIP to a normal folder in Documents or Downloads,
echo not Program Files, a restricted company folder, or inside the ZIP.
goto help_end
:startup_failed
echo.
echo ERROR: BidFit did not finish starting. It has NOT been marked ready.
echo Check the error immediately above this message.
echo - Download error: check your internet connection and try again.
echo - Port 8000 already in use: see the Windows start guide.
echo - Not enough memory or disk space: close other apps or ask IT.
echo For help, send the error text above; do not send passwords.
goto help_end
:example_failed
echo ERROR: The app started, but the example RFQ could not be prepared.
echo Run this launcher once more. If it fails again, keep the error text.
goto help_end
:address_failed
echo ERROR: The app's local address could not be found.
echo Keep this error text and ask for help; no browser address was guessed.
goto help_end
:help_end
echo.
echo Read WINDOWS-START-HERE.txt in this folder for numbered instructions.
echo No purchase or public deployment is needed by this launcher.
pause
exit /b 1
