from fetch_emails import *


def get_email_date(message):
    headers = message['payload']['headers']
    for header in headers:
        if header['name'] == 'Date':
            return header['value']
    return None

def sort_by_date(messages):
	for message in messages:
        curr_date = get_email_date(message)

	return sorted_messages