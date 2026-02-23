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

from dml_stream.cli.main import cli


def main() -> None:
    """
    Main entry point for the YouTube Downloader application.
    
    This function initializes the application and starts the CLI.
    """
    try:
        cli()
    except KeyboardInterrupt:
        print("\n\n🛑 Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
