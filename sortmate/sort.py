"""
Gmail Label Organizer - Email Sorting Module

This module contains functions to sort emails by date (year/month) using Gmail API.
It creates appropriate labels and applies them to emails in batches for efficiency.
"""

import logging
from collections import defaultdict
from email.utils import parsedate_to_datetime

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import BatchHttpRequest

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('gmail_organizer')


def format_date(date_str):
    """
    Parse email date string and extract year and month.
    
    Args:
        date_str (str): Date string from email header
        
    Returns:
        tuple: (year, month) as strings, or (None, None) if parsing fails
    """
    try:
        parsed_date = parsedate_to_datetime(date_str)
        year = str(parsed_date.year)
        month = parsed_date.strftime('%b')
        return year, month
    except Exception as e:
        logger.error(f"Error parsing date '{date_str}': {e}")
        return None, None


def fetch_labels(service):
    """
    Fetch all existing Gmail labels and create a cache mapping names to IDs.
    
    Args:
        service: Gmail API service instance
        
    Returns:
        dict: Label name to label ID mapping
    """
    logger.info("Fetching labels and populating cache...")
    label_cache = {}
    
    try:
        response = service.users().labels().list(userId='me').execute()
        for label in response.get('labels', []):
            label_cache[label['name']] = label['id']
        logger.info(f"Fetched {len(label_cache)} labels")
        return label_cache
    except HttpError as e:
        logger.error(f"Error fetching labels: {e}")
        return {}


def label_exists(label_name, label_cache):
    """
    Check if a label exists in the label cache.
    
    Args:
        label_name (str): Name of the label to check
        label_cache (dict): Cache of label names to IDs
        
    Returns:
        bool: True if the label exists, False otherwise
    """
    return label_name in label_cache


def create_label(service, label_name, label_cache):
    """
    Create a new Gmail label and update the label cache.
    
    Args:
        service: Gmail API service instance
        label_name (str): Name of the label to create
        label_cache (dict): Cache of label names to IDs to update
        
    Returns:
        str: ID of the created or existing label
    """
    logger.info(f"Creating label: {label_name}")
    
    # define new label body
    label_body = {
        'name': label_name,
        'labelListVisibility': 'labelShow',
        'messageListVisibility': 'show',
    }
    
    try:
        # try to create the label
        new_label = service.users().labels().create(userId='me', body=label_body).execute()
        label_id = new_label['id']
        
        # update cache
        label_cache[label_name] = label_id
        logger.info(f"Label '{label_name}' created with ID: {label_id}")
        
        return label_id
    except HttpError as e:
        if e.resp.status == 409:  # label already exists
            logger.info(f"Label '{label_name}' already exists")
            
            # if the label exists but isn't in our cache, fetch all labels again
            if label_name not in label_cache:
                logger.info("Refreshing label cache")
                new_cache = fetch_labels(service)
                label_cache.update(new_cache)
            
            return label_cache.get(label_name)
        else:
            logger.error(f"Error creating label '{label_name}': {e}")
            raise


def batch_get_email_details(service, message_ids, batch_size=5):
    """
    Retrieve email details in batches for efficiency.
    
    Args:
        service: Gmail API service instance
        message_ids (list): List of email IDs to fetch
        batch_size (int): Number of emails to fetch in each batch
        
    Returns:
        list: Email details for each message
    """
    logger.info(f"Getting details for {len(message_ids)} emails in batches of {batch_size}")
    email_details = []
    
    # callback function to handle individual responses
    def callback(request_id, response, exception):
        if exception is not None:
            logger.error(f"Error fetching message {request_id}: {exception}")
        else:
            email_details.append(response)
    
    # process in batches
    for i in range(0, len(message_ids), batch_size):
        batch = BatchHttpRequest(callback=callback, batch_uri='https://gmail.googleapis.com/batch')
        current_batch = message_ids[i:i + batch_size]
        
        # add up to batch_size requests to the batch
        for msg_id in current_batch:
            batch.add(service.users().messages().get(userId='me', id=msg_id))
        
        # execute the batch
        try:
            batch.execute()
            logger.info(f"Processed batch {i//batch_size + 1}/{(len(message_ids) + batch_size - 1)//batch_size}")
        except Exception as e:
            logger.error(f"Error executing batch: {e}")
    
    logger.info(f"Retrieved {len(email_details)} email details")
    return email_details


