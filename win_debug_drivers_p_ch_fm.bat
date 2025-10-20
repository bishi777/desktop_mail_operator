@echo off
:loop
python debug_drivers_p_ch_fm.py
echo スクリプトが終了しました。再起動します...
timeout /t 720
goto loop