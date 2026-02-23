"""
File utilities for YouTube Downloader.

This module provides file operation helpers including:
- Filename sanitization
- Directory management
- File size formatting
- Disk space checking
"""

import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional

from dml_stream.core.constants import INVALID_FILENAME_CHARS, MAX_FILENAME_LENGTH


def safe_filename(filename: str, max_length: int = MAX_FILENAME_LENGTH) -> str:
    """
    Create a safe filename by removing invalid characters.
    
    This function:
    - Removes or replaces invalid characters for cross-platform compatibility
    - Truncates to maximum length while preserving extension
    - Handles Unicode characters safely
    - Preserves spaces, dots, underscores, and hyphens
    
    Args:
        filename: Original filename to sanitize.
        max_length: Maximum filename length (excluding extension).
        
    Returns:
        Sanitized filename safe for all platforms.
    """
    if not filename:
        return "unnamed"
    
    # Separate name and extension
    name, ext = os.path.splitext(filename)
    
    # Remove invalid characters
    # Keep: alphanumeric, spaces, dots, underscores, hyphens
    safe_name = "".join(
        c for c in name 
        if c.isalnum() or c in " ._-"
    )
    
    # Replace multiple spaces/dots with single
    safe_name = re.sub(r'[ .]+', '.', safe_name.strip())
    
    # Remove leading/trailing dots and spaces
    safe_name = safe_name.strip(" .")
    
    # Truncate if too long (preserve extension)
    if len(safe_name) > max_length:
        # Try to preserve word boundary
        truncated = safe_name[:max_length]
        last_space = truncated.rfind(' ')
        last_dot = truncated.rfind('.')
        
        if last_space > max_length // 2:
            safe_name = truncated[:last_space]
        elif last_dot > max_length // 2:
            safe_name = truncated[:last_dot]
        else:
            safe_name = truncated
    
    # Ensure we have at least some name
    if not safe_name:
        safe_name = "file"
    
    # Clean extension
    ext = ext.lower().strip('.')
    
    if ext:
        return f"{safe_name}.{ext}"
    return safe_name


def ensure_dir(path: str) -> str:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to ensure.
        
    Returns:
        The ensured directory path.
        
    Raises:
        OSError: If directory cannot be created.
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return path
    except OSError as e:
        raise OSError(f"Failed to create directory '{path}': {str(e)}")


def format_file_size(size_bytes: int) -> str:
    """
    Convert bytes to human-readable file size.
    
    Args:
        size_bytes: Size in bytes.
        
    Returns:
        Formatted string (e.g., "150.25 MB").
    """
    if size_bytes < 0:
        return "Invalid size"
    
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    return f"{size:.2f} {units[unit_index]}"


def format_duration(seconds: int) -> str:
    """
    Convert seconds to human-readable duration.
    
    Args:
        seconds: Duration in seconds.
        
    Returns:
        Formatted string (e.g., "1h 30m 45s").
    """
    if seconds < 0:
        return "Invalid duration"
    
    if seconds < 60:
        return f"{seconds}s"
    
    if seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s" if secs else f"{minutes}m"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs:
        parts.append(f"{secs}s")
    
    return " ".join(parts)


def get_available_disk_space(path: str = ".") -> int:
    """
    Get available disk space in bytes.
    
    Args:
        path: Path to check (uses current directory if not specified).
        
    Returns:
        Available space in bytes, or -1 if unable to determine.
    """
    try:
        if os.name == 'nt':  # Windows
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(path),
                None,
                None,
                ctypes.byref(free_bytes)
            )
            return free_bytes.value
        else:  # Unix-like
            stat = shutil.disk_usage(path)
            return stat.free
    except Exception:
        return -1


def get_total_disk_space(path: str = ".") -> int:
    """
    Get total disk space in bytes.
    
    Args:
        path: Path to check.
        
    Returns:
        Total space in bytes, or -1 if unable to determine.
    """
    try:
        if os.name == 'nt':
            import ctypes
            total_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(path),
                None,
                ctypes.byref(total_bytes),
                None
            )
            return total_bytes.value
        else:
            stat = shutil.disk_usage(path)
            return stat.total
    except Exception:
        return -1


