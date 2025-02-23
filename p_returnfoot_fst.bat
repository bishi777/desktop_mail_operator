@echo off
:loop
python p_returnfoot_and_fst.py
echo スクリプトが終了しました。再起動します...
timeout /t 5 >nul
goto loop
