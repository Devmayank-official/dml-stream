"""
Models module for YouTube Downloader.

This module contains all data models and dataclasses used throughout
the application for consistent data representation.
"""

from dml_stream.models.entities import (
    DownloadHistory,
    ScheduledDownload,
    ProcessInfo,
    BatchDownloadItem,
    BatchDownload,
    StreamCandidate,
    DownloadProgress,
)
from dml_stream.models.repositories import (
    HistoryRepository,
    ScheduledDownloadRepository,
    BatchDownloadRepository,
    ProcessRepository,
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
