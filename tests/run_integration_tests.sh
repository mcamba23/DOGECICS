#!/bin/bash
# Run integration/SIT tests

echo "================================================"
echo "Running DOGECICS Integration Tests (SIT)"
echo "================================================"

# Install dependencies if needed
if ! command -v pytest &> /dev/null; then
    echo "Installing test dependencies..."
    pip install -r requirements.txt
fi

# Run integration tests
echo "Executing integration tests..."
pytest tests/integration/ \
    -v \
    -m integration \
    --html=tests/reports/integration-test-report.html \
    --self-contained-html \
    --tb=short

# Check exit code
if [ $? -eq 0 ]; then
    echo "SUCCESS: All integration tests passed"
else
    echo "FAILURE: Some integration tests failed"
    exit 1
fi
