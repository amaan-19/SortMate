"""
Gmail Label Organizer

This module contains functions to sort emails by multiple criteria:
- Date (year/month)
- Sender domain/organization
- Keywords in subject/content
"""

import logging
import re
from collections import defaultdict
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse

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

# Default keywords for content-based categorization
DEFAULT_KEYWORDS = {
    'urgent': ['urgent', 'asap', 'emergency', 'immediate', 'priority'],
    'meeting': ['meeting', 'conference', 'call', 'zoom', 'teams', 'appointment'],
    'financial': ['invoice', 'payment', 'bill', 'receipt', 'bank', 'transaction'],
    'travel': ['flight', 'hotel', 'booking', 'ticket', 'travel', 'reservation'],
    'newsletter': ['newsletter', 'unsubscribe', 'weekly', 'monthly', 'digest'],
    'social': ['facebook', 'twitter', 'linkedin', 'instagram', 'notification'],
    'shopping': ['order', 'shipping', 'delivery', 'cart', 'purchase', 'amazon'],
    'work': ['project', 'deadline', 'report', 'task', 'assignment', 'review']
}

# Common organization domains for sender categorization
ORGANIZATION_DOMAINS = {
    'google.com': 'Google',
    'microsoft.com': 'Microsoft', 
    'apple.com': 'Apple',
    'amazon.com': 'Amazon',
    'facebook.com': 'Meta',
    'linkedin.com': 'LinkedIn',
    'github.com': 'GitHub',
    'slack.com': 'Slack',
    'zoom.us': 'Zoom',
    'dropbox.com': 'Dropbox'
}


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


def extract_sender_info(email):
    """
    Extract sender information from email headers.
    
    Args:
        email (dict): Email details from Gmail API
        
    Returns:
        tuple: (sender_email, sender_domain, sender_name) or (None, None, None) if extraction fails
    """
    try:
        headers = email['payload']['headers']
        from_header = next((header['value'] for header in headers if header['name'] == 'From'), None)
        
        if not from_header:
            return None, None, None
        
        # Extract email from "Name <email@domain.com>" format
        email_match = re.search(r'<([^>]+)>', from_header)
        if email_match:
            sender_email = email_match.group(1).lower()
            sender_name = from_header.split('<')[0].strip().strip('"')
        else:
            # Handle cases where email is not in angle brackets
            if '@' in from_header:
                sender_email = from_header.strip().lower()
                sender_name = sender_email.split('@')[0]
            else:
                return None, None, None
        
        # Extract domain
        sender_domain = sender_email.split('@')[1] if '@' in sender_email else None
        
        return sender_email, sender_domain, sender_name
    except Exception as e:
        logger.error(f"Error extracting sender info: {e}")
        return None, None, None


def extract_email_content(email):
    """
    Extract text content from email payload.
    
    Args:
        email (dict): Email details from Gmail API
        
    Returns:
        tuple: (subject, snippet) containing email content
    """
    try:
        headers = email['payload']['headers']
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), '')
        snippet = email.get('snippet', '')
        
        return subject, snippet
    except Exception as e:
        logger.error(f"Error extracting email content: {e}")
        return '', ''


def get_sender_label(service, email, label_cache, categorization_type='domain'):
    """
    Create and apply sender-based labels.
    
    Args:
        service: Gmail API service instance
        email (dict): Email details from Gmail API
        label_cache (dict): Cache of label names to IDs
        categorization_type (str): 'domain', 'organization', or 'individual'
        
    Returns:
        str: Label ID for the sender category, or None if extraction fails
    """
    sender_email, sender_domain, sender_name = extract_sender_info(email)
    
    if not sender_domain:
        return None
    
    try:
        if categorization_type == 'domain':
            # Categorize by domain
            label_name = f"Senders/Domains/{sender_domain}"
        elif categorization_type == 'organization':
            # Categorize by known organizations
            org_name = ORGANIZATION_DOMAINS.get(sender_domain, sender_domain)
            label_name = f"Senders/Organizations/{org_name}"
        elif categorization_type == 'individual':
            # Categorize by individual sender
            clean_name = re.sub(r'[^\w\s-]', '', sender_name)[:50]  # Limit length and clean
            if clean_name:
                label_name = f"Senders/People/{clean_name}"
            else:
                label_name = f"Senders/People/{sender_email.split('@')[0]}"
        else:
            logger.warning(f"Unknown categorization type: {categorization_type}")
            return None
        
        # Create parent labels if they don't exist
        parent_labels = label_name.split('/')[:-1]
        for i in range(1, len(parent_labels) + 1):
            parent_label = '/'.join(parent_labels[:i])
            if not label_exists(parent_label, label_cache):
                create_label(service, parent_label, label_cache)
        
        # Create the main label if it doesn't exist
        if not label_exists(label_name, label_cache):
            create_label(service, label_name, label_cache)
        
        return label_cache.get(label_name)
    except Exception as e:
        logger.error(f"Error creating sender label: {e}")
        return None


