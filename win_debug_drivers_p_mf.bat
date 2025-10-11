@echo off
:loop
python debug_drivers_p_mf.py
echo スクリプトが終了しました。再起動します...
timeout /t 60
goto loop