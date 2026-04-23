"""
DML Stream Exceptions Package.

Hierarchical exception structure for precise error handling
throughout the application.
"""

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

__all__ = [
    # Base
    "DMLBaseException",
    # Download exceptions
    "DownloadError",
    "NetworkError",
    "AuthError",
    "StreamNotFoundError",
    "PlaylistError",
    # Config exceptions
    "ConfigError",
    "ValidationError",
    "NotFoundError",
    # FFmpeg exceptions
    "FFmpegError",
    "ConversionError",
    "FFmpegNotFoundError",
    # Storage exceptions
    "DatabaseError",
    "RepositoryError",
]
