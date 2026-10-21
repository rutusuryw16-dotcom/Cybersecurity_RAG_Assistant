@echo off
TITLE CyberSec RAG SOC Assistant - Dependency Installer
color 0a

:: Change working directory to script directory
cd /d "%~dp0"

echo ===============================================================================
echo     DESIGN AND DEVELOPMENT OF A CLOUD-BASED RAG ASSISTANT FOR CYBERSECURITY
echo               DEPENDENCY INSTALLER & ENVIRONMENT SETUP
echo ===============================================================================
echo.

:: 1. Check Python installation
echo [*] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ===============================================================================
    echo [ERROR] Python is not installed or not added to your system PATH!
    echo ===============================================================================
    echo Please install Python 3.10 or newer:
    echo   1. Download Python from: https://www.python.org/downloads/
    echo   2. Run the installer.
    echo   3. CRITICAL: Check the box "Add python.exe to PATH" at the bottom of the installer!
    echo   4. Restart this script after installing Python.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] Detected %PYTHON_VERSION%
echo.

:: 2. Check Node.js & npm installation
set HAS_NODE=1
echo [*] Checking Node.js and npm installation...
node -v >nul 2>&1
if %errorlevel% neq 0 (
    set HAS_NODE=0
    echo [NOTICE] Node.js is NOT installed on this laptop.
    echo.
    echo You have 2 options:
    echo   [1] Auto-install Node.js via Windows Package Manager (winget)
    echo   [2] Skip Node.js completely - this project already includes a pre-built
    echo       frontend distribution that runs 100%% with Python alone!
    echo.
    set /p INSTALL_NODE="Would you like to install Node.js now? (Y/N) [Default: N]: "
)

if /i "%INSTALL_NODE%"=="Y" (
    echo.
    echo [*] Attempting to install Node.js via winget...
    winget --version >nul 2>&1
    if %errorlevel% equ 0 (
        winget install OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
        echo.
        echo [INFO] Refreshing environment variables...
        call refreshenv >nul 2>&1
        node -v >nul 2>&1
        if %errorlevel% equ 0 (
            set HAS_NODE=1
            echo [OK] Node.js installed successfully!
        ) else (
            echo [NOTE] Node.js installed, but terminal needs restart to detect PATH.
            echo Proceeding with Python-only mode for now.
            set HAS_NODE=0
        )
    ) else (
        echo [WARNING] Windows winget not found. Skipping Node.js installation.
        echo You can manually install Node.js from https://nodejs.org/ if desired.
        set HAS_NODE=0
    )
)

if %HAS_NODE% equ 1 (
    for /f "tokens=*" %%i in ('node -v') do set NODE_VERSION=%%i
    echo [OK] Detected Node.js %NODE_VERSION%
) else (
    echo [OK] Running in Lightweight Mode (No Node.js needed - powered by Python).
)
echo.

:: 3. Upgrade pip
echo [*] Ensuring pip is up to date...
python -m pip install --upgrade pip
echo.

:: 4. Install Backend Dependencies
echo ===============================================================================
echo [1/2] Installing Backend Dependencies (FastAPI, PyTorch, ChromaDB, etc.)...
echo ===============================================================================
echo Note: PyTorch and Sentence-Transformers may take a few minutes to download.
echo Please wait...
echo.

cd /d "%~dp0backend"
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ===============================================================================
    echo [ERROR] Failed to install backend Python dependencies!
    echo ===============================================================================
    echo Please verify your internet connection or Python setup and try again.
    pause
    exit /b 1
)

echo.
echo [*] Verifying backend Python modules...
python -c "import fastapi, sentence_transformers, chromadb, uvicorn; print('[OK] All essential backend packages successfully imported!')"
if %errorlevel% neq 0 (
    echo [WARNING] Verification test had warnings, but packages were installed.
)
echo.

:: 5. Install Frontend Dependencies (Only if Node.js is present)
echo ===============================================================================
echo [2/2] Frontend Setup...
echo ===============================================================================
if %HAS_NODE% equ 1 (
    echo Installing Frontend Packages with npm...
    cd /d "%~dp0frontend"
    call npm install
    if %errorlevel% neq 0 (
        echo [WARNING] npm install encountered an issue, but pre-built frontend is available.
    ) else (
        echo [OK] Frontend dependencies installed successfully!
    )
) else (
    echo [INFO] Pre-compiled React frontend detected in 'frontend/dist'.
    echo Python's FastAPI will serve the full web dashboard automatically!
    echo No npm installation required.
)

echo.
echo ===============================================================================
echo               ALL DEPENDENCIES INSTALLED SUCCESSFULLY!
echo ===============================================================================
echo.
echo You are all set to run the application on this laptop!
echo.
if %HAS_NODE% equ 1 (
    echo To start both Backend and Vite Frontend dev servers:
    echo    run_demo.bat (Dashboard will open at http://localhost:5173)
) else (
    echo To start the Unified Backend + Frontend server:
    echo    run_demo.bat (Dashboard will open at http://localhost:8000)
)
echo.

cd /d "%~dp0"
set /p START_NOW="Would you like to launch the application right now? (Y/N): "
if /i "%START_NOW%"=="Y" (
    echo.
    echo Starting CyberSec RAG SOC Assistant...
    call run_demo.bat
) else (
    echo.
    echo You can start the app anytime by double-clicking run_demo.bat.
    echo Press any key to exit this installer...
    pause >nul
)
