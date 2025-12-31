#!/bin/bash

# Script to run Playwright tests in Podman/Docker container
# Starts backend and Nuxt dev server in background, runs tests, then stops servers

set -e

echo "🎭 Starting Playwright UI Tests in Container..."
echo ""

# Detect container runtime (podman or docker)
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
    echo "✓ Using Podman"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
    echo "✓ Using Docker"
else
    echo "❌ Error: Neither podman nor docker found in PATH"
    echo "Please install Podman or Docker to run these tests"
    exit 1
fi
echo ""

# Get absolute paths
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
BACKEND_DIR="$SCRIPT_DIR/backend"

echo "📂 Frontend directory: $FRONTEND_DIR"
echo "📂 Backend directory: $BACKEND_DIR"
echo ""

# Create screenshots directory if it doesn't exist
mkdir -p "$FRONTEND_DIR/tests/screenshots"

# =============================================================================
# Backend Server Management
# =============================================================================
BACKEND_PORT=8000
BACKEND_DIR="$SCRIPT_DIR/backend"
START_BACKEND=true
BACKEND_PID=""

# Check if backend is already running
if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
    echo "✓ Detected running backend at http://localhost:$BACKEND_PORT"
    echo ""
    START_BACKEND=false
else
    echo "⚠️  No backend detected at http://localhost:$BACKEND_PORT"
    echo "📦 Starting backend server..."

    # Check if virtual environment exists
    if [ -d "$BACKEND_DIR/venv" ]; then
        cd "$BACKEND_DIR"
        source venv/bin/activate

        # Reset and seed database
        echo "🗄️  Resetting and seeding database..."
        python3 reset_and_seed.py 2>&1 | grep -v "^/" | grep -v "DeprecationWarning" || true
        echo ""

        # Start backend in background
        python3 -m uvicorn app.main:app --host 127.0.0.1 --port $BACKEND_PORT > /tmp/backend.log 2>&1 &
        BACKEND_PID=$!

        # Wait for backend to be ready
        echo "⏳ Waiting for backend to start..."
        for i in {1..20}; do
            if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
                echo "✅ Backend started successfully (PID: $BACKEND_PID)"
                echo ""
                break
            fi
            sleep 1
        done

        if ! curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
            echo "❌ Failed to start backend after 20 seconds"
            echo "Check logs at /tmp/backend.log"
            [ -n "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null || true
            exit 1
        fi
    else
        echo "❌ Backend virtual environment not found at: $BACKEND_DIR/venv"
        echo "Please run: cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        exit 1
    fi
fi

# =============================================================================
# Frontend Server Management
# =============================================================================
FRONTEND_PORT=3000
START_FRONTEND=true
NUXT_PID=""

# Check if frontend is already running
if curl -s http://localhost:$FRONTEND_PORT/login > /dev/null 2>&1; then
    echo "✓ Detected running frontend at http://localhost:$FRONTEND_PORT"
    echo ""
    START_FRONTEND=false
else
    echo "⚠️  No frontend server detected at http://localhost:$FRONTEND_PORT"
    echo "📦 Starting Nuxt dev server..."

    # Build frontend first to ensure latest changes
    echo "🔨 Building frontend..."
    cd "$FRONTEND_DIR"
    npm run build > /tmp/frontend-build.log 2>&1
    echo "✅ Frontend built"

    # Start production server (more stable for tests than dev)
    nohup node .output/server/index.mjs > /tmp/frontend.log 2>&1 &
    NUXT_PID=$!

    # Wait for frontend to be ready
    echo "⏳ Waiting for frontend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:$FRONTEND_PORT/login > /dev/null 2>&1; then
            echo "✅ Frontend started successfully (PID: $NUXT_PID)"
            echo ""
            break
        fi
        sleep 1
    done

    if ! curl -s http://localhost:$FRONTEND_PORT/login > /dev/null 2>&1; then
        echo "❌ Failed to start frontend after 30 seconds"
        echo "Check logs at /tmp/frontend.log"
        [ -n "$NUXT_PID" ] && kill $NUXT_PID 2>/dev/null || true
        [ -n "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
fi

# =============================================================================
# Cleanup Function
# =============================================================================
cleanup() {
    echo ""
    echo "🧹 Cleaning up..."

    if [ "$START_FRONTEND" = true ] && [ -n "$NUXT_PID" ]; then
        echo "🛑 Stopping frontend server (PID: $NUXT_PID)..."
        kill $NUXT_PID 2>/dev/null || true
        sleep 1
        kill -9 $NUXT_PID 2>/dev/null || true
        echo "✅ Frontend stopped"
    fi

    if [ "$START_BACKEND" = true ] && [ -n "$BACKEND_PID" ]; then
        echo "🛑 Stopping backend server (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
        sleep 1
        kill -9 $BACKEND_PID 2>/dev/null || true
        echo "✅ Backend stopped"
    fi
}

trap cleanup EXIT INT TERM

# =============================================================================
# Run Playwright Tests
# =============================================================================
echo "🧪 Running Playwright E2E tests..."
echo "📸 Screenshots will be saved to: $FRONTEND_DIR/tests/screenshots/"
echo ""

cd "$FRONTEND_DIR"

# Run Playwright in container
$CONTAINER_CMD run --rm \
  --network="host" \
  -v "$FRONTEND_DIR:/work:z" \
  -w /work \
  --ipc=host \
  mcr.microsoft.com/playwright:v1.57.0-jammy \
  /bin/bash -c "
    set -e
    echo '📦 Installing dependencies...'
    npm install --silent 2>/dev/null
    echo '✅ Dependencies installed'
    echo ''
    echo '🌐 Ensuring Chromium browser...'
    npx playwright install chromium --with-deps 2>/dev/null
    echo '✅ Browser ready'
    echo ''
    echo '🧪 Running UI tests...'
    npx playwright test tests/e2e/ --reporter=list --project=chromium
  "

RESULT=$?

echo ""
if [ $RESULT -eq 0 ]; then
    echo "✅ All tests passed!"
    echo "📸 Screenshots saved to: $FRONTEND_DIR/tests/screenshots/"
else
    echo "❌ Tests failed with exit code: $RESULT"
fi
echo ""

echo "Screenshots generated:"
ls -lh "$FRONTEND_DIR/tests/screenshots/"*.png 2>/dev/null | tail -10 || echo "  (No screenshots found)"
echo ""

exit $RESULT
