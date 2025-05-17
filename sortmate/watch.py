"""
Gmail Organizer - Watch Module

This module contains functions to set up the Gmail API notification system.
It configures Gmail to send notifications to a Google Cloud Pub/Sub topic
when new emails arrive in the user's inbox.
"""

import os
import logging
from googleapiclient.errors import HttpError

# Set up logging
logger = logging.getLogger('sortmate.watch')

def start_watch(service):
    """
    Set up Gmail API notification for inbox changes.
    
    Args:
        service: Gmail API service instance
        
    Returns:
        dict: Response from Gmail API with watch details
        
    Raises:
        ValueError: If required environment variables are not set
        HttpError: If there's an error setting up the watch
    """
    # Get configuration from environment variables
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set")
    
    topic_name = os.environ.get('PUBSUB_TOPIC')
    if not topic_name:
        raise ValueError("PUBSUB_TOPIC environment variable not set")
    
    # Form the full topic path
    topic_path = f"projects/{project_id}/topics/{topic_name}"
    
    logger.info(f"Setting up Gmail API watch notification for topic: {topic_path}")
    
    # Create the watch request
    request_body = {
        'labelIds': ['INBOX'],  # Only monitor the INBOX label
        'topicName': topic_path,
        'labelFilterAction': 'include'  # Only include events for listed labels
    }
    
    try:
        # Submit the watch request
        response = service.users().watch(userId='me', body=request_body).execute()
        
        # Log watch details
        history_id = response.get('historyId', 'unknown')
        expiration = response.get('expiration', 'unknown')
        
        logger.info(f"Watch established. History ID: {history_id}, Expiration: {expiration}")
        logger.info(f"Watch details: {response}")
        
        return response
    
    except HttpError as e:
        logger.error(f"Error setting up Gmail API watch: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in start_watch: {e}")
        raise

def stop_watch(service):
    """
    Stop Gmail API notification.
    
    Args:
        service: Gmail API service instance
        
    Returns:
        dict: Response from Gmail API
    """
    logger.info("Stopping Gmail API watch notification")
    
    try:
        response = service.users().stop(userId='me').execute()
        logger.info("Watch stopped successfully")
        return response
    
    except HttpError as e:
        logger.error(f"Error stopping Gmail API watch: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in stop_watch: {e}")
        raise