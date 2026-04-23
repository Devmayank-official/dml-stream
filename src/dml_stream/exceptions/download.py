"""
Download-Related Exceptions.

Exceptions specific to download operations, network errors,
and stream handling.
"""

from typing import Optional

from dml_stream.exceptions.base import DMLBaseException


class DownloadError(DMLBaseException):
    """
    Raised when a download fails.
    
    This exception is raised for various download-related failures:
    - Network connectivity issues
    - Server errors
    - Stream unavailability
    - File write errors
    
    Attributes:
        message: Error message.
        url: Optional URL that failed to download.
        retryable: Whether the download can be retried.
    """

    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        retryable: bool = True,
    ) -> None:
        """
        Initialize download error.
        
        Args:
            message: Error message.
            url: Optional URL that failed.
            retryable: Whether retry is possible.
        """
        super().__init__(message)
        self.url = url
        self.retryable = retryable


class NetworkError(DownloadError):
    """
    Raised when a network error occurs during download.
    
    This includes:
    - Connection timeouts
    - DNS resolution failures
    - SSL/TLS errors
    - Connection resets
    """

    def __init__(
        self,
        message: str = "Network error occurred",
        url: Optional[str] = None,
        retryable: bool = True,
    ) -> None:
        """
        Initialize network error.
        
        Args:
            message: Error message.
            url: Optional URL that failed.
            retryable: Whether retry is possible.
        """
        super().__init__(message, url, retryable)


class AuthError(DownloadError):
    """
    Raised when authentication fails for restricted content.
    
    This includes:
    - Age-restricted videos requiring login
    - Private videos
    - Member-only content
    - Region-locked content requiring authentication
    """

    def __init__(
        self,
        message: str = "Authentication required for this content",
        url: Optional[str] = None,
    ) -> None:
        """
        Initialize authentication error.
        
        Args:
            message: Error message.
            url: Optional URL that requires auth.
        """
        super().__init__(message, url, retryable=False)


class StreamNotFoundError(DownloadError):
    """
    Raised when no suitable streams are found for download.
    
    This can happen when:
    - The video is unavailable or has been removed
    - The video has region restrictions
    - No streams match the requested criteria
    """

    def __init__(
        self,
        message: str = "No streams found for the video",
        url: Optional[str] = None,
    ) -> None:
        """
        Initialize stream not found error.
        
        Args:
            message: Error message.
            url: Optional URL with no streams.
        """
        super().__init__(message, url, retryable=False)


class PlaylistError(DownloadError):
    """
    Raised when a playlist operation fails.
    
    This includes:
    - Playlist not found
    - Playlist is private
    - Failed to extract playlist items
    - Empty playlist
    """

    def __init__(
        self,
        message: str = "Playlist operation failed",
        url: Optional[str] = None,
        retryable: bool = False,
    ) -> None:
        """
        Initialize playlist error.
        
        Args:
            message: Error message.
            url: Optional playlist URL.
            retryable: Whether retry is possible.
        """
        super().__init__(message, url, retryable)
