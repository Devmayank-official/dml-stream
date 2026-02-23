"""
Models module for YouTube Downloader.

This module contains all data models and dataclasses used throughout
the application for consistent data representation.
"""

from dml_stream.models.entities import (
    BatchDownload,
    BatchDownloadItem,
    DownloadHistory,
    DownloadProgress,
    ProcessInfo,
    ScheduledDownload,
    StreamCandidate,
)
from dml_stream.models.repositories import (
    BatchDownloadRepository,
    HistoryRepository,
    ProcessRepository,
    ScheduledDownloadRepository,
)

__all__ = [
    # Entities
    "DownloadHistory",
    "ScheduledDownload",
    "ProcessInfo",
    "BatchDownloadItem",
    "BatchDownload",
    "StreamCandidate",
    "DownloadProgress",
    # Repositories
    "HistoryRepository",
    "ScheduledDownloadRepository",
    "BatchDownloadRepository",
    "ProcessRepository",
]
