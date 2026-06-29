@echo off
TITLE Unibliss Financial Dashboard
color 0B
echo ===================================================
echo    Starting Unibliss Financial Dashboard...
echo ===================================================
echo.
echo Please leave this window OPEN while using the dashboard.
echo Closing this window will shut down the application.
echo.

IF NOT EXIST "venv\Scripts\activate.bat" (
    echo [Setup] First time setup detected. Creating virtual environment...
    python -m venv venv
    echo [Setup] Installing required dependencies - this may take a minute...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) ELSE (
    call venv\Scripts\activate.bat
)

:: Start the FastAPI server in the background
echo [System] Starting server...
start /B python -m uvicorn main:app --host 127.0.0.1 --port 8000

:: Wait for the server to respond before opening the browser
echo [System] Waiting for server to be ready...
:waitloop
timeout /t 2 /nobreak > NUL
python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000')" 2>NUL && goto ready
goto waitloop

:ready
echo [System] Dashboard is running. You can now use your browser.
start http://127.0.0.1:8000

:: On shutdown, kill only the server (not other Python processes)
echo.
echo Close this window to shut down the server.

pause