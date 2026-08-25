@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
REM ============================================================
REM  デバッグ用Chrome起動スクリプト (Windows版)
REM  使い方: start_debug_chrome_win.bat [ポート番号] [UAプリセット]
REM  例:     start_debug_chrome_win.bat 9222 iphone14
REM          start_debug_chrome_win.bat 9222 mac
REM
REM  UAプリセット (第2引数):
REM    iphone14 (デフォルト) : iPhone14 相当のUA
REM    mac                   : UA上書きなし (Chrome標準のWindows UA)
REM
REM  PCMAX は UA とログインセッションを紐付けているため、ログイン後にUAを
REM  変えるとセッションが切れる。UAごとに別プロファイルを使い、その UA の
REM  ままログインすること。プロファイルは DebugProfile_(port)_(uaタグ)。
REM
REM  自動化(ロボット)判定の回避:
REM    1) --disable-blink-features=AutomationControlled で
REM       navigator.webdriver=false になり自動化バナーも消える(bat側の唯一の実効フラグ)
REM    2) 起動前に patch_chromedriver_cdc.py を実行し、chromedriver の
REM       cdc_ 痕跡を除去する(Chromeが更新されても起動のたびに再パッチされる)
REM ============================================================

set PORT=%1
if "%PORT%"=="" set PORT=9222
set UA_PRESET=%2
if "%UA_PRESET%"=="" set UA_PRESET=iphone14

REM このバッチのあるディレクトリ(末尾に \ が付く)
set "SCRIPT_DIR=%~dp0"

REM --- cdc_ パッチを起動前に実行(Chrome更新で新ドライバが来ても毎回パッチ) ---
REM venv の python を優先。無ければ system の python にフォールバック
set "PYEXE=%SCRIPT_DIR%myenv\Scripts\python.exe"
if not exist "%PYEXE%" set "PYEXE=python"
echo [cdc_パッチ] chromedriver をパッチします...
"%PYEXE%" "%SCRIPT_DIR%patch_chromedriver_cdc.py"

REM iPhone14 相当UA (widget/jmail.py, happymail.py と同一文字列で統一)
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

REM ロボット判定回避フラグ (bat の起動フラグとして実効性があるものだけ)
REM   --disable-blink-features=AutomationControlled : navigator.webdriver を消し自動化バナーも消す
REM   ※ --exclude-switches=enable-automation は ChromeDriver 専用オプションで
REM     bat の生フラグとしては無効なため使わない(以前これがエラーの原因だった)
set "BOT_OPTS=--disable-blink-features=AutomationControlled"

if defined USER_AGENT (
  echo デバッグ用Chromeを起動します ^(port: %PORT%, UA: %UA_TAG%, bot回避: ON^)
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
  echo デバッグ用Chromeを起動します ^(port: %PORT%, UA: 標準Windows, bot回避: ON^)
  start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
    --remote-debugging-port=%PORT% ^
    --user-data-dir="%PROFILE_DIR%" ^
    %BOT_OPTS% ^
    --disable-popup-blocking ^
    --disk-cache-size=104857600 ^
    --media-cache-size=52428800
)

endlocal
