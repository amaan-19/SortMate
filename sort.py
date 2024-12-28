from authenticate_email import authenticate

def sort_past_emails(service):
    """Sort all past emails."""
    messages = get_emails(service, user_id='me')
    for msg in messages:
        message = service.users().messages().get(userId='me', id=msg['id']).execute()
        # add email sorting logic here

