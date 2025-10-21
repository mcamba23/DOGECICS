# DOGECICS Testing Quick Start Guide

## 🚀 Quick Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run all tests
./tests/run_all_tests.sh
```

## 📋 Common Commands

### Run Specific Test Types

```bash
# Unit tests only
./tests/run_unit_tests.sh
# or
pytest tests/unit/ -v -m unit

# Integration tests only
./tests/run_integration_tests.sh
# or
pytest tests/integration/ -v -m integration

# E2E/UAT tests only
./tests/run_e2e_tests.sh
# or
pytest tests/e2e/ -v -m e2e

# Load tests
./tests/run_load_tests.sh
# or
k6 run tests/load/basic-load-test.js
```

### Run Specific Tests

```bash
# Run single test file
pytest tests/unit/test_dogedcams_unit.py -v

# Run specific test class
pytest tests/unit/test_dogedcams_unit.py::TestGenerateFakeRecords -v

# Run specific test
pytest tests/unit/test_dogedcams_unit.py::TestGenerateFakeRecords::test_generate_fake_records_default -v
```

### Coverage

```bash
# Run with coverage
pytest tests/unit/ --cov=PYTHON --cov-report=html

# View coverage report
open tests/reports/coverage/index.html
```

## 📊 View Reports

```bash
# Unit test report
open tests/reports/unit-test-report.html

# Coverage report
open tests/reports/coverage/index.html

# Integration test report
open tests/reports/integration-test-report.html

# E2E test report
open tests/reports/e2e-test-report.html
```

## 🐛 Debug Tests

```bash
# Run with verbose output
pytest tests/unit/ -vv

# Show print statements
pytest tests/unit/ -v -s

# Show full traceback
pytest tests/unit/ -v --tb=long

# Run only failed tests
pytest tests/unit/ --lf
```

## 🏷️ Test Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only E2E tests
pytest -m e2e

# Run only slow tests
pytest -m slow

# Skip slow tests
pytest -m "not slow"
```

## 🔧 Troubleshooting

### Import Errors
```bash
export PYTHONPATH="${PYTHONPATH}:${PWD}/PYTHON"
```

### Playwright Not Installed
```bash
playwright install --with-deps
```

### K6 Not Found
```bash
# Ubuntu/Debian
sudo apt-get install k6

# macOS
brew install k6
```

## 📈 K6 Load Tests

```bash
# Basic load test
k6 run tests/load/basic-load-test.js

# Stress test
k6 run tests/load/stress-test.js

# Spike test
k6 run tests/load/spike-test.js

# Soak test (24 minutes)
k6 run tests/load/soak-test.js

# With custom URL
BASE_URL=http://localhost:22555 k6 run tests/load/basic-load-test.js
```

## 🎯 Testing Checklist

Before committing:
- [ ] Run unit tests: `./tests/run_unit_tests.sh`
- [ ] Check coverage: Should be >63%
- [ ] Run integration tests: `./tests/run_integration_tests.sh`

Before releasing:
- [ ] Run all tests: `./tests/run_all_tests.sh`
- [ ] Run E2E tests: `./tests/run_e2e_tests.sh`
- [ ] Run load tests: `./tests/run_load_tests.sh`
- [ ] Review test reports
- [ ] Update documentation if needed

## 📚 More Information

- Full documentation: [tests/README.md](README.md)
- Evidence report: [tests/TESTING_EVIDENCE.md](TESTING_EVIDENCE.md)
- Main README: [../readme.md](../readme.md)

## 💡 Pro Tips

1. **Use markers** to run subsets of tests quickly
2. **Run fast tests frequently**, slow tests before commits
3. **Check coverage** for new code additions
4. **Use `-k` flag** to run tests matching a pattern
5. **View HTML reports** for detailed analysis

```bash
# Run tests matching pattern
pytest -k "test_generate" -v

# Run tests NOT matching pattern
pytest -k "not slow" -v
```

## 🆘 Need Help?

1. Check [tests/README.md](README.md) for detailed docs
2. Review test examples in test files
3. Check pytest docs: https://docs.pytest.org/
4. Check K6 docs: https://k6.io/docs/

---
**Happy Testing! 🧪**
