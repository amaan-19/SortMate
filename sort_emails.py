from authenticate_email import authenticate

def get_current_labels(service):
	return service.users().labels().list(userId='me')
