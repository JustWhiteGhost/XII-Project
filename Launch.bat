@echo off
REM ========================================
REM Fog-Shrouded Chronicles - Launcher
REM ========================================

title Fog-Shrouded Chronicles

echo.
echo ======================================
echo   FOG-SHROUDED CHRONICLES
echo   AI-Powered Virtual D&D
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Check if setup has been run
if not exist "config.json" (
    echo First time setup required...
    echo.
    echo Running setup script...
    echo.
    python setup.py
    echo.
    echo Setup complete! Please run this launcher again.
    pause
    exit /b 0
)

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import pandas, groq, sentence_transformers, networkx" >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Some dependencies are missing!
    echo.
    echo Would you like to run setup now? (Y/N)
    set /p choice="> "
    
    if /i "%choice%"=="Y" (
        echo.
        echo Running setup...
        python setup.py
        pause
        exit /b 0
    ) else (
        echo.
        echo Cannot start game without dependencies.
        pause
        exit /b 1
    )
)

echo Dependencies OK
echo.

REM Check API key
findstr /C:"YOUR_API_KEY_HERE" config.json >nul 2>&1
if not errorlevel 1 (
    echo.
    echo ========================================
    echo WARNING: API Key Not Configured!
    echo ========================================
    echo.
    echo Please edit config.json and add your Groq API key
    echo Get a free key at: https://console.groq.com/
    echo.
    pause
    exit /b 1
)

REM All checks passed - launch game
echo Starting game...
echo.
echo ======================================
echo.

python Main.py

echo.
echo ======================================
echo Game closed
echo ======================================
echo.
pause