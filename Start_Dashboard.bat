@echo off
TITLE Kareena Financial Dashboard
color 0B
echo ===================================================
echo    Starting Kareena Financial Dashboard...
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

timeout /t 2 /nobreak > NUL
start http://127.0.0.1:8000

:: Start the FastAPI server
echo [System] Dashboard is running. You can now use your browser.
python -m uvicorn main:app --host 127.0.0.1 --port 8000

pause