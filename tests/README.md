# DOGECICS Testing Documentation

This directory contains a comprehensive testing suite for the DOGECICS project, including Unit Tests, System Integration Tests (SIT), User Acceptance Tests (UAT), and Load Tests.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Types](#test-types)
- [Coverage Reports](#coverage-reports)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

## Overview

The DOGECICS testing strategy includes:

1. **Unit Tests**: Test individual functions and components in isolation
2. **Integration Tests (SIT)**: Test system integration and component interactions
3. **E2E/UAT Tests**: Test complete user scenarios and acceptance criteria
4. **Load Tests**: Test system performance under various load conditions

## Prerequisites

### Python Dependencies

Install Python testing dependencies:

```bash
pip install -r requirements.txt
```

### K6 (for Load Testing)

**Ubuntu/Debian:**
```bash
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

**macOS:**
```bash
brew install k6
```

**Windows:**
```bash
choco install k6
```

### Playwright (for E2E Testing)

```bash
playwright install
```

## Test Structure

```
tests/
├── unit/                    # Unit tests
│   └── test_dogedcams_unit.py
├── integration/             # Integration/SIT tests
│   └── test_dogedcams_integration.py
├── e2e/                     # E2E/UAT tests
│   ├── features/           # BDD feature files
│   │   └── wallet_sync.feature
│   ├── test_uat_scenarios.py
│   └── test_bdd_steps.py
├── load/                    # K6 load tests
│   ├── basic-load-test.js
│   ├── stress-test.js
│   ├── spike-test.js
│   └── soak-test.js
├── fixtures/                # Test data fixtures
│   ├── sample_wallet_data.json
│   └── sample_vsam_records.txt
├── reports/                 # Generated test reports
├── screenshots/             # UAT evidence screenshots
├── run_unit_tests.sh       # Unit test runner
├── run_integration_tests.sh # Integration test runner
├── run_e2e_tests.sh        # E2E test runner
├── run_load_tests.sh       # Load test runner
└── run_all_tests.sh        # Run all tests
```

## Running Tests

### Run All Tests

```bash
./tests/run_all_tests.sh
```

### Run Specific Test Suites

**Unit Tests:**
```bash
./tests/run_unit_tests.sh
```

**Integration Tests (SIT):**
```bash
./tests/run_integration_tests.sh
```

**E2E/UAT Tests:**
```bash
./tests/run_e2e_tests.sh
```

**Load Tests:**
```bash
./tests/run_load_tests.sh
```

**Load Tests with Soak Test (24 minutes):**
```bash
./tests/run_load_tests.sh --full
```

### Run Tests with Pytest Directly

**Run specific test file:**
```bash
pytest tests/unit/test_dogedcams_unit.py -v
```

**Run tests by marker:**
```bash
pytest -m unit          # Only unit tests
pytest -m integration   # Only integration tests
pytest -m e2e           # Only E2E tests
pytest -m slow          # Only slow tests
```

**Run with coverage:**
```bash
pytest tests/unit/ --cov=PYTHON --cov-report=html
```

## Test Types

### 1. Unit Tests

**Location:** `tests/unit/`

**Coverage:** Tests individual functions in `dogedcams.py`

**Key Test Classes:**
- `TestGenerateFakeRecords`: Tests fake record generation
- `TestNewRecords`: Tests record comparison logic
- `TestGenerateIDCAMSJCL`: Tests JCL generation
- `TestGetRecords`: Tests RPC wallet record retrieval
- `TestSendJCL`: Tests JCL submission to TK4-
- `TestGetCommands`: Tests printer queue reading
- `TestSendDoge`: Tests dogecoin sending

**Run:**
```bash
pytest tests/unit/ -v -m unit
```

**Coverage Requirement:** > 80%

### 2. System Integration Tests (SIT)

**Location:** `tests/integration/`

**Coverage:** Tests integration between components

**Key Test Classes:**
- `TestRPCIntegration`: Tests RPC server integration
- `TestVSAMFileGeneration`: Tests end-to-end VSAM generation
- `TestSocketCommunication`: Tests TK4- socket communication
- `TestDataPersistence`: Tests file operations
- `TestFullWorkflow`: Tests complete workflow
- `TestErrorHandling`: Tests error scenarios

**Run:**
```bash
pytest tests/integration/ -v -m integration
```

### 3. E2E/UAT Tests

**Location:** `tests/e2e/`

**Coverage:** Tests complete user scenarios

**User Scenarios Tested:**
- New user setup
- Wallet balance check
- Transaction history view
- Sending dogecoin
- High volume transactions
- Incremental updates
- Error recovery
- Data validation
- Concurrent operations

**BDD Scenarios:**
- First time wallet synchronization
- Viewing wallet balance
- Viewing transaction history
- Incremental sync with new transactions
- Handling large transaction volumes
- Sending Dogecoin from CICS
- Error handling for invalid send
- System recovery after connection loss

**Run:**
```bash
pytest tests/e2e/ -v -m e2e
```

**Evidence:** Screenshots and reports captured in `tests/screenshots/` and `tests/reports/`

### 4. Load Tests (K6)

**Location:** `tests/load/`

**Test Scripts:**

1. **basic-load-test.js**: Basic load test
   - Duration: ~4 minutes
   - Users: Ramps from 0 → 10 → 20 → 0
   - Threshold: p95 < 500ms

2. **stress-test.js**: Stress test
   - Duration: ~13 minutes
   - Users: Ramps from 0 → 50 → 100 → 150 → 0
   - Threshold: p95 < 1000ms

3. **spike-test.js**: Spike test
   - Duration: ~5 minutes
   - Users: Spikes from 10 → 200 → 10 → 300 → 0
   - Threshold: p95 < 2000ms

4. **soak-test.js**: Soak/endurance test
   - Duration: ~24 minutes
   - Users: 30 users sustained for 20 minutes
   - Threshold: p95 < 800ms

**Run:**
```bash
# Run basic, stress, and spike tests
./tests/run_load_tests.sh

# Run all including soak test
./tests/run_load_tests.sh --full

# Run individual test
k6 run tests/load/basic-load-test.js
```

**Configuration:**

Set environment variables for custom configuration:
```bash
export BASE_URL=http://your-rpc-server:22555
k6 run tests/load/basic-load-test.js
```

## Coverage Reports

After running tests, reports are generated in `tests/reports/`:

- **Unit Test Report:** `unit-test-report.html`
- **Coverage Report:** `coverage/index.html`
- **Coverage XML:** `coverage.xml` (for CI/CD)
- **Integration Report:** `integration-test-report.html`
- **E2E Report:** `e2e-test-report.html`
- **BDD Report:** `bdd-test-report.html`
- **Load Test Reports:** `*-summary.json`

### Viewing Reports

Open in browser:
```bash
# Coverage report
open tests/reports/coverage/index.html

# Unit test report
open tests/reports/unit-test-report.html

# E2E test report
open tests/reports/e2e-test-report.html
```

### Coverage Threshold

The project requires **minimum 80% code coverage** for unit tests.

Check current coverage:
```bash
coverage report
```

## CI/CD Integration

Tests are automatically run on GitHub Actions for:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

**Workflow:** `.github/workflows/testing.yml`

**Jobs:**
1. `unit-tests`: Runs unit tests with coverage
2. `integration-tests`: Runs SIT tests
3. `e2e-tests`: Runs UAT/E2E tests with evidence capture
4. `load-tests`: Runs K6 load tests

**Artifacts:**
- Coverage reports
- Test reports (HTML)
- Screenshots (UAT evidence)
- Load test summaries (JSON)

## Test Data and Fixtures

Test fixtures are located in `tests/fixtures/`:

- `sample_wallet_data.json`: Sample wallet data for testing
- `sample_vsam_records.txt`: Sample VSAM records

These fixtures can be used in tests for consistent test data.

## Troubleshooting

### Common Issues

**1. Import errors:**
```bash
# Ensure PYTHON directory is in path
export PYTHONPATH="${PYTHONPATH}:${PWD}/PYTHON"
```

**2. Playwright not installed:**
```bash
playwright install --with-deps
```

**3. K6 not found:**
```bash
# Follow installation instructions in Prerequisites section
```

**4. Coverage below threshold:**
```bash
# Check which files need more tests
coverage report -m
```

**5. Tests fail with connection errors:**
- Tests use mocks for RPC and socket connections
- No actual dogecoin server or TK4- required
- Check that mock configurations are correct

### Debug Mode

Run tests with verbose output:
```bash
pytest tests/unit/ -vv -s
```

Run specific test:
```bash
pytest tests/unit/test_dogedcams_unit.py::TestGenerateFakeRecords::test_generate_fake_records_default -v
```

Show test output:
```bash
pytest tests/unit/ -v --capture=no
```

## Best Practices

1. **Always run unit tests before committing:**
   ```bash
   ./tests/run_unit_tests.sh
   ```

2. **Check coverage after adding new code:**
   ```bash
   pytest tests/unit/ --cov=PYTHON --cov-report=term-missing
   ```

3. **Run integration tests before major changes:**
   ```bash
   ./tests/run_integration_tests.sh
   ```

4. **Execute E2E tests before releases:**
   ```bash
   ./tests/run_e2e_tests.sh
   ```

5. **Run load tests to verify performance:**
   ```bash
   ./tests/run_load_tests.sh
   ```

## Contributing

When adding new features:

1. Write unit tests for new functions
2. Add integration tests for component interactions
3. Create E2E scenarios for user-facing features
4. Update this documentation
5. Ensure all tests pass and coverage > 80%

## Support

For issues or questions about testing:
- Check the troubleshooting section
- Review test examples in existing test files
- Consult pytest documentation: https://docs.pytest.org/
- Consult K6 documentation: https://k6.io/docs/

## License

Same as DOGECICS project license.
