from googleapiclient.discovery import build
from fetch_emails import *
from sort_emails import *


if __name__ == "__main__":
    # authenticate and build Gmail service
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)

    messages = get_all_emails(service, user_id='me')

    print(f"Found {len(messages)} emails.")
        

    """
    # fetch all messages recieved in the last 24 hours
    QUERY = 'newer_than:1d'
    messages = get_messages(service, query=QUERY)

    # display message details
    print(f"Found {len(messages)} emails matching '{QUERY}'")
    print(f"Sorted messages")
    for msg in messages[:5]: # limit to first 5 messages for demo
        subject = get_message_subject(service, msg['id'])
        labelIds = get_message_labels(service, msg['id'])
        print(f"Subject: {subject}")
        print(f"labelIds: {labelIds}\n")
        
    # get current labels
    current_labels = get_current_labels(service)
    for label in current_labels['labels']:
        print(label)
    """