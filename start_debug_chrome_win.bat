@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
REM デバッグ用Chrome起動スクリプト (Windows版)
REM 使い方: start_debug_chrome_win.bat [ポート番号] [UAプリセット]
REM 例:     start_debug_chrome_win.bat 9222 iphone14
REM         start_debug_chrome_win.bat 9222 mac
REM
REM UAプリセット (第2引数):
REM   iphone14 (デフォルト) → iPhone14 相当のUA
REM   mac                   → UA上書きなし (Chrome標準のWindows UA)
REM
REM ※ PCMAX は UA とログインセッションを紐付けているため、ログイン後にUAを
REM   変えるとセッションが切れる。UAごとに別プロファイルを使い、その UA の
REM   ままログインすること。プロファイルは DebugProfile_<port>_<uaタグ>。

set PORT=%1
if "%PORT%"=="" set PORT=9222
set UA_PRESET=%2
if "%UA_PRESET%"=="" set UA_PRESET=iphone14

REM iPhone14 相当UA（widget/jmail.py・happymail.py と同一文字列で統一）
set "IPHONE14_UA=Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/537.36"

REM UAプリセットを解決
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

if defined USER_AGENT (
  echo デバッグ用Chromeを起動します (port: %PORT%, UA: %UA_TAG%)
  echo   UA: !USER_AGENT!
  start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
    --remote-debugging-port=%PORT% ^
    --user-data-dir="%PROFILE_DIR%" ^
    --user-agent="!USER_AGENT!" ^
    --disable-popup-blocking ^
    --disk-cache-size=104857600 ^
    --media-cache-size=52428800
) else (
  echo デバッグ用Chromeを起動します (port: %PORT%, UA: 標準Windows)
  start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
    --remote-debugging-port=%PORT% ^
    --user-data-dir="%PROFILE_DIR%" ^
    --disable-popup-blocking ^
    --disk-cache-size=104857600 ^
    --media-cache-size=52428800
)

endlocal
