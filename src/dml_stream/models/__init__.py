"""
DML Stream Models Package.

Data models split by domain for better separation of concerns.
"""

from dml_stream.models.video import VideoInfo, StreamInfo
from dml_stream.models.download import DownloadJob, DownloadProgress, DownloadResult
from dml_stream.models.history import HistoryEntry
from dml_stream.models.config import AppConfig

# Legacy imports for backward compatibility
# TODO: Remove in v3.0.0 after full migration
from dml_stream.models.entities import (
    BatchDownload,
    BatchDownloadItem,
    DownloadHistory as LegacyDownloadHistory,
    ProcessInfo,
    ScheduledDownload,
    StreamCandidate,
)

__all__ = [
    # Video models
    "VideoInfo",
    "StreamInfo",
    # Download models
    "DownloadJob",
    "DownloadProgress",
    "DownloadResult",
    # History models
    "HistoryEntry",
    # Config models
    "AppConfig",
    # Legacy models (for backward compatibility)
    "BatchDownload",
    "BatchDownloadItem",
    "LegacyDownloadHistory",
    "ProcessInfo",
    "ScheduledDownload",
    "StreamCandidate",
]
