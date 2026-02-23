"""
Core module for YouTube Downloader.

This module contains fundamental components including exceptions,
validators, and constants used throughout the application.
"""

from dml_stream.core.exceptions import (
    YouTubeDownloaderError,
    InvalidURLError,
    DownloadError,
    FFmpegNotFoundError,
    NoStreamsFoundError,
)
from dml_stream.core.validators import (
    validate_youtube_url,
    validate_threads,
    validate_output_folder,
)
from dml_stream.core.constants import (
    VIDEO_FORMATS,
    AUDIO_FORMATS,
    DEFAULT_CONFIG,
    MAX_RETRIES,
    TIMEOUT_SECONDS,
    CHUNK_SIZE,
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
