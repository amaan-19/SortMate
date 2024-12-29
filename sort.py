from googleapiclient.discovery import build  # for interacting with gmail API (modifying labels, etc.)
from googleapiclient.errors import HttpError  # for handling errors during gmail API calls
from email.utils import parsedate_to_datetime
from fetch_emails import *
import concurrent.futures
import json

def format_date(date):
    try:
        parsed_date = parsedate_to_datetime(date)
        year = str(parsed_date.year)
        month = parsed_date.strftime('%b')  # Abbreviated month name (e.g., "Dec")
        return year, month
    except Exception as e:
        print(f"Error parsing date: {e}")
        return None, None

def label_exists(service, label_name, label_cache, parent_id=None):
    if label_name in label_cache:
        # check if the label has the correct parentId
        if parent_id:
            existing_label = service.users().labels().get(userId='me', id=label_cache[label_name]).execute()
            return existing_label.get('parentId') == parent_id
        return True
    return False

def create_label(service, label_name, parent_id=None, label_cache=None):
    # define label body
    label_body = {
        'name': label_name,
        'labelListVisibility': 'labelShow',
        'messageListVisibility': 'show',
    }
    if parent_id: # add to label body if new label is sublabel
        label_body['parentId'] = parent_id

    try:
        new_label = service.users().labels().create(userId='me', body=label_body).execute()
        label_cache[label_name] = new_label['id']
        return new_label
    except HttpError as e:
        if e.resp.status == 409:
            print(f"Label '{label_name}' already exists. Skipping creation.")
        else:
            raise

def fetch_labels(service):
    label_cache = {}
    response = service.users().labels().list(userId='me').execute()
    return {label['name']: label['id'] for label in response.get('labels', [])}

def batch_get_email_details(service, message_ids):
    def fetch_message(msg_id):
        return service.users().messages().get(userId='me', id=msg_id).execute()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        return list(executor.map(fetch_message, message_ids))

def batch_get_email_details(service, message_ids):
    email_details = []
    for msg_id in message_ids:
        email_details.append(service.users().messages().get(userId='me', id=msg_id).execute())
    return email_details

def apply_labels_in_parallel(service, email_updates):
    def modify_email_labels(email_id, labels):
        service.users().messages().modify(
            userId='me',
            id=email_id,
            body={'addLabelIds': labels}
        ).execute()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(lambda update: modify_email_labels(update[0], update[1]), email_updates)

def apply_labels_in_bulk(service, email_updates):
    body = {
        'ids': [update[0] for update in email_updates],
        'addLabelIds': list(set(label_id for _, labels in email_updates for label_id in labels))
    }
    service.users().messages().batchModify(userId='me', body=body).execute()

def sort_past_emails(service):
    label_cache = fetch_labels(service)
    page_token = None
    print("Fetching emails...")
    while True:
        # fetch batch of emails
        response = service.users().messages().list(
            userId='me',
            pageToken=page_token,
            labelIds=['INBOX'],
            maxResults=50,  # Smaller batch size
            fields='messages/id,nextPageToken'
        ).execute()

        # break if no messages
        if 'messages' not in response:
            break

        print(f"Processing {len(response['messages'])} messages...")

        # get message details
        message_ids = [msg['id'] for msg in response['messages']]
        email_details = batch_get_email_details(service, message_ids)

        email_updates = []

        # for every email in batch of details
        for email in email_details:
            # define list for labels to add
            labels_to_add = []

            # get date for current email
            headers = email['payload']['headers']
            date = next((header['value'] for header in headers if header['name'] == 'Date'), None)

            # if email has date info
            if date:
                year, month = format_date(date) # format date

                # handle year label
                if not label_exists(service, year, label_cache):
                    create_label(service, year, label_cache=label_cache)
                
                # update cache with new label id
                year_id = label_cache[year]

                print(f"Cache updated with year: {year} -> {year_id}")

                # Handle month sublabel
                month_label_name = f"{year}/{month}"
                if not label_exists(service, month_label_name, label_cache, parent_id=year_id):
                    create_label(service, month_label_name, parent_id=year_id, label_cache=label_cache)
                
                # update cache and add new labels to list of lables to add
                month_id = label_cache.get(month_label_name)
                labels_to_add.append(label_cache[month_label_name])

                print(f"Cache updated with month: {month_label_name} -> {month_id}")

            if labels_to_add:
                email_updates.append((email['id'], labels_to_add))

        apply_labels_in_bulk(service, email_updates)

        page_token = response.get('nextPageToken')
        if not page_token:
            break

    print("Emails sorted!")
