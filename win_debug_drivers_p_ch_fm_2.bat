@echo off
:loop
python debug_drivers_p_ch_fm_2.py
echo スクリプトが終了しました。再起動します...
timeout /t 600
goto loop