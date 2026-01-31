@echo off
echo Starting University History System Server...
echo.

:: Change to the directory where this script is located
cd /d "%~dp0"

echo Activating virtual environment...
if exist "..\.venv\Scripts\activate.bat" (
    call "..\.venv\Scripts\activate.bat"
) else (
    echo Virtual environment not found at ..\.venv
    pause
    exit /b
)

echo Starting Django Server...
python manage.py runserver

pause

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