"""
Cross-platform input validation utilities for DML Stream.

This module provides comprehensive validation functions for user inputs
including URLs, file paths, and configuration values.

Fully cross-platform compatible: Windows, macOS, Linux
"""

import platform
import re
from pathlib import Path
from typing import Optional, Tuple


# Default thread limits (avoid circular import with Config)
DEFAULT_MIN_THREADS = 1
DEFAULT_MAX_THREADS = 12


def validate_youtube_url(url: str) -> Tuple[bool, str]:
    """
    Validate if the provided URL is a valid YouTube URL.
    
    This function checks for various YouTube URL formats including:
    - Standard watch URLs: https://www.youtube.com/watch?v=VIDEO_ID
    - Short URLs: https://youtu.be/VIDEO_ID
    - Embed URLs: https://www.youtube.com/embed/VIDEO_ID
    - Shorts URLs: https://www.youtube.com/shorts/VIDEO_ID
    
    Args:
        url: URL string to validate.
        
    Returns:
        Tuple of (is_valid, error_message).
        If valid, error_message will be an empty string.
    """
    if not url or not isinstance(url, str):
        return False, "URL must be a non-empty string"

    url = url.strip()

    # Comprehensive YouTube URL regex pattern
    youtube_patterns = [
        # Standard watch URL
        r'^(https?:\/\/)?(www\.)?youtube\.com\/watch\?v=[\w-]{11}(&[\w=&]*)?$',
        # Short URL
        r'^(https?:\/\/)?(www\.)?youtu\.be\/[\w-]{11}(\?[\w=&]*)?$',
        # Embed URL
        r'^(https?:\/\/)?(www\.)?youtube\.com\/embed\/[\w-]{11}(\?[\w=&]*)?$',
        # Shorts URL
        r'^(https?:\/\/)?(www\.)?youtube\.com\/shorts\/[\w-]{11}(\?[\w=&]*)?$',
        # Playlist URL
        r'^(https?:\/\/)?(www\.)?youtube\.com\/playlist\?list=[\w-]+$',
        # Live URL
        r'^(https?:\/\/)?(www\.)?youtube\.com\/live\/[\w-]{11}(\?[\w=&]*)?$',
    ]

    for pattern in youtube_patterns:
        if re.match(pattern, url, re.IGNORECASE):
            return True, ""

    # Extract video ID if possible for better error message
    video_id_pattern = r'([?&]v=|\.be\/|\/embed\/|\/shorts\/)([\w-]{11})'
    match = re.search(video_id_pattern, url)

    if match:
        return False, (
            f"URL appears to be incomplete or malformed. "
            f"Extracted video ID: {match.group(2)}"
        )

    return False, "Invalid YouTube URL format. Please provide a valid YouTube video or playlist URL."


def validate_threads(threads: int, min_threads: int = DEFAULT_MIN_THREADS, max_threads: int = DEFAULT_MAX_THREADS) -> Tuple[bool, str]:
    """
    Validate if the number of threads is within acceptable range.

    Args:
        threads: Number of threads to validate.
        min_threads: Minimum allowed threads (default: 1).
        max_threads: Maximum allowed threads (default: 12).

    Returns:
        Tuple of (is_valid, error_message).
        If valid, error_message will be an empty string.
    """
    if not isinstance(threads, int):
        return False, f"Threads must be an integer, got {type(threads).__name__}"

    if threads < min_threads:
        return False, f"Threads must be at least {min_threads}"

    if threads > max_threads:
        return False, f"Threads must be at most {max_threads}"

    return True, ""


