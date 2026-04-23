"""
Error Handler Middleware.

Global exception handler for user-friendly error messages
and consistent error reporting.
"""

import sys
from typing import Optional

from rich.console import Console

from dml_stream.constants.messages import ERROR_PREFIX
from dml_stream.exceptions.base import DMLBaseException
from dml_stream.exceptions.download import (
    DownloadError,
    NetworkError,
    AuthError,
    StreamNotFoundError,
    PlaylistError,
)
from dml_stream.exceptions.config import (
    ConfigError,
    ValidationError,
    NotFoundError,
)
from dml_stream.exceptions.ffmpeg import (
    FFmpegError,
    ConversionError,
    FFmpegNotFoundError,
)
from dml_stream.exceptions.storage import (
    DatabaseError,
    RepositoryError,
)


class ErrorHandler:
    """
    Global error handler for CLI.
    
    Catches exceptions and displays user-friendly error messages
    with appropriate styling and exit codes.
    """

    def __init__(self, console: Optional[Console] = None) -> None:
        """
        Initialize error handler.
        
        Args:
            console: Optional Rich console instance.
        """
        self.console = console or Console()

    def handle(
        self,
        exc: Exception,
        verbose: bool = False,
    ) -> int:
        """
        Handle an exception and return appropriate exit code.
        
        Args:
            exc: Exception to handle.
            verbose: Whether to show detailed error information.
            
        Returns:
            Exit code (0-127).
        """
        # Handle DML Stream custom exceptions
        if isinstance(exc, DMLBaseException):
            return self._handle_dml_exception(exc, verbose)
        
        # Handle known exception types
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            return 0
        
        # Handle unexpected exceptions
        return self._handle_unknown_exception(exc, verbose)

    def _handle_dml_exception(
        self,
        exc: DMLBaseException,
        verbose: bool,
    ) -> int:
        """Handle DML Stream custom exceptions."""
        # Display user-friendly message
        self.console.print(
            f"\n[{self._get_error_color()}]{ERROR_PREFIX} {exc.message}[/]",
        )
        
        # Show details if verbose
        if verbose and exc.details:
            self.console.print(f"\n[yellow]Details:[/] {exc.details}")
        
        # Show technical info in verbose mode
        if verbose:
            self.console.print(f"\n[dim]Error type: {exc.__class__.__name__}[/]")
            if exc.code:
                self.console.print(f"[dim]Error code: {exc.code}[/]")
        
        return self._get_exit_code(exc)

    def _handle_unknown_exception(
        self,
        exc: Exception,
        verbose: bool,
    ) -> int:
        """Handle unexpected exceptions."""
        if verbose:
            # Show full traceback in verbose mode
            import traceback
            self.console.print_exception(show_locals=False)
        else:
            # Show simplified message
            self.console.print(
                f"\n[{self._get_error_color()}]{ERROR_PREFIX} An unexpected error occurred: {exc}[/]",
            )
            self.console.print(
                "\n[dim]Run with --verbose for more details[/]",
            )
        
        return 1

    def _get_error_color(self) -> str:
        """Get color for error messages."""
        return "bold red"

    def _get_exit_code(self, exc: DMLBaseException) -> int:
        """
        Get appropriate exit code for exception.
        
        Args:
            exc: Exception to get exit code for.
            
        Returns:
            Exit code (1-127).
        """
        # Network-related errors
        if isinstance(exc, NetworkError):
            return 2
        
        # Authentication errors
        if isinstance(exc, AuthError):
            return 3
        
        # Not found errors
        if isinstance(exc, (StreamNotFoundError, NotFoundError)):
            return 4
        
        # FFmpeg errors
        if isinstance(exc, (FFmpegError, FFmpegNotFoundError, ConversionError)):
            return 5
        
        # Configuration errors
        if isinstance(exc, (ConfigError, ValidationError)):
            return 6
        
        # Database/storage errors
        if isinstance(exc, (DatabaseError, RepositoryError)):
            return 7
        
        # Download errors
        if isinstance(exc, DownloadError):
            return 8
        
        # Playlist errors
        if isinstance(exc, PlaylistError):
            return 9
        
        # Default
        return 1


def handle_error(
    exc: Exception,
    console: Optional[Console] = None,
    verbose: bool = False,
) -> int:
    """
    Handle an exception and return exit code.
    
    Convenience function for error handling.
    
    Args:
        exc: Exception to handle.
        console: Optional Rich console.
        verbose: Whether to show details.
        
    Returns:
        Exit code.
    """
    handler = ErrorHandler(console)
    return handler.handle(exc, verbose)
