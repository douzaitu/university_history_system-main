@echo off
setlocal
cd /d "%~dp0"
title Update Knowledge Graph

echo ========================================================
echo        University History System - KG Update Tool
echo ========================================================
echo.

REM --- 1. Find Virtual Environment ---
echo [1/4] Checking environment...
set "VENV_PATH="
if exist "venv\Scripts\activate.bat" (
    set "VENV_PATH=venv"
) else (
    if exist "backend\venv\Scripts\activate.bat" (
        set "VENV_PATH=backend\venv"
    )
)

if "%VENV_PATH%"=="" (
    echo.
    echo [ERROR] Virtual enviroment not found.
    pause
    exit /b 1
)

echo    Environment: %VENV_PATH%
call "%VENV_PATH%\Scripts\activate.bat"

REM --- 2. Install Dependencies ---
echo.
echo [2/4] Checking dependencies...
pip install -r backend/requirements.txt >nul 2>&1

REM --- 3. Check Ollama ---
echo.
echo [3/4] Checking AI Service (Ollama)...
where ollama >nul 2>nul
if errorlevel 1 (
    echo    [NOTE] Ollama not found. Running in basic mode.
) else (
    echo    Ollama found. Checking model...
    ollama list | findstr "qwen2:7b" >nul
    if errorlevel 1 (
        echo    Downloading qwen2:7b model...
        ollama pull qwen2:7b
    ) else (
        echo    Model ready.
    )
)

REM --- 4. Run Script ---
echo.
echo [4/4] Starting data analysis...
echo.
echo NOTE: Existing teachers in Neo4j will be SKIPPED.
echo.
pause

set PYTHONIOENCODING=utf-8
python -u reg5.py

echo.
echo Done.
pause
