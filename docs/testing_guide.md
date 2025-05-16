# Unit Testing Guide for SortMate

This guide explains how to run and write unit tests for the SortMate project.

## Running the Tests

### Prerequisites

Make sure you have the testing tools installed:

```bash
pip install pytest pytest-mock pytest-cov
```

### Running All Tests

From the project root directory, run:

```bash
pytest
```

### Running Specific Test Files

To run tests from a specific file:

```bash
# Run only the sort.py tests
pytest tests/test_sort.py

# Run only the authentication tests
pytest tests/test_authenticate.py
```

### Running Specific Test Functions

To run a specific test function:

```bash
pytest tests/test_sort.py::test_format_date_valid_input
```

### Running Tests with Coverage

To see test coverage (install pytest-cov first: `pip install pytest-cov`):

```bash
pytest --cov=sortmate
```

For a detailed HTML coverage report:

```bash
pytest --cov=sortmate --cov-report=html
```

Then open `htmlcov/index.html` in your browser.

## Understanding the Tests

### Test Structure

Each test file corresponds to a module in the SortMate package:

- `test_sort.py` - Tests for the email sorting functionality
- `test_authenticate.py` - Tests for the authentication system
- `test_pubsub.py` - Tests for real-time email monitoring
- `test_watch.py` - Tests for Gmail API watch setup

### Mocking

Many tests use mocking to simulate external dependencies like the Gmail API:

```python
@patch('sortmate.authenticate.get_token_path')
def test_function(mock_get_token_path):
    # Configure the mock
    mock_get_token_path.return_value = "/test/path"
    
    # Test your code...
```

### Fixtures

Fixtures provide reusable test data or mock objects:

```python
@pytest.fixture
def mock_gmail_service():
    """Create a mock Gmail service object."""
    mock_service = MagicMock()
    # Configure the mock...
    return mock_service

def test_with_fixture(mock_gmail_service):
    # Use the fixture in your test
    result = function_under_test(mock_gmail_service)
```

## Writing New Tests

### Basic Test Structure

A basic test function looks like this:

```python
def test_my_function():
    # 1. Set up test data
    input_data = "test input"
    
    # 2. Call the function being tested
    result = my_function(input_data)
    
    # 3. Verify the result
    assert result == "expected output"
```

### Testing Tips

1. **Test Each Function Separately**: Focus on testing one function at a time.

2. **Test the Happy Path First**: Start by testing the expected behavior when everything works correctly.

3. **Then Test Edge Cases**: Test boundary conditions, empty inputs, and error cases.

4. **Use Descriptive Test Names**: The test name should explain what it's testing, e.g., `test_format_date_handles_empty_input`.

5. **Mock External Dependencies**: Don't rely on external services (Gmail API, etc.) for tests.

6. **Keep Tests Independent**: Each test should be able to run independently of others.

7. **Add Comments**: Explain what your test is verifying, especially for complex tests.

### Example Test Workflow

To add a new test:

1. **Identify what to test**: Choose a function that needs testing.
2. **Understand its behavior**: What does the function do? What are its inputs and outputs?
3. **Write test cases**: Start with normal behavior, then edge cases.
4. **Run the tests**: Use pytest to verify your tests pass.
5. **Check coverage**: Use pytest-cov to identify untested code.

## Testing Different Components

### Testing Functions with API Calls

For functions that call external APIs (like Gmail), use mocking:

```python
def test_api_function():
    # Create a mock for the API response
    with patch('module.requests.get') as mock_get:
        # Configure the mock to return a fake response
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Call the function that uses the API
        result = function_that_calls_api()
        
        # Verify results
        assert result == expected_result
```

### Testing Error Handling

Test how your code handles errors:

```python
def test_error_handling():
    # Create a mock that raises an exception
    with patch('module.function') as mock_func:
        mock_func.side_effect = ValueError("Test error")
        
        # Call the function that should handle this error
        result = function_that_handles_errors()
        
        # Verify error was handled correctly
        assert result == expected_fallback_value
```

### Testing Command-line Interface

For testing the CLI module:

```python
def test_cli_arguments():
    # Mock sys.argv
    with patch('sys.argv', ['program_name', '--verbose', '--max-emails', '10']):
        # Mock argparse.ArgumentParser
        with patch('argparse.ArgumentParser.parse_args') as mock_parse_args:
            # Set up the mock to return appropriate args
            args = MagicMock()
            args.verbose = True
            args.max_emails = 10
            mock_parse_args.return_value = args
            
            # Call the function that parses arguments
            result = parse_arguments()
            
            # Verify parsing worked correctly
            assert result.verbose is True
            assert result.max_emails == 10
```

## Integration Tests

Besides unit tests, consider adding integration tests that test multiple components together:

```python
def test_end_to_end_sorting():
    # Set up test environment
    # This might involve creating sample emails in a test account
    
    # Run the entire sorting process
    # This would call several functions in sequence
    
    # Verify the results
    # Check that emails were properly labeled
```

Integration tests are more complex and may require special setup, but they're valuable for ensuring the entire system works together.

## Continuous Integration

Consider setting up continuous integration (CI) to run tests automatically:

1. Create a `.github/workflows/tests.yml` file for GitHub Actions
2. Configure it to run pytest on each push
3. Add badges to your README showing test status

This ensures tests are run consistently and catches issues early.

## Conclusion

Unit testing is a crucial part of software development. By thoroughly testing each component of SortMate, you can:

- Ensure your code works as expected
- Catch bugs early
- Make changes confidently
- Document how your code should behave

As you continue developing SortMate, aim to add tests for each new feature before or as you implement it (Test-Driven Development).
