#!/bin/bash
# Run all tests in sequence

echo "================================================"
echo "DOGECICS - Complete Test Suite Execution"
echo "================================================"

# Track failures
failed_tests=""

# Run unit tests
echo ""
echo "STEP 1: Running Unit Tests..."
bash tests/run_unit_tests.sh
if [ $? -ne 0 ]; then
    failed_tests="${failed_tests}Unit Tests, "
fi

# Run integration tests
echo ""
echo "STEP 2: Running Integration Tests..."
bash tests/run_integration_tests.sh
if [ $? -ne 0 ]; then
    failed_tests="${failed_tests}Integration Tests, "
fi

# Run E2E tests
echo ""
echo "STEP 3: Running E2E/UAT Tests..."
bash tests/run_e2e_tests.sh
if [ $? -ne 0 ]; then
    failed_tests="${failed_tests}E2E Tests, "
fi

# Run load tests (skip soak test by default)
echo ""
echo "STEP 4: Running Load Tests..."
bash tests/run_load_tests.sh
if [ $? -ne 0 ]; then
    failed_tests="${failed_tests}Load Tests, "
fi

# Summary
echo ""
echo "================================================"
echo "TEST EXECUTION SUMMARY"
echo "================================================"

if [ -z "$failed_tests" ]; then
    echo "✅ ALL TESTS PASSED!"
    echo ""
    echo "Reports available in:"
    echo "  - Unit Tests: tests/reports/unit-test-report.html"
    echo "  - Coverage: tests/reports/coverage/index.html"
    echo "  - Integration: tests/reports/integration-test-report.html"
    echo "  - E2E/UAT: tests/reports/e2e-test-report.html"
    echo "  - BDD: tests/reports/bdd-test-report.html"
    echo "  - Load Tests: tests/reports/*-summary.json"
    exit 0
else
    echo "❌ SOME TESTS FAILED: ${failed_tests%??}"
    echo ""
    echo "Check reports for details in tests/reports/"
    exit 1
fi