def apply_labels_grouped(service, email_updates):
    """
    Apply labels to emails in groups for efficiency.
    
    Args:
        service: Gmail API service instance
        email_updates (list): List of tuples (email_id, [label_ids])
    """
    if not email_updates:
        logger.info("No email updates to apply")
        return
    
    # group emails by the set of labels to add
    grouped_updates = defaultdict(list)
    for email_id, labels in email_updates:
        # filter out None values
        valid_labels = [label for label in labels if label]
        if valid_labels:
            grouped_updates[frozenset(valid_labels)].append(email_id)
    
    # apply labels to each group
    for labels, email_ids in grouped_updates.items():
        body = {
            'ids': email_ids,
            'addLabelIds': list(labels)
        }
        try:
            service.users().messages().batchModify(userId='me', body=body).execute()
            logger.info(f"Applied {len(labels)} labels to {len(email_ids)} emails")
        except Exception as e:
            logger.error(f"Error applying labels to emails: {e}")


def get_date_label(service, email, label_cache):
    """
    Extract date from email and get/create appropriate labels.
    
    Args:
        service: Gmail API service instance
        email (dict): Email details from Gmail API
        label_cache (dict): Cache of label names to IDs
        
    Returns:
        str: Label ID for the email's month, or None if date couldn't be parsed
    """
    try:
        # get date from email headers
        headers = email['payload']['headers']
        date = next((header['value'] for header in headers if header['name'] == 'Date'), None)
        
        # if email has date info
        if date:
            year, month = format_date(date)
            
            if year and month:
                # handle year label
                if not label_exists(year, label_cache):
                    create_label(service, year, label_cache)
                
                # handle month sublabel
                month_label_name = f"{year}/{month}"
                if not label_exists(month_label_name, label_cache):
                    create_label(service, month_label_name, label_cache)
                
                return label_cache.get(month_label_name)
    except KeyError as e:
        logger.error(f"Key error processing email {email.get('id', 'unknown')}: {e}")
    except Exception as e:
        logger.error(f"Error getting date label: {e}")
    
    return None


def sort_past_emails(service, max_emails=None):
    """
    Sort emails in the inbox by applying date-based labels.
    
    Args:
        service: Gmail API service instance
        max_emails (int, optional): Maximum number of emails to process, or None for all
    """
    label_cache = fetch_labels(service)
    page_token = None
    max_results_per_page = 100  # gmail API limit is 500
    emails_processed = 0
    
    logger.info("Starting email sorting")
    
    try:
        while True:
            # check if we've reached the maximum emails to process
            if max_emails and emails_processed >= max_emails:
                logger.info(f"Reached maximum number of emails to process: {max_emails}")
                break
            
            # calculate how many emails to fetch in this iteration
            current_max_results = max_results_per_page
            if max_emails:
                remaining = max_emails - emails_processed
                if remaining < max_results_per_page:
                    current_max_results = remaining
            
            # fetch list of email IDs
            logger.info(f"Fetching up to {current_max_results} email IDs")
            response = service.users().messages().list(
                userId='me',
                pageToken=page_token,
                labelIds=['INBOX'],
                maxResults=current_max_results,
                fields='messages/id,nextPageToken'
            ).execute()
            
            if 'messages' not in response:
                logger.info("No messages found in inbox")
                break
            
            message_ids = [msg['id'] for msg in response['messages']]
            emails_processed += len(message_ids)
            
            # get email details
            email_details = batch_get_email_details(service, message_ids)
            
            if email_details:
                # process emails and collect updates
                email_updates = []
                for email in email_details:
                    date_label = get_date_label(service, email, label_cache)
                    if date_label:
                        email_updates.append((email['id'], [date_label]))
                
                # apply labels
                if email_updates:
                    apply_labels_grouped(service, email_updates)
            
            # check for more pages
            page_token = response.get('nextPageToken')
            if not page_token:
                logger.info("No more pages of emails")
                break
            
            logger.info(f"Processed {emails_processed} emails so far")
            
    except HttpError as e:
        logger.error(f"Error accessing Gmail API: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    
    logger.info(f"Email sorting complete. Processed {emails_processed} emails total.")
