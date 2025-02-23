@echo off
:loop
python check_mail.py
if %ERRORLEVEL% NEQ 0 (
    echo スクリプトがエラーで終了しました。エラーログを記録します...
    echo %DATE% %TIME% - スクリプトがエラーで終了しました。 >> error_log.txt
)
echo スクリプトが終了しました。再起動します...
choice /t 180 /d y /n >nul
goto loop