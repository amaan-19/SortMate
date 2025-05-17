"""
Tests for the enhanced categorization features in the sort.py module.
"""

import pytest
from unittest.mock import MagicMock, patch
from sortmate.sort import (
    extract_sender_info,
    extract_email_content,
    get_sender_label,
    get_keyword_label,
    get_all_labels_for_email,
    DEFAULT_KEYWORDS
)


@pytest.fixture
def mock_gmail_service():
    """Create a mock Gmail service object."""
    mock_service = MagicMock()
    
    # Mock the labels.create method response
    def create_label_response(*args, **kwargs):
        # Extract label name from the body
        body = kwargs.get('body', {})
        label_name = body.get('name', 'TestLabel')
        return {'id': f"Label_{hash(label_name) % 1000}", 'name': label_name}
    
    mock_service.users().labels().create().execute.side_effect = create_label_response
    
    return mock_service


@pytest.fixture
def label_cache():
    """Create a sample label cache."""
    return {
        'Senders': 'Label_Senders',
        'Senders/Domains': 'Label_Senders_Domains',
        'Senders/Domains/example.com': 'Label_example_com',
        'Keywords': 'Label_Keywords',
        'Keywords/Urgent': 'Label_Keywords_Urgent',
        '2025': 'Label_2025',
        '2025/May': 'Label_2025_May',
    }


class TestSenderInfoExtraction:
    """Tests for sender information extraction."""
    
    def test_extract_sender_info_with_name_and_brackets(self):
        """Test extracting sender info from 'Name <email>' format."""
        email = {
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'John Doe <john.doe@example.com>'}
                ]
            }
        }
        
        sender_email, sender_domain, sender_name = extract_sender_info(email)
        
        assert sender_email == 'john.doe@example.com'
        assert sender_domain == 'example.com'
        assert sender_name == 'John Doe'
    
    def test_extract_sender_info_email_only(self):
        """Test extracting sender info from email-only format."""
        email = {
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'test@company.org'}
                ]
            }
        }
        
        sender_email, sender_domain, sender_name = extract_sender_info(email)
        
        assert sender_email == 'test@company.org'
        assert sender_domain == 'company.org'
        assert sender_name == 'test'
    
    def test_extract_sender_info_with_quotes(self):
        """Test extracting sender info with quoted names."""
        email = {
            'payload': {
                'headers': [
                    {'name': 'From', 'value': '"Customer Service" <service@shop.com>'}
                ]
            }
        }
        
        sender_email, sender_domain, sender_name = extract_sender_info(email)
        
        assert sender_email == 'service@shop.com'
        assert sender_domain == 'shop.com'
        assert sender_name == 'Customer Service'
    
    def test_extract_sender_info_missing_from_header(self):
        """Test handling missing From header."""
        email = {
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Subject'}
                ]
            }
        }
        
        sender_email, sender_domain, sender_name = extract_sender_info(email)
        
        assert sender_email is None
        assert sender_domain is None
        assert sender_name is None
    
    def test_extract_sender_info_invalid_format(self):
        """Test handling invalid email format."""
        email = {
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'Not an email address'}
                ]
            }
        }
        
        sender_email, sender_domain, sender_name = extract_sender_info(email)
        
        assert sender_email is None
        assert sender_domain is None
        assert sender_name is None


class TestEmailContentExtraction:
    """Tests for email content extraction."""
    
    def test_extract_email_content_complete(self):
        """Test extracting both subject and snippet."""
        email = {
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Important Meeting Tomorrow'},
                    {'name': 'From', 'value': 'boss@company.com'}
                ]
            },
            'snippet': 'Please join us for the quarterly review meeting...'
        }
        
        subject, snippet = extract_email_content(email)
        
        assert subject == 'Important Meeting Tomorrow'
        assert snippet == 'Please join us for the quarterly review meeting...'
    
    def test_extract_email_content_missing_subject(self):
        """Test handling missing subject."""
        email = {
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'sender@example.com'}
                ]
            },
            'snippet': 'Email content without subject'
        }
        
        subject, snippet = extract_email_content(email)
        
        assert subject == ''
        assert snippet == 'Email content without subject'
    
    def test_extract_email_content_missing_snippet(self):
        """Test handling missing snippet."""
        email = {
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Subject'}
                ]
            }
        }
        
        subject, snippet = extract_email_content(email)
        
        assert subject == 'Test Subject'
        assert snippet == ''


