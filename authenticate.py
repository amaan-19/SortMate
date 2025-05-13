import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import warnings


def authenticate():
    CLIENTSECRETS_LOCATION = r'C:\Users\amaan\PersonalProjects\SortMate\client_secret.json'
    REDIRECT_URI = 'http://localhost:8080/'

    SCOPES = [
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.labels', 
        'openid',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile']

    # token.pickle stores the user's access and refresh tokens
    creds = None
    token_path = 'token.pickle'
    
    # oad credentials from the saved token file if it exists
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # ff there are no valid credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENTSECRETS_LOCATION, SCOPES)
                creds = flow.run_local_server(port=8080)
        
        # save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds
