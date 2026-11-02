@echo off
chcp 65001 >nul
REM デバッグ用Chrome終了スクリプト (Windows版)
REM start_debug_chrome_win.bat で起動したポート指定のChromeだけを安全に終了する
REM (普段使いのChromeには影響しない)
REM 使い方: stop_debug_chrome_win.bat [ポート番号]
REM 例: stop_debug_chrome_win.bat 9223
REM
REM プロキシ付きで起動していた場合は proxy_auth_relay.py も一緒に終了する
REM (中継は Chrome より長生きさせているため、放置するとプロセスが残る)

set PORT=%1
if "%PORT%"=="" set PORT=9222
set /a RELAY_PORT=10000 + %PORT%

echo デバッグ用Chromeを終了します (port: %PORT%)

powershell -NoProfile -Command "$procs = Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'chrome.exe' -and $_.CommandLine -match '--remote-debugging-port=%PORT%\b' -and $_.CommandLine -notmatch '--type=' }; if (-not $procs) { Write-Host 'port %PORT% のデバッグ用Chromeは見つかりません'; exit 0 }; foreach ($p in $procs) { Write-Host ('PID ' + $p.ProcessId + ' へ終了要求を送信 (graceful)'); taskkill /PID $p.ProcessId | Out-Null }; Start-Sleep -Seconds 5; $rest = Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'chrome.exe' -and $_.CommandLine -match '--remote-debugging-port=%PORT%\b' }; if ($rest) { Write-Host '終了しないため強制終了します (/F /T)'; foreach ($p in $rest) { taskkill /F /T /PID $p.ProcessId | Out-Null }; Write-Host '強制終了しました' } else { Write-Host '正常に終了しました' }"

REM --- プロキシ認証中継も終了する (起動していれば) ---
powershell -NoProfile -Command "$relay = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'proxy_auth_relay\.py' -and $_.CommandLine -match '--listen\s+%RELAY_PORT%\b' }; if (-not $relay) { exit 0 }; foreach ($p in $relay) { Write-Host ('[proxy] 中継を終了します PID ' + $p.ProcessId + ' (127.0.0.1:%RELAY_PORT%)'); taskkill /F /PID $p.ProcessId | Out-Null }"
