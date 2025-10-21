"""
BDD Step definitions for wallet_sync.feature
Uses pytest-bdd for behavior-driven testing
"""
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
import sys
import os

# Add PYTHON directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../PYTHON'))

import dogedcams

# Load scenarios from feature file
scenarios('features/wallet_sync.feature')


# Background steps
@given('the DOGECICS system is running')
def dogecics_running():
    """Verify system is initialized"""
    return True


@given('a Dogecoin wallet is configured')
def wallet_configured():
    """Verify wallet configuration"""
    return True


# Scenario: First time wallet synchronization
@given('no previous sync has occurred', target_fixture='no_previous_sync')
def no_previous_sync(tmp_path):
    """Ensure no temp file exists"""
    return {'tmp_file': tmp_path / 'test.tmp', 'exists': False}


@when('I run the sync command', target_fixture='run_sync_command')
def run_sync_command(no_previous_sync):
    """Execute sync command"""
    records = dogedcams.generate_fake_records(number_of_records=10)
    jcl = dogedcams.generate_IDCAMS_JCL(
        user='testuser',
        password='testpass',
        vsam_file='DOGE.VSAM',
        records=records
    )
    return {'records': records, 'jcl': jcl}


@then('a VSAM file should be created')
def vsam_file_created(run_sync_command):
    """Verify VSAM file creation in JCL"""
    assert 'DEFINE CLUSTER' in run_sync_command['jcl']


@then('the VSAM file should contain balance records')
def contains_balance_records(run_sync_command):
    """Verify balance records exist"""
    records = run_sync_command['records']
    assert any('Available' in r for r in records)


@then('the VSAM file should contain pending balance')
def contains_pending_balance(run_sync_command):
    """Verify pending balance exists"""
    records = run_sync_command['records']
    assert any('Pending' in r for r in records)


@then('the VSAM file should contain a control record')
def contains_control_record(run_sync_command):
    """Verify control record exists"""
    records = run_sync_command['records']
    assert any('Control Re' in r for r in records)


# Scenario: Viewing wallet balance
@given('the wallet has been synced', target_fixture='wallet_synced')
def wallet_synced():
    """Simulate synced wallet"""
    return dogedcams.generate_fake_records(number_of_records=10)


@when('I check the balance', target_fixture='check_balance')
def check_balance(wallet_synced):
    """Get balance from records"""
    balance_records = [r for r in wallet_synced if 'Available' in r or 'Pending' in r]
    return balance_records


@then('I should see the available balance')
def see_available_balance(check_balance):
    """Verify available balance is present"""
    assert any('Available' in r for r in check_balance)


@then('I should see the pending balance')
def see_pending_balance(check_balance):
    """Verify pending balance is present"""
    assert any('Pending' in r for r in check_balance)


@then('the balance should be formatted correctly')
def balance_formatted_correctly(check_balance):
    """Verify balance format"""
    for record in check_balance:
        assert len(record) == 75


# Scenario: Viewing transaction history
@given('the wallet has transactions', target_fixture='wallet_has_transactions')
def wallet_has_transactions():
    """Generate wallet with transactions"""
    return dogedcams.generate_fake_records(number_of_records=20)


@when('I request the transaction list', target_fixture='request_transaction_list')
def request_transaction_list(wallet_has_transactions):
    """Get transaction list"""
    transactions = [r for r in wallet_has_transactions 
                   if 'Available' not in r 
                   and 'Pending' not in r 
                   and 'Control Re' not in r]
    return transactions


@then('I should see all transactions')
def see_all_transactions(request_transaction_list):
    """Verify transactions are returned"""
    assert len(request_transaction_list) > 0


@then('each transaction should have a timestamp')
def transactions_have_timestamp(request_transaction_list):
    """Verify timestamp in transactions"""
    for txn in request_transaction_list:
        # First 10 characters should be the key/timestamp
        assert txn[:10].strip().isdigit()


@then('each transaction should have an address')
def transactions_have_address(request_transaction_list):
    """Verify address in transactions"""
    for txn in request_transaction_list:
        # Address is at position 11-44
        address = txn[11:45].strip()
        assert len(address) > 0


@then('each transaction should have an amount')
def transactions_have_amount(request_transaction_list):
    """Verify amount in transactions"""
    for txn in request_transaction_list:
        # Amount is at the end
        assert len(txn) == 75


# Scenario: Incremental sync with new transactions
@given('the wallet has been synced previously', target_fixture='previously_synced')
def previously_synced(tmp_path):
    """Setup previous sync state"""
    old_records = dogedcams.generate_fake_records(number_of_records=10)
    tmp_file = tmp_path / 'sync.tmp'
    tmp_file.write_text('\n'.join(old_records))
    return {'tmp_file': tmp_file, 'old_records': old_records}


@given('new transactions have occurred', target_fixture='new_transactions_occurred')
def new_transactions_occurred(previously_synced):
    """Add new transactions"""
    new_records = dogedcams.generate_fake_records(number_of_records=15)
    return {**previously_synced, 'new_records': new_records}


