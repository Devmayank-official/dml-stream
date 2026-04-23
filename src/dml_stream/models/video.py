"""
Video and Stream Models.

Data classes for video metadata and stream information.
"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class VideoInfo:
    """
    Represents YouTube video metadata.
    
    Attributes:
        video_id: YouTube video identifier.
        title: Video title.
        author: Channel/author name.
        duration: Duration in seconds.
        view_count: Number of views.
        publish_date: Publication date.
        description: Video description.
        thumbnail_url: Thumbnail image URL.
        is_live: Whether this is a live stream.
        age_restricted: Whether age-restricted.
    """

    video_id: str
    title: str
    author: str
    duration: int
    view_count: int
    publish_date: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_live: bool = False
    age_restricted: bool = False

    @property
    def duration_formatted(self) -> str:
        """Get formatted duration string."""
        if not self.duration:
            return "Unknown"
        
        hours, remainder = divmod(self.duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"

    @property
    def view_count_formatted(self) -> str:
        """Get formatted view count."""
        if self.view_count >= 1_000_000:
            return f"{self.view_count / 1_000_000:.1f}M"
        if self.view_count >= 1_000:
            return f"{self.view_count / 1_000:.1f}K"
        return str(self.view_count)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        from dataclasses import asdict
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "VideoInfo":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class StreamInfo:
    """
    Represents a downloadable stream option.
    
    Attributes:
        itag: YouTube stream identifier.
        mime_type: MIME type of the stream.
        type: Stream type ('progressive', 'video', 'audio').
        resolution: Video resolution (e.g., '1080p', None for audio).
        fps: Frames per second (for video streams).
        video_codec: Video codec (e.g., 'h264', None for audio).
        audio_codec: Audio codec (e.g., 'mp4a', None for video-only).
        abr: Audio bitrate in kbps (for audio streams).
        filesize: File size in bytes.
        is_default: Whether this is the default stream.
    """

    itag: int
    mime_type: str
    type: str
    resolution: Optional[str]
    fps: Optional[int]
    video_codec: Optional[str]
    audio_codec: Optional[str]
    abr: Optional[float]
    filesize: Optional[int]
    is_default: bool = False

    @property
    def filesize_mb(self) -> float:
        """Get file size in megabytes."""
        if not self.filesize:
            return 0.0
        return self.filesize / (1024 * 1024)

    @property
    def filesize_formatted(self) -> str:
        """Get human-readable file size."""
        if not self.filesize:
            return "Unknown"
        
        size = self.filesize
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f}{unit}"
            size /= 1024.0
        return f"{size:.2f}TB"

    @property
    def quality_label(self) -> str:
        """Get quality label for display."""
        if self.type == "audio":
            return f"Audio {int(self.abr)}kbps" if self.abr else "Audio"
        return self.resolution or "Unknown"

    def __str__(self) -> str:
        type_str = self.type.upper()
        quality = self.quality_label
        size_str = self.filesize_formatted
        return f"{type_str} | {quality} | Size: {size_str}"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        from dataclasses import asdict
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "StreamInfo":
        """Create from dictionary."""
        return cls(**data)
