from googleapiclient.discovery import build  # for interacting with gmail API (modifying labels, etc.)
from googleapiclient.errors import HttpError  # for handling errors during gmail API calls
from email.utils import parsedate_to_datetime # for handling datetime objects
from googleapiclient.http import BatchHttpRequest # for fetching details
from collections import defaultdict
import json # for formatting

def format_date(date):
    try:
        parsed_date = parsedate_to_datetime(date)
        year = str(parsed_date.year)
        month = parsed_date.strftime('%b')
        return year, month
    except Exception as e:
        print(f"Error parsing date: {e}")
        return None, None

def label_exists(service, label_name, label_cache):
    if label_name in label_cache:
        return True
    return False

def create_label(service, label_name, label_cache=None):
    print(f"Creating {label_name} label...")
    # define new label body
    label_body = {
        'name': label_name,
        'labelListVisibility': 'labelShow',
        'messageListVisibility': 'show',
    }
    try:
        new_label = service.users().labels().create(userId='me', body=label_body).execute()
        print(f"{label_name} created!")
        if label_cache is not None:
            label_cache[label_name] = new_label['id']
            print(f"Cache updated with {label_name}. Current cache contents: {label_cache}")
        return new_label
    except HttpError as e:
        if e.resp.status == 409:
            print(f"Label '{label_name}' already exists. Skipping creation.")
        else:
            raise

def fetch_labels(service):
    print("Fetching labels and populating cache...")
    label_cache = {}
    response = service.users().labels().list(userId='me').execute()
    for label in response.get('labels', []):
        label_cache[label['name']] = label['id']
    return label_cache

def batch_get_email_details(service, message_ids, batch_size=2):
    print("Getting batch details...")
    email_details = []

    # callback function to handle individual responses
    def callback(request_id, response, exception):
        if exception is not None:
            print(f"Error fetching message {request_id}: {exception}")
        else:
            email_details.append(response)

    for i in range(0, len(message_ids), batch_size):
        batch = BatchHttpRequest(callback=callback, batch_uri='https://gmail.googleapis.com/batch')

        # add up to batch_size requests to the batch
        for msg_id in message_ids[i:i + batch_size]:
            batch.add(service.users().messages().get(userId='me', id=msg_id))

        # execute the batch
        try:
            batch.execute()
        except Exception as e:
            print(f"Error executing batch: {e}")

    print("Finished getting details!")
    return email_details

def apply_labels_grouped(service, email_updates):
    grouped_updates = defaultdict(list)
    for email_id, labels in email_updates:
        grouped_updates[frozenset(labels)].append(email_id)

    for labels, email_ids in grouped_updates.items():
        body = {
            'ids': email_ids,
            'addLabelIds': list(labels)
        }
        try:
            service.users().messages().batchModify(userId='me', body=body).execute()
            print(f"Applied labels {labels} to {len(email_ids)} emails.")
        except Exception as e:
            print(f"Error applying labels {labels} to emails: {e}")

def get_date_label(email):
    # get date for current email
    headers = email['payload']['headers']
    date = next((header['value'] for header in headers if header['name'] == 'Date'), None)

    # if email has date info
    if date:
        year, month = format_date(date) # format date

        # handle year label
        if not label_exists(service, year, label_cache):
            create_label(service, year, label_cache=label_cache)
        year_id = label_cache[year]

        # handle month sublabel
        month_label_name = f"{year}/{month}"
        if not label_exists(service, month_label_name, label_cache):
            create_label(service, month_label_name, label_cache=label_cache)
        month_id = label_cache[month_label_name]

        return month_id

def sort_past_emails(service):
    label_cache = fetch_labels(service)
    page_token = None
    max_results = 500
    print("Fetching emails...")

    while True:
        response = service.users().messages().list(
            userId='me',
            pageToken=page_token,
            labelIds=['INBOX'],
            maxResults=max_results,
            fields='messages/id,nextPageToken'
        ).execute()

        if 'messages' not in response:
            break

        message_ids = [msg['id'] for msg in response['messages']]
        email_details = batch_get_email_details(service, message_ids)

        if email_details:
            email_updates = []
            for email in email_details:
                labels_to_add = []
                date_label = get_date_label(email)
                labels_to_add.append(date_label)
                # include more sorting logic here...

                if labels_to_add:
                    email_updates.append((email['id'], labels_to_add))
            
            if email_updates:
                apply_labels_grouped(service, email_updates)
                print("Applied labels. Fetching next batch...")

        page_token = response.get('nextPageToken')
        if not page_token:
            break

    print("Emails sorted!")
