@echo off
setlocal enabledelayedexpansion
REM ============================================================
REM  Debug Chrome launcher (Windows)
REM  Usage: start_debug_chrome_win.bat [PORT] [UA_PRESET] [PROXY_KEY]
REM  Ex:    start_debug_chrome_win.bat 9222
REM         start_debug_chrome_win.bat 9222 iphone14
REM         start_debug_chrome_win.bat 9222 none erika
REM         start_debug_chrome_win.bat 9222 iphone14 erika
REM
REM  UA_PRESET (2nd arg):
REM    none (default)     : no UA override (default Chrome/Windows UA)
REM    iphone14           : iPhone14-like UA
REM    mac                : same as none (no UA override)
REM    anything else      : used verbatim as the UA string
REM
REM  PROXY_KEY (3rd arg):
REM    A key of JPROXY_PROXYS in settings.py (e.g. erika).
REM    Omit it to connect directly (no proxy).
REM    Chrome's --proxy-server cannot take user:pass in the URL (it pops an
REM    auth dialog), so proxy_auth_relay.py is started locally to handle the
REM    auth and Chrome is pointed at 127.0.0.1:<relay port> instead.
REM    Relay port is 10000+PORT (e.g. 9222 -> 19222).
REM
REM  NOTE: argument order differs between platforms.
REM    Windows: [PORT] [UA_PRESET] [PROXY_KEY]   <- proxy is the 3rd arg
REM    macOS  : [PORT] [PROXY_KEY]               <- proxy is the 2nd arg
REM    The Windows script keeps UA as the 2nd arg so existing commands
REM    (e.g. "9222 iphone14") keep working.
REM
REM  --proxy-server applies to the whole Chrome process, so IPs cannot be
REM  split per tab. To use a different IP per character, launch a separate
REM  port per character:
REM    start_debug_chrome_win.bat 9222 none erika
REM    start_debug_chrome_win.bat 9223 none sui
REM
REM  PCMAX ties the UA (and the IP) to the login session, so changing them
REM  after login drops the session. Use a separate profile per UA/proxy and
REM  log in with that combination.
REM  Profile dir: DebugProfile_(port)_(uatag)            when no proxy
REM               DebugProfile_(port)_(uatag)_(proxytag) when a proxy is set
REM  (the no-proxy name is kept as-is so existing sessions stay usable)
REM
REM  Anti-bot detection:
REM    1) Runs patch_chromedriver_cdc.py before launch to strip the
REM       cdc_ fingerprint from chromedriver (re-applied every launch).
REM
REM  2026-09-28: removed --disable-blink-features=AutomationControlled.
REM    Verified on Chrome 153: navigator.webdriver is false with or without
REM    the flag, so it no longer does anything (Chrome itself warns that it
REM    is an unsupported flag). Worse, the warning bar it triggers widened
REM    outerHeight-innerHeight from 87px to 143px, which is itself a
REM    detectable signal.
REM ============================================================

set PORT=%1
if "%PORT%"=="" set PORT=9222
set UA_PRESET=%2
if "%UA_PRESET%"=="" set UA_PRESET=none
set PROXY_KEY=%3

REM Directory of this bat (trailing backslash included)
set "SCRIPT_DIR=%~dp0"

REM --- cdc_ patch before launch (covers Chrome updates + direct python runs) ---
set "PYEXE=%SCRIPT_DIR%myenv\Scripts\python.exe"
if not exist "%PYEXE%" set "PYEXE=python"
echo [cdc_ patch] patching chromedriver ...
"%PYEXE%" "%SCRIPT_DIR%patch_chromedriver_cdc.py"

REM iPhone14-like UA (same string as widget/jmail.py and happymail.py)
set "IPHONE14_UA=Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/537.36"

REM Resolve UA preset (goto labels avoid the if() block breaking on UA parens)
if /i "%UA_PRESET%"=="none" goto ua_none
if /i "%UA_PRESET%"=="mac" goto ua_none
if /i "%UA_PRESET%"=="iphone14" goto ua_iphone14
REM custom: use the 2nd arg verbatim as UA
set "USER_AGENT=%UA_PRESET%"
set "UA_TAG=custom"
goto ua_done

:ua_none
REM no UA override (default Chrome/Windows UA)
set "USER_AGENT="
set "UA_TAG=none"
goto ua_done

:ua_iphone14
set "USER_AGENT=%IPHONE14_UA%"
set "UA_TAG=iphone14"
goto ua_done

:ua_done

REM --- Resolve proxy settings -------------------------------------------
REM PROXY_OPTS stays empty when no proxy key is given.
set "PROXY_OPTS="
set "PROFILE_SUFFIX="
if "%PROXY_KEY%"=="" goto proxy_done

set /a RELAY_PORT=10000 + %PORT%
set "PROFILE_SUFFIX=_%PROXY_KEY%"

if not exist "%SCRIPT_DIR%proxy_auth_relay.py" (
  echo ERROR: proxy_auth_relay.py not found in %SCRIPT_DIR%
  goto end
)

