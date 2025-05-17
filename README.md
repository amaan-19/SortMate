# SortMate

A smart Gmail organization tool that automatically categorizes emails using intelligent labeling. This Python application uses Gmail API and Google Cloud services to sort your inbox by date, sender, keywords, and more - saving you time and keeping your emails neatly organized without manual effort.

## Features

- **Multi-Category Organization**: Sort emails by date, sender domain/organization, and content keywords
- **Secure Authentication**: Google OAuth2 integration with secure token storage
- **Batch Processing**: Efficiently processes thousands of emails at once
- **Real-time Monitoring**: Automatically sort new emails as they arrive using Gmail API webhooks
- **Flexible Configuration**: Customizable sorting rules and categorization options
- **Command-line Interface**: Easy-to-use CLI with multiple options
- **Comprehensive Logging**: Detailed logging for monitoring and debugging
- **Robust Testing**: Full unit test coverage for reliability and maintainability

## Project Structure

```
SortMate/
├── .env.example              # Environment configuration template
├── requirements.txt          # Python dependencies
├── setup.py                 # Package installation configuration  
├── run_sortmate.py          # Development script for easy testing
├── sortmate/                # Main package directory
│   ├── __init__.py          # Package initialization and exports
│   ├── authenticate.py      # Google OAuth2 authentication
│   ├── sort.py              # Email sorting and labeling logic
│   ├── watch.py             # Gmail API watch notifications
│   ├── pubsub.py            # Real-time monitoring via Pub/Sub
│   ├── cli.py               # Command-line interface
│   └── config.py            # Configuration management
├── tests/                   # Comprehensive test suite
│   ├── test_authenticate.py # Authentication tests
│   ├── test_sort.py         # Date parsing tests
│   ├── test_sort_labels.py  # Label management tests  
│   ├── test_pubsub.py       # Real-time monitoring tests
│   └── test_watch.py        # Gmail API watch tests
└── docs/
    └── testing_guide.md     # Detailed testing documentation
```

## Installation

### Prerequisites

- **Python 3.8+** (Python 3.6+ supported but 3.8+ recommended)
- **Google Cloud Project** with Gmail API enabled
- **OAuth2 client credentials** for desktop application
- **Google Cloud Pub/Sub API** enabled (for real-time monitoring - optional)

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/amaan-19/SortMate.git
   cd SortMate
   ```

2. **Set up virtual environment**:
   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\activate
   # macOS/Linux: source .venv/bin/activate
   ```

3. **Install SortMate**:
   ```bash
   pip install -e .
   ```

