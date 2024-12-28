from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def start_watch(service):
    request_body = {
        'labelIds': ['INBOX'],  # Monitor only the inbox for simplicity
        'topicName': 'projects/emailorganizer-445912/topics/email_notifications'
    }
    response = service.users().watch(userId='me', body=request_body).execute()
    print("Watch response:", response)
