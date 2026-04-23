"""
Message Constants.

CLI message templates, prefixes, and user-facing strings.
"""

from typing import Final

# =============================================================================
# MESSAGE PREFIXES (for Rich console styling)
# =============================================================================

#: Success message prefix
SUCCESS_PREFIX: Final[str] = "✓"

#: Error message prefix
ERROR_PREFIX: Final[str] = "✗"

#: Warning message prefix
WARNING_PREFIX: Final[str] = "⚠"

#: Info message prefix
INFO_PREFIX: Final[str] = "ℹ"

#: Download progress prefix
DOWNLOAD_PREFIX: Final[str] = "↓"

#: Upload progress prefix
UPLOAD_PREFIX: Final[str] = "↑"

#: Processing prefix
PROCESSING_PREFIX: Final[str] = "⟳"


# =============================================================================
# SUCCESS MESSAGES
# =============================================================================

SUCCESS_MESSAGES: Final[dict[str, str]] = {
    "download_complete": "Download completed successfully",
    "conversion_complete": "Conversion completed successfully",
    "config_saved": "Configuration saved",
    "config_reset": "Configuration reset to defaults",
    "history_cleared": "Download history cleared",
    "queue_cleared": "Download queue cleared",
    "file_deleted": "File deleted successfully",
    "file_moved": "File moved successfully",
    "file_renamed": "File renamed successfully",
    "update_available": "Update available: {version}",
    "update_complete": "Update completed successfully",
    "service_started": "Service started",
    "service_stopped": "Service stopped",
    "batch_created": "Batch download created",
    "schedule_created": "Download scheduled",
    "schedule_cancelled": "Schedule cancelled",
}


# =============================================================================
# ERROR MESSAGES
# =============================================================================

ERROR_MESSAGES: Final[dict[str, str]] = {
    "ffmpeg_not_found": (
        "FFmpeg is required for this operation but was not found. "
        "Please install FFmpeg from https://ffmpeg.org/download.html"
    ),
    "invalid_url": (
        "Invalid YouTube URL. Please provide a valid YouTube video or playlist URL."
    ),
    "no_streams": (
        "No downloadable streams found for this video."
    ),
    "download_failed": (
        "Download failed. Please check your internet connection and try again."
    ),
    "permission_denied": (
        "Permission denied. Please check file permissions and try again."
    ),
    "disk_full": (
        "Insufficient disk space. Please free up space and try again."
    ),
    "file_not_found": (
        "File not found: {path}"
    ),
    "config_not_found": (
        "Configuration file not found: {path}"
    ),
    "config_invalid": (
        "Invalid configuration: {error}"
    ),
    "network_error": (
        "Network error: {error}"
    ),
    "timeout": (
        "Operation timed out. Please try again."
    ),
    "already_exists": (
        "File already exists: {path}"
    ),
    "invalid_format": (
        "Invalid format: {format}. Supported formats: {formats}"
    ),
    "invalid_resolution": (
        "Invalid resolution: {resolution}"
    ),
    "playlist_empty": (
        "Playlist is empty or inaccessible"
    ),
    "age_restricted": (
        "This video is age-restricted and requires authentication"
    ),
    "region_locked": (
        "This video is not available in your region"
    ),
    "private_video": (
        "This video is private or has been removed"
    ),
    "live_stream": (
        "Live streams are not supported"
    ),
    "membership_required": (
        "This video requires channel membership"
    ),
}


# =============================================================================
# WARNING MESSAGES
# =============================================================================

WARNING_MESSAGES: Final[dict[str, str]] = {
    "low_disk_space": (
        "Warning: Low disk space ({free} remaining)"
    ),
    "slow_connection": (
        "Warning: Slow connection detected"
    ),
    "large_file": (
        "Warning: Large file size ({size})"
    ),
    "deprecated_option": (
        "Warning: Option '{option}' is deprecated and will be removed in a future version"
    ),
    "experimental_feature": (
        "Warning: This is an experimental feature"
    ),
    "overwriting_file": (
        "Warning: Overwriting existing file: {path}"
    ),
    "skipping_item": (
        "Warning: Skipping item: {reason}"
    ),
    "retry_attempt": (
        "Warning: Retry attempt {attempt}/{max}"
    ),
}


# =============================================================================
# INFO MESSAGES
# =============================================================================

INFO_MESSAGES: Final[dict[str, str]] = {
    "checking_updates": "Checking for updates...",
    "fetching_metadata": "Fetching video metadata...",
    "selecting_stream": "Selecting best stream...",
    "downloading": "Downloading...",
    "converting": "Converting...",
    "processing": "Processing...",
    "saving": "Saving to: {path}",
    "eta": "ETA: {time}",
    "speed": "Speed: {speed}/s",
    "progress": "Progress: {percent}%",
    "file_size": "File size: {size}",
    "duration": "Duration: {duration}",
    "resolution": "Resolution: {resolution}",
    "format": "Format: {format}",
    "audio_bitrate": "Audio bitrate: {bitrate}kbps",
    "video_codec": "Video codec: {codec}",
    "audio_codec": "Audio codec: {codec}",
    "total_items": "Total items: {count}",
    "processing_item": "Processing item {current}/{total}",
    "queue_status": "Queue: {pending} pending, {running} running",
    "history_stats": "History: {total} downloads, {size} total",
}


# =============================================================================
# PROMPT MESSAGES
# =============================================================================

PROMPT_MESSAGES: Final[dict[str, str]] = {
    "confirm_overwrite": "File exists. Overwrite?",
    "confirm_delete": "Are you sure you want to delete?",
    "confirm_exit": "Exit and cancel operation?",
    "enter_url": "Enter YouTube URL:",
    "enter_output_path": "Enter output path:",
    "select_format": "Select format:",
    "select_quality": "Select quality:",
    "enter_filename": "Enter filename:",
}


# =============================================================================
# TABLE HEADERS
# =============================================================================

TABLE_HEADERS: Final[dict[str, list[str]]] = {
    "history": ["ID", "Title", "Type", "Size", "Date", "Status"],
    "queue": ["ID", "URL", "Type", "Priority", "Status", "Created"],
    "scheduled": ["ID", "URL", "Type", "Scheduled", "Status"],
    "batch": ["ID", "Name", "Items", "Progress", "Status"],
    "config": ["Key", "Value", "Type"],
    "streams": ["itag", "Type", "Resolution", "Audio", "Size", "Codec"],
}
