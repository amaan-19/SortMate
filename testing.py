from googleapiclient.discovery import build
from fetch_emails import *
from sort_emails import *


if __name__ == "__main__":
    # Authenticate and build Gmail service
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)

    # Fetch all messages recieved in the last 24 hours
    QUERY = 'newer_than:1d'
    messages = get_messages(service, query=QUERY)

    # Display message details
    print(f"Found {len(messages)} emails matching '{QUERY}'")
    print(f"Sorted messages")
    for msg in messages[:5]:  # Limit to first 5 messages for demo
        subject, snippet = get_message_details(service, msg['id'])
        print(f"Subject: {subject}")
        print(f"Snippet: {snippet}\n")
        
    # get current labels
    current_labels = get_current_labels(service)
    print(current_labels)