class TestSenderLabeling:
    """Tests for sender-based labeling."""
    
    def test_get_sender_label_domain_categorization(self, mock_gmail_service, label_cache):
        """Test domain-based sender categorization."""
        email = {
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'user@newdomain.com'}
                ]
            }
        }
        
        with patch('sortmate.sort.label_exists') as mock_label_exists:
            with patch('sortmate.sort.create_label') as mock_create_label:
                # Mock that the label doesn't exist
                mock_label_exists.return_value = False
                mock_create_label.return_value = 'Label_newdomain'
                label_cache['Senders/Domains/newdomain.com'] = 'Label_newdomain'
                
                result = get_sender_label(mock_gmail_service, email, label_cache, 'domain')
                
                # Should create the domain label
                assert result == 'Label_newdomain'
                # Should have called create_label for the domain
                assert mock_create_label.called
    
    def test_get_sender_label_organization_categorization(self, mock_gmail_service, label_cache):
        """Test organization-based sender categorization."""
        email = {
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'notification@google.com'}
                ]
            }
        }
        
        with patch('sortmate.sort.label_exists') as mock_label_exists:
            with patch('sortmate.sort.create_label') as mock_create_label:
                # Mock that the label doesn't exist
                mock_label_exists.return_value = False
                mock_create_label.return_value = 'Label_Google'
                label_cache['Senders/Organizations/Google'] = 'Label_Google'
                
                result = get_sender_label(mock_gmail_service, email, label_cache, 'organization')
                
                # Should create the organization label for Google
                assert result == 'Label_Google'
    
    def test_get_sender_label_individual_categorization(self, mock_gmail_service, label_cache):
        """Test individual-based sender categorization."""
        email = {
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'Jane Smith <jane.smith@company.com>'}
                ]
            }
        }
        
        with patch('sortmate.sort.label_exists') as mock_label_exists:
            with patch('sortmate.sort.create_label') as mock_create_label:
                # Mock that the label doesn't exist
                mock_label_exists.return_value = False
                mock_create_label.return_value = 'Label_Jane_Smith'
                label_cache['Senders/People/Jane Smith'] = 'Label_Jane_Smith'
                
                result = get_sender_label(mock_gmail_service, email, label_cache, 'individual')
                
                # Should create the individual label
                assert result == 'Label_Jane_Smith'
    
    def test_get_sender_label_no_sender_info(self, mock_gmail_service, label_cache):
        """Test handling email with no sender information."""
        email = {
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test'}
                ]
            }
        }
        
        result = get_sender_label(mock_gmail_service, email, label_cache, 'domain')
        
        # Should return None when no sender info available
        assert result is None


class TestKeywordLabeling:
    """Tests for keyword-based labeling."""
    
    def test_get_keyword_label_single_match(self, mock_gmail_service, label_cache):
        """Test keyword labeling with single keyword match."""
        email = {
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'URGENT: Server Down'}
                ]
            },
            'snippet': 'The production server is experiencing issues...'
        }
        
        with patch('sortmate.sort.label_exists') as mock_label_exists:
            with patch('sortmate.sort.create_label') as mock_create_label:
                # Mock that Keywords label exists but Urgent doesn't
                def label_exists_side_effect(label_name, cache):
                    return label_name == 'Keywords'
                mock_label_exists.side_effect = label_exists_side_effect
                
                mock_create_label.return_value = 'Label_Keywords_Urgent'
                label_cache['Keywords/Urgent'] = 'Label_Keywords_Urgent'
                
                result = get_keyword_label(mock_gmail_service, email, label_cache)
                
                # Should return the urgent keyword label
                assert result == ['Label_Keywords_Urgent']
    
    def test_get_keyword_label_multiple_matches(self, mock_gmail_service, label_cache):
        """Test keyword labeling with multiple keyword matches."""
        email = {
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Meeting Invitation - Project Review'}
                ]
            },
            'snippet': 'Join our zoom call to discuss the quarterly project report...'
        }
        
        with patch('sortmate.sort.label_exists') as mock_label_exists:
            with patch('sortmate.sort.create_label') as mock_create_label:
                # Mock that Keywords label exists but specific ones don't
                def label_exists_side_effect(label_name, cache):
                    return label_name == 'Keywords'
                mock_label_exists.side_effect = label_exists_side_effect
                
                # Mock creating both meeting and work labels
                def create_label_side_effect(service, label_name, cache):
                    if 'Meeting' in label_name:
                        cache[label_name] = 'Label_Keywords_Meeting'
                        return 'Label_Keywords_Meeting'
                    elif 'Work' in label_name:
                        cache[label_name] = 'Label_Keywords_Work'
                        return 'Label_Keywords_Work'
                mock_create_label.side_effect = create_label_side_effect
                
                result = get_keyword_label(mock_gmail_service, email, label_cache)
                
                # Should return both meeting and work labels
                assert len(result) == 2
                assert 'Label_Keywords_Meeting' in result
                assert 'Label_Keywords_Work' in result
    
    def test_get_keyword_label_custom_keywords(self, mock_gmail_service, label_cache):
        """Test keyword labeling with custom keyword dictionary."""
        custom_keywords = {
            'custom_category': ['special', 'custom', 'unique']
        }
        
        email = {
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Special Offer'}
                ]
            },
            'snippet': 'This is a special promotion just for you...'
        }
        
        with patch('sortmate.sort.label_exists') as mock_label_exists:
            with patch('sortmate.sort.create_label') as mock_create_label:
                # Mock that Keywords label exists but specific one doesn't
                def label_exists_side_effect(label_name, cache):
                    return label_name == 'Keywords'
                mock_label_exists.side_effect = label_exists_side_effect
                
                mock_create_label.return_value = 'Label_Keywords_Custom_category'
                label_cache['Keywords/Custom_category'] = 'Label_Keywords_Custom_category'
                
                result = get_keyword_label(mock_gmail_service, email, label_cache, custom_keywords)
                
                # Should return the custom category label
                assert result == ['Label_Keywords_Custom_category']
    
    def test_get_keyword_label_no_matches(self, mock_gmail_service, label_cache):
        """Test keyword labeling with no keyword matches."""
        email = {
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Regular Email'}
                ]
            },
            'snippet': 'Just a normal conversation...'
        }
        
        result = get_keyword_label(mock_gmail_service, email, label_cache)
        
        # Should return empty list when no keywords match
        assert result == []


