"""
Tests for the pubsub.py module in the SortMate package.
"""

import json
import base64
import pytest
from unittest.mock import MagicMock, patch

from sortmate.pubsub import (
    callback, 
    decode_pubsub_message, 
    fetch_history, 
    process_new_email,
    get_gmail_service
)


@pytest.fixture
def mock_pubsub_message():
    """Create a mock Pub/Sub message."""
    # Sample Gmail notification data
    notification_data = {
        "emailAddress": "test@example.com",
        "historyId": "12345"
    }
    
    # Create a mock message object
    message = MagicMock()
    
    # Base64 encode the notification data as it would be in a real message
    encoded_data = base64.b64encode(json.dumps(notification_data).encode('utf-8'))
    message.data = encoded_data
    
    return message


def test_decode_pubsub_message(mock_pubsub_message):
    """Test that decode_pubsub_message correctly decodes message data."""
    result = decode_pubsub_message(mock_pubsub_message)
    
    # Verify the decoded data
    assert result == {
        "emailAddress": "test@example.com",
        "historyId": "12345"
    }


def test_decode_pubsub_message_invalid():
    """Test that decode_pubsub_message handles invalid messages."""
    # Message with no data attribute
    message = MagicMock(spec=[])
    result = decode_pubsub_message(message)
    assert result is None
    
    # Message with invalid data
    message = MagicMock()
    message.data = b'not valid json'
    result = decode_pubsub_message(message)
    assert result is None


@patch('sortmate.pubsub.get_gmail_service')
def test_fetch_history(mock_get_service):
    """Test that fetch_history correctly retrieves email history."""
    # Setup mock service
    mock_service = MagicMock()
    mock_get_service.return_value = mock_service
    
    # Mock history response
    history_response = {
        'history': [
            {
                'messagesAdded': [
                    {
                        'message': {
                            'id': 'msg1',
                            'labelIds': ['INBOX']
                        }
                    },
                    {
                        'message': {
                            'id': 'msg2',
                            'labelIds': ['INBOX', 'UNREAD']
                        }
                    }
                ]
            },
            {
                'messagesAdded': [
                    {
                        'message': {
                            'id': 'msg3',
                            'labelIds': ['SENT']  # Not in INBOX
                        }
                    }
                ]
            }
        ]
    }
    
    # Configure the mock to return our sample data
    mock_service.users().history().list().execute.return_value = history_response
    
    # Call the function
    result = fetch_history(mock_service, "12345")
    
    # Verify the mock was called correctly
    mock_service.users().history().list.assert_called_once_with(
        userId='me',
        startHistoryId='12345',
        historyTypes=['messageAdded'],
        labelId='INBOX'
    )
    
    # Verify we got the correct message IDs (only those in INBOX)
    assert result == ['msg1', 'msg2']


@patch('sortmate.pubsub.get_date_label')
def test_process_new_email(mock_get_date_label):
    """Test that process_new_email correctly processes a new email."""
    # Setup mock service
    mock_service = MagicMock()
    
    # Mock email response
    email = {
        'id': 'msg1',
        'payload': {
            'headers': [
                {'name': 'Date', 'value': 'Mon, 15 May 2025 14:23:01 +0000'}
            ]
        }
    }
    
    # Configure the mock to return our sample email
    mock_service.users().messages().get().execute.return_value = email
    
    # Mock get_date_label to return a label ID
    mock_get_date_label.return_value = 'Label_1'
    
    # Sample label cache
    label_cache = {'2025/May': 'Label_1'}
    
    # Call the function
    result = process_new_email(mock_service, 'msg1', label_cache)
    
    # Verify the mock was called correctly
    mock_service.users().messages().get.assert_called_once_with(userId='me', id='msg1')
    
    # Verify get_date_label was called with the right arguments
    mock_get_date_label.assert_called_once_with(mock_service, email, label_cache)
    
    # Verify the returned result
    assert result == ('msg1', ['Label_1'])


@patch('sortmate.pubsub.get_gmail_service')
@patch('sortmate.pubsub.fetch_history')
@patch('sortmate.pubsub.fetch_labels')
@patch('sortmate.pubsub.process_new_email')
@patch('sortmate.pubsub.apply_labels_grouped')
def test_callback(mock_apply_labels, mock_process_email, mock_fetch_labels, 
                  mock_fetch_history, mock_get_service, mock_pubsub_message):
    """Test the main callback function for processing Pub/Sub messages."""
    # Setup mocks
    mock_service = MagicMock()
    mock_get_service.return_value = mock_service
    
    # Mock history response (return 2 message IDs)
    mock_fetch_history.return_value = ['msg1', 'msg2']
    
    # Mock label cache
    mock_label_cache = {'2025/May': 'Label_1'}
    mock_fetch_labels.return_value = mock_label_cache
    
    # Mock email processing (return update tuples)
    mock_process_email.side_effect = [
        ('msg1', ['Label_1']),  # First email gets a label
        None  # Second email doesn't need labeling
    ]
    
    # Call the callback function
    callback(mock_pubsub_message)
    
    # Verify the message was acknowledged
    mock_pubsub_message.ack.assert_called_once()
    
    # Verify Gmail service was retrieved
    mock_get_service.assert_called_once()
    
    # Verify history was fetched with correct historyId
    mock_fetch_history.assert_called_once_with(mock_service, '12345')
    
    # Verify labels were fetched
    mock_fetch_labels.assert_called_once_with(mock_service)
    
    # Verify emails were processed
    assert mock_process_email.call_count == 2
    mock_process_email.assert_any_call(mock_service, 'msg1', mock_label_cache)
    mock_process_email.assert_any_call(mock_service, 'msg2', mock_label_cache)
    
    # Verify labels were applied
    mock_apply_labels.assert_called_once_with(mock_service, [('msg1', ['Label_1'])])


def test_get_gmail_service():
    """Test that get_gmail_service returns a service instance."""
    with patch('sortmate.pubsub.get_credentials') as mock_get_credentials:
        with patch('sortmate.pubsub.build') as mock_build:
            # First call should create a new service
            get_gmail_service()
            
            # Verify credentials were retrieved
            mock_get_credentials.assert_called_once()
            
            # Verify Gmail API service was built
            mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_get_credentials())
            
            # Reset the mocks
            mock_get_credentials.reset_mock()
            mock_build.reset_mock()
            
            # Second call should use cached service
            get_gmail_service()
            
            # Verify credentials were not retrieved again
            mock_get_credentials.assert_not_called()
            
            # Verify Gmail API service was not built again
            mock_build.assert_not_called()