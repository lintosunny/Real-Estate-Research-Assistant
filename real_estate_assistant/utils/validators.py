import re
from typing import List 
from urllib.parse import urlparse
from real_estate_assistant.utils.exceptions import ValidationError
from real_estate_assistant.config import settings

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


import re
from urllib.parse import urlparse

def sanitize_input(url: str) -> str:
    """
    Sanitize a URL string to ensure it's clean and safe.

    Args:
        url: The URL string to sanitize.

    Returns:
        A sanitized URL string.

    Raises:
        ValidationError: If the URL is malformed or missing a scheme.
    """
    url = url.strip()
    
    # Parse the URL and validate components
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValidationError("Invalid URL: missing scheme or host")

    # Remove suspicious characters
    url = re.sub(r'[<>\"\'`]', '', url)

    return url[:1000]



if __name__ == "__main__":
    
    # Example usage
    try:
        urls = ["https://example.com", "http://test.com"]
        valid_urls = validate_urls(urls)
        print("Valid URLs:", valid_urls)
        
        query = "Find properties in New York"
        validated_query = validate_query(query)
        print("Validated Query:", validated_query)
        
    except ValidationError as e:
        print(f"Validation Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")