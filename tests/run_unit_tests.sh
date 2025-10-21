#!/bin/bash
# Run unit tests with coverage

echo "================================================"
echo "Running DOGECICS Unit Tests"
echo "================================================"

# Install dependencies if needed
if ! command -v pytest &> /dev/null; then
    echo "Installing test dependencies..."
    pip install -r requirements.txt
fi

# Run unit tests
echo "Executing unit tests..."
pytest tests/unit/ \
    -v \
    -m unit \
    --cov=PYTHON \
    --cov-report=html:tests/reports/coverage \
    --cov-report=term-missing \
    --cov-report=xml:tests/reports/coverage.xml \
    --html=tests/reports/unit-test-report.html \
    --self-contained-html

# Check coverage threshold
coverage_percent=$(coverage report | grep TOTAL | awk '{print $NF}' | sed 's/%//')
echo "Coverage: ${coverage_percent}%"

if (( $(echo "$coverage_percent < 80" | bc -l) )); then
    echo "WARNING: Coverage is below 80% threshold"
    exit 1
else
    echo "SUCCESS: Coverage meets 80% threshold"
fi