4. **Configure environment** (see [Configuration](#configuration) section):
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Run SortMate**:
   ```bash
   sortmate --verbose
   ```

### Installation Options

#### Option 1: Development Installation (Recommended)

For development or if you want to modify the code:

```bash
git clone https://github.com/amaan-19/SortMate.git
cd SortMate
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .
```

#### Option 2: Package Installation (Coming Soon)

```bash
pip install sortmate
```

#### Option 3: Testing Without Installation

For quick testing without installation:

```bash
git clone https://github.com/amaan-19/SortMate.git
cd SortMate
pip install -r requirements.txt
python run_sortmate.py --help
```

## Configuration

### 1. Google Cloud Setup

#### Gmail API Setup:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gmail API
4. Go to "Credentials" → "Create Credentials" → "OAuth client ID"
5. Choose "Desktop application" as application type
6. Download credentials as `client_secret.json`
7. Store this file securely outside your project directory

#### Pub/Sub Setup (Optional - for real-time monitoring):
1. Enable the Cloud Pub/Sub API
2. Create a topic: `gcloud pubsub topics create gmail-notifications`
3. Create a subscription: `gcloud pubsub subscriptions create gmail-sub --topic=gmail-notifications`
4. Grant Gmail service account publish permissions to your topic

### 2. Environment Configuration

1. **Copy the example configuration**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** with your settings:
   ```bash
   # Google OAuth Configuration
   GOOGLE_CLIENT_SECRETS_FILE=/path/to/your/client_secret.json
   GOOGLE_TOKEN_DIR=~/.config/SortMate/tokens
   GOOGLE_API_SCOPES=https://www.googleapis.com/auth/gmail.modify,https://www.googleapis.com/auth/gmail.labels

   # Google Cloud Project Details (for real-time monitoring)
   GOOGLE_CLOUD_PROJECT=your-project-id
   PUBSUB_TOPIC=gmail-notifications
   PUBSUB_SUBSCRIPTION=gmail-sub
   ```

### 3. Application Configuration

SortMate creates a configuration file at `~/.config/SortMate/config.json` with customizable options:

```json
{
    "sorting_methods": ["date"],
    "ignore_labels": ["SPAM", "TRASH"],
    "categorization_options": {
        "date": true,
        "sender": {"enabled": false, "type": "domain"},
        "keywords": {"enabled": false, "keywords": null}
    },
    "max_emails_per_batch": 100
}
```

## Usage

### Basic Commands

```bash
# Basic email sorting
sortmate

# Sort with verbose output
sortmate --verbose

# Sort limited number for testing
sortmate --max-emails 10

# Sort and monitor for new emails
sortmate --monitor

# Combined options
sortmate --monitor --verbose --max-emails 50
```

### Command-Line Options

| Option | Description |
|--------|-------------|
| `--monitor` | Enable real-time email monitoring |
| `--max-emails N` | Limit processing to N emails (useful for testing) |
| `--verbose` | Enable detailed logging output |
| `--help` | Show help message and exit |

### Running Methods

```bash
# Method 1: Installed package
sortmate

# Method 2: Python module
python -m sortmate.cli

# Method 3: Development script
python run_sortmate.py

# Method 4: Direct execution (if executable)
./run_sortmate.py
```

## Email Organization Features

### 1. Date-Based Organization (Default)

Automatically creates labels by year and month:
- `2025/Jan`, `2025/Feb`, etc.
- `2024/Dec`, `2024/Nov`, etc.

### 2. Sender-Based Organization (Optional)

Organize by sender with three modes:

**Domain Mode**:
- `Senders/Domains/gmail.com`
- `Senders/Domains/company.org`

**Organization Mode**:
- `Senders/Organizations/Google`
- `Senders/Organizations/Microsoft`

**Individual Mode**:
- `Senders/People/John Doe`
- `Senders/People/Jane Smith`

### 3. Keyword-Based Organization (Optional)

Automatic categorization based on email content:
- `Keywords/Meeting` - meeting, conference, call, zoom
- `Keywords/Financial` - invoice, payment, bill, receipt
- `Keywords/Urgent` - urgent, asap, emergency, priority
- `Keywords/Travel` - flight, hotel, booking, ticket
- `Keywords/Shopping` - order, shipping, delivery, purchase

## Real-time Email Monitoring

SortMate can continuously monitor your inbox and automatically sort new emails as they arrive.

### How It Works

1. **Gmail API Push Notifications**: Gmail sends notifications to Google Cloud Pub/Sub when new emails arrive
2. **Real-time Processing**: SortMate receives notifications and processes new emails immediately
3. **Automatic Sorting**: New emails are automatically labeled according to your configuration

### Setup Monitoring

1. **Configure Pub/Sub** (see Configuration section)
2. **Run with monitoring**:
   ```bash
   sortmate --monitor
   ```
3. **Keep running**: The process continues until you stop it with Ctrl+C

### Monitoring Notes

- **Watch Expiration**: Gmail API watch expires after 7 days and requires restart
- **Background Operation**: Process runs continuously when `--monitor` is enabled
- **Graceful Shutdown**: Press Ctrl+C for clean exit
- **Production Use**: Consider using systemd, supervisor, or Docker for production deployments

## Testing

SortMate includes comprehensive tests for reliability and maintainability.

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-mock pytest-cov

# Run all tests
pytest

# Run with coverage report
pytest --cov=sortmate

# Run specific test file
pytest tests/test_sort.py

# Run with detailed output
pytest -v
```

### Test Structure

- **Unit Tests**: Individual function testing with mocking
- **Integration Tests**: Multi-component testing
- **Mocking**: External services (Gmail API, Pub/Sub) are mocked
- **Coverage**: Comprehensive test coverage for critical paths

### Continuous Integration

Set up automated testing with GitHub Actions:

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-mock pytest-cov
      - name: Run tests
        run: pytest --cov=sortmate
```

## Security & Privacy

SortMate handles sensitive Google API credentials with security best practices:

### Security Measures

1. **OAuth2 Authentication**: No password storage, uses secure Google OAuth2 flow
2. **Secure Token Storage**: Tokens stored in `~/.config/SortMate/tokens` with restricted permissions (600)
3. **Environment Variables**: Credential paths stored in environment variables, not hard-coded
4. **Minimal Permissions**: Only requests necessary Gmail API scopes
5. **No Data Storage**: SortMate doesn't store email content, only processes and labels

### Privacy Protection

- **Local Processing**: All email processing happens locally on your machine
- **No Data Transmission**: Email content is not sent to external servers
- **Credential Isolation**: API credentials are isolated from the codebase
- **Audit Trail**: Comprehensive logging for transparency

### Security Checklist

- ✅ Never commit credentials to version control
- ✅ Store `client_secret.json` outside project directory
- ✅ Use environment variables for configuration
- ✅ Regularly rotate OAuth tokens if needed
- ✅ Monitor API usage in Google Cloud Console

## Troubleshooting

### Authentication Issues

**Problem**: `GOOGLE_CLIENT_SECRETS_FILE not set` error
```bash
# Solution: Set the environment variable
export GOOGLE_CLIENT_SECRETS_FILE=/path/to/your/client_secret.json
# Or add it to your .env file
```

**Problem**: `redirect_uri_mismatch` error
```bash
# Solution: Add authorized redirect URI in Google Cloud Console
# Add: http://localhost:8080/
```

**Problem**: Token refresh errors
```bash
# Solution: Delete existing tokens to force re-authentication
rm ~/.config/SortMate/tokens/*
sortmate
```

### Installation Issues

**Problem**: `No module named 'sortmate'` error
```bash
# Solution 1: Install in development mode
pip install -e .

# Solution 2: Use module execution
python -m sortmate.cli

# Solution 3: Use development script
python run_sortmate.py
```

**Problem**: Permission denied errors
```bash
# Solution: Check file permissions
chmod +x run_sortmate.py
# Ensure virtual environment is activated
source .venv/bin/activate
```

### Monitoring Issues

**Problem**: Pub/Sub connection errors
```bash
# Check environment variables
echo $GOOGLE_CLOUD_PROJECT
echo $PUBSUB_SUBSCRIPTION

# Verify Pub/Sub setup
gcloud pubsub topics list
gcloud pubsub subscriptions list
```

**Problem**: Watch notifications not working
```bash
# Check Gmail API quotas in Google Cloud Console
# Verify Pub/Sub permissions for Gmail service account
# Run with --verbose for detailed logging
sortmate --monitor --verbose
```

### Performance Issues

**Problem**: Slow email processing
```bash
# Use --max-emails for testing
sortmate --max-emails 100

# Check batch size in config
cat ~/.config/SortMate/config.json
```

## Advanced Configuration

### Custom Keyword Rules

Edit `~/.config/SortMate/config.json` to add custom keywords:

```json
{
    "categorization_options": {
        "keywords": {
            "enabled": true,
            "keywords": {
                "work": ["project", "deadline", "meeting"],
                "personal": ["family", "friends", "vacation"],
                "bills": ["utility", "insurance", "mortgage"]
            }
        }
    }
}
```

### Sender Organization Mapping

Customize organization mappings in the source code or configuration:

```python
# In sortmate/sort.py or custom config
ORGANIZATION_DOMAINS = {
    'company.com': 'My Company',
    'university.edu': 'University',
    'government.gov': 'Government'
}
```

### Batch Processing Optimization

Adjust batch sizes for performance:

```json
{
    "max_emails_per_batch": 50,  // Reduce for slower systems
    "batch_size": 10             // API request batch size
}
```

## Development

### Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Write tests** for your changes
4. **Ensure tests pass**: `pytest`
5. **Add documentation** for new features
6. **Commit changes**: `git commit -m 'Add amazing feature'`
7. **Push to branch**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**

### Development Setup

```bash
# Clone and setup
git clone https://github.com/amaan-19/SortMate.git
cd SortMate
python -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-mock pytest-cov black flake8

# Setup pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Code Style

We use Black for code formatting and Flake8 for linting:

```bash
# Format code
black sortmate/ tests/

# Check linting
flake8 sortmate/ tests/

# Run before committing
pre-commit run --all-files
```

### Adding New Features

When adding new features:

1. **Write tests first** (TDD approach)
2. **Update documentation** in README and docstrings
3. **Add configuration options** if needed
4. **Ensure backward compatibility**
5. **Update the changelog**

## Roadmap

### Completed ✅
- [x] Core email sorting by date
- [x] Real-time monitoring
- [x] Comprehensive test coverage
- [x] Sender-based categorization
- [x] Keyword-based categorization
- [x] Flexible configuration system

### In Progress 🚧
- [ ] Web-based user interface
- [ ] Multiple email account support
- [ ] Advanced filtering rules
- [ ] Label hierarchy customization

### Planned 📋
- [ ] System tray application
- [ ] Email analytics and reporting
- [ ] Machine learning categorization
- [ ] IMAP support for other providers
- [ ] Email archiving features
- [ ] Undo/redo labeling operations

## FAQ

**Q: Does SortMate store my emails?**
A: No, SortMate only adds labels to your Gmail messages. All emails remain in your Gmail account.

**Q: Can I use SortMate with multiple Gmail accounts?**
A: Currently, SortMate works with one Gmail account at a time. Multi-account support is planned.

**Q: What happens if I stop the monitoring process?**
A: New emails won't be automatically sorted, but you can run SortMate manually to catch up.

**Q: Can I customize the labeling rules?**
A: Yes, you can customize keyword rules in the configuration file and modify sender categorization.

**Q: Is SortMate safe to use with my Gmail account?**
A: Yes, SortMate uses Google's official OAuth2 authentication and only requests the minimum necessary permissions.

## Support

- **Documentation**: [GitHub Wiki](https://github.com/amaan-19/SortMate/wiki)
- **Issues**: [GitHub Issues](https://github.com/amaan-19/SortMate/issues)
- **Discussions**: [GitHub Discussions](https://github.com/amaan-19/SortMate/discussions)
- **Email**: [amaanakhan523@gmail.com](mailto:amaanakhan523@gmail.com)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Google Gmail API team for excellent documentation
- Python community for amazing libraries
- Contributors and beta testers
- Open source community for inspiration

---

Made with ❤️ by [Amaan Khan](https://github.com/amaan-19)

**⭐ Star this repository if SortMate helps organize your inbox!**