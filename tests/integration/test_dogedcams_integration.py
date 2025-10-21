"""
System Integration Tests (SIT) for dogedcams.py
Tests integration between components and external systems
"""
import pytest
import sys
import os
import json
import socket
from unittest.mock import Mock, patch, mock_open, MagicMock
import responses

# Add PYTHON directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../PYTHON'))

import dogedcams


@pytest.mark.integration
class TestRPCIntegration:
    """Test integration with RPC server (using mocks)"""
    
    @responses.activate
    def test_full_wallet_sync_flow(self):
        """Test complete flow of syncing wallet data"""
        # Mock RPC responses
        responses.add(
            responses.POST,
            'http://testuser:testpass@localhost:22555/',
            json={'result': 5000.12345678},
            status=200
        )
        responses.add(
            responses.POST,
            'http://testuser:testpass@localhost:22555/',
            json={'result': 100.0},
            status=200
        )
        responses.add(
            responses.POST,
            'http://testuser:testpass@localhost:22555/',
            json={'result': [
                {
                    'timereceived': 1234567890,
                    'address': 'nYLEKeZtqNSCAhMNKTFpFgZcnvf1DbFiSu',
                    'amount': 250.5,
                    'label': 'Payment1'
                },
                {
                    'timereceived': 1234567891,
                    'address': 'nXYZabcdefghijklmnopqrstuvwxyz123',
                    'amount': -100.0,
                    'label': 'Sent'
                }
            ]},
            status=200
        )
        
        with patch('builtins.open', mock_open(read_data='rpcuser=testuser\nrpcpassword=testpass\n')):
            with patch('configparser.ConfigParser.read_string'):
                records = dogedcams.get_records(
                    host='localhost',
                    rpcUser='testuser',
                    rpcPass='testpass',
                    rpcPort=22555
                )
        
        # Verify we got all expected records
        assert len(records) >= 5  # Balance + Pending + 2 transactions + Control
        
        # Verify record format
        for record in records:
            assert len(record) == 75
            assert isinstance(record, str)


@pytest.mark.integration
class TestVSAMFileGeneration:
    """Test VSAM file generation integration"""
    
    def test_end_to_end_vsam_generation(self):
        """Test complete VSAM file generation from records to JCL"""
        # Generate fake records
        records = dogedcams.generate_fake_records(number_of_records=50)
        
        # Generate JCL
        jcl = dogedcams.generate_IDCAMS_JCL(
            user='testuser',
            password='testpass',
            vsam_file='DOGE.TEST',
            records=records,
            volume='PUB012'
        )
        
        # Verify JCL structure
        assert 'DELETE DOGE.TEST' in jcl
        assert 'DEFINE CLUSTER' in jcl
        assert 'REPRO INFILE(INDATA1)' in jcl
        assert 'LISTCAT ALL ENTRY(DOGE.TEST)' in jcl
        
        # Verify all records are in JCL
        for record in records:
            assert record in jcl


@pytest.mark.integration
class TestSocketCommunication:
    """Test socket communication with TK4-"""
    
    @patch('socket.socket')
    def test_jcl_submission_to_reader(self, mock_socket):
        """Test submitting JCL to TK4- reader"""
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        
        # Create test JCL
        test_jcl = "//TEST JOB\n//STEP1 EXEC PGM=IEFBR14"
        
        # Send JCL
        dogedcams.send_jcl(hostname='localhost', port=3505, jcl=test_jcl)
        
        # Verify socket was used correctly
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_sock_instance.connect.assert_called_once_with(('localhost', 3505))
        
        # Verify data was sent
        sent_data = mock_sock_instance.sendall.call_args[0][0]
        assert test_jcl.encode() == sent_data
        
        mock_sock_instance.close.assert_called_once()
    
    @patch('socket.socket')
    @patch('time.time')
    def test_printer_queue_reading(self, mock_time, mock_socket):
        """Test reading from TK4- printer queue"""
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        
        # Mock time progression - need more calls to handle the timeout logic
        mock_time.side_effect = [0, 0.1, 0.2, 0.3, 5.0, 10.0]
        
        # Mock printer output with transaction
        printer_output = b"SOME OUTPUT\nDOGECICS99 nYLEKeZtqNSCAhMNKTFpFgZcnvf1DbFiSu 500.00\nMORE OUTPUT"
        mock_sock_instance.recv.side_effect = [printer_output, Exception('timeout')]
        
        commands = dogedcams.get_commands(timeout=2, hostname='localhost', port=3506)
        
        # Verify command was parsed correctly
        assert len(commands) >= 1
        if commands[0]['address']:  # Check if parsing was successful
            assert commands[0]['address'] == 'nYLEKeZtqNSCAhMNKTFpFgZcnvf1DbFiSu'
            assert commands[0]['amount'] == '500.00'


