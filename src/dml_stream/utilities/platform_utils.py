"""
Cross-platform utilities for DML Stream.

This module provides platform-aware utilities for:
- System paths and directories
- Executable detection
- File permissions
- Environment variables
- Shell commands

Fully cross-platform compatible: Windows, macOS, Linux
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_platform() -> str:
    """
    Get current platform name.
    
    Returns:
        'windows', 'macos', or 'linux'
    """
    system = platform.system()
    if system == 'Windows':
        return 'windows'
    elif system == 'Darwin':
        return 'macos'
    else:
        return 'linux'


def is_windows() -> bool:
    """Check if running on Windows."""
    return platform.system() == 'Windows'


def is_macos() -> bool:
    """Check if running on macOS."""
    return platform.system() == 'Darwin'


def is_linux() -> bool:
    """Check if running on Linux."""
    return platform.system() == 'Linux'


def is_arm() -> bool:
    """Check if running on ARM architecture (M1/M2, ARM64)."""
    machine = platform.machine().lower()
    return machine in ('arm64', 'aarch64', 'armv7l')


# =============================================================================
# PATH UTILITIES
# =============================================================================

def get_config_dir() -> Path:
    """
    Get platform-specific configuration directory.
    
    Follows platform conventions:
    - Windows: %APPDATA%/DML Labs/DML Stream
    - macOS: ~/Library/Application Support/DML Stream
    - Linux: ~/.config/dml-stream (XDG compliant)
    
    Returns:
        Path to configuration directory.
    """
    system = platform.system()

    if system == 'Windows':
        # Use APPDATA for roaming config
        appdata = os.environ.get('APPDATA', '')
        if appdata:
            return Path(appdata) / 'DML Labs' / 'DML Stream'
        else:
            return Path.home() / 'AppData' / 'Roaming' / 'DML Labs' / 'DML Stream'

    elif system == 'Darwin':  # macOS
        return Path.home() / 'Library' / 'Application Support' / 'DML Stream'

    else:  # Linux
        # Follow XDG Base Directory specification
        xdg_config = os.environ.get('XDG_CONFIG_HOME', '')
        if xdg_config:
            return Path(xdg_config) / 'dml-stream'
        else:
            return Path.home() / '.config' / 'dml-stream'


def get_data_dir() -> Path:
    """
    Get platform-specific data directory.
    
    Follows platform conventions:
    - Windows: %LOCALAPPDATA%/DML Labs/DML Stream
    - macOS: ~/Library/Application Support/DML Stream
    - Linux: ~/.local/share/dml-stream (XDG compliant)
    
    Returns:
        Path to data directory.
    """
    system = platform.system()

    if system == 'Windows':
        local_appdata = os.environ.get('LOCALAPPDATA', '')
        if local_appdata:
            return Path(local_appdata) / 'DML Labs' / 'DML Stream'
        else:
            return Path.home() / 'AppData' / 'Local' / 'DML Labs' / 'DML Stream'

    elif system == 'Darwin':  # macOS
        return Path.home() / 'Library' / 'Application Support' / 'DML Stream'

    else:  # Linux
        # Follow XDG Base Directory specification
        xdg_data = os.environ.get('XDG_DATA_HOME', '')
        if xdg_data:
            return Path(xdg_data) / 'dml-stream'
        else:
            return Path.home() / '.local' / 'share' / 'dml-stream'


def get_cache_dir() -> Path:
    """
    Get platform-specific cache directory.
    
    Follows platform conventions:
    - Windows: %LOCALAPPDATA%/DML Labs/DML Stream/Cache
    - macOS: ~/Library/Caches/DML Stream
    - Linux: ~/.cache/dml-stream (XDG compliant)
    
    Returns:
        Path to cache directory.
    """
    system = platform.system()

    if system == 'Windows':
        local_appdata = os.environ.get('LOCALAPPDATA', '')
        if local_appdata:
            return Path(local_appdata) / 'DML Labs' / 'DML Stream' / 'Cache'
        else:
            return Path.home() / 'AppData' / 'Local' / 'DML Labs' / 'DML Stream' / 'Cache'

    elif system == 'Darwin':  # macOS
        return Path.home() / 'Library' / 'Caches' / 'DML Stream'

    else:  # Linux
        # Follow XDG Base Directory specification
        xdg_cache = os.environ.get('XDG_CACHE_HOME', '')
        if xdg_cache:
            return Path(xdg_cache) / 'dml-stream'
        else:
            return Path.home() / '.cache' / 'dml-stream'


def ensure_config_dir() -> Path:
    """
    Ensure configuration directory exists.
    
    Returns:
        Path to configuration directory (created if necessary).
    """
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def ensure_data_dir() -> Path:
    """
    Ensure data directory exists.
    
    Returns:
        Path to data directory (created if necessary).
    """
    data_dir = get_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


# =============================================================================
# EXECUTABLE DETECTION
# =============================================================================

def find_ffmpeg() -> Optional[str]:
    """
    Find FFmpeg executable on any platform.
    
    Searches:
    1. System PATH
    2. Platform-specific installation locations
    
    Returns:
        Path to ffmpeg executable or None if not found.
    """
    # Try system PATH first
    ffmpeg = shutil.which('ffmpeg')
    if ffmpeg:
        return ffmpeg

    # Platform-specific locations
    system = platform.system()
    machine = platform.machine().lower()

    if system == 'Windows':
        paths = [
            Path('C:/Program Files/ffmpeg/bin/ffmpeg.exe'),
            Path('C:/Program Files (x86)/ffmpeg/bin/ffmpeg.exe'),
            Path.home() / 'scoop/apps/ffmpeg/current/ffmpeg.exe',
            Path.home() / 'AppData/Local/Microsoft/WinGet/Packages/ffmpeg/GnuPG/bin/ffmpeg.exe',
        ]
    elif system == 'Darwin':  # macOS
        if machine in ('arm64', 'aarch64'):  # Apple Silicon
            paths = [
                Path('/opt/homebrew/bin/ffmpeg'),
                Path('/usr/local/bin/ffmpeg'),
            ]
        else:  # Intel
            paths = [
                Path('/usr/local/bin/ffmpeg'),
                Path('/opt/homebrew/bin/ffmpeg'),
            ]
    else:  # Linux
        paths = [
            Path('/usr/bin/ffmpeg'),
            Path('/usr/local/bin/ffmpeg'),
            Path('/snap/bin/ffmpeg'),
            Path('/usr/local/sbin/ffmpeg'),
        ]

    # Check each path
    for path in paths:
        if path.exists() and os.access(path, os.X_OK):
            return str(path)

    return None


def find_python() -> str:
    """
    Find Python executable.
    
    Returns:
        Path to Python executable.
    """
    # Use current Python executable
    return sys.executable


# =============================================================================
# FILE PERMISSIONS
# =============================================================================

def make_executable(path: Path) -> bool:
    """
    Make a file executable (Unix only, no-op on Windows).
    
    Args:
        path: Path to file.
        
    Returns:
        True if successful or not needed (Windows).
    """
    if platform.system() == 'Windows':
        # Windows doesn't have execute permission
        return True

    try:
        import stat
        current_mode = path.stat().st_mode
        path.chmod(current_mode | stat.S_IEXEC | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        return True
    except OSError:
        return False


def is_executable(path: Path) -> bool:
    """
    Check if a file is executable.
    
    Args:
        path: Path to file.
        
    Returns:
        True if executable.
    """
    if platform.system() == 'Windows':
        # On Windows, check if it's a known executable type
        return path.suffix.lower() in ('.exe', '.bat', '.cmd', '.com', '.ps1')
    else:
        # On Unix, check execute permission
        return os.access(path, os.X_OK)


# =============================================================================
# ENVIRONMENT VARIABLES
# =============================================================================

def get_env(var_name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get environment variable with platform awareness.
    
    Windows environment variables are case-insensitive,
    while Unix variables are case-sensitive.
    
    Args:
        var_name: Variable name.
        default: Default value if not found.
        
    Returns:
        Environment variable value or default.
    """
    if platform.system() == 'Windows':
        # Try uppercase and lowercase on Windows
        return os.environ.get(var_name.upper(), os.environ.get(var_name.lower(), default))
    else:
        return os.environ.get(var_name, default)