def validate_output_folder(folder_path: str) -> Tuple[bool, str]:
    """
    Validate if the output folder path is valid and writable.
    
    This function checks:
    - Path contains no invalid characters
    - Path length is within system limits
    - Directory exists or can be created
    - Directory is writable
    
    Cross-platform: Works on Windows, macOS, and Linux.
    
    Args:
        folder_path: Folder path to validate.
        
    Returns:
        Tuple of (is_valid, error_message).
        If valid, error_message will be an empty string.
    """
    if not folder_path or not isinstance(folder_path, str):
        return False, "Folder path must be a non-empty string"

    folder_path = folder_path.strip()

    # Convert to Path object for cross-platform handling
    path = Path(folder_path)

    # Check for invalid characters (excluding Windows drive letter colon)
    # Allow : only in Windows drive letters (e.g., C:)
    check_path = str(path)
    if platform.system() == 'Windows' and len(check_path) >= 2 and check_path[1] == ':':
        check_path = check_path[2:]

    # Invalid characters for file systems
    invalid_chars = '<>"|?*'

    for char in invalid_chars:
        if char in check_path:
            return False, f"Folder path contains invalid character: '{char}'"

    # Check path length (Windows has 260 character limit by default)
    max_path_length = 260 if platform.system() == 'Windows' else 4096
    if len(str(path)) > max_path_length - 50:  # Leave room for filenames
        return False, f"Folder path is too long (max {max_path_length - 50} characters)"

    # Check if parent directory exists or is root
    try:
        parent = path.parent if path.parent != path else Path('.')
        if parent != Path('.') and not parent.exists():
            return False, f"Parent directory does not exist: {parent}"
    except (OSError, RuntimeError):
        pass  # Continue to writability test

    # Check if path is writable (try to create if doesn't exist)
    try:
        if not path.exists():
            # Try to create directory
            path.mkdir(parents=True, exist_ok=True)
            # Clean up test directory
            path.rmdir()
        else:
            # Check if directory is writable
            test_file = path / '.dml_write_test'
            try:
                test_file.write_text('test')
                test_file.unlink()
            except (OSError, PermissionError):
                return False, "Folder is not writable"
    except PermissionError:
        return False, "Permission denied: Cannot create or write to folder"
    except OSError as e:
        return False, f"OS error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

    return True, ""


def validate_video_id(video_id: str) -> Tuple[bool, str]:
    """
    Validate a YouTube video ID.
    
    YouTube video IDs are exactly 11 characters consisting of
    alphanumeric characters, hyphens, and underscores.
    
    Args:
        video_id: The video ID to validate.
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    if not video_id or not isinstance(video_id, str):
        return False, "Video ID must be a non-empty string"

    video_id = video_id.strip()

    if len(video_id) != 11:
        return False, f"Video ID must be exactly 11 characters, got {len(video_id)}"

    # YouTube video ID pattern: alphanumeric, hyphen, underscore
    pattern = r'^[\w-]{11}$'
    if not re.match(pattern, video_id):
        return False, "Video ID contains invalid characters"

    return True, ""


def validate_download_speed(speed: Optional[float]) -> Tuple[bool, str]:
    """
    Validate download speed limit.
    
    Args:
        speed: Speed limit in bytes/second. None means no limit.
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    if speed is None:
        return True, ""

    if not isinstance(speed, (int, float)):
        return False, "Speed must be a number"

    if speed <= 0:
        return False, "Speed must be greater than 0"

    # Minimum 1 KB/s
    if speed < 1024:
        return False, "Speed must be at least 1 KB/s (1024 bytes/s)"

    return True, ""


def validate_format_extension(ext: str, format_type: str = 'video') -> Tuple[bool, str]:
    """
    Validate a file extension for the given format type.
    
    Args:
        ext: File extension (with or without leading dot).
        format_type: Either 'video' or 'audio'.
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    from dml_stream.core.constants import AUDIO_FORMATS, VIDEO_FORMATS

    if not ext or not isinstance(ext, str):
        return False, "Extension must be a non-empty string"

    ext = ext.lower().lstrip('.')

    if format_type == 'video':
        valid_formats = VIDEO_FORMATS
    elif format_type == 'audio':
        valid_formats = AUDIO_FORMATS
    else:
        return False, f"Invalid format type: {format_type}. Must be 'video' or 'audio'"

    if ext not in valid_formats:
        return False, f"Invalid {format_type} format: {ext}. Valid formats: {', '.join(valid_formats)}"

    return True, ""


def get_platform_info() -> dict:
    """
    Get current platform information.
    
    Returns:
        Dictionary with platform details.
    """
    system = platform.system()
    release = platform.release()
    version = platform.version()
    machine = platform.machine()

    return {
        'system': system,  # 'Windows', 'Darwin' (macOS), 'Linux'
        'release': release,
        'version': version,
        'machine': machine,  # 'x86_64', 'arm64', 'AMD64', etc.
        'python_version': platform.python_version(),
        'is_windows': system == 'Windows',
        'is_macos': system == 'Darwin',
        'is_linux': system == 'Linux',
        'is_arm': machine in ('arm64', 'aarch64', 'ARM64'),
    }
