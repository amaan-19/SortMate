# Gmail Organizer

An automated system to organize Gmail messages by applying date labels (year/month) and monitoring for new emails.

## Features

- **Authentication**: Securely authenticate with Google OAuth2
- **Date-based Organization**: Automatically labels emails by year and month
- **Batch Processing**: Efficiently processes multiple emails at once
- **Real-time Monitoring**: Watch for new emails using Gmail API webhooks and Google Cloud Pub/Sub
- **Command-line Interface**: Flexible options for running the application
- **Logging**: Comprehensive logging system for monitoring and debugging

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

### Development Environment Setup

1. Clone this repository:
```
git clone https://github.com/yourusername/gmail-organizer.git
cd gmail-organizer
```

2. Set up a virtual environment:
```
python -m venv venv
```

3. Activate the virtual environment:
   - On Windows:
   ```
   venv\Scripts\activate
   ```
   - On macOS/Linux:
   ```
   source venv/bin/activate
   ```

4. Install development dependencies:
```
pip install -r requirements.txt
pip install pytest flake8 black  # Optional development tools
```

5. Set up pre-commit hooks (optional):
```
pip install pre-commit
pre-commit install
```

### Installation for Users

1. Clone this repository
2. Navigate to the project directory:
```
cd gmail-organizer  # or whatever your repository is named
```
3. Set up a virtual environment (recommended):
```
python -m venv venv
```
4. Activate the virtual environment:
   - On Windows:
   ```
   venv\Scripts\activate
   ```
   - On macOS/Linux:
   ```
   source venv/bin/activate
   ```
5. Install the required dependencies:
```
pip install -r requirements.txt
```

3. Set up Google API credentials:
   - Create a project in the [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Gmail API
   - Create OAuth client credentials and download as `client_secret.json`
   - Place `client_secret.json` in the project directory

4. Update the path in `authenticate.py` to point to your client_secret.json file

### Usage

After installation, you can run the application with various options:

```bash
# Basic usage - just sort emails
python testing.py

# Sort with verbose logging
python testing.py --verbose

# Sort only the first 10 emails (for testing)
python testing.py --max-emails 10

# Sort emails and then start monitoring
python testing.py --monitor

# Sort a limited number and monitor with verbose logging
python testing.py --monitor --max-emails 20 --verbose
```

#### Command-line Options

- `--monitor`: Enable real-time email monitoring
- `--max-emails N`: Limit processing to N emails (useful for testing)
- `--verbose`: Enable detailed logging output

#### Real-time Email Monitoring

To set up real-time monitoring:

1. Enable Pub/Sub API in Google Cloud Console
2. Create a Pub/Sub topic named `email_notifications`
3. Create a subscription named `email_notifications-sub`
4. Grant the necessary permissions for Gmail to publish to your topic
5. Run the application with the `--monitor` flag

## Project Setup

If you want to modify or contribute to this project, follow these steps:

1. Clone the repository
2. Set up a development environment
3. Install dependencies
4. Configure authentication
5. Run with test parameters

## Current Limitations

- Only implements date-based sorting (year/month)
- Requires manual setup of Google Cloud project
- No graphical user interface
- Requires Pub/Sub setup for real-time monitoring

## Future Enhancements

- Add more sophisticated sorting rules based on sender, subject, etc.
- Create a user interface for configuration
- Add support for custom label hierarchies
- Implement a system tray application for easier monitoring
- Add support for filtering emails by content
- Create a configuration file for persistent settings