def get_keyword_label(service, email, label_cache, keywords=None):
    """
    Create and apply keyword-based labels based on email subject and content.
    
    Args:
        service: Gmail API service instance
        email (dict): Email details from Gmail API
        label_cache (dict): Cache of label names to IDs
        keywords (dict): Custom keyword mapping, or None to use defaults
        
    Returns:
        list: List of label IDs for matched keywords
    """
    if keywords is None:
        keywords = DEFAULT_KEYWORDS
    
    subject, snippet = extract_email_content(email)
    combined_text = f"{subject} {snippet}".lower()
    
    matched_labels = []
    
    try:
        for category, keyword_list in keywords.items():
            for keyword in keyword_list:
                if keyword.lower() in combined_text:
                    label_name = f"Keywords/{category.title()}"
                    
                    # Create parent label if it doesn't exist
                    if not label_exists("Keywords", label_cache):
                        create_label(service, "Keywords", label_cache)
                    
                    # Create the keyword label if it doesn't exist
                    if not label_exists(label_name, label_cache):
                        create_label(service, label_name, label_cache)
                    
                    label_id = label_cache.get(label_name)
                    if label_id and label_id not in matched_labels:
                        matched_labels.append(label_id)
                    break  # Only match one keyword per category
        
        return matched_labels
    except Exception as e:
        logger.error(f"Error creating keyword labels: {e}")
        return []


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
    
    # Define new label body
    label_body = {
        'name': label_name,
        'labelListVisibility': 'labelShow',
        'messageListVisibility': 'show',
    }
    
    try:
        # Try to create the label
        new_label = service.users().labels().create(userId='me', body=label_body).execute()
        label_id = new_label['id']
        
        # Update cache
        label_cache[label_name] = label_id
        logger.info(f"Label '{label_name}' created with ID: {label_id}")
        
        return label_id
    except HttpError as e:
        if e.resp.status == 409:  # Label already exists
            logger.info(f"Label '{label_name}' already exists")
            
            # If the label exists but isn't in our cache, fetch all labels again
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
    
    # Callback function to handle individual responses
    def callback(request_id, response, exception):
        if exception is not None:
            logger.error(f"Error fetching message {request_id}: {exception}")
        else:
            email_details.append(response)
    
    # Process in batches
    for i in range(0, len(message_ids), batch_size):
        batch = BatchHttpRequest(callback=callback, batch_uri='https://gmail.googleapis.com/batch')
        current_batch = message_ids[i:i + batch_size]
        
        # Add up to batch_size requests to the batch
        for msg_id in current_batch:
            batch.add(service.users().messages().get(userId='me', id=msg_id))
        
        # Execute the batch
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
    
    # Group emails by the set of labels to add
    grouped_updates = defaultdict(list)
    for email_id, labels in email_updates:
        # Filter out None values and flatten lists
        valid_labels = []
        for label in labels:
            if isinstance(label, list):
                valid_labels.extend([l for l in label if l])
            elif label:
                valid_labels.append(label)
        
        if valid_labels:
            grouped_updates[frozenset(valid_labels)].append(email_id)
    
    # Apply labels to each group
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
        # Get date from email headers
        headers = email['payload']['headers']
        date = next((header['value'] for header in headers if header['name'] == 'Date'), None)
        
        # If email has date info
        if date:
            year, month = format_date(date)
            
            if year and month:
                # Handle year label
                if not label_exists(year, label_cache):
                    create_label(service, year, label_cache)
                
                # Handle month sublabel
                month_label_name = f"{year}/{month}"
                if not label_exists(month_label_name, label_cache):
                    create_label(service, month_label_name, label_cache)
                
                return label_cache.get(month_label_name)
    except KeyError as e:
        logger.error(f"Key error processing email {email.get('id', 'unknown')}: {e}")
    except Exception as e:
        logger.error(f"Error getting date label: {e}")
    
    return None


