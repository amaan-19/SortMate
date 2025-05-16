import os
import json
import pickle
import logging
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# set up logging
logger = logging.getLogger(__name__)

# load environment variables from .env for development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("python-dotenv not installed, skipping .env loading")

# get configuration from environment variables
CLIENT_SECRETS_FILE = os.environ.get('GOOGLE_CLIENT_SECRETS_FILE')
if CLIENT_SECRETS_FILE:
    CLIENT_SECRETS_FILE = os.path.expanduser(CLIENT_SECRETS_FILE)

TOKEN_DIR = os.environ.get('GOOGLE_TOKEN_DIR', '~/.config/SortMate/tokens')
TOKEN_DIR = os.path.expanduser(TOKEN_DIR)  # expand ~ to home directory

SCOPES = os.environ.get('GOOGLE_API_SCOPES', 
                      'https://www.googleapis.com/auth/gmail.modify,https://www.googleapis.com/auth/gmail.labels').split(',')


def get_token_path():
    """
    Get secure token storage path.
    
    Returns:
        str: Path to the token file
    """
    # create a hash of the scopes to use in filename
    import hashlib
    scopes_hash = hashlib.md5(','.join(sorted(SCOPES)).encode()).hexdigest()[:8]
    token_filename = f"google_token_{scopes_hash}.pickle"
    
    # create token directory with secure permissions if it doesn't exist
    os.makedirs(TOKEN_DIR, mode=0o700, exist_ok=True)
    
    return os.path.join(TOKEN_DIR, token_filename)


def get_credentials():
    """
    Get valid credentials for Google API access.
    
    Returns:
        google.oauth2.credentials.Credentials: A valid credentials object
        
    Raises:
        ValueError: If GOOGLE_CLIENT_SECRETS_FILE environment variable is not set
        FileNotFoundError: If the client secrets file doesn't exist
    """
    if not CLIENT_SECRETS_FILE:
        raise ValueError(
            "GOOGLE_CLIENT_SECRETS_FILE environment variable not set. "
            "Please set it to the path of your credentials.json file."
        )
    
    token_path = get_token_path()
    creds = None
    
    # try to load credentials from pickle file if it exists
    if os.path.exists(token_path):
        try:
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
            logger.info("Loaded credentials from token file")
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
            logger.info("Removing potentially corrupted token file")
            try:
                os.remove(token_path)
            except Exception as remove_error:
                logger.error(f"Could not remove token file: {remove_error}")
    
    # if no valid credentials, get new ones
    if not creds or not creds.valid:
        logger.info("Need to get new credentials")
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired credentials")
            try:
                creds.refresh(Request())
                logger.info("Successfully refreshed credentials")
            except Exception as e:
                logger.error(f"Error refreshing credentials: {e}")
                creds = None  # Force new credentials flow
        
        # if still no valid credentials, get new ones via OAuth flow
        if not creds or not creds.valid:
            # make sure the client secrets file exists
            if not os.path.exists(CLIENT_SECRETS_FILE):
                raise FileNotFoundError(
                    f"Client secrets file '{CLIENT_SECRETS_FILE}' not found."
                )
            
            logger.info("Starting OAuth flow for new credentials")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRETS_FILE, SCOPES)
                # try port 8080 first, fall back to dynamic port if needed
                try:
                    creds = flow.run_local_server(port=8080)
                except OSError:
                    logger.info("Port 8080 unavailable, using dynamic port")
                    creds = flow.run_local_server(port=0)
                logger.info("Successfully obtained new credentials")
            except Exception as e:
                logger.error(f"Error during OAuth flow: {e}")
                raise
        
            # Save the credentials for the next run
            try:
                logger.info(f"Saving credentials to {token_path}")
                os.chmod(TOKEN_DIR, 0o700)  # ensure directory permissions are secure
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
                os.chmod(token_path, 0o600)  # restrict token file permissions
                logger.info("Credentials saved successfully")
            except Exception as e:
                logger.error(f"Error saving credentials: {e}")
    
    return creds