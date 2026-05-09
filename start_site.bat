@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  start "Logoped Assistant" py server.py
  timeout /t 2 >nul
  start http://127.0.0.1:8000/
  exit /b
)

where python >nul 2>nul
if %errorlevel%==0 (
  start "Logoped Assistant" python server.py
  timeout /t 2 >nul
  start http://127.0.0.1:8000/
  exit /b
)

echo Python табылмады.
echo ИИ сұрақтары жұмыс істеуі үшін Python орнату керек немесе сайтты .exe/онлайн backend ретінде жинау керек.
pause
