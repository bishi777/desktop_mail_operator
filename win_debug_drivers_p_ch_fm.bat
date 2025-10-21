@REM @echo off
@REM :loop
@REM python debug_drivers_p_ch_fm.py
@REM echo スクリプトが終了しました。再起動します...
@REM timeout /t 600
@REM goto loop

@echo off
setlocal
chcp 65001 >NUL

REM このBATのあるフォルダをカレントに
cd /d "%~dp0"

:loop
REM settings.py から pcmax_mf_port を取得
for /f "usebackq delims=" %%P in (`python -c "import settings; print(getattr(settings, 'pcmax_ch_port', ''))"`) do set "PORT=%%P"



echo [RUN] python debug_drivers_p_ch_fm.py %PORT%
python debug_drivers_p_ch_fm.py %PORT%

echo スクリプトが終了しました。再起動します...
timeout /t 600 >NUL
goto loop
