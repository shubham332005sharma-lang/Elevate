@echo off
setlocal
set "WT_SESSION=Elevate"
cd /d "%~dp0backend"

python manage.py migrate --noinput
if errorlevel 1 goto failed

python manage.py setup_roles
if errorlevel 1 goto failed

python manage.py check
if errorlevel 1 goto failed

echo.
echo Starting Elevate on port 8010.
echo On this computer open http://127.0.0.1:8010/
echo Keep this window open while using the website or connecting an ESP32.
echo Press Ctrl+C here when you want to stop the server.
echo.
python manage.py runserver 0.0.0.0:8010 --noreload

if errorlevel 1 goto failed
exit /b 0

:failed
echo.
echo Elevate stopped or could not start. Read the error above.
pause
exit /b 1
