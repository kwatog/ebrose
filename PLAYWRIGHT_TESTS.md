# Playwright UI Tests with Screenshots

This directory contains Playwright E2E tests that capture UI screenshots demonstrating the access control implementation.

## Running the Tests in Container (Podman/Docker)

The easiest way to run the Playwright tests is using Podman or Docker (no local Node.js or Playwright installation required):

```bash
# From the project root
./run-playwright-tests.sh
```

The script automatically detects whether you have **Podman** or **Docker** installed and uses the appropriate command.

This script will:
1. Detect container runtime (Podman or Docker)
2. Pull the official Microsoft Playwright container image
3. Install dependencies inside the container
4. Install Chromium browser
5. Run the UI tests
6. Save screenshots to `frontend/tests/screenshots/`

## Test Scenarios Covered

The `access-control-ui.spec.ts` test file includes the following scenarios:

### 1. **Admin Sees All Budget Items**
- Screenshot: `admin-sees-all-budgets.png`
- Demonstrates: Admin role bypasses all access controls

### 2. **Regular User Filtered View**
- Screenshot: `user-filtered-budgets.png`
- Demonstrates: Owner-group membership filtering in action

### 3. **Access Denied (403)**
- Screenshot: `access-denied-403.png`
- Demonstrates: User denied access to specific record

### 4. **Business Case Creator Access**
- Screenshot: `bc-creator-access.png`
- Demonstrates: Creator always has Read access to their BCs

### 5. **BC Status Transition Validation**
- Screenshot: `bc-transition-validation-error.png`
- Demonstrates: Cannot transition from Draft without line items

### 6. **User Groups Management**
- Screenshot: `admin-user-groups.png`
- Demonstrates: Admin interface for managing user groups

### 7. **Dashboard Health Check**
- Screenshot: `dashboard-health-check.png`
- Demonstrates: System health monitoring

### 8. **Access Sharing Modal**
- Screenshot: `access-sharing-modal.png`
- Demonstrates: Record-level permission management UI

## Requirements

- **Podman** or **Docker** must be installed and running
  - Install Podman: https://podman.io/getting-started/installation
  - Install Docker: https://www.docker.com/products/docker-desktop
- **No other dependencies** (Node.js, npm, Playwright are all containerized)

## Running Tests Locally (Without Docker)

If you prefer to run tests locally:

```bash
cd frontend

# Install dependencies (including Playwright)
npm install

# Install Playwright browsers
npx playwright install chromium

# Run tests
npm run test:e2e tests/e2e/access-control-ui.spec.ts
```

## Notes

- Tests use **mocked API responses** - backend does not need to be running
- Screenshots are saved in **PNG format** at full page resolution
- Tests run in **headless mode** by default (use `--headed` flag for visible browser)
- The `--network="host"` Docker flag allows tests to access `localhost` if needed

## Viewing Screenshots

After running tests, view the generated screenshots:

```bash
# List all screenshots
ls -lh frontend/tests/screenshots/

# Open a specific screenshot (macOS)
open frontend/tests/screenshots/admin-sees-all-budgets.png

# Or use any image viewer
```

## Test Configuration

Playwright configuration is in `frontend/playwright.config.ts`:
- **Base URL**: `http://localhost:3000`
- **Browsers**: Chromium (Chrome/Edge)
- **Test timeout**: 30 seconds per test
- **Retries**: 2 (in CI mode)

## Troubleshooting

### Docker Not Found
```bash
# Install Docker Desktop
# https://www.docker.com/products/docker-desktop
```

### Permission Denied
```bash
# Make script executable
chmod +x run-playwright-tests.sh
```

### Screenshots Not Generating
- Check test output for errors
- Ensure `/frontend/tests/screenshots/` directory exists
- Verify Docker has permission to write to mounted volume

## CI/CD Integration

The script is CI-ready:
- Returns exit code 0 on success, non-zero on failure
- Uses `--reporter=list` for clean console output
- Screenshots are generated even if tests fail (for debugging)

Example in Jenkins/GitHub Actions:
```yaml
- name: Run Playwright Tests
  run: ./run-playwright-tests.sh

- name: Upload Screenshots
  uses: actions/upload-artifact@v3
  if: always()
  with:
    name: playwright-screenshots
    path: frontend/tests/screenshots/
```
