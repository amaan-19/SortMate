from googleapiclient.discovery import build
from authenticate_email import authenticate


def get_messages(service, query=''):
    # Fetch messages based on a search query.
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    return messages

def get_message_details(service, msg_id):
    # Fetch details of a specific message.
    msg = service.users().messages().get(userId='me', id=msg_id).execute()
    payload = msg['payload']
    headers = payload['headers']
    subject = next(header['value'] for header in headers if header['name'] == 'Subject')
    snippet = msg.get('snippet', '')
    return subject, snippet

if __name__ == "__main__":
    # Authenticate and build Gmail service
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)

    # Fetch messages with a query
    query = 'invoice'  # Example search query
    messages = get_messages(service, query=query)

    # Display message details
    print(f"Found {len(messages)} emails matching '{query}'")
    for msg in messages[:5]:  # Limit to first 5 messages for demo
        subject, snippet = get_message_details(service, msg['id'])
        print(f"Subject: {subject}")
        print(f"Snippet: {snippet}\n")
