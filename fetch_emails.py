from authenticate_email import authenticate

def get_all_emails(service, user_id='me', query=''):
    """
    Fetch all emails for a user, respecting the 500-email limit per call.
    :param service: Authorized Gmail API service instance
    :param user_id: User's email address (default: 'me')
    :param query: Search query to filter emails (optional)
    :return: List of all messages
    """
    all_emails = []
    page_token = None

    while True:
        # Fetch a page of emails
        response = service.users().messages().list(
            userId=user_id,
            q=query,
            maxResults=500,  # Fetch up to 500 emails per call
            pageToken=page_token  # Specify the next page token
        ).execute()

        # Add retrieved emails to the list
        if 'messages' in response:
            all_emails.extend(response['messages'])

        # Check for the next page token
        page_token = response.get('nextPageToken')
        if not page_token:
            break  # Exit the loop if no more pages

    return all_emails


def get_message_subject(service, msg_id):
    msg = service.users().messages().get(userId='me', id=msg_id).execute()
    payload = msg['payload']
    headers = payload['headers']
    subject = next(header['value'] for header in headers if header['name'] == 'Subject')
    return subject

def get_message_snippet(service, msg_id):
    msg = service.users().messages().get(userId='me', id=msg_id).execute()
    snippet = msg.get('snippet', '')
    return snippet

def get_message_labels(service, msg_id):
    msg = service.users().messages().get(userId='me', id=msg_id).execute()
    labelIds = msg['labelIds']
    return labelIds
