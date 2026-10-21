#!/usr/bin/env bash
# ===============================================================================
#     DESIGN AND DEVELOPMENT OF A CLOUD-BASED RAG ASSISTANT FOR CYBERSECURITY
#                 INCIDENT INVESTIGATION & EVIDENCE-BASED ANALYSIS
#                            macOS / Linux Launcher
# ===============================================================================

set -e

# Resolve script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/backend"
FRONTEND_DIR="${SCRIPT_DIR}/frontend"

echo "==============================================================================="
echo "    DESIGN AND DEVELOPMENT OF A CLOUD-BASED RAG ASSISTANT FOR CYBERSECURITY"
echo "                INCIDENT INVESTIGATION & EVIDENCE-BASED ANALYSIS"
echo "==============================================================================="
echo ""

# 1. Check Python 3
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python 3 is not installed or not in PATH!"
    echo "Please install Python 3 (e.g., 'brew install python') and retry."
    exit 1
fi
echo "[✓] Python detected: $($PYTHON_CMD --version)"

# 2. Check Node.js and npm
if ! command -v node >/dev/null 2>&1; then
    echo "[ERROR] Node.js is not installed or not in PATH!"
    echo "Please install Node.js (e.g., 'brew install node') and retry."
    exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
    echo "[ERROR] npm is not installed or not in PATH!"
    exit 1
fi
echo "[✓] Node.js detected: $(node -v) / npm: $(npm -v)"

# 3. Setup Virtual Environment & Backend Dependencies
echo ""
echo "[1/3] Verifying Backend Dependencies..."
cd "$BACKEND_DIR"

if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment in backend/.venv..."
    $PYTHON_CMD -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Check if fastapi and sentence_transformers are installed
if ! python -c "import fastapi, sentence_transformers" >/dev/null 2>&1; then
    echo "Installing backend dependencies from requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "[✓] Backend dependencies verified."
fi

# 4. Verify Frontend Dependencies
echo ""
echo "[2/3] Verifying Frontend Dependencies..."
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    echo "Installing frontend npm packages..."
    npm install
else
    echo "[✓] Frontend node_modules verified."
fi

# 5. Launch Backend & Frontend Services
echo ""
echo "[3/3] Launching Backend & Frontend Services..."

# Process tracking and cleanup on exit
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    echo ""
    echo "Shutting down services..."
    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    echo "All services stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Start Backend
cd "$BACKEND_DIR"
source .venv/bin/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!
echo "[✓] FastAPI Backend running (PID: $BACKEND_PID) on http://127.0.0.1:8000"

# Start Frontend
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!
echo "[✓] Vite React Frontend running (PID: $FRONTEND_PID) on http://localhost:5173"

sleep 3

echo ""
echo "==============================================================================="
echo "   SUCCESS! Services are running:"
echo "   - Frontend SOC Dashboard:  http://localhost:5173"
echo "   - Backend FastAPI API:     http://localhost:8000"
echo "   - API Interactive Docs:    http://localhost:8000/docs"
echo "   - Health Check:            http://localhost:8000/health"
echo "==============================================================================="
echo ""
echo "Press [Ctrl+C] to stop all services."

# Attempt to open browser automatically on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "http://localhost:5173" 2>/dev/null || true
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "http://localhost:5173" 2>/dev/null || true
fi

# Keep script running to monitor child processes
wait
