"""
Tests for the watch.py module in the SortMate package.
"""

import os
import pytest
from unittest.mock import MagicMock, patch

from sortmate.watch import start_watch, stop_watch


@patch.dict(os.environ, {
    "GOOGLE_CLOUD_PROJECT": "test-project",
    "PUBSUB_TOPIC": "test-topic"
})
def test_start_watch():
    """Test that start_watch correctly sets up Gmail API watch."""
    # Create a mock service
    mock_service = MagicMock()
    
    # Mock the watch response
    watch_response = {
        'historyId': '12345',
        'expiration': '1622505600000'
    }
    mock_service.users().watch().execute.return_value = watch_response
    
    # Call the function
    result = start_watch(mock_service)
    
    # Verify the service was called with correct parameters
    mock_service.users().watch.assert_called_once_with(
        userId='me',
        body={
            'labelIds': ['INBOX'],
            'topicName': 'projects/test-project/topics/test-topic',
            'labelFilterAction': 'include'
        }
    )
    
    # Verify the watch response was returned
    assert result == watch_response


def test_start_watch_missing_project():
    """Test that start_watch raises error when project ID is missing."""
    # Mock empty environment variables
    with patch.dict(os.environ, {}, clear=True):
        # Create a mock service
        mock_service = MagicMock()
        
        # Call the function and expect an error
        with pytest.raises(ValueError) as exc_info:
            start_watch(mock_service)
        
        # Verify the error message
        assert "GOOGLE_CLOUD_PROJECT environment variable not set" in str(exc_info.value)


def test_start_watch_missing_topic():
    """Test that start_watch raises error when topic name is missing."""
    # Mock environment with project but no topic
    with patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project"}, clear=True):
        # Create a mock service
        mock_service = MagicMock()
        
        # Call the function and expect an error
        with pytest.raises(ValueError) as exc_info:
            start_watch(mock_service)
        
        # Verify the error message
        assert "PUBSUB_TOPIC environment variable not set" in str(exc_info.value)


def test_stop_watch():
    """Test that stop_watch correctly stops Gmail API watch."""
    # Create a mock service
    mock_service = MagicMock()
    
    # Mock the stop response
    stop_response = {}
    mock_service.users().stop().execute.return_value = stop_response
    
    # Call the function
    result = stop_watch(mock_service)
    
    # Verify the service was called correctly
    mock_service.users().stop.assert_called_once_with(userId='me')
    
    # Verify the stop response was returned
    assert result == stop_response