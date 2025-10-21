# DOGE Bank CICS

Welcome to DOGE Bank CICS. The code on in the various subfolders allows you to create a CICS frontend to everyones favorite crypto currency: **DOGE COIN**. 

When you connect you're presented with a familiar and friendly splash screen. Where you go from there is up to you. 

<img>

## Much Details

Included with this repo:

* Python script to sync between **TK4-** KICKS and dogecoin wallet. **Note**: Only dogecoin core is supported. 
* 4 CICS transactions to interact with your wallet, including a main menu, transaction history, sending doge and transaction details.
* JCL to assemble and compile DOGEBANK on **TK4-**
* New KICKS SIT/FCT/PPT/PCT tables
* Instructions on what changes to make in **TK4-** so you can send DOGE coin from KICKS

## WOW Install

Read INSTALL.md for instalation details.

## Such Screenshots

**DOGE Splash Screen**

<img src="https://raw.githubusercontent.com/mainframed/DOGECICS/main/screenshots/01-DOGE.png">

**Main Menu**
<img src="https://raw.githubusercontent.com/mainframed/DOGECICS/main/screenshots/02-MAIN.png">

**Transaction History**

<img src="https://raw.githubusercontent.com/mainframed/DOGECICS/main/screenshots/03-DTRN.png">

**Transaction Details**

<img src="https://raw.githubusercontent.com/mainframed/DOGECICS/main/screenshots/04-DEET.png">

**Send Doge Coin**

<img src="https://raw.githubusercontent.com/mainframed/DOGECICS/main/screenshots/05-DSND.png">


## Testing

DOGECICS includes a comprehensive testing suite with:

* **Unit Tests**: Test individual functions with >80% coverage
* **Integration Tests (SIT)**: Test system integration and component interactions
* **E2E/UAT Tests**: Test complete user scenarios with BDD (Behavior-Driven Development)
* **Load Tests**: K6-based performance testing (load, stress, spike, soak)

### Quick Start

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
./tests/run_all_tests.sh

# Run specific test suites
./tests/run_unit_tests.sh          # Unit tests
./tests/run_integration_tests.sh   # Integration tests
./tests/run_e2e_tests.sh           # E2E/UAT tests
./tests/run_load_tests.sh          # Load tests
```

### View Reports

After running tests, open the reports:

```bash
# Coverage report
open tests/reports/coverage/index.html

# Test reports
open tests/reports/unit-test-report.html
open tests/reports/e2e-test-report.html
```

For detailed testing documentation, see [tests/README.md](tests/README.md).

## Credits:

* Philip Young (Soldier of FORTRAN)
* Mike Noel for KICKS for TSO
* Murrach CICS for COBOL programmer book
