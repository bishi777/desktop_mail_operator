@echo off
chcp 65001 >nul
REM デバッグ用Chrome起動スクリプト (Windows版)
REM 使い方: start_debug_chrome_win.bat [ポート番号]
REM 例: start_debug_chrome_win.bat 9222

set PORT=%1
if "%PORT%"=="" set PORT=9222

echo デバッグ用Chromeを起動します (port: %PORT%)

start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
  --remote-debugging-port=%PORT% ^
  --user-data-dir="%USERPROFILE%\AppData\Local\Google\Chrome\DebugProfile_%PORT%" ^
  --disable-popup-blocking
