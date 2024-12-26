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
