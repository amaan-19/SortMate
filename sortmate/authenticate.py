import os
import json
import pickle
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Load environment variables from .env for development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, skip loading

# Get configuration from environment variables
CLIENT_SECRETS_FILE = os.environ.get('GOOGLE_CLIENT_SECRETS_FILE')
TOKEN_DIR = os.environ.get('GOOGLE_TOKEN_DIR', '~/.config/SortMate/tokens')
TOKEN_DIR = os.path.expanduser(TOKEN_DIR)  # Expand ~ to home directory
SCOPES = os.environ.get('GOOGLE_API_SCOPES', 'https://www.googleapis.com/auth/gmail.modify,https://www.googleapis.com/auth/gmail.labels').split(',')


def get_token_path():
    """Get secure token storage path."""
    # Create a hash of the scopes to use in filename
    import hashlib
    scopes_hash = hashlib.md5(','.join(sorted(SCOPES)).encode()).hexdigest()[:8]
    token_filename = f"google_token_{scopes_hash}.pickle"
    
    # Create token directory with secure permissions if it doesn't exist
    os.makedirs(TOKEN_DIR, mode=0o700, exist_ok=True)
    
    return os.path.join(TOKEN_DIR, token_filename)

def get_credentials():
    """Get valid credentials for Google API access."""
    if not CLIENT_SECRETS_FILE:
        raise ValueError(
            "GOOGLE_CLIENT_SECRETS_FILE environment variable not set. "
            "Please set it to the path of your credentials.json file."
        )
    
    token_path = get_token_path()
    creds = None
    
    # Try to load credentials from pickle file if it exists
    if os.path.exists(token_path):
        try:
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        except Exception as e:
            print(f"Error loading credentials: {e}")
    
    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Make sure the client secrets file exists
            if not os.path.exists(CLIENT_SECRETS_FILE):
                raise FileNotFoundError(
                    f"Client secrets file '{CLIENT_SECRETS_FILE}' not found."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        os.chmod(TOKEN_DIR, 0o700)  # Ensure directory permissions are secure
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
        os.chmod(token_path, 0o600)  # Restrict token file permissions
    
    return creds