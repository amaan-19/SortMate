from googleapiclient.discovery import build
from sort_emails import *

if __name__ == "__main__":
    # Authenticate and build Gmail service
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)

    # Fetch messages with a query
    query = input("Query Input: ")
    messages = get_messages(service, query=query)

    # Sort messages
    sorted_messages = sort_by_date(messages)

    # Display message details
    print(f"Found {len(messages)} emails matching '{query}'")
    print(f"Sorted messages")
    for msg in sorted_messages[:5]:  # Limit to first 5 messages for demo
        subject, snippet = get_message_details(service, msg['id'])
        print(f"Subject: {subject}")
        print(f"Snippet: {snippet}\n")
