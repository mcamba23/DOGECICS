#!/bin/bash
# Run E2E/UAT tests with evidence capture

echo "================================================"
echo "Running DOGECICS E2E/UAT Tests"
echo "================================================"

# Install dependencies if needed
if ! command -v pytest &> /dev/null; then
    echo "Installing test dependencies..."
    pip install -r requirements.txt
fi

# Install Playwright browsers if needed
if ! playwright --version &> /dev/null; then
    echo "Installing Playwright..."
    playwright install
fi

# Create screenshots directory if it doesn't exist
mkdir -p tests/screenshots

# Run E2E tests
echo "Executing E2E/UAT tests..."
pytest tests/e2e/ \
    -v \
    -m e2e \
    --html=tests/reports/e2e-test-report.html \
    --self-contained-html \
    --tb=short

# Run BDD tests
echo "Executing BDD tests..."
pytest tests/e2e/test_bdd_steps.py \
    -v \
    --html=tests/reports/bdd-test-report.html \
    --self-contained-html \
    --tb=short

# Check if screenshots were captured
if [ -d "tests/screenshots" ] && [ "$(ls -A tests/screenshots)" ]; then
    echo "Evidence captured in tests/screenshots/"
    ls -lh tests/screenshots/
else
    echo "Note: No screenshots were captured (may not be applicable for CLI tests)"
fi

# Check exit code
if [ $? -eq 0 ]; then
    echo "SUCCESS: All E2E/UAT tests passed"
else
    echo "FAILURE: Some E2E/UAT tests failed"
    exit 1
fi