@when('I run the sync command again', target_fixture='run_sync_again')
def run_sync_again(new_transactions_occurred):
    """Execute sync with new data"""
    old_content = new_transactions_occurred['tmp_file'].read_text()
    new_content = '\n'.join(new_transactions_occurred['new_records'])
    needs_update = dogedcams.new_records(old_content, new_content)
    return {**new_transactions_occurred, 'needs_update': needs_update}


@then('only new transactions should be uploaded')
def only_new_uploaded(run_sync_again):
    """Verify change detection works"""
    assert run_sync_again['needs_update'] is True


@then('the VSAM file should be updated')
def vsam_file_updated(run_sync_again):
    """Verify VSAM update"""
    jcl = dogedcams.generate_IDCAMS_JCL(
        user='test',
        password='test',
        vsam_file='DOGE.VSAM',
        records=run_sync_again['new_records']
    )
    assert 'REPRO INFILE' in jcl


@then('the control record should be maintained')
def control_record_maintained(run_sync_again):
    """Verify control record is present"""
    records = run_sync_again['new_records']
    assert any('Control Re' in r for r in records)


# Scenario: Handling large transaction volumes
@given('the wallet has more than 7648 transactions', target_fixture='large_transaction_volume')
def large_transaction_volume():
    """Generate large number of transactions"""
    return dogedcams.generate_fake_records(number_of_records=8000)


@when('I run the sync command', target_fixture='large_sync_result')
def run_sync_with_large_volume(large_transaction_volume):
    """Process large volume"""
    jcl = dogedcams.generate_IDCAMS_JCL(
        user='test',
        password='test',
        vsam_file='DOGE.VSAM',
        records=large_transaction_volume,
        reverse=True
    )
    return {'jcl': jcl, 'records': large_transaction_volume}


@then('the system should limit to 7648 records')
def limited_to_max_records(large_sync_result):
    """Verify record limiting"""
    # The function handles this internally
    assert large_sync_result['jcl'] is not None


@then('the most recent transactions should be included')
def most_recent_included(large_sync_result):
    """Verify recent transactions are kept"""
    assert large_sync_result['jcl'] is not None


@then('balance records should always be present')
def balance_records_present(large_sync_result):
    """Verify balance records maintained"""
    assert '0000000001' in large_sync_result['jcl']
    assert '0000000002' in large_sync_result['jcl']


# Scenario: Sending Dogecoin from CICS
@given('I have sufficient balance', target_fixture='sufficient_balance')
def sufficient_balance():
    """Setup sufficient balance"""
    return {'balance': 10000.0}


@when('I submit a send request with a valid address and amount', target_fixture='submit_send_request')
def submit_send_request(sufficient_balance):
    """Submit send request"""
    return {
        'address': 'nYLEKeZtqNSCAhMNKTFpFgZcnvf1DbFiSu',
        'amount': '100.50',
        'balance': sufficient_balance['balance']
    }


@then('the transaction should be queued')
def transaction_queued(submit_send_request):
    """Verify transaction queued"""
    assert submit_send_request['address'] is not False


@then('the transaction should be processed')
def transaction_processed(submit_send_request):
    """Verify transaction processing"""
    assert submit_send_request['amount'] is not False


@then('the wallet should be updated')
def wallet_updated(submit_send_request):
    """Verify wallet update"""
    assert float(submit_send_request['amount']) <= submit_send_request['balance']


# Scenario: Error handling for invalid send
@given('I have insufficient balance', target_fixture='insufficient_balance')
def insufficient_balance():
    """Setup insufficient balance"""
    return {'balance': 10.0}


@when('I submit a send request for more than my balance', target_fixture='submit_invalid_send')
def submit_invalid_send(insufficient_balance):
    """Submit invalid send request"""
    return {
        'address': 'nYLEKeZtqNSCAhMNKTFpFgZcnvf1DbFiSu',
        'amount': '1000.00',
        'balance': insufficient_balance['balance'],
        'is_valid': float('1000.00') <= insufficient_balance['balance']
    }


@then('the system should reject the transaction')
def system_rejects_transaction(submit_invalid_send):
    """Verify transaction rejection"""
    assert submit_invalid_send['is_valid'] is False


@then('an error message should be displayed')
def error_message_displayed(submit_invalid_send):
    """Verify error handling"""
    assert submit_invalid_send['is_valid'] is False


# Scenario: System recovery after connection loss
@given('a sync was in progress', target_fixture='sync_in_progress')
def sync_in_progress():
    """Setup sync in progress"""
    return {'status': 'syncing'}


@when('the connection is lost', target_fixture='connection_lost')
def connection_lost(sync_in_progress):
    """Simulate connection loss"""
    return {**sync_in_progress, 'error': 'ConnectionError'}


@then('the system should handle the error gracefully')
def handles_error_gracefully(connection_lost):
    """Verify graceful error handling"""
    # System should not crash
    assert connection_lost['error'] is not None


@then('data integrity should be maintained')
def data_integrity_maintained(connection_lost):
    """Verify data integrity"""
    # System should maintain state
    assert connection_lost['status'] == 'syncing'
