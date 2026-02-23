"""
Utilities module for DML Stream.

This module contains utility functions and helpers used throughout
the application for common operations.

Fully cross-platform compatible: Windows, macOS, Linux
"""

from dml_stream.utilities.file_utils import (
    cleanup_temp_files,
    ensure_dir,
    format_duration,
    format_file_size,
    get_available_disk_space,
    safe_filename,
)
from dml_stream.utilities.logging_utils import (
    get_logger,
    log_function_call,
    setup_logging,
)
from dml_stream.utilities.platform_utils import (
    ensure_config_dir,
    ensure_data_dir,
    expand_user,
    expand_vars,
    find_ffmpeg,
    find_python,
    get_cache_dir,
    get_config_dir,
    get_data_dir,
    get_default_shell,
    get_env,
    get_platform,
    get_system_info,
    is_arm,
    is_executable,
    is_linux,
    is_macos,
    is_windows,
    make_executable,
    normalize_path,
    open_file,
    run_command,
    safe_path_join,
    set_env,
)

__all__ = [
    # File utilities
    "safe_filename",
    "ensure_dir",
    "format_file_size",
    "format_duration",
    "get_available_disk_space",
    "cleanup_temp_files",
    # Logging utilities
    "setup_logging",
    "get_logger",
    "log_function_call",
    # Platform utilities
    "get_platform",
    "is_windows",
    "is_macos",
    "is_linux",
    "is_arm",
    "get_config_dir",
    "get_data_dir",
    "get_cache_dir",
    "ensure_config_dir",
    "ensure_data_dir",
    "find_ffmpeg",
    "find_python",
    "make_executable",
    "is_executable",
    "get_env",
    "set_env",
    "run_command",
    "open_file",
    "normalize_path",
    "expand_user",
    "expand_vars",
    "safe_path_join",
    "get_system_info",
    "get_default_shell",
]