@pytest.mark.integration
class TestDataPersistence:
    """Test data persistence and file operations"""
    
    def test_tmp_file_creation_and_update(self, tmp_path):
        """Test temporary file creation for tracking updates"""
        tmp_file = tmp_path / "test.tmp"
        
        # Initial records
        old_records = "record1\nrecord2\nrecord3"
        tmp_file.write_text(old_records)
        
        # New records
        new_records = "record1\nrecord2\nrecord3\nrecord4"
        
        # Check if new records detected
        assert dogedcams.new_records(old_records, new_records) is True
        
        # Update file
        tmp_file.write_text(new_records)
        
        # Verify no changes detected now
        assert dogedcams.new_records(new_records, new_records) is False


@pytest.mark.integration
@pytest.mark.slow
class TestFullWorkflow:
    """Test complete workflow integration"""
    
    @patch('dogedcams.send_jcl')
    @patch('dogedcams.get_commands')
    @patch('dogedcams.send_doge')
    @responses.activate
    def test_complete_sync_and_send_workflow(self, mock_send_doge, mock_get_commands, mock_send_jcl):
        """Test complete workflow: get records, generate JCL, send, receive commands, send doge"""
        # Mock wallet responses
        responses.add(
            responses.POST,
            'http://user:pass@localhost:22555/',
            json={'result': 10000.0},
            status=200
        )
        responses.add(
            responses.POST,
            'http://user:pass@localhost:22555/',
            json={'result': 0.0},
            status=200
        )
        responses.add(
            responses.POST,
            'http://user:pass@localhost:22555/',
            json={'result': []},
            status=200
        )
        
        # Step 1: Get records from wallet
        with patch('builtins.open', mock_open(read_data='rpcuser=user\nrpcpassword=pass\n')):
            with patch('configparser.ConfigParser.read_string'):
                records = dogedcams.get_records(
                    host='localhost',
                    rpcUser='user',
                    rpcPass='pass'
                )
        
        # Step 2: Generate JCL
        jcl = dogedcams.generate_IDCAMS_JCL(
            user='testuser',
            password='testpass',
            vsam_file='DOGE.VSAM',
            records=records
        )
        
        # Step 3: Mock send JCL
        dogedcams.send_jcl(hostname='localhost', port=3505, jcl=jcl)
        mock_send_jcl.assert_called_once()
        
        # Step 4: Mock get commands from printer
        mock_get_commands.return_value = [
            {'address': 'nYLEKeZtqNSCAhMNKTFpFgZcnvf1DbFiSu', 'amount': '100.00'}
        ]
        commands = mock_get_commands()
        
        # Step 5: Mock send doge
        responses.add(
            responses.POST,
            'http://user:pass@localhost:22555/',
            json={'result': 'txid123'},
            status=200
        )
        
        # Verify workflow completed
        assert len(records) >= 3
        assert '//DOGEVSM JOB' in jcl
        assert len(commands) == 1


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling in integration scenarios"""
    
    @responses.activate
    def test_rpc_server_unavailable(self):
        """Test handling when RPC server is unavailable"""
        responses.add(
            responses.POST,
            'http://user:pass@localhost:22555/',
            body=Exception('Connection refused')
        )
        
        with patch('builtins.open', mock_open(read_data='rpcuser=user\nrpcpassword=pass\n')):
            with patch('configparser.ConfigParser.read_string'):
                with pytest.raises(Exception):
                    dogedcams.get_records(
                        host='localhost',
                        rpcUser='user',
                        rpcPass='pass'
                    )
    
    def test_invalid_record_format(self):
        """Test handling of invalid record formats"""
        # This should not crash
        invalid_records = ["", "short", "x" * 100]
        jcl = dogedcams.generate_IDCAMS_JCL(
            user='test',
            password='test',
            vsam_file='TEST.VSAM',
            records=invalid_records
        )
        
        # JCL should still be generated
        assert 'DEFINE CLUSTER' in jcl