def set_env(var_name: str, value: str) -> None:
    """
    Set environment variable.
    
    Args:
        var_name: Variable name.
        value: Value to set.
    """
    os.environ[var_name] = value


# =============================================================================
# SHELL COMMANDS
# =============================================================================

def run_command(cmd: List[str], capture: bool = True, **kwargs) -> subprocess.CompletedProcess:
    """
    Run shell command with platform-specific handling.
    
    Args:
        cmd: Command and arguments as list.
        capture: Whether to capture output.
        **kwargs: Additional arguments for subprocess.run().
        
    Returns:
        CompletedProcess instance.
    """
    # Windows often needs shell=True for certain commands
    if platform.system() == 'Windows':
        # Convert to string for Windows if needed
        cmd_str = ' '.join(cmd) if isinstance(cmd, list) else cmd
        return subprocess.run(cmd_str, shell=True, capture_output=capture, **kwargs)
    else:
        # Unix doesn't need shell
        return subprocess.run(cmd, shell=False, capture_output=capture, **kwargs)


def open_file(path: Path) -> bool:
    """
    Open a file with the default application (platform-specific).
    
    Args:
        path: Path to file.
        
    Returns:
        True if successful.
    """
    try:
        system = platform.system()

        if system == 'Windows':
            os.startfile(str(path))
        elif system == 'Darwin':  # macOS
            subprocess.run(['open', str(path)], check=False)
        else:  # Linux
            subprocess.run(['xdg-open', str(path)], check=False)

        return True
    except Exception:
        return False


