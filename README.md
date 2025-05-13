# Gmail Organizer

An automated system to organize Gmail messages by applying date labels (year/month) and monitoring for new emails.

## Features

- **Authentication**: Securely authenticate with Google OAuth2
- **Date-based Organization**: Automatically labels emails by year and month
- **Batch Processing**: Efficiently processes multiple emails at once
- **Real-time Monitoring** (in development): Watch for new emails using Gmail API webhooks and Google Cloud Pub/Sub

## Project Structure

- `authenticate.py` - Handles Google OAuth2 authentication
- `sort.py` - Contains email sorting and labeling logic
- `watch.py` - Sets up Gmail API watch notification
- `pubsub.py` - Processes notifications from Pub/Sub
- `testing.py` - Main entry point to run the application

## Setup Instructions

### Prerequisites

- Python 3.6+
- A Google Cloud project with Gmail API enabled
- OAuth2 client credentials

### Installation

1. Clone this repository
2. Install the required dependencies:
```
pip install -r requirements.txt
pip install google-api-python-client google-cloud-pubsub
```

3. Set up Google API credentials:
   - Create a project in the [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Gmail API
   - Create OAuth client credentials and download as `client_secret.json`
   - Place `client_secret.json` in the project directory

4. Update the path in `authenticate.py` to point to your client_secret.json file

### Usage

#### Basic Email Sorting

To sort existing emails in your inbox:

```
python testing.py
```

This will:
1. Authenticate with your Google account
2. Create year and month labels if they don't exist
3. Apply appropriate date labels to your emails

#### Real-time Email Monitoring (In Development)

To set up real-time monitoring:

1. Enable Pub/Sub API in Google Cloud
2. Create a Pub/Sub topic and subscription
3. Update the topic and subscription names in `watch.py` and `pubsub.py`
4. Uncomment the pub/sub sections in `testing.py`
5. Run the application

## Current Limitations

- Authentication flow needs to be completed
- Hardcoded paths need to be updated
- Only basic date-based sorting is implemented
- Pub/Sub integration is prepared but commented out

## Future Enhancements

- Add more sophisticated sorting rules based on sender, subject, etc.
- Create a user interface for configuration
- Add error handling and logging
- Implement a more robust authentication flow
