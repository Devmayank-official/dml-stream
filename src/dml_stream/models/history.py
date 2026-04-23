"""
History Models.

Data classes for download history tracking.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class HistoryEntry:
    """
    Represents a completed download entry in history.
    
    Attributes:
        id: Unique entry identifier.
        title: Title of downloaded content.
        url: Original YouTube URL.
        file_path: Path to downloaded file.
        file_size: File size in bytes.
        download_date: ISO format timestamp.
        download_type: Type ('video', 'audio', 'playlist').
        status: Status ('success', 'failed').
        duration: Video duration in seconds.
        format: Output format (e.g., 'mp4', 'mp3').
    """

    id: Optional[int]
    title: str
    url: str
    file_path: str
    file_size: int
    download_date: str
    download_type: str
    status: str
    duration: Optional[int] = None
    format: Optional[str] = None

    @classmethod
    def create(
        cls,
        title: str,
        url: str,
        file_path: str,
        download_type: str = "video",
        status: str = "success",
        duration: Optional[int] = None,
        format: Optional[str] = None,
    ) -> "HistoryEntry":
        """
        Create a new history entry.
        
        Args:
            title: Title of content.
            url: Original URL.
            file_path: Path to file.
            download_type: Type of download.
            status: Download status.
            duration: Video duration.
            format: Output format.
            
        Returns:
            New HistoryEntry instance.
        """
        return cls(
            id=None,
            title=title,
            url=url,
            file_path=file_path,
            file_size=cls._get_file_size(file_path),
            download_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            download_type=download_type,
            status=status,
            duration=duration,
            format=format,
        )

    @staticmethod
    def _get_file_size(file_path: str) -> int:
        """Get file size in bytes."""
        import os
        try:
            if os.path.exists(file_path):
                return os.path.getsize(file_path)
        except Exception:
            pass
        return 0

    @property
    def file_size_formatted(self) -> str:
        """Get formatted file size."""
        if not self.file_size:
            return "Unknown"
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f}{unit}"
            size /= 1024.0
        return f"{size:.2f}TB"

    @property
    def duration_formatted(self) -> str:
        """Get formatted duration."""
        if not self.duration:
            return "Unknown"
        
        hours, remainder = divmod(self.duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        from dataclasses import asdict
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "HistoryEntry":
        """Create from dictionary."""
        return cls(**data)
