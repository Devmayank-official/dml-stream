"""
CLI command groups for DML Stream v2.5.

This package contains all CLI command groups organized by category:
- info: Video information commands
- download: Download commands (video, audio, playlist)
- file_ops: File operation commands
- storage: Storage management commands
- config: Configuration commands
- dev: Developer commands
- system: System commands

Backward Compatibility:
- download_video_alias: v2.0 'download' command
- download_audio_alias: v2.0 'audio' command
- download_playlist_alias: v2.0 'playlist' command
"""

from dml_stream.cli.commands.info import info
from dml_stream.cli.commands.download import (
    download,
    download_video_alias,
    download_audio_alias,
    download_playlist_alias,
)
from dml_stream.cli.commands.file_ops import file_ops
from dml_stream.cli.commands.storage import storage
from dml_stream.cli.commands.config import config
from dml_stream.cli.commands.dev import dev
from dml_stream.cli.commands.system import system

__all__ = [
    'info',
    'download',
    'file_ops',
    'storage',
    'config',
    'dev',
    'system',
    # Backward compatibility aliases
    'download_video_alias',
    'download_audio_alias',
    'download_playlist_alias',
]
