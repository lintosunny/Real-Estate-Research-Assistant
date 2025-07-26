class RealEstateToolException(Exception):
    """Base exception for Real Estate Tool"""
    pass


class URLProcessingError(RealEstateToolException):
    """Raised when URL processing fails"""
    pass


class VectorStoreError(RealEstateToolException):
    """Raised when vector store operations fail"""
    pass


class LLMError(RealEstateToolException):
    """Raised when LLM operations fail"""  
    pass


class ValidationError(RealEstateToolException):
    """Raised when input validation fails"""
    pass


class ConfigurationError(RealEstateToolException):
    """Raised when configuration is invalid"""
    pass


class RateLimitError(RealEstateToolException):
    """Raised when rate limits are exceeded"""
    pass