"""
Data entities for YouTube Downloader.

This module defines all dataclasses used to represent domain entities
such as downloads, processes, and batch operations.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from dml_stream.core.constants import (
    PROCESS_STATUS_PENDING,
    PROCESS_STATUS_RUNNING,
    PROCESS_STATUS_COMPLETED,
    PROCESS_STATUS_FAILED,
    DOWNLOAD_TYPE_VIDEO,
    DOWNLOAD_TYPE_AUDIO,
    DOWNLOAD_TYPE_PLAYLIST,
)


@dataclass
class DownloadHistory:
    """
    Represents a completed download entry in history.
    
    Attributes:
        title: Title of the downloaded content.
        url: Original YouTube URL.
        file_path: Path to the downloaded file.
        file_size: Human-readable file size (e.g., "150.25MB").
        download_date: ISO format timestamp of download completion.
        download_type: Type of download ('video', 'audio', 'playlist').
        status: Download status ('success', 'failed').
    """
    
    title: str
    url: str
    file_path: str
    file_size: str
    download_date: str
    download_type: str  # 'video', 'audio', 'playlist'
    status: str  # 'success', 'failed'
    
    @classmethod
    def create(
        cls,
        title: str,
        url: str,
        file_path: str,
        download_type: str = DOWNLOAD_TYPE_VIDEO,
        status: str = "success"
    ) -> 'DownloadHistory':
        """
        Create a new download history entry.
        
        Args:
            title: Title of the downloaded content.
            url: Original YouTube URL.
            file_path: Path to the downloaded file.
            download_type: Type of download.
            status: Download status.
            
        Returns:
            New DownloadHistory instance.
        """
        # Get file size
        file_size = "Unknown"
        try:
            import os
            if os.path.exists(file_path):
                size_bytes = os.path.getsize(file_path)
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size_bytes < 1024.0:
                        file_size = f"{size_bytes:.2f}{unit}"
                        break
                    size_bytes /= 1024.0
        except Exception:
            pass
        
        return cls(
            title=title,
            url=url,
            file_path=file_path,
            file_size=file_size,
            download_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            download_type=download_type,
            status=status
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        from dataclasses import asdict
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DownloadHistory':
        """Create instance from dictionary."""
        return cls(**data)


@dataclass
class ScheduledDownload:
    """
    Represents a scheduled download task.
    
    Attributes:
        id: Unique identifier for the scheduled download.
        url: YouTube URL to download.
        download_type: Type of download ('video', 'audio', 'playlist').
        output_folder: Destination folder for the download.
        scheduled_time: Scheduled execution time (ISO format or HH:MM).
        method: Download method ('normal' or 'fast').
        threads: Number of download threads.
        output_format: Optional output format for conversion.
        max_speed: Optional download speed limit in bytes/second.
        status: Current status ('pending', 'in_progress', 'completed', 'failed', 'cancelled').
        created_at: ISO format timestamp of creation.
        completed_at: Optional ISO format timestamp of completion.
    """
    
    id: str
    url: str
    download_type: str
    output_folder: str
    scheduled_time: str
    method: str
    threads: int
    output_format: Optional[str] = None
    max_speed: Optional[float] = None
    status: str = PROCESS_STATUS_PENDING
    created_at: str = ""
    completed_at: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        url: str,
        download_type: str,
        output_folder: str,
        scheduled_time: str,
        method: str = "normal",
        threads: int = 4,
        output_format: Optional[str] = None,
        max_speed: Optional[float] = None,
    ) -> 'ScheduledDownload':
        """
        Create a new scheduled download.
        
        Args:
            url: YouTube URL to download.
            download_type: Type of download.
            output_folder: Destination folder.
            scheduled_time: Scheduled execution time.
            method: Download method.
            threads: Number of threads.
            output_format: Optional output format.
            max_speed: Optional speed limit.
            
        Returns:
            New ScheduledDownload instance.
        """
        return cls(
            id=str(uuid.uuid4()),
            url=url,
            download_type=download_type,
            output_folder=output_folder,
            scheduled_time=scheduled_time,
            method=method,
            threads=threads,
            output_format=output_format,
            max_speed=max_speed,
            status=PROCESS_STATUS_PENDING,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def is_due(self) -> bool:
        """
        Check if the scheduled download is due for execution.
        
        Returns:
            True if the scheduled time has passed.
        """
        try:
            # Try full datetime format first
            scheduled_datetime = datetime.strptime(self.scheduled_time, "%Y-%m-%d %H:%M:%S")
            return datetime.now() >= scheduled_datetime
        except ValueError:
            # Try time-only format (HH:MM)
            try:
                time_part = datetime.strptime(self.scheduled_time, "%H:%M").time()
                now = datetime.now()
                scheduled_datetime = datetime.combine(now.date(), time_part)
                return now >= scheduled_datetime
            except ValueError:
                return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        from dataclasses import asdict
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScheduledDownload':
        """Create instance from dictionary."""
        return cls(**data)


@dataclass
class ProcessInfo:
    """
    Represents a running or completed process.
    
    Attributes:
        pid: Process ID (system or synthetic).
        name: Process name/type (e.g., 'download', 'conversion').
        url: Source URL being processed.
        status: Process status ('running', 'completed', 'failed', 'cancelled').
        start_time: ISO format timestamp of start.
        end_time: Optional ISO format timestamp of completion.
        progress: Progress percentage (0.0 to 100.0).
        output_path: Path to output file.
        error_message: Optional error message if failed.
        download_type: Type of download ('video', 'audio', 'playlist').
    """
    
    pid: int
    name: str
    url: str
    status: str
    start_time: str
    end_time: Optional[str] = None
    progress: float = 0.0
    output_path: str = ""
    error_message: Optional[str] = None
    download_type: str = ""
    
    @classmethod
    def create(
        cls,
        name: str,
        url: str,
        download_type: str = DOWNLOAD_TYPE_VIDEO,
        pid: Optional[int] = None
    ) -> 'ProcessInfo':
        """
        Create a new process info entry.
        
        Args:
            name: Process name/type.
            url: Source URL.
            download_type: Type of download.
            pid: Optional process ID (uses system PID if not provided).
            
        Returns:
            New ProcessInfo instance.
        """
        import os
        return cls(
            pid=pid or os.getpid(),
            name=name,
            url=url,
            status=PROCESS_STATUS_RUNNING,
            start_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            download_type=download_type
        )
    
    def update_progress(self, progress: float, output_path: str = "") -> None:
        """
        Update process progress.
        
        Args:
            progress: Progress percentage (0.0 to 100.0).
            output_path: Optional output path.
        """
        self.progress = max(0.0, min(100.0, progress))
        if output_path:
            self.output_path = output_path
    
    def complete(self, status: str = PROCESS_STATUS_COMPLETED, error_message: Optional[str] = None) -> None:
        """
        Mark process as completed.
        
        Args:
            status: Final status.
            error_message: Optional error message for failed status.
        """
        self.status = status
        self.end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if error_message:
            self.error_message = error_message
    
    def is_running(self) -> bool:
        """Check if process is currently running."""
        return self.status == PROCESS_STATUS_RUNNING
    
    def is_completed(self) -> bool:
        """Check if process completed successfully."""
        return self.status == PROCESS_STATUS_COMPLETED
    
    def is_failed(self) -> bool:
        """Check if process failed."""
        return self.status == PROCESS_STATUS_FAILED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        from dataclasses import asdict
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessInfo':
        """Create instance from dictionary."""
        return cls(**data)


@dataclass
class BatchDownloadItem:
    """
    Represents a single item in a batch download.
    
    Attributes:
        url: YouTube URL to download.
        download_type: Type of download.
        output_folder: Destination folder.
        method: Download method.
        threads: Number of threads.
        output_format: Optional output format.
        max_speed: Optional speed limit.
    """
    
    url: str
    download_type: str
    output_folder: str
    method: str
    threads: int
    output_format: Optional[str] = None
    max_speed: Optional[float] = None
    
    @classmethod
    def create(
        cls,
        url: str,
        download_type: str,
        output_folder: str,
        method: str = "normal",
        threads: int = 4,
        output_format: Optional[str] = None,
        max_speed: Optional[float] = None,
    ) -> 'BatchDownloadItem':
        """Create a new batch download item."""
        return cls(
            url=url,
            download_type=download_type,
            output_folder=output_folder,
            method=method,
            threads=threads,
            output_format=output_format,
            max_speed=max_speed
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        from dataclasses import asdict
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BatchDownloadItem':
        """Create instance from dictionary."""
        return cls(**data)


@dataclass
class BatchDownload:
    """
    Represents a batch download collection.
    
    Attributes:
        id: Unique identifier.
        name: Batch name.
        items: List of batch download items.
        status: Batch status.
        created_at: Creation timestamp.
        completed_at: Optional completion timestamp.
        current_index: Current item being processed.
    """
    
    id: str
    name: str
    items: List[BatchDownloadItem]
    status: str = PROCESS_STATUS_PENDING
    created_at: str = ""
    completed_at: Optional[str] = None
    current_index: int = 0
    
    @classmethod
    def create(
        cls,
        name: str,
        items: Optional[List[BatchDownloadItem]] = None
    ) -> 'BatchDownload':
        """
        Create a new batch download.
        
        Args:
            name: Batch name.
            items: Optional list of items.
            
        Returns:
            New BatchDownload instance.
        """
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            items=items or [],
            status=PROCESS_STATUS_PENDING,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def add_item(self, item: BatchDownloadItem) -> None:
        """Add an item to the batch."""
        self.items.append(item)
    
    def remove_item(self, index: int) -> bool:
        """Remove an item by index."""
        if 0 <= index < len(self.items):
            self.items.pop(index)
            return True
        return False
    
    def get_progress(self) -> float:
        """Get overall batch progress percentage."""
        if not self.items:
            return 0.0
        return (self.current_index / len(self.items)) * 100.0
    
    def is_complete(self) -> bool:
        """Check if batch is complete."""
        return self.current_index >= len(self.items)
    
    def get_current_item(self) -> Optional[BatchDownloadItem]:
        """Get the current item being processed."""
        if 0 <= self.current_index < len(self.items):
            return self.items[self.current_index]
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        from dataclasses import asdict
        data = asdict(self)
        data['items'] = [item.to_dict() if hasattr(item, 'to_dict') else item for item in self.items]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BatchDownload':
        """Create instance from dictionary."""
        items = [
            BatchDownloadItem.from_dict(item) if isinstance(item, dict) else item
            for item in data.get('items', [])
        ]
        return cls(
            id=data['id'],
            name=data['name'],
            items=items,
            status=data.get('status', PROCESS_STATUS_PENDING),
            created_at=data.get('created_at', ''),
            completed_at=data.get('completed_at'),
            current_index=data.get('current_index', 0)
        )


@dataclass
class StreamCandidate:
    """
    Represents a downloadable stream option.
    
    Attributes:
        itag: YouTube stream identifier.
        type: Stream type ('progressive', 'video', 'audio').
        mime: MIME type of the stream.
        resolution: Video resolution (None for audio).
        abr: Audio bitrate (None for video-only).
        filesize: File size in bytes.
        stream: Original pytubefix stream object.
    """
    
    itag: int
    type: str
    mime: str
    resolution: Optional[str]
    abr: Optional[str]
    filesize: int
    stream: Any  # pytubefix.Stream object
    
    def get_size_mb(self) -> float:
        """Get file size in megabytes."""
        return self.filesize / (1024 * 1024) if self.filesize else 0.0
    
    def get_size_formatted(self) -> str:
        """Get human-readable file size."""
        if not self.filesize:
            return "unknown"
        size = self.filesize
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f}{unit}"
            size /= 1024.0
        return f"{size:.2f}TB"
    
    def __str__(self) -> str:
        type_str = self.type.upper()
        res_str = self.resolution or 'N/A'
        abr_str = self.abr or 'N/A'
        size_str = self.get_size_formatted()
        return f"{type_str} | {res_str} | Audio: {abr_str} | Size: {size_str}"


@dataclass
class DownloadProgress:
    """
    Represents download progress information.
    
    Attributes:
        total_bytes: Total bytes to download.
        downloaded_bytes: Bytes downloaded so far.
        speed: Current download speed in bytes/second.
        eta_seconds: Estimated time remaining in seconds.
        percentage: Download percentage (0.0 to 100.0).
        status: Download status.
    """
    
    total_bytes: int = 0
    downloaded_bytes: int = 0
    speed: float = 0.0
    eta_seconds: float = 0.0
    percentage: float = 0.0
    status: str = "pending"
    
    @property
    def is_complete(self) -> bool:
        """Check if download is complete."""
        return self.percentage >= 100.0
    
    @property
    def speed_mb(self) -> float:
        """Get speed in MB/s."""
        return self.speed / (1024 * 1024)
    
    @property
    def eta_formatted(self) -> str:
        """Get formatted ETA string."""
        if self.eta_seconds <= 0:
            return "N/A"
        if self.eta_seconds < 60:
            return f"{int(self.eta_seconds)}s"
        if self.eta_seconds < 3600:
            minutes = int(self.eta_seconds / 60)
            seconds = int(self.eta_seconds % 60)
            return f"{minutes}m {seconds}s"
        hours = int(self.eta_seconds / 3600)
        minutes = int((self.eta_seconds % 3600) / 60)
        return f"{hours}h {minutes}m"
    
    def update(
        self,
        downloaded_bytes: int,
        total_bytes: int,
        speed: float = 0.0
    ) -> None:
        """
        Update progress with new values.
        
        Args:
            downloaded_bytes: Bytes downloaded so far.
            total_bytes: Total bytes to download.
            speed: Current download speed.
        """
        self.downloaded_bytes = downloaded_bytes
        self.total_bytes = total_bytes
        self.speed = speed
        self.percentage = (downloaded_bytes / total_bytes * 100) if total_bytes > 0 else 0.0
        self.eta_seconds = (total_bytes - downloaded_bytes) / speed if speed > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'total_bytes': self.total_bytes,
            'downloaded_bytes': self.downloaded_bytes,
            'speed': self.speed,
            'speed_mb': self.speed_mb,
            'eta_seconds': self.eta_seconds,
            'eta_formatted': self.eta_formatted,
            'percentage': self.percentage,
            'status': self.status,
            'is_complete': self.is_complete,
        }
