"""
Tests for the authenticate.py module in the SortMate package.
"""

import os
import sys
import pytest
from unittest.mock import patch, mock_open, MagicMock

from sortmate.authenticate import get_token_path, get_credentials


@patch.dict(os.environ, {"GOOGLE_TOKEN_DIR": "/test/token/dir"})
def test_get_token_path():
    """Test that get_token_path correctly constructs the token path."""
    # Patch the sorted scopes hash
    with patch('sortmate.authenticate.SCOPES', ['scope1', 'scope2']):
        with patch('hashlib.md5') as mock_md5:
            # Configure the mock to return a predictable hash
            mock_hash = MagicMock()
            mock_hash.hexdigest.return_value = "abcdef1234567890"
            mock_md5.return_value = mock_hash
            
            path = get_token_path()
            
            # Verify the correct path is generated
            assert path == "/test/token/dir/google_token_abcdef12.pickle"


@patch('sortmate.authenticate.get_token_path')
@patch('sortmate.authenticate.os.makedirs')
@patch('sortmate.authenticate.os.path.exists')
@patch('sortmate.authenticate.pickle.load')
def test_get_credentials_from_file(mock_pickle_load, mock_path_exists, mock_makedirs, mock_get_token_path):
    """Test loading credentials from an existing token file."""
    # Setup our mocks
    mock_get_token_path.return_value = "/test/token/path"
    mock_path_exists.return_value = True
    
    # Create a mock credentials object
    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_pickle_load.return_value = mock_creds
    
    # Mock open to avoid actually opening files
    mock_file = mock_open()
    with patch('builtins.open', mock_file):
        # Call the function
        creds = get_credentials()
        
        # Verify we got the credentials from pickle
        assert creds == mock_creds
        mock_pickle_load.assert_called_once()


@patch('sortmate.authenticate.get_token_path')
@patch('sortmate.authenticate.os.makedirs')
@patch('sortmate.authenticate.os.path.exists')
@patch('sortmate.authenticate.InstalledAppFlow')
def test_get_credentials_new_flow(mock_flow, mock_path_exists, mock_makedirs, mock_get_token_path):
    """Test getting credentials via OAuth flow when no token exists."""
    # Mock environment variable
    with patch.dict(os.environ, {"GOOGLE_CLIENT_SECRETS_FILE": "/test/secret.json"}):
        # Setup our mocks
        mock_get_token_path.return_value = "/test/token/path"
        mock_path_exists.side_effect = [False, True]  # No token, but secrets file exists
        
        # Create a mock flow
        mock_flow_instance = MagicMock()
        mock_creds = MagicMock()
        mock_flow_instance.run_local_server.return_value = mock_creds
        mock_flow.from_client_secrets_file.return_value = mock_flow_instance
        
        # Mock open to avoid actually opening files
        mock_file = mock_open()
        with patch('builtins.open', mock_file):
            # Call the function
            creds = get_credentials()
            
            # Verify flow was created with correct arguments
            mock_flow.from_client_secrets_file.assert_called_once_with(
                "/test/secret.json", 
                ['https://www.googleapis.com/auth/gmail.modify', 
                 'https://www.googleapis.com/auth/gmail.labels']
            )
            
            # Verify we got credentials from the flow
            assert creds == mock_creds
            
            # Verify credentials were saved
            mock_file.assert_called_once_with('/test/token/path', 'wb')


@patch('sortmate.authenticate.get_token_path')
@patch('sortmate.authenticate.os.makedirs')
@patch('sortmate.authenticate.os.path.exists')
@patch('sortmate.authenticate.pickle.load')
@patch('sortmate.authenticate.Request')
def test_get_credentials_refresh(mock_request, mock_pickle_load, mock_path_exists, mock_makedirs, mock_get_token_path):
    """Test refreshing expired credentials."""
    # Setup our mocks
    mock_get_token_path.return_value = "/test/token/path"
    mock_path_exists.return_value = True
    
    # Create a mock credentials object that needs refreshing
    mock_creds = MagicMock()
    mock_creds.valid = False
    mock_creds.expired = True
    mock_creds.refresh_token = True
    mock_pickle_load.return_value = mock_creds
    
    # Mock open to avoid actually opening files
    mock_file = mock_open()
    with patch('builtins.open', mock_file):
        # Call the function
        creds = get_credentials()
        
        # Verify credentials were refreshed
        mock_creds.refresh.assert_called_once_with(mock_request())
        
        # Verify we got the refreshed credentials
        assert creds == mock_creds