REM Reuse the relay if it is already listening on the same port.
REM Get-NetTCPConnection is not on every edition, so fall back to a TCP connect.
set "RELAY_UP="
for /f %%L in ('powershell -NoProfile -Command "$p=%RELAY_PORT%; $up=$false; try { $up=[bool](Get-NetTCPConnection -State Listen -LocalPort $p -ErrorAction Stop) } catch { try { $c=New-Object Net.Sockets.TcpClient; $c.Connect('127.0.0.1',$p); $up=$c.Connected; $c.Close() } catch { $up=$false } }; if($up){'up'}else{'down'}"') do set "RELAY_UP=%%L"
if /i "%RELAY_UP%"=="up" (
  echo [proxy] relay already running on 127.0.0.1:%RELAY_PORT%
  goto proxy_flags
)

if not exist "%SCRIPT_DIR%logs" mkdir "%SCRIPT_DIR%logs"
set "RELAY_LOG=%SCRIPT_DIR%logs\proxy_relay_%PORT%.log"
echo [proxy] starting auth relay for '%PROXY_KEY%' on 127.0.0.1:%RELAY_PORT%
REM Start detached so the relay outlives this bat (and Chrome)
start "proxy_relay_%PORT%" /b "%PYEXE%" "%SCRIPT_DIR%proxy_auth_relay.py" --key %PROXY_KEY% --listen %RELAY_PORT% >>"%RELAY_LOG%" 2>&1

REM Wait up to ~8s for the relay to start listening.
REM The retry loop lives inside PowerShell: a bat "for /l" cannot read a
REM variable it set in the same iteration (delayed expansion still resolves
REM once per block), and spawning PowerShell 25 times is slow anyway.
REM Fall back to a TCP connect test when Get-NetTCPConnection is unavailable.
set "RELAY_UP="
for /f %%L in ('powershell -NoProfile -Command "$p=%RELAY_PORT%; for($i=0;$i -lt 40;$i++){ $up=$false; try { $up=[bool](Get-NetTCPConnection -State Listen -LocalPort $p -ErrorAction Stop) } catch { try { $c=New-Object Net.Sockets.TcpClient; $c.Connect('127.0.0.1',$p); $up=$c.Connected; $c.Close() } catch { $up=$false } }; if($up){ 'up'; exit }; Start-Sleep -Milliseconds 200 }; 'down'"') do set "RELAY_UP=%%L"
if /i "%RELAY_UP%"=="up" goto proxy_flags

echo ERROR: relay failed to start. See the log: %RELAY_LOG%
powershell -NoProfile -Command "if (Test-Path '%RELAY_LOG%') { Get-Content '%RELAY_LOG%' -Tail 20 }"
goto end

:proxy_flags
REM Excluding loopback keeps remote-debugging off the relay (more stable)
set "PROXY_OPTS=--proxy-server=127.0.0.1:%RELAY_PORT% --proxy-bypass-list=<-loopback>"

:proxy_done

REM Do not launch twice on the same port
for /f %%S in ('powershell -NoProfile -Command "try { $null = Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 'http://localhost:%PORT%/json/version'; 'up' } catch { 'down' }"') do set "ALREADY=%%S"
if "%ALREADY%"=="up" (
  echo debug Chrome on port %PORT% is already running
  goto end
)

REM Profiles are split per UA and per proxy so IP/session pairs stay intact.
REM Without a proxy the name is unchanged, so existing logins keep working.
set "PROFILE_DIR=%USERPROFILE%\AppData\Local\Google\Chrome\DebugProfile_%PORT%_%UA_TAG%%PROFILE_SUFFIX%"

REM Note: --exclude-switches=enable-automation is a ChromeDriver-only option,
REM   invalid as a raw bat flag.

REM Label for the log line (goto instead of if() to dodge paren issues)
set "PROXY_LABEL=%PROXY_KEY%"
if "%PROXY_KEY%"=="" set "PROXY_LABEL=noproxy"

REM Branch by whether a UA override is set (goto avoids if() paren issues)
if defined USER_AGENT goto launch_ua
goto launch_no_ua

:launch_ua
echo Launching debug Chrome port %PORT% UA %UA_TAG% proxy !PROXY_LABEL!
echo   UA: !USER_AGENT!
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
  --remote-debugging-port=%PORT% ^
  --user-data-dir="%PROFILE_DIR%" ^
  --user-agent="!USER_AGENT!" ^
  !PROXY_OPTS! ^
  --disable-popup-blocking ^
  --disk-cache-size=104857600 ^
  --media-cache-size=52428800
goto end

:launch_no_ua
echo Launching debug Chrome port %PORT% UA default-Windows proxy !PROXY_LABEL!
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
  --remote-debugging-port=%PORT% ^
  --user-data-dir="%PROFILE_DIR%" ^
  !PROXY_OPTS! ^
  --disable-popup-blocking ^
  --disk-cache-size=104857600 ^
  --media-cache-size=52428800
goto end

:end
endlocal