def get_all_labels_for_email(service, email, label_cache, categorization_options=None):
    """
    Get all applicable labels for an email based on enabled categorization options.
    
    Args:
        service: Gmail API service instance
        email (dict): Email details from Gmail API
        label_cache (dict): Cache of label names to IDs
        categorization_options (dict): Options for categorization types
        
    Returns:
        list: List of all applicable label IDs
    """
    if categorization_options is None:
        categorization_options = {
            'date': True,
            'sender': {'enabled': True, 'type': 'domain'},
            'keywords': {'enabled': True, 'keywords': None}
        }
    
    all_labels = []
    
    try:
        # Date-based labeling
        if categorization_options.get('date', True):
            date_label = get_date_label(service, email, label_cache)
            if date_label:
                all_labels.append(date_label)
        
        # Sender-based labeling
        sender_config = categorization_options.get('sender', {})
        if sender_config.get('enabled', False):
            sender_type = sender_config.get('type', 'domain')
            sender_label = get_sender_label(service, email, label_cache, sender_type)
            if sender_label:
                all_labels.append(sender_label)
        
        # Keyword-based labeling
        keyword_config = categorization_options.get('keywords', {})
        if keyword_config.get('enabled', False):
            keywords = keyword_config.get('keywords', None)
            keyword_labels = get_keyword_label(service, email, label_cache, keywords)
            all_labels.extend(keyword_labels)
        
        return all_labels
    except Exception as e:
        logger.error(f"Error getting labels for email: {e}")
        return []


def sort_past_emails(service, max_emails=None, categorization_options=None):
    """
    Sort emails in the inbox by applying multiple types of labels.
    
    Args:
        service: Gmail API service instance
        max_emails (int, optional): Maximum number of emails to process, or None for all
        categorization_options (dict): Configuration for categorization methods
    """
    if categorization_options is None:
        # Default configuration - only date labeling for backward compatibility
        categorization_options = {
            'date': True,
            'sender': {'enabled': False, 'type': 'domain'},
            'keywords': {'enabled': False, 'keywords': None}
        }
    
    label_cache = fetch_labels(service)
    page_token = None
    max_results_per_page = 100  # Gmail API limit is 500
    emails_processed = 0
    
    logger.info("Starting enhanced email sorting")
    logger.info(f"Categorization options: {categorization_options}")
    
    try:
        while True:
            # Check if we've reached the maximum emails to process
            if max_emails and emails_processed >= max_emails:
                logger.info(f"Reached maximum number of emails to process: {max_emails}")
                break
            
            # Calculate how many emails to fetch in this iteration
            current_max_results = max_results_per_page
            if max_emails:
                remaining = max_emails - emails_processed
                if remaining < max_results_per_page:
                    current_max_results = remaining
            
            # Fetch list of email IDs
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
            
            # Get email details
            email_details = batch_get_email_details(service, message_ids)
            
            if email_details:
                # Process emails and collect updates
                email_updates = []
                for email in email_details:
                    all_labels = get_all_labels_for_email(service, email, label_cache, categorization_options)
                    if all_labels:
                        email_updates.append((email['id'], all_labels))
                
                # Apply labels
                if email_updates:
                    apply_labels_grouped(service, email_updates)
            
            # Check for more pages
            page_token = response.get('nextPageToken')
            if not page_token:
                logger.info("No more pages of emails")
                break
            
            logger.info(f"Processed {emails_processed} emails so far")
            
    except HttpError as e:
        logger.error(f"Error accessing Gmail API: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    
    logger.info(f"Enhanced email sorting complete. Processed {emails_processed} emails total.")