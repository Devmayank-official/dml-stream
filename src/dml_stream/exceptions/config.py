"""
Configuration-Related Exceptions.

Exceptions for configuration loading, validation, and access errors.
"""

from typing import Optional

from dml_stream.exceptions.base import DMLBaseException


class ConfigError(DMLBaseException):
    """
    Raised when there's an issue with configuration.
    
    This exception is raised for:
    - Invalid configuration values
    - Missing required configuration
    - Configuration file corruption
    - Configuration loading failures
    
    Attributes:
        message: Error message.
        config_key: Optional configuration key that caused the error.
    """

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
    ) -> None:
        """
        Initialize configuration error.
        
        Args:
            message: Error message.
            config_key: Optional key that caused error.
        """
        super().__init__(message)
        self.config_key = config_key


class ValidationError(ConfigError):
    """
    Raised when configuration validation fails.
    
    This includes:
    - Invalid data types
    - Values out of range
    - Missing required fields
    - Invalid format
    """

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        expected_type: Optional[str] = None,
        actual_value: Optional[str] = None,
    ) -> None:
        """
        Initialize validation error.
        
        Args:
            message: Error message.
            config_key: Optional key that failed validation.
            expected_type: Optional expected type description.
            actual_value: Optional actual value received.
        """
        super().__init__(message, config_key)
        self.expected_type = expected_type
        self.actual_value = actual_value


class NotFoundError(ConfigError):
    """
    Raised when a configuration key or file is not found.
    
    This includes:
    - Missing configuration file
    - Unknown configuration key
    - Missing required path
    """

    def __init__(
        self,
        message: str = "Not found",
        config_key: Optional[str] = None,
        path: Optional[str] = None,
    ) -> None:
        """
        Initialize not found error.
        
        Args:
            message: Error message.
            config_key: Optional missing key.
            path: Optional missing path.
        """
        super().__init__(message, config_key)
        self.path = path
