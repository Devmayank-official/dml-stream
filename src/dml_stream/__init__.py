"""
YouTube Downloader - Enterprise-Level Terminal-Based Video Download Solution

A production-ready, scalable, and modular YouTube downloader with advanced features
including scheduled downloads, batch processing, and real-time process monitoring.

Author: Santosh
Version: 2.0.0
License: MIT
"""

__version__ = "2.0.0"
__author__ = "Santosh"
__email__ = ""
__license__ = "MIT"

from dml_stream.core.exceptions import (
    YouTubeDownloaderError,
    InvalidURLError,
    DownloadError,
    FFmpegNotFoundError,
    NoStreamsFoundError,
)
from dml_stream.config.settings import Config

__all__ = [
    "__version__",
    "YouTubeDownloaderError",
    "InvalidURLError",
    "DownloadError",
    "FFmpegNotFoundError",
    "NoStreamsFoundError",
    "Config",
]