# =============================================================================
# PATH UTILITIES
# =============================================================================

def normalize_path(path: str) -> str:
    """
    Normalize a path for the current platform.
    
    Converts forward slashes to backslashes on Windows,
    and backslashes to forward slashes on Unix.
    
    Args:
        path: Path string to normalize.
        
    Returns:
        Normalized path string.
    """
    # Use pathlib for proper normalization
    return str(Path(path).resolve())


def expand_user(path: str) -> str:
    """
    Expand user home directory (~ or %USERPROFILE%).
    
    Args:
        path: Path string.
        
    Returns:
        Expanded path string.
    """
    return str(Path(path).expanduser())


def expand_vars(path: str) -> str:
    """
    Expand environment variables in path.
    
    Args:
        path: Path string.
        
    Returns:
        Expanded path string.
    """
    return os.path.expandvars(path)


def safe_path_join(*parts: str) -> str:
    """
    Safely join path components (cross-platform).
    
    Args:
        *parts: Path components.
        
    Returns:
        Joined path string.
    """
    return str(Path(*parts))


# =============================================================================
# SYSTEM INFORMATION
# =============================================================================

def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information.
    
    Returns:
        Dictionary with system details.
    """
    system = platform.system()
    release = platform.release()
    version = platform.version()
    machine = platform.machine()
    processor = platform.processor()

    return {
        'platform': get_platform(),
        'system': system,
        'release': release,
        'version': version,
        'machine': machine,
        'processor': processor,
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
        'is_windows': system == 'Windows',
        'is_macos': system == 'Darwin',
        'is_linux': system == 'Linux',
        'is_arm': machine.lower() in ('arm64', 'aarch64', 'armv7l'),
        'is_x86': machine.lower() in ('amd64', 'x86_64', 'i386', 'i686'),
    }


def get_default_shell() -> str:
    """
    Get the default shell for the current platform.
    
    Returns:
        Shell name.
    """
    if platform.system() == 'Windows':
        # Prefer PowerShell if available
        if shutil.which('powershell'):
            return 'powershell'
        return 'cmd'
    else:
        return os.environ.get('SHELL', '/bin/bash')