def check_disk_space(
    required_bytes: int,
    path: str = ".",
    safety_margin: float = 1.1
) -> bool:
    """
    Check if there's enough disk space for a download.
    
    Args:
        required_bytes: Required space in bytes.
        path: Path to check.
        safety_margin: Safety margin multiplier (default 10%).
        
    Returns:
        True if enough space is available.
    """
    available = get_available_disk_space(path)
    if available < 0:
        return True  # Can't determine, assume OK
    
    required_with_margin = int(required_bytes * safety_margin)
    return available >= required_with_margin


def cleanup_temp_files(
    temp_dir: Optional[str] = None,
    pattern: str = "*.tmp"
) -> int:
    """
    Clean up temporary files.
    
    Args:
        temp_dir: Directory to clean (uses system temp if not specified).
        pattern: Glob pattern for files to delete.
        
    Returns:
        Number of files deleted.
    """
    if temp_dir is None:
        temp_dir = tempfile.gettempdir()
    
    count = 0
    try:
        temp_path = Path(temp_dir)
        for file in temp_path.glob(pattern):
            try:
                file.unlink()
                count += 1
            except (OSError, PermissionError):
                pass
    except Exception:
        pass
    
    return count


def get_file_info(path: str) -> dict:
    """
    Get detailed file information.
    
    Args:
        path: Path to file.
        
    Returns:
        Dictionary with file information.
    """
    try:
        stat = os.stat(path)
        return {
            'path': path,
            'exists': True,
            'size': stat.st_size,
            'size_formatted': format_file_size(stat.st_size),
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'accessed': stat.st_atime,
            'is_file': os.path.isfile(path),
            'is_dir': os.path.isdir(path),
        }
    except FileNotFoundError:
        return {
            'path': path,
            'exists': False,
        }
    except Exception as e:
        return {
            'path': path,
            'exists': False,
            'error': str(e),
        }


def delete_file(path: str, force: bool = False) -> bool:
    """
    Delete a file safely.
    
    Args:
        path: Path to file.
        force: Force deletion even if file is in use (Windows).
        
    Returns:
        True if deleted successfully.
    """
    if not os.path.exists(path):
        return False
    
    try:
        if force and os.name == 'nt':
            # Try to delete even if in use
            import ctypes
            ctypes.windll.kernel32.DeleteFileW(path)
        else:
            os.remove(path)
        return True
    except Exception:
        return False


def move_file(src: str, dst: str, overwrite: bool = True) -> bool:
    """
    Move a file from source to destination.
    
    Args:
        src: Source path.
        dst: Destination path.
        overwrite: Whether to overwrite existing destination.
        
    Returns:
        True if moved successfully.
    """
    try:
        if os.path.exists(dst) and not overwrite:
            return False
        
        dst_dir = os.path.dirname(dst)
        if dst_dir:
            ensure_dir(dst_dir)
        
        shutil.move(src, dst)
        return True
    except Exception:
        return False


def copy_file(src: str, dst: str, overwrite: bool = True) -> bool:
    """
    Copy a file from source to destination.
    
    Args:
        src: Source path.
        dst: Destination path.
        overwrite: Whether to overwrite existing destination.
        
    Returns:
        True if copied successfully.
    """
    try:
        if os.path.exists(dst) and not overwrite:
            return False
        
        dst_dir = os.path.dirname(dst)
        if dst_dir:
            ensure_dir(dst_dir)
        
        shutil.copy2(src, dst)
        return True
    except Exception:
        return False


def find_files(
    directory: str,
    pattern: str = "*",
    recursive: bool = False
) -> List[str]:
    """
    Find files matching a pattern.
    
    Args:
        directory: Directory to search.
        pattern: Glob pattern.
        recursive: Whether to search recursively.
        
    Returns:
        List of matching file paths.
    """
    try:
        path = Path(directory)
        if recursive:
            return [str(p) for p in path.rglob(pattern)]
        return [str(p) for p in path.glob(pattern)]
    except Exception:
        return []
