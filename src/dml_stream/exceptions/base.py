"""
Base Exception Class.

Root of the DML Stream exception hierarchy.
"""

from typing import Optional


class DMLBaseException(Exception):
    """
    Base exception for all DML Stream errors.
    
    All custom exceptions in this application inherit from this base class.
    Provides consistent error handling and reporting capabilities.
    
    Attributes:
        message: Human-readable error message.
        details: Optional additional context or technical details.
        code: Optional error code for programmatic handling.
    """

    def __init__(
        self,
        message: str,
        details: Optional[str] = None,
        code: Optional[str] = None,
    ) -> None:
        """
        Initialize the base exception.
        
        Args:
            message: Human-readable error message.
            details: Optional additional context.
            code: Optional error code.
        """
        super().__init__(message)
        self.message = message
        self.details = details
        self.code = code

    def __str__(self) -> str:
        """Return string representation."""
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message

    def to_dict(self) -> dict:
        """
        Convert exception to dictionary for logging/serialization.
        
        Returns:
            Dictionary with message, details, and code.
        """
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
            "code": self.code,
        }
