"""
Custom exceptions for YouTube Downloader.

This module defines all custom exceptions used throughout the application
for consistent error handling and reporting.
"""

from typing import Optional


class YouTubeDownloaderError(Exception):
    """
    Base exception for all YouTube Downloader errors.
    
    All custom exceptions in this application inherit from this base class.
    This allows for centralized error handling and consistent error reporting.
    """
    
    def __init__(self, message: str, details: Optional[str] = None):
        """
        Initialize the exception.
        
        Args:
            message: The error message to display.
            details: Optional additional details about the error.
        """
        super().__init__(message)
        self.message = message
        self.details = details
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class InvalidURLError(YouTubeDownloaderError):
    """
    Raised when an invalid YouTube URL is provided.
    
    This exception is raised when:
    - The URL doesn't match YouTube URL patterns
    - The URL is malformed or incomplete
    - The URL points to a non-YouTube domain
    """
    
    def __init__(self, url: str, message: Optional[str] = None):
        """
        Initialize the invalid URL error.
        
        Args:
            url: The invalid URL that caused the error.
            message: Optional custom error message.
        """
        self.url = url
        default_message = f"Invalid YouTube URL: {url}"
        super().__init__(message or default_message)


class DownloadError(YouTubeDownloaderError):
    """
    Raised when a download fails.
    
    This exception is raised for various download-related failures:
    - Network connectivity issues
    - Server errors
    - Stream unavailability
    - File write errors
    """
    
    def __init__(
        self, 
        message: str, 
        url: Optional[str] = None,
        retryable: bool = True
    ):
        """
        Initialize the download error.
        
        Args:
            message: The error message.
            url: Optional URL that failed to download.
            retryable: Whether the download can be retried.
        """
        super().__init__(message)
        self.url = url
        self.retryable = retryable


class FFmpegNotFoundError(YouTubeDownloaderError):
    """
    Raised when FFmpeg is not found in the system PATH.
    
    FFmpeg is required for:
    - Merging video and audio streams
    - Format conversion
    - Audio extraction
    """
    
    def __init__(self, message: Optional[str] = None):
        """
        Initialize the FFmpeg not found error.
        
        Args:
            message: Optional custom error message.
        """
        default_message = (
            "FFmpeg is required for this operation but was not found in the system PATH. "
            "Please install FFmpeg from https://ffmpeg.org/download.html and ensure it's "
            "added to your system PATH."
        )
        super().__init__(message or default_message)


class NoStreamsFoundError(YouTubeDownloaderError):
    """
    Raised when no suitable streams are found for download.
    
    This can happen when:
    - The video is unavailable or has been removed
    - The video has region restrictions
    - No streams match the requested criteria
    """
    
    def __init__(self, message: str = "No streams found for the video."):
        """
        Initialize the no streams found error.
        
        Args:
            message: Custom error message.
        """
        super().__init__(message)


class ConfigurationError(YouTubeDownloaderError):
    """
    Raised when there's an issue with configuration.
    
    This exception is raised for:
    - Invalid configuration values
    - Missing required configuration
    - Configuration file corruption
    """
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        """
        Initialize the configuration error.
        
        Args:
            message: The error message.
            config_key: Optional configuration key that caused the error.
        """
        super().__init__(message)
        self.config_key = config_key


class ProcessError(YouTubeDownloaderError):
    """
    Raised when a background process fails.
    
    This exception is raised for:
    - Download process failures
    - Conversion process failures
    - Merge process failures
    """
    
    def __init__(
        self, 
        message: str, 
        process_type: Optional[str] = None,
        process_id: Optional[int] = None
    ):
        """
        Initialize the process error.
        
        Args:
            message: The error message.
            process_type: Optional type of process that failed.
            process_id: Optional ID of the failed process.
        """
        super().__init__(message)
        self.process_type = process_type
        self.process_id = process_id


class AuthenticationError(YouTubeDownloaderError):
    """
    Raised when authentication fails for restricted content.
    
    Note: Currently the application only supports public videos.
    This exception is reserved for future authentication features.
    """
    
    def __init__(self, message: str = "Authentication required for this content."):
        """
        Initialize the authentication error.
        
        Args:
            message: The error message.
        """
        super().__init__(message)
