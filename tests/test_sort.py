"""
Tests for the sort.py module in the SortMate package.
"""

import pytest
from sortmate.sort import format_date


def test_format_date_valid_input():
    """Test that format_date correctly extracts year and month from a valid date string."""
    # Example date format from email headers
    date_str = "Mon, 15 May 2025 14:23:01 +0000"
    
    # Call the function
    year, month = format_date(date_str)
    
    # Verify results
    assert year == "2025"
    assert month == "May"


def test_format_date_different_timezone():
    """Test that format_date handles different timezone formats."""
    date_str = "Tue, 16 Jan 2024 09:45:17 -0800 (PST)"
    
    year, month = format_date(date_str)
    
    assert year == "2024"
    assert month == "Jan"


def test_format_date_invalid_input():
    """Test that format_date returns None values for invalid input."""
    # Invalid date string
    date_str = "Not a valid date"
    
    # Call the function
    year, month = format_date(date_str)
    
    # Verify results
    assert year is None
    assert month is None


def test_format_date_empty_input():
    """Test that format_date handles empty input."""
    date_str = ""
    
    year, month = format_date(date_str)
    
    assert year is None
    assert month is None