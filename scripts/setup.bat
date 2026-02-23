@echo off
REM =============================================================================
REM DML Stream - Setup Script (Windows)
REM =============================================================================
REM Developed by DML Labs
REM Lead Engineer: @devmayank-official
REM =============================================================================

echo ========================================
echo DML Stream - Setup Script
echo ========================================
echo.

REM Check Python version
echo Checking Python version...
python --version > nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python %PYTHON_VERSION% found
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    exit /b 1
)
echo Virtual environment created
echo.

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo pip upgraded
echo.

REM Install dependencies
echo Installing dependencies...
pip install -e .[dev,docs]
if errorlevel 1 (
    echo Error: Failed to install dependencies
    exit /b 1
)
echo Dependencies installed
echo.

REM Install pre-commit hooks
echo Installing pre-commit hooks...
pre-commit install
echo Pre-commit hooks installed
echo.

REM Check FFmpeg
echo Checking FFmpeg...
where ffmpeg > nul 2>&1
if errorlevel 1 (
    echo FFmpeg not found. Install FFmpeg for format conversion:
    echo   choco install ffmpeg
    echo   or scoop install ffmpeg
) else (
    for /f "tokens=*" %%i in ('ffmpeg -version 2^>^&1 ^| findstr /C:"ffmpeg version"') do set FFMPEG_VERSION=%%i
    echo FFmpeg found: %FFMPEG_VERSION%
)
echo.

REM Run tests
echo Running tests...
pytest tests/unit -v --tb=short
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To activate the virtual environment, run:
echo   .venv\Scripts\activate
echo.
echo To start the application:
echo   dml-stream interactive
echo   OR
echo   dmls interactive
echo.
echo To run tests:
echo   pytest
echo.
echo To run linters:
echo   pre-commit run --all-files
echo.

pause
