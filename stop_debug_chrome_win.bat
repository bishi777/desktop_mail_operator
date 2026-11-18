@echo off
chcp 65001 >nul
REM ============================================================
REM  Debug Chrome stopper (Windows)
REM  Stops only the debug Chrome started by start_debug_chrome_win.bat on
REM  the given port (your everyday Chrome is not touched).
REM  Usage: stop_debug_chrome_win.bat [PORT]
REM  Ex:    stop_debug_chrome_win.bat 9223
REM
REM  If it was started with a proxy, proxy_auth_relay.py is stopped too
REM  (the relay outlives Chrome on purpose, so it would otherwise linger).
REM
REM  Keep this file ASCII only. With chcp 65001, cmd mis-reads lines that
REM  contain multibyte characters and runs fragments of them as commands
REM  (e.g. "'me...' is not recognized as an internal or external command").
REM ============================================================

set PORT=%1
if "%PORT%"=="" set PORT=9222
set /a RELAY_PORT=10000 + %PORT%

echo Stopping debug Chrome (port: %PORT%)

powershell -NoProfile -Command "$procs = Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'chrome.exe' -and $_.CommandLine -match '--remote-debugging-port=%PORT%\b' -and $_.CommandLine -notmatch '--type=' }; if (-not $procs) { Write-Host 'No debug Chrome found on port %PORT%'; exit 0 }; foreach ($p in $procs) { Write-Host ('Sent close request to PID ' + $p.ProcessId + ' (graceful)'); taskkill /PID $p.ProcessId | Out-Null }; Start-Sleep -Seconds 5; $rest = Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'chrome.exe' -and $_.CommandLine -match '--remote-debugging-port=%PORT%\b' }; if ($rest) { Write-Host 'Still running, forcing it to stop (/F /T)'; foreach ($p in $rest) { taskkill /F /T /PID $p.ProcessId | Out-Null }; Write-Host 'Forced stop done' } else { Write-Host 'Stopped cleanly' }"

REM --- Stop the proxy auth relay as well (if running) ---
REM A venv python.exe is a launcher that starts the real interpreter as a
REM child, so one relay shows up as two processes. Killing one usually ends
REM the other, so "process not found" for the second is expected: hide it.
powershell -NoProfile -Command "$relay = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'proxy_auth_relay\.py' -and $_.CommandLine -match '--listen\s+%RELAY_PORT%\b' }; if (-not $relay) { exit 0 }; Write-Host ('[proxy] stopping relay on 127.0.0.1:%RELAY_PORT% (PID ' + (($relay | ForEach-Object { $_.ProcessId }) -join ', ') + ')'); foreach ($p in $relay) { taskkill /F /PID $p.ProcessId 2>&1 | Out-Null }"
