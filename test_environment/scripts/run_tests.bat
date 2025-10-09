@echo off
echo =============================================
echo   Resume Screener Test Environment
echo =============================================

cd /d "%~dp0\.."

echo.
echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo =============================================
echo   Running Backend Tests
echo =============================================
echo.

python scripts\run_backend_tests.py

echo.
echo =============================================
echo   Test Execution Complete
echo =============================================
echo.
echo Press any key to exit...
pause > nul