"""
Core module for YouTube Downloader.

This module contains fundamental components including exceptions,
validators, and constants used throughout the application.
"""

from dml_stream.core.constants import (
    AUDIO_FORMATS,
    CHUNK_SIZE,
    DEFAULT_CONFIG,
    MAX_RETRIES,
    TIMEOUT_SECONDS,
    VIDEO_FORMATS,
)
from dml_stream.core.exceptions import (
    DownloadError,
    FFmpegNotFoundError,
    InvalidURLError,
    NoStreamsFoundError,
    YouTubeDownloaderError,
)
from dml_stream.core.validators import (
    validate_output_folder,
    validate_threads,
    validate_youtube_url,
)

__all__ = [
    # Exceptions
    "YouTubeDownloaderError",
    "InvalidURLError",
    "DownloadError",
    "FFmpegNotFoundError",
    "NoStreamsFoundError",
    # Validators
    "validate_youtube_url",
    "validate_threads",
    "validate_output_folder",
    # Constants
    "VIDEO_FORMATS",
    "AUDIO_FORMATS",
    "DEFAULT_CONFIG",
    "MAX_RETRIES",
    "TIMEOUT_SECONDS",
    "CHUNK_SIZE",
]
