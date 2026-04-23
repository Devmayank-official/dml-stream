"""
Main entry point for YouTube Downloader application.

This module provides the CLI entry point and orchestrates the application startup.

Usage:
    python -m dml_stream [OPTIONS]
    dml-stream [OPTIONS]

Examples:
    python -m dml_stream                    # Interactive mode
    python -m dml_stream --daemon           # Daemon mode
    python -m dml_stream download --url URL # Download single video
"""

import sys
from pathlib import Path

# Add the parent directory to the path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Suppress import warning
import warnings
warnings.filterwarnings("ignore", message=".*found in sys.modules.*")

from dml_stream.cli.app import main


if __name__ == "__main__":
    main()
