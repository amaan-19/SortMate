"""
Tests for the label handling functions in the sort.py module.
"""

import pytest
from unittest.mock import MagicMock, patch
from sortmate.sort import (
    fetch_labels,
    label_exists,
    create_label,
    get_date_label,
    batch_get_email_details
)


@pytest.fixture
def mock_gmail_service():
    """Create a mock Gmail service object."""
    mock_service = MagicMock()
    
    # Mock the labels.list method response
    mock_response = {
        'labels': [
            {'id': 'Label_1', 'name': '2025'},
            {'id': 'Label_2', 'name': '2025/May'},
            {'id': 'Label_3', 'name': 'Inbox'},
        ]
    }
    
    # Configure the mock to return our sample data
    mock_service.users().labels().list().execute.return_value = mock_response
    
    return mock_service


@pytest.fixture
def label_cache():
    """Create a sample label cache."""
    return {
        '2025': 'Label_1',
        '2025/May': 'Label_2',
        'Inbox': 'Label_3',
    }


def test_fetch_labels(mock_gmail_service):
    """Test that fetch_labels correctly retrieves and caches labels."""
    # Call the function with our mock service
    result = fetch_labels(mock_gmail_service)
    
    # Verify the mock was called correctly
    mock_gmail_service.users().labels().list.assert_called_once_with(userId='me')
    
    # Verify the returned cache has the expected values
    assert result == {
        '2025': 'Label_1',
        '2025/May': 'Label_2',
        'Inbox': 'Label_3',
    }


def test_label_exists(label_cache):
    """Test that label_exists correctly checks if a label is in the cache."""
    # Test with an existing label
    assert label_exists('2025', label_cache) is True
    
    # Test with a non-existent label
    assert label_exists('NonExistent', label_cache) is False


def test_create_label_new(mock_gmail_service, label_cache):
    """Test creating a new label that doesn't exist yet."""
    # Mock the labels.create method response
    new_label = {'id': 'Label_4', 'name': '2024'}
    mock_gmail_service.users().labels().create().execute.return_value = new_label
    
    # Call the function with our mocks
    result = create_label(mock_gmail_service, '2024', label_cache)
    
    # Verify the mock was called correctly
    mock_gmail_service.users().labels().create.assert_called_once()
    
    # Verify the label cache was updated
    assert label_cache['2024'] == 'Label_4'
    
    # Verify the returned label ID
    assert result == 'Label_4'


@patch('sortmate.sort.create_label')
def test_get_date_label(mock_create_label, mock_gmail_service, label_cache):
    """Test that get_date_label extracts date from email and gets/creates labels."""
    # Mock the create_label function
    mock_create_label.return_value = 'Label_4'
    
    # Create a sample email with a date header
    email = {
        'id': 'msg123',
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'test@example.com'},
                {'name': 'Date', 'value': 'Mon, 15 May 2025 14:23:01 +0000'},
                {'name': 'Subject', 'value': 'Test email'}
            ]
        }
    }
    
    # Test with a date that has an existing month label
    result = get_date_label(mock_gmail_service, email, label_cache)
    
    # Verify the result
    assert result == 'Label_2'  # Should find existing '2025/May' label
    
    # Now test with a different date that requires new labels
    # Update the email date
    email['payload']['headers'][1]['value'] = 'Fri, 10 Jun 2025 09:30:00 +0000'
    
    # Since we don't have Jun label yet, mock_create_label should be called
    # and we should get back a new label ID
    mock_create_label.side_effect = ['Label_5']  # Return for '2025/Jun'
    
    # Call the function again with the updated email
    result = get_date_label(mock_gmail_service, email, label_cache)
    
    # Verify mock_create_label was called for the new month
    mock_create_label.assert_called_with(mock_gmail_service, '2025/Jun', label_cache)
    
    # Verify the returned label matches what mock_create_label returned
    assert result == 'Label_5'


def test_batch_get_email_details(mock_gmail_service):
    """Test that batch_get_email_details correctly processes message IDs in batches."""
    # Sample messages to be returned by the API
    sample_messages = [
        {'id': 'msg1', 'snippet': 'test message 1'},
        {'id': 'msg2', 'snippet': 'test message 2'},
        {'id': 'msg3', 'snippet': 'test message 3'},
    ]
    
    # Configure the mock BatchHttpRequest
    class MockBatchHttpRequest:
        def __init__(self, callback, batch_uri):
            self.callback = callback
            self.batch_uri = batch_uri
            self.requests = []
        
        def add(self, request, request_id=None):
            self.requests.append((request, request_id))
        
        def execute(self):
            # Simulate executing the batch by calling callback for each request
            for i, (request, _) in enumerate(self.requests):
                # Use request_id as index to sample_messages
                self.callback(i, sample_messages[i], None)
    
    # Patch the BatchHttpRequest class
    with patch('sortmate.sort.BatchHttpRequest', MockBatchHttpRequest):
        result = batch_get_email_details(mock_gmail_service, ['msg1', 'msg2', 'msg3'], batch_size=2)
        
        # Verify we got all 3 messages back
        assert len(result) == 3
        assert result[0]['id'] == 'msg1'
        assert result[1]['id'] == 'msg2'
        assert result[2]['id'] == 'msg3'