from googleapiclient.discovery import build  # For interacting with Gmail API (modifying labels, etc.)
from googleapiclient.errors import HttpError  # For handling errors during Gmail API calls
import json


def sort_past_emails(service):
    """Sort all past emails."""
    messages = get_emails(service, user_id='me')
    for msg in messages:
        message = service.users().messages().get(userId='me', id=msg['id']).execute()
        # add email sorting logic here

