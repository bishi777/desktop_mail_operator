@echo off
:loop
python h_ch_ma_rf_mf.py
echo スクリプトが終了しました。再起動します...
timeout /t 600
goto loop