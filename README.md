# SortMate

A smart Gmail organization tool that automatically categorizes emails using date-based labels. This Python application uses Gmail API and Google Cloud services to intelligently sort your inbox, saving you time and keeping your emails neatly organized without manual effort.

## Features

- **Authentication**: Securely authenticate with Google OAuth2
- **Date-based Organization**: Automatically labels emails by year and month
- **Batch Processing**: Efficiently processes multiple emails at once
- **Real-time Monitoring**: Watch for new emails using Gmail API webhooks and Google Cloud Pub/Sub
- **Command-line Interface**: Flexible options for running the application
- **Logging**: Comprehensive logging system for monitoring and debugging

## Project Structure

- `sortmate/` - Main package directory
  - `__init__.py` - Package initialization and exports
  - `authenticate.py` - Handles Google OAuth2 authentication
  - `sort.py` - Contains email sorting and labeling logic
  - `watch.py` - Sets up Gmail API watch notification
  - `pubsub.py` - Processes notifications from Pub/Sub
  - `cli.py` - Command-line interface and entry point
- `tests/` - Test directory
- `run_sortmate.py` - Development script for easy testing

## Installation

### Prerequisites

- Python 3.6+
- A Google Cloud project with Gmail API enabled
- OAuth2 client credentials
- For real-time monitoring: Pub/Sub API enabled

### Installation Options

#### Option 1: Install from GitHub (Development Mode)

1. Clone this repository:
```bash
git clone https://github.com/amaan-19/SortMate.git
cd SortMate
```

2. Set up a virtual environment:
```bash
python -m venv .venv
```

3. Activate the virtual environment:
   - On Windows:
   ```bash
   .venv\Scripts\activate
   ```
   - On macOS/Linux:
   ```bash
   source .venv/bin/activate
   ```

4. Install in development mode:
```bash
pip install -e .
```

#### Option 2: Install via pip (Coming Soon)

```bash
pip install sortmate
```

### Development Setup

If you're contributing to the project:

1. Install development dependencies:
```bash
pip install -r requirements.txt
pip install pytest flake8 black  # Development tools
```

2. Set up pre-commit hooks (optional):
```bash
pip install pre-commit
pre-commit install
```

## Configuration

### Setting Up Environment Variables

1. Create a `.env` file in the project root:
```bash
# Copy the example configuration
cp .env.example .env
```

2. Configure your environment variables:
```
# Google OAuth Configuration
GOOGLE_CLIENT_SECRETS_FILE=/path/to/your/credentials.json
GOOGLE_TOKEN_DIR=~/.config/SortMate/tokens
GOOGLE_API_SCOPES=https://www.googleapis.com/auth/gmail.modify,https://www.googleapis.com/auth/gmail.labels

# Google Cloud Project Details (needed for real-time monitoring)
GOOGLE_CLOUD_PROJECT=your-project-id
PUBSUB_TOPIC=your-topic-name
PUBSUB_SUBSCRIPTION=your-subscription-name
```

### Google API Setup

1. Create a project in the [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Gmail API
3. Create OAuth client credentials (Desktop application type)
4. Download the credentials as `client_secret.json`
5. Store this file securely outside your project directory
6. Update your `.env` file with the path to this file

For real-time monitoring:
1. Enable the Pub/Sub API in Google Cloud Console
2. Create a Pub/Sub topic and subscription
3. Update your `.env` file with the topic and subscription names

## Usage

### Running SortMate

After installation, you can run SortMate with various options:

```bash
# If installed with pip or in development mode
sortmate

# Or run the module directly from the project root
python -m sortmate.cli

# Use the development script
python run_sortmate.py

# With command-line options
sortmate --monitor --verbose --max-emails 50
```

### Command-line Options

- `--monitor`: Enable real-time email monitoring
- `--max-emails N`: Limit processing to N emails (useful for testing)
- `--verbose`: Enable detailed logging output

### Examples

```bash
# Basic usage - just sort existing emails
sortmate

# Sort with verbose logging
sortmate --verbose

# Sort only the first 10 emails (for testing)
sortmate --max-emails 10

# Sort emails and then start monitoring for new emails
sortmate --monitor

# Sort a limited number and monitor with verbose logging
sortmate --monitor --max-emails 20 --verbose
```

## Real-time Email Monitoring

SortMate can continuously monitor your inbox for new emails and automatically sort them as they arrive.

### How It Works

1. Gmail API sends a notification to Google Cloud Pub/Sub when new emails arrive
2. SortMate receives this notification and processes the new emails
3. The emails are automatically sorted with date-based labels

### Setting Up Monitoring

1. Configure Google Cloud Pub/Sub (see Configuration section)
2. Run SortMate with the `--monitor` flag:
```bash
sortmate --monitor
```

### Monitoring Notes

- The Gmail API watch will expire after 7 days, requiring a restart of SortMate
- Running with `--monitor` keeps the process running indefinitely
- Press Ctrl+C to gracefully stop monitoring
- For production use, consider using a system service manager like systemd

## Security Considerations

SortMate handles sensitive Google API credentials. Follow these security best practices:

1. **Never commit credentials to Git**: All credential files are listed in `.gitignore`
2. **Store tokens securely**: By default, tokens are stored in `~/.config/SortMate/tokens` with secure file permissions
3. **Use environment variables**: Store paths to credential files in your `.env` file
4. **Restrict API scopes**: Only request the minimum permissions needed

## Troubleshooting

### Authentication Issues

If you encounter authentication errors:

1. Verify your `GOOGLE_CLIENT_SECRETS_FILE` path is correct
2. Ensure Gmail API is enabled in your Google Cloud project
3. Check that OAuth consent screen is properly configured
4. For `redirect_uri_mismatch` errors, add `http://localhost:8080/` to your authorized redirect URIs in Google Cloud Console
5. Try removing existing token files to force re-authentication

### Monitoring Issues

If real-time monitoring isn't working:

1. Verify Pub/Sub API is enabled
2. Check topic and subscription names in your `.env` file
3. Ensure your service account has appropriate permissions
4. Run with `--verbose` flag for detailed logging
5. Check if you've exceeded your Google Cloud free tier limits

### Common Import Errors

If you get a "No module named 'sortmate'" error:

1. Run from the project root using: `python -m sortmate.cli`
2. Or install in development mode: `pip install -e .`
3. Or use the provided development script: `python run_sortmate.py`

## Roadmap

- [x] Core email sorting functionality
- [x] Real-time monitoring of new emails
- [ ] Add additional sorting methods (sender, subject, keywords)
- [ ] Implement user interface (web-based or desktop)
- [ ] Support custom label hierarchies and rules
- [ ] Create a system tray application for continuous monitoring
- [ ] Add support for multi-user environments
- [ ] Implement filtering capability based on email content
- [ ] Add configuration file for persistent settings
- [ ] Support for other email providers (via IMAP)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
