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
REM
REM ※ 自動化(ロボット)判定の回避フラグを付与している(下記 BOT_OPTS)。
REM   これで navigator.webdriver=false になり "Chromeは自動テストソフトウェア
REM   によって制御されています" バナーも消える。ただし --remote-debugging-port
REM   で起動して Selenium/CDP 接続する限り、ChromeDriver 固有の cdc_ 変数など
REM   一部の痕跡は残るため、Cloudflare Turnstile 等の強力な検知は完全には
REM   回避できない点に注意(その場合は JS 注入 stealth_setup を併用する)。

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

REM ロボット判定回避フラグ（func.py の起動オプションと整合）
REM   --disable-blink-features=AutomationControlled : navigator.webdriver を消し自動化バナーも消す(最重要)
REM   --exclude-switches=enable-automation           : "自動テストソフトウェアが制御" バナーを抑止
REM   --no-default-browser-check / --no-first-run    : 初回起動ダイアログ抑止(自動化っぽい挙動を避ける)
REM   --disable-infobars                             : 情報バー抑止
set "BOT_OPTS=--disable-blink-features=AutomationControlled --disable-features=AutomationControlled --exclude-switches=enable-automation --no-default-browser-check --no-first-run --disable-infobars"

if defined USER_AGENT (
  echo デバッグ用Chromeを起動します (port: %PORT%, UA: %UA_TAG%, bot回避: ON)
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
  echo デバッグ用Chromeを起動します (port: %PORT%, UA: 標準Windows, bot回避: ON)
  start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
    --remote-debugging-port=%PORT% ^
    --user-data-dir="%PROFILE_DIR%" ^
    %BOT_OPTS% ^
    --disable-popup-blocking ^
    --disk-cache-size=104857600 ^
    --media-cache-size=52428800
)

endlocal
