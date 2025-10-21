"""
Unit tests for dogedcams.py
Tests individual functions in isolation
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, mock_open, MagicMock
from decimal import Decimal

# Add PYTHON directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../PYTHON'))

import dogedcams


@pytest.mark.unit
class TestGenerateFakeRecords:
    """Test the generate_fake_records function"""
    
    def test_generate_fake_records_default(self):
        """Test generating default number of fake records"""
        records = dogedcams.generate_fake_records()
        # Function generates records from 1 to number_of_records, plus 2 balance records + 1 control
        # With default 100, it generates: balance(2) + range(1,100)=99 + control(1) = 102 total
        assert len(records) >= 100  # At least 100 records
        # Check first record is Available balance
        assert "Available" in records[0]
        # Check second record is Pending balance
        assert "Pending" in records[1]
        # Check last record is control record
        assert "Control Re" in records[-1]  # Truncated to fit format
        assert "9999999999" in records[-1]
    
    def test_generate_fake_records_custom_count(self):
        """Test generating custom number of fake records"""
        records = dogedcams.generate_fake_records(number_of_records=10)
        # Function generates: balance(2) + range(1,10)=9 + control(1) = 12 total
        assert len(records) >= 10  # At least 10 records
    
    def test_generate_fake_records_format(self):
        """Test that generated records have correct format"""
        records = dogedcams.generate_fake_records(number_of_records=5)
        for record in records:
            # Check record length (75 characters actual)
            assert len(record) == 75
            # Records should contain numbers and text
            assert isinstance(record, str)


@pytest.mark.unit
class TestNewRecords:
    """Test the new_records function"""
    
    def test_no_new_records(self):
        """Test when there are no new records"""
        old = "record1\nrecord2"
        new = "record1\nrecord2"
        assert dogedcams.new_records(old, new) is False
    
    def test_has_new_records(self):
        """Test when there are new records"""
        old = "record1\nrecord2"
        new = "record1\nrecord2\nrecord3"
        assert dogedcams.new_records(old, new) is True


@pytest.mark.unit
class TestGenerateIDCAMSJCL:
    """Test the generate_IDCAMS_JCL function"""
    
    def test_generate_jcl_basic(self):
        """Test basic JCL generation"""
        records = ["record1", "record2"]
        jcl = dogedcams.generate_IDCAMS_JCL(
            user='testuser',
            password='testpass',
            vsam_file='TEST.VSAM',
            records=records,
            volume='VOL001'
        )
        
        assert 'TESTUSER' in jcl  # Should be uppercase
        assert 'TESTPASS' in jcl
        assert 'TEST.VSAM' in jcl
        assert 'VOL001' in jcl
        assert 'record1' in jcl
        assert 'record2' in jcl
    
    def test_generate_jcl_case_conversion(self):
        """Test that JCL converts to uppercase"""
        jcl = dogedcams.generate_IDCAMS_JCL(
            user='lowercase',
            password='password',
            vsam_file='test.vsam',
            records=['test'],
            volume='vol'
        )
        
        assert 'LOWERCASE' in jcl
        assert 'TEST.VSAM' in jcl
        assert 'VOL' in jcl
    
    def test_generate_jcl_max_records_reverse(self):
        """Test JCL generation with more than max records (reverse mode)"""
        # Create more than 7648 records
        records = ["record{}".format(i) for i in range(8000)]
        # Add special first and second records
        records[0] = "0000000001 address1                           label1     +00000000.12345678"
        records[1] = "0000000002 address2                           label2     +00000000.23456789"
        
        jcl = dogedcams.generate_IDCAMS_JCL(
            user='test',
            password='test',
            vsam_file='TEST.VSAM',
            records=records,
            volume='VOL',
            reverse=True
        )
        
        # Should contain the special first two records
        assert "0000000001" in jcl
        assert "0000000002" in jcl
    
    def test_generate_jcl_max_records_no_reverse(self):
        """Test JCL generation with more than max records (no reverse)"""
        # Create more than 7648 records
        records = ["record{}".format(i) for i in range(8000)]
        records[-1] = "9999999999 0                                  Control Re +00000000.00000000"
        
        jcl = dogedcams.generate_IDCAMS_JCL(
            user='test',
            password='test',
            vsam_file='TEST.VSAM',
            records=records,
            volume='VOL',
            reverse=False
        )
        
        # Should contain the control record
        assert "9999999999" in jcl


@pytest.mark.unit
class TestGetRecords:
    """Test the get_records function with mocked RPC calls"""
    
    @patch('dogedcams.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data='rpcuser=testuser\nrpcpassword=testpass\n')
    @patch('os.path.isfile', return_value=True)
    def test_get_records_success(self, mock_isfile, mock_file, mock_post):
        """Test successful record retrieval"""
        # Mock responses for different RPC calls
        mock_responses = [
            Mock(json=lambda: {'result': 1000.0}),  # getbalance
            Mock(json=lambda: {'result': 50.0}),    # getunconfirmedbalance
            Mock(json=lambda: {'result': [          # listtransactions
                {
                    'timereceived': 1234567890,
                    'address': 'nYLEKeZtqNSCAhMNKTFpFgZcnvf1DbFiSu',
                    'amount': 100.5,
                    'label': 'Test'
                }
            ]})
        ]
        mock_post.side_effect = mock_responses
        
        with patch('configparser.ConfigParser.read_string'):
            records = dogedcams.get_records(
                host='localhost',
                rpcUser='testuser',
                rpcPass='testpass',
                rpcPort=22555
            )
        
        # Should have balance, pending, transaction, and control record
        assert len(records) >= 4
        assert 'Available' in records[0]
        assert 'Pending' in records[1]
        assert 'Control Re' in records[-1]  # Truncated in format
    
    @patch('dogedcams.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data='rpcuser=testuser\nrpcpassword=testpass\n')
    def test_get_records_connection_error(self, mock_file, mock_post):
        """Test handling of connection errors"""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectTimeout()
        
        with patch('configparser.ConfigParser.read_string'):
            with pytest.raises(SystemExit):
                dogedcams.get_records(
                    host='localhost',
                    rpcUser='testuser',
                    rpcPass='testpass'
                )


@pytest.mark.unit
class TestSendJCL:
    """Test the send_jcl function"""
    
    @patch('socket.socket')
    def test_send_jcl_success(self, mock_socket):
        """Test successful JCL sending"""
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        
        jcl = "//TEST JOB"
        dogedcams.send_jcl(hostname='localhost', port=3505, jcl=jcl)
        
        # Verify socket operations
        mock_sock_instance.connect.assert_called_once_with(('localhost', 3505))
        mock_sock_instance.sendall.assert_called_once()
        mock_sock_instance.close.assert_called_once()
    
    @patch('socket.socket')
    def test_send_jcl_with_print(self, mock_socket):
        """Test JCL sending with print option"""
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        
        jcl = "//TEST JOB"
        dogedcams.send_jcl(hostname='localhost', port=3505, jcl=jcl, print_jcl=True)
        
        mock_sock_instance.connect.assert_called_once()


@pytest.mark.unit
class TestGetCommands:
    """Test the get_commands function"""
    
    @patch('socket.socket')
    @patch('time.time')
    def test_get_commands_with_transaction(self, mock_time, mock_socket):
        """Test getting commands from printer"""
        # Mock socket to return transaction data
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        
        # Simulate time progression
        mock_time.side_effect = [0, 0.5, 1.0, 5.0]
        
        # Simulate receiving data with DOGECICS99 marker
        test_data = b"DOGECICS99 nYLEKeZtqNSCAhMNKTFpFgZcnvf1DbFiSu 100.50"
        mock_sock_instance.recv.side_effect = [test_data, b'']
        
        commands = dogedcams.get_commands(timeout=2, hostname='localhost', port=3506)
        
        assert len(commands) >= 1
        if len(commands) > 0:
            assert 'address' in commands[0]
            assert 'amount' in commands[0]


@pytest.mark.unit
class TestSendDoge:
    """Test the send_doge function"""
    
    @patch('dogedcams.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data='rpcuser=testuser\nrpcpassword=testpass\n')
    def test_send_doge_success(self, mock_file, mock_post):
        """Test successful doge sending"""
        mock_response = Mock()
        mock_response.json.return_value = {'result': 'txid12345'}
        mock_post.return_value = mock_response
        
        with patch('configparser.ConfigParser.read_string'):
            result = dogedcams.send_doge(
                address='nYLEKeZtqNSCAhMNKTFpFgZcnvf1DbFiSu',
                amount=100.0,
                host='localhost',
                rpcUser='testuser',
                rpcPass='testpass'
            )
        
        # Verify the post was called
        mock_post.assert_called_once()
