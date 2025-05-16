"""
Gmail Organizer - Pub/Sub Notification Handler

This module handles real-time notifications from Gmail via Google Cloud Pub/Sub.
It processes incoming messages, fetches the corresponding email details,
and applies the same sorting logic used for past emails.
"""

import json
import logging
import base64
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from sortmate.authenticate import get_credentials
from sortmate.sort import get_date_label, fetch_labels, apply_labels_grouped

# set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('gmail_organizer')

# cache for Gmail API service instance
_gmail_service = None

def get_gmail_service():
    """
    Get or create a Gmail API service instance.
    
    Returns:
        A Gmail API service instance.
    """
    global _gmail_service
    if _gmail_service is None:
        credentials = get_credentials()
        _gmail_service = build('gmail', 'v1', credentials=credentials)
    return _gmail_service

def fetch_history(service, history_id, history_types=None):
    """
    Fetch email history changes from Gmail.
    
    Args:
        service: Gmail API service instance
        history_id (str): History ID to start from
        history_types (list, optional): Types of history to fetch, e.g., ['messageAdded']
        
    Returns:
        list: New message IDs from the history
    """
    logger.info(f"Fetching history starting from history ID: {history_id}")
    
    # default to messageAdded if no types specified
    if history_types is None:
        history_types = ['messageAdded']
    
    try:
        # request parameters
        params = {
            'userId': 'me',
            'startHistoryId': history_id,
            'historyTypes': history_types,
            'labelId': 'INBOX'  # Only look for changes in the inbox
        }
        
        # execute the request
        response = service.users().history().list(**params).execute()
        
        # extract new message IDs from the history
        new_message_ids = []
        
        if 'history' in response:
            for item in response['history']:
                # check for message additions
                if 'messagesAdded' in item:
                    for message in item['messagesAdded']:
                        msg = message.get('message', {})
                        # only include inbox messages
                        labels = msg.get('labelIds', [])
                        if 'INBOX' in labels:
                            new_message_ids.append(msg['id'])
        
        logger.info(f"Found {len(new_message_ids)} new messages")
        return new_message_ids
    
    except HttpError as e:
        logger.error(f"Error fetching history: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching history: {e}")
        return []

def process_new_email(service, message_id, label_cache):
    """
    Process a newly arrived email and apply date-based labels.
    
    Args:
        service: Gmail API service instance
        message_id (str): ID of the email to process
        label_cache (dict): Cache of label names to IDs
        
    Returns:
        tuple: Message ID and the date label ID if successful, or None if not
    """
    try:
        # get the full email details
        email = service.users().messages().get(userId='me', id=message_id).execute()
        
        # apply date-based labeling
        date_label = get_date_label(service, email, label_cache)
        
        if date_label:
            return (message_id, [date_label])
        
    except HttpError as e:
        logger.error(f"Error processing email {message_id}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error processing email {message_id}: {e}")
    
    return None

def decode_pubsub_message(message):
    """
    Decode the Pub/Sub message data.
    
    Args:
        message: The Pub/Sub message object
        
    Returns:
        dict: Decoded message data as a dictionary, or None if decoding fails
    """
    try:
        # the data field in a Pub/Sub message is base64-encoded
        if hasattr(message, 'data'):
            data_bytes = message.data
            decoded_data = base64.b64decode(data_bytes).decode('utf-8')
            return json.loads(decoded_data)
        else:
            logger.error("No data field in Pub/Sub message")
            return None
    except Exception as e:
        logger.error(f"Error decoding Pub/Sub message: {e}")
        return None

def callback(message):
    """
    Process Gmail notification messages from Pub/Sub.
    
    Args:
        message: The Pub/Sub message object
    """
    try:
        logger.info("Received Pub/Sub notification")
        
        # decode the message
        data = decode_pubsub_message(message)
        if not data:
            logger.warning("Could not decode message, acknowledging and continuing")
            message.ack()
            return
        
        logger.info(f"Notification data: {data}")
        
        # extract Gmail-specific details
        if 'historyId' in data and 'emailAddress' in data:
            history_id = data['historyId']
            email_address = data['emailAddress']
            
            logger.info(f"Processing Gmail notification for {email_address}, history ID: {history_id}")
            
            # get Gmail service
            service = get_gmail_service()
            
            # fetch email history to get new message IDs
            new_message_ids = fetch_history(service, history_id)
            
            if new_message_ids:
                # get label cache for efficient labeling
                label_cache = fetch_labels(service)
                
                # process each new email
                email_updates = []
                for msg_id in new_message_ids:
                    result = process_new_email(service, msg_id, label_cache)
                    if result:
                        email_updates.append(result)
                
                # apply labels in batch if we have any updates
                if email_updates:
                    apply_labels_grouped(service, email_updates)
                    logger.info(f"Applied date labels to {len(email_updates)} new emails")
                else:
                    logger.info("No new emails needed labeling")
        else:
            logger.warning("Message doesn't contain expected Gmail notification data")
    
    except Exception as e:
        logger.error(f"Error in Pub/Sub callback: {e}")
    
    finally:
        # always acknowledge the message to prevent redelivery
        message.ack()
        logger.info("Message acknowledged")