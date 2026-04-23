"""
DML Stream: A Scalable, Module-Driven Media Acquisition Framework

A modern, type-safe Python framework designed for high-volume media extraction.
DML Stream leverages a modular manager-pattern to orchestrate complex download batches 
and scheduled workloads. With full Docker support and a persistent SQLite storage layer, 
it bridges the gap between simple CLI tools and enterprise media ingestion pipelines.

Version 2.5.1 - 35+ CLI Commands, Enhanced Storage Management, Developer Tools

Author: DML Labs
Lead Engineer: @devmayank-official
"""

__version__ = "2.5.1"

__version__ = "2.5.0"
__author__ = "DML Labs"
__email__ = "devmayank.inbox@gmail.com"
__license__ = "Apache-2.0"

# Import main components for easy access
from dml_stream.config.settings import Config
from dml_stream.core.exceptions import (
    DownloadError,
    FFmpegNotFoundError,
    InvalidURLError,
    NoStreamsFoundError,
    YouTubeDownloaderError,
)

__all__ = [
    "__version__",
    "YouTubeDownloaderError",
    "InvalidURLError",
    "DownloadError",
    "FFmpegNotFoundError",
    "NoStreamsFoundError",
    "Config",
]
