@echo off
setlocal enabledelayedexpansion
REM ============================================================
REM  Debug Chrome launcher (Windows)
REM  Usage: start_debug_chrome_win.bat [PORT] [UA_PRESET]
REM  Ex:    start_debug_chrome_win.bat 9222 iphone14
REM         start_debug_chrome_win.bat 9222 mac
REM
REM  UA_PRESET (2nd arg):
REM    iphone14 (default) : iPhone14-like UA
REM    mac                : no UA override (default Windows UA)
REM
REM  PCMAX ties the UA to the login session, so changing UA after
REM  login drops the session. Use a separate profile per UA and log in
REM  with that UA. Profile dir: DebugProfile_(port)_(uatag).
REM
REM  Anti-bot detection:
REM    1) --disable-blink-features=AutomationControlled makes
REM       navigator.webdriver=false and hides the automation banner
REM       (the only effective flag on the bat side).
REM    2) Runs patch_chromedriver_cdc.py before launch to strip the
REM       cdc_ fingerprint from chromedriver (re-applied every launch,
REM       so a Chrome update that pulls a new driver stays covered).
REM ============================================================

set PORT=%1
if "%PORT%"=="" set PORT=9222
set UA_PRESET=%2
if "%UA_PRESET%"=="" set UA_PRESET=iphone14

REM Directory of this bat (trailing backslash included)
set "SCRIPT_DIR=%~dp0"

REM --- cdc_ patch before launch (covers Chrome updates + direct python runs) ---
set "PYEXE=%SCRIPT_DIR%myenv\Scripts\python.exe"
if not exist "%PYEXE%" set "PYEXE=python"
echo [cdc_ patch] patching chromedriver ...
"%PYEXE%" "%SCRIPT_DIR%patch_chromedriver_cdc.py"

REM iPhone14-like UA (same string as widget/jmail.py and happymail.py)
set "IPHONE14_UA=Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/537.36"

REM Resolve UA preset
if /i "%UA_PRESET%"=="iphone14" (
  set "USER_AGENT=%IPHONE14_UA%"
  set "UA_TAG=iphone14"
) else if /i "%UA_PRESET%"=="mac" (
  set "USER_AGENT="
  set "UA_TAG=mac"
) else (
  set "USER_AGENT=%UA_PRESET%"
  set "UA_TAG=custom"
)

set "PROFILE_DIR=%USERPROFILE%\AppData\Local\Google\Chrome\DebugProfile_%PORT%_%UA_TAG%"

REM Anti-bot flag that actually works as a bat launch flag.
REM --disable-blink-features=AutomationControlled : hides webdriver + banner
REM Note: --exclude-switches=enable-automation is a ChromeDriver-only option,
REM   invalid as a raw bat flag (it previously caused the launch error).
set "BOT_OPTS=--disable-blink-features=AutomationControlled"

if defined USER_AGENT (
  echo Launching debug Chrome (port: %PORT%, UA: %UA_TAG%, anti-bot: ON)
  echo   UA: !USER_AGENT!
  start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
    --remote-debugging-port=%PORT% ^
    --user-data-dir="%PROFILE_DIR%" ^
    --user-agent="!USER_AGENT!" ^
    %BOT_OPTS% ^
    --disable-popup-blocking ^
    --disk-cache-size=104857600 ^
    --media-cache-size=52428800
) else (
  echo Launching debug Chrome (port: %PORT%, UA: default Windows, anti-bot: ON)
  start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
    --remote-debugging-port=%PORT% ^
    --user-data-dir="%PROFILE_DIR%" ^
    %BOT_OPTS% ^
    --disable-popup-blocking ^
    --disk-cache-size=104857600 ^
    --media-cache-size=52428800
)

endlocal
