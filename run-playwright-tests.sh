#!/bin/bash

# Script to run Playwright tests in Podman/Docker container
# This captures UI screenshots for access control features

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

# Get the absolute path to the frontend directory
FRONTEND_DIR="$(cd "$(dirname "$0")/frontend" && pwd)"

# Create screenshots directory if it doesn't exist
mkdir -p "$FRONTEND_DIR/tests/screenshots"

echo "📂 Frontend directory: $FRONTEND_DIR"
echo "📸 Screenshots will be saved to: $FRONTEND_DIR/tests/screenshots/"
echo ""

# Run Playwright in container
# Note: Using --network="host" to access localhost services (backend/frontend)
# If backend/frontend are not running, tests will fail with mocked data only
$CONTAINER_CMD run --rm \
  --network="host" \
  -v "$FRONTEND_DIR:/work:z" \
  -w /work \
  --ipc=host \
  mcr.microsoft.com/playwright:v1.55.0-jammy \
  /bin/bash -c "
    set -e
    echo '📦 Installing dependencies...'
    npm install --silent
    echo '✅ Dependencies installed'
    echo ''
    echo '🌐 Installing Playwright Chromium browser...'
    npx playwright install chromium --with-deps
    echo '✅ Browser installed'
    echo ''
    echo '🧪 Running UI tests with screenshots...'
    echo ''
    npx playwright test tests/e2e/access-control-ui.spec.ts --reporter=list --project=chromium
  "

RESULT=$?

echo ""
if [ $RESULT -eq 0 ]; then
    echo "✅ Tests complete! Screenshots saved to: $FRONTEND_DIR/tests/screenshots/"
else
    echo "❌ Tests failed with exit code: $RESULT"
fi
echo ""
echo "Screenshots generated:"
ls -lh "$FRONTEND_DIR/tests/screenshots/"*.png 2>/dev/null || echo "  (No screenshots found - tests may have failed)"
echo ""

exit $RESULT