class TestAllLabelsForEmail:
    """Tests for getting all applicable labels for an email."""
    
    def test_get_all_labels_default_options(self, mock_gmail_service, label_cache):
        """Test getting all labels with default options (only date)."""
        email = {
            'id': 'msg123',
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'test@example.com'},
                    {'name': 'Date', 'value': 'Mon, 15 May 2025 14:23:01 +0000'},
                    {'name': 'Subject', 'value': 'Test Email'}
                ]
            },
            'snippet': 'Test email content'
        }
        
        with patch('sortmate.sort.get_date_label') as mock_get_date_label:
            mock_get_date_label.return_value = 'Label_2025_May'
            
            result = get_all_labels_for_email(mock_gmail_service, email, label_cache)
            
            # Should only return date label with default options
            assert result == ['Label_2025_May']
    
    def test_get_all_labels_multiple_options(self, mock_gmail_service, label_cache):
        """Test getting all labels with multiple categorization options enabled."""
        email = {
            'id': 'msg123',
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'urgent@company.com'},
                    {'name': 'Date', 'value': 'Mon, 15 May 2025 14:23:01 +0000'},
                    {'name': 'Subject', 'value': 'URGENT: Action Required'}
                ]
            },
            'snippet': 'This requires immediate attention...'
        }
        
        categorization_options = {
            'date': True,
            'sender': {'enabled': True, 'type': 'domain'},
            'keywords': {'enabled': True, 'keywords': None}
        }
        
        with patch('sortmate.sort.get_date_label') as mock_get_date_label:
            with patch('sortmate.sort.get_sender_label') as mock_get_sender_label:
                with patch('sortmate.sort.get_keyword_label') as mock_get_keyword_label:
                    mock_get_date_label.return_value = 'Label_2025_May'
                    mock_get_sender_label.return_value = 'Label_company_com'
                    mock_get_keyword_label.return_value = ['Label_Keywords_Urgent']
                    
                    result = get_all_labels_for_email(
                        mock_gmail_service, email, label_cache, categorization_options
                    )
                    
                    # Should return all three types of labels
                    assert len(result) == 3
                    assert 'Label_2025_May' in result
                    assert 'Label_company_com' in result
                    assert 'Label_Keywords_Urgent' in result
    
    def test_get_all_labels_selective_options(self, mock_gmail_service, label_cache):
        """Test getting labels with only some options enabled."""
        email = {
            'id': 'msg123',
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'newsletter@company.com'},
                    {'name': 'Date', 'value': 'Mon, 15 May 2025 14:23:01 +0000'},
                    {'name': 'Subject', 'value': 'Weekly Newsletter'}
                ]
            },
            'snippet': 'Your weekly updates are here...'
        }
        
        categorization_options = {
            'date': False,  # Disabled
            'sender': {'enabled': True, 'type': 'organization'},
            'keywords': {'enabled': False}  # Disabled
        }
        
        with patch('sortmate.sort.get_sender_label') as mock_get_sender_label:
            mock_get_sender_label.return_value = 'Label_Company'
            
            result = get_all_labels_for_email(
                mock_gmail_service, email, label_cache, categorization_options
            )
            
            # Should only return sender label
            assert result == ['Label_Company']


if __name__ == "__main__":
    pytest.main([__file__])
