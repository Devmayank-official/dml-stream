"""
CLI module for DML Stream v2.5.

This module provides the command-line interface using Click
and Rich for beautiful terminal output.

v2.5 Changes:
- Modular command structure with dedicated command groups
- Backward compatible with v2.0 commands
"""

# Import main CLI entry point
from dml_stream.cli.app import cli

# Import command groups for export (used by main.py)
from dml_stream.cli.commands import (
    info,
    download,
    file_ops,
    storage,
    config,
    dev,
    system,
)

# Import standalone commands for backward compatibility
from dml_stream.cli.commands.download import (
    download_video_alias,
    download_audio_alias,
    download_playlist_alias,
)

# Import history and service (standalone commands)
from dml_stream.cli.commands.history import history
from dml_stream.cli.commands.service import service

__all__ = [
    # Main CLI
    "cli",
    # Command groups
    "info",
    "download",
    "file_ops",
    "storage",
    "config",
    "dev",
    "system",
    # Standalone commands
    "history",
    "service",
    # Backward compatibility aliases
    "download_video_alias",
    "download_audio_alias",
    "download_playlist_alias",
]
