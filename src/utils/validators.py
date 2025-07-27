import re
from typing import List 
from urllib.parse import urlparse
import urllib.parse
from src.utils.exceptions import ValidationError
from src.config import settings

def validate_url(url: str) -> bool:
    """
    Validate if the given URL is well-formed and matches the allowed patterns.
    
    Args:
        url: The URL to validate.
        
    Returns:
        True if the URL is valid, raises ValidationError otherwise.
    """
    try:
        parsed = urlparse(url)
        
        # Check if scheme and netloc are present
        if not parsed.scheme or not parsed.netloc:
            raise ValidationError(f"Invalid URL: {url}")
        
        # Check for allowed schemes
        if parsed.scheme not in ['http', 'https']:
            raise ValidationError(f"Unsupported URL scheme: {parsed.scheme}")
        
        return True
    except Exception as e:
        raise ValidationError(f"Error validating URL '{url}': {str(e)}")
    

def validate_urls(urls: List[str]) -> List[str]:
    """
    Validate a list of URLs.
    
    Args:
        urls: List of URLs to validate.
        
    Returns:
        List of valid URLs.
        
    Raises:
        ValidationError if any URL is invalid.
    """

    if not urls:
        raise ValidationError("At least one URL must be provided")
    
    valid_urls = []
    
    for url in urls:
        if validate_url(url):
            valid_urls.append(url)
    
    if len(valid_urls) > settings.max_urls_per_request:
        raise ValidationError(f"Exceeded maximum allowed URLs: {settings.max_urls_per_request}")
    
    if not valid_urls:
        raise ValidationError("No valid URLs provided")
    
    return valid_urls


def validate_query(query:str) -> str:
    """
    Validate the query string.
    
    Args:
        query: The query string to validate.
        
    Returns:
        The validated query string.
        
    Raises:
        ValidationError if the query is invalid.
    """
    
    if not query or not query.strip():
        raise ValidationError("Query cannot be empty")
    
    query = query.strip()

    if len(query) > settings.max_query_length:
        raise ValidationError(
            f"Query too long. Maximum {settings.max_query_length} characters allowed"
        )
    
    # Basic sanitization - remove potentially harmful characters
    query = re.sub(r'[<>"\']', '', query)
    
    return query[:1000]


MAX_LENGTH = 2048  # Reasonable max length to avoid buffer overflow

def sanitize_input(user_input: str) -> str:
    """Sanitize and validate a URL or search query."""
    # Truncate overly long input
    user_input = user_input[:MAX_LENGTH].strip()

    # Basic HTML & script tag stripping to avoid XSS
    user_input = re.sub(r'<.*?>', '', user_input)

    # Remove suspicious characters often used in injection attacks
    user_input = re.sub(r"[;\"\'`<>]", "", user_input)

    # Decode percent-encoded strings (e.g., %3Cscript%3E)
    decoded_input = urllib.parse.unquote(user_input)

    # Re-encode to ensure safe output (if a URL)
    sanitized = urllib.parse.quote_plus(decoded_input, safe=':/?&=')

    return sanitized