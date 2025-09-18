@echo off
echo ============================================
echo   Starting Math Routing Agent Project
echo   Backend + Frontend will run together
echo ============================================

:: Check if Python and Node.js are installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in PATH
    goto :error
)

where npm >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Node.js/npm is not installed or not in PATH
    goto :error
)

:: Start backend in a new window
echo Starting backend...
start "Math Agent Backend" cmd /c "cd /d %~dp0backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

:: Wait for backend to initialize
echo Waiting for backend to initialize...
timeout /t 10 /nobreak >nul

:: Start frontend in a new window
echo Starting frontend...
start "Math Agent Frontend" cmd /c "cd /d %~dp0frontend && npm start"

echo.
echo ============================================
echo Both services started successfully!
echo --------------------------------------------
echo Frontend:   http://localhost:3000
echo Backend:    http://localhost:8000
echo API Docs:   http://localhost:8000/docs
echo ============================================
echo.
echo The services are running in separate windows.
echo Close this window and the service windows when you're done.
echo.
pause
exit /b 0

:error
echo.
echo Failed to start services. Please check the error message above.
pause
exit /b 1
