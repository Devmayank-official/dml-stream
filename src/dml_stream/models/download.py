"""
Download Models.

Data classes for download jobs, progress tracking, and results.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import uuid4


@dataclass
class DownloadJob:
    """
    Represents a download operation.
    
    Attributes:
        id: Unique job identifier.
        url: YouTube URL to download.
        download_type: Type ('video', 'audio', 'playlist').
        output_path: Destination file/folder path.
        format: Output format (e.g., 'mp4', 'mp3').
        quality: Quality setting (e.g., '1080p', 'best').
        created_at: Job creation timestamp.
        started_at: Download start timestamp.
        completed_at: Download completion timestamp.
    """

    id: str
    url: str
    download_type: str
    output_path: str
    format: str
    quality: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    @classmethod
    def create(
        cls,
        url: str,
        download_type: str,
        output_path: str,
        format: str = "mp4",
        quality: str = "best",
    ) -> "DownloadJob":
        """
        Create a new download job.
        
        Args:
            url: YouTube URL.
            download_type: Type of download.
            output_path: Destination path.
            format: Output format.
            quality: Quality setting.
            
        Returns:
            New DownloadJob instance.
        """
        return cls(
            id=str(uuid4()),
            url=url,
            download_type=download_type,
            output_path=output_path,
            format=format,
            quality=quality,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

    def start(self) -> None:
        """Mark job as started."""
        self.started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def complete(self) -> None:
        """Mark job as completed."""
        self.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def is_complete(self) -> bool:
        """Check if job is complete."""
        return self.completed_at is not None

    @property
    def is_running(self) -> bool:
        """Check if job is running."""
        return self.started_at is not None and not self.is_complete

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        from dataclasses import asdict
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "DownloadJob":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class DownloadProgress:
    """
    Represents download progress information.
    
    Attributes:
        total_bytes: Total bytes to download.
        downloaded_bytes: Bytes downloaded so far.
        speed: Current download speed in bytes/second.
        eta_seconds: Estimated time remaining.
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
    def speed_formatted(self) -> str:
        """Get formatted speed string."""
        if self.speed_mb >= 1:
            return f"{self.speed_mb:.2f} MB/s"
        return f"{self.speed / 1024:.2f} KB/s"

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
        speed: float = 0.0,
    ) -> None:
        """
        Update progress with new values.
        
        Args:
            downloaded_bytes: Bytes downloaded.
            total_bytes: Total bytes.
            speed: Current speed.
        """
        self.downloaded_bytes = downloaded_bytes
        self.total_bytes = total_bytes
        self.speed = speed
        self.percentage = (downloaded_bytes / total_bytes * 100) if total_bytes > 0 else 0.0
        self.eta_seconds = (total_bytes - downloaded_bytes) / speed if speed > 0 else 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_bytes": self.total_bytes,
            "downloaded_bytes": self.downloaded_bytes,
            "speed": self.speed,
            "speed_mb": self.speed_mb,
            "speed_formatted": self.speed_formatted,
            "eta_seconds": self.eta_seconds,
            "eta_formatted": self.eta_formatted,
            "percentage": self.percentage,
            "status": self.status,
            "is_complete": self.is_complete,
        }


@dataclass
class DownloadResult:
    """
    Represents the result of a download operation.
    
    Attributes:
        success: Whether download succeeded.
        file_path: Path to downloaded file.
        file_size: File size in bytes.
        duration: Download duration in seconds.
        error: Error message if failed.
        retry_count: Number of retry attempts.
    """

    success: bool
    file_path: Optional[str] = None
    file_size: int = 0
    duration: float = 0.0
    error: Optional[str] = None
    retry_count: int = 0

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
        if self.duration < 60:
            return f"{self.duration:.1f}s"
        minutes = int(self.duration / 60)
        seconds = int(self.duration % 60)
        return f"{minutes}m {seconds}s"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        from dataclasses import asdict
        return asdict(self)

    @classmethod
    def success_result(
        cls,
        file_path: str,
        file_size: int,
        duration: float,
    ) -> "DownloadResult":
        """Create a success result."""
        return cls(
            success=True,
            file_path=file_path,
            file_size=file_size,
            duration=duration,
        )

    @classmethod
    def failure_result(
        cls,
        error: str,
        retry_count: int = 0,
    ) -> "DownloadResult":
        """Create a failure result."""
        return cls(
            success=False,
            error=error,
            retry_count=retry_count,
        )
