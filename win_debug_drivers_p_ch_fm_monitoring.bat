@echo off
chcp 65001 >nul
REM debug_drivers_p_ch_fm.py を無限リスタートで回す監視スクリプト (Windows)
REM 使い方: debug_drivers_p_ch_fm_monitoring.bat [ポート番号] [再起動間隔秒]
REM 例:     debug_drivers_p_ch_fm_monitoring.bat 9223
REM 例:     debug_drivers_p_ch_fm_monitoring.bat 9224 300

set PORT=%1
if "%PORT%"=="" set PORT=9223

set SLEEP_SEC=%2
if "%SLEEP_SEC%"=="" set SLEEP_SEC=600

echo =======================================
echo  debug_drivers_p_ch_fm 監視スクリプト起動
echo  port      : %PORT%
echo  restart間隔 : %SLEEP_SEC% 秒
echo =======================================

:loop
python debug_drivers_p_ch_fm.py %PORT%
echo スクリプトが終了しました。%SLEEP_SEC%秒後に再起動します...
timeout /t %SLEEP_SEC% /nobreak >nul
goto loop
