@echo off
echo Starting University History System Server...
echo.

:: Change to correct directory if needed
cd /d "E:\Projects\SchoolHistory\university_history_system\backend"

echo Activating virtual environment...
call ..\venv\Scripts\activate.bat

if errorlevel 1 (
    echo ERROR: Cannot activate virtual environment
    echo Please check the virtual environment path
    pause
    exit /b 1
)

echo Virtual environment activated successfully
echo Starting Django development server...
echo Server will be available at: http://127.0.0.1:8000/
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver

echo.
echo Server has been stopped
pause