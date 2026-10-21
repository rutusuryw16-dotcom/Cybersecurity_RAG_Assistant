@echo off
TITLE CyberSec RAG SOC Assistant - Cloud Incident Investigation
color 0b
cd /d "%~dp0"

echo ===============================================================================
echo     DESIGN AND DEVELOPMENT OF A CLOUD-BASED RAG ASSISTANT FOR CYBERSECURITY
echo                 INCIDENT INVESTIGATION & EVIDENCE-BASED ANALYSIS
echo ===============================================================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo (Make sure to check "Add Python to PATH" during installation)
    pause
    exit /b 1
)

:: 2. Check Node.js
set HAS_NODE=1
node -v >nul 2>&1
if %errorlevel% neq 0 (
    set HAS_NODE=0
)

:: 3. Verify Backend Dependencies
echo [1/2] Verifying Backend Dependencies...
cd /d "%~dp0backend"
python -c "import fastapi, sentence_transformers; print('Backend modules verified!')" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing backend dependencies from requirements.txt...
    python -m pip install -r requirements.txt
)

:: 4. Launch Services
if %HAS_NODE% equ 1 (
    echo.
    echo [2/2] Node.js detected! Verifying Frontend packages...
    cd /d "%~dp0frontend"
    if not exist "node_modules\" (
        echo Installing frontend packages (npm install)...
        call npm install
    )
    
    echo.
    echo Launching FastAPI Backend Server on port 8000...
    start "CyberSec RAG - FastAPI Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
    
    timeout /t 3 >nul
    
    echo Launching Vite React Frontend on port 5173...
    start "CyberSec RAG - React Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
    
    timeout /t 3 >nul
    
    echo.
    echo ===============================================================================
    echo   SUCCESS! Services are running in Dual-Dev Mode:
    echo   - Frontend SOC Dashboard:  http://localhost:5173
    echo   - Backend FastAPI API:     http://localhost:8000
    echo   - API Interactive Docs:    http://localhost:8000/docs
    echo   - Health Check:            http://localhost:8000/health
    echo ===============================================================================
) else (
    echo.
    echo ===============================================================================
    echo [NOTE] Node.js is not installed on this system.
    echo Using pre-built frontend distribution served directly by FastAPI!
    echo ===============================================================================
    echo.
    echo Launching Unified Server (Frontend + Backend) on port 8000...
    start "CyberSec RAG - Unified Server" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
    
    timeout /t 3 >nul
    
    echo.
    echo ===============================================================================
    echo   SUCCESS! Unified Service is running:
    echo   - Frontend SOC Dashboard:  http://localhost:8000
    echo   - API Interactive Docs:    http://localhost:8000/docs
    echo   - Health Check:            http://localhost:8000/health
    echo ===============================================================================
)

echo.
echo Press any key to exit this launcher window (services keep running).
pause >nul
