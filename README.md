# SortMate

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
git clone https://github.com/amaan-19/SortMate.git
cd SortMate
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

### Configuration and Environment Variables

1. Create a `.env` file in the project root directory:
```
# Copy the example configuration
cp .env.example .env
```

2. Edit the `.env` file and set your configuration values:
```
# Google OAuth Configuration
GOOGLE_CLIENT_SECRETS_FILE=/path/to/your/credentials.json
GOOGLE_TOKEN_DIR=~/.config/SortMate/tokens
GOOGLE_API_SCOPES=https://www.googleapis.com/auth/gmail.modify,https://www.googleapis.com/auth/gmail.labels

# Google Cloud Project Details
GOOGLE_CLOUD_PROJECT=your-project-id
PUBSUB_TOPIC=your-topic-name
PUBSUB_SUBSCRIPTION=your-subscription-name
```

### Setting Up Google API Credentials

1. Set up Google API credentials:
   - Create a project in the [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Gmail API
   - Create OAuth client credentials and download as `client_secret.json`
   - Store `client_secret.json` in a secure location outside your project directory

2. Update the `GOOGLE_CLIENT_SECRETS_FILE` in your `.env` file to point to this location

3. For real-time monitoring:
   - Enable the Pub/Sub API in Google Cloud Console
   - Create a Pub/Sub topic (use the same name as in your `.env` file)
   - Create a subscription for the topic
   - Update your `.env` file with the topic and subscription names

### Installation for Users

1. Clone this repository
2. Navigate to the project directory:
```
cd SortMate
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
6. Create and configure your `.env` file as described in the Configuration section

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
python testing.py --max-emails 20 --verbose
```

#### Command-line Options

- `--monitor`: Enable real-time email monitoring
- `--max-emails N`: Limit processing to N emails (useful for testing)
- `--verbose`: Enable detailed logging output

## Security Considerations

SortMate handles sensitive Google API credentials. Follow these security best practices:

1. **Never commit credentials to Git**: All credential files are listed in `.gitignore`
2. **Store tokens securely**: By default, tokens are stored in `~/.config/SortMate/tokens` with secure file permissions
3. **Use environment variables**: Set paths to credential files in your `.env` file
4. **Restrict scopes**: Only request the minimum scopes needed for the application

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

## Troubleshooting

### Authentication Issues

If you encounter authentication errors:

1. Check that your `GOOGLE_CLIENT_SECRETS_FILE` path is correct
2. Verify that you've enabled the Gmail API in your Google Cloud project
3. Try removing the token file and re-authenticating
4. Ensure your OAuth consent screen is properly configured

### Monitoring Issues

If real-time monitoring isn't working:

1. Verify that the Pub/Sub API is enabled
2. Check that your topic and subscription names match the values in your `.env` file
3. Ensure your service account has appropriate permissions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.