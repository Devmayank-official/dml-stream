"""
Main CLI entry point for DML Stream v2.5.

This module defines the main Click command group and orchestrates
all subcommands including:
- info: Video information commands
- download: Download commands (video, audio, playlist)
- file-ops: File operation commands
- storage: Storage management commands
- config: Configuration commands
- dev: Developer commands
- system: System commands
- service: Service commands (daemon, scheduling)
- history: History management
- interactive: Interactive mode

Backward Compatibility:
- v2.0 commands (download, audio, playlist) work as aliases
"""

import sys
from typing import Optional

import click
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel

from dml_stream import __version__
from dml_stream.config.settings import Config
from dml_stream.utilities.logging_utils import setup_logging

console = Console()


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="DML Stream")
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Enable verbose output"
)
@click.option(
    "--config", "-c",
    type=click.Path(exists=True),
    help="Path to configuration file"
)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, config: Optional[str]) -> None:
    """
    DML Stream v2.5 - Enterprise-Level Terminal-Based Video Download Solution

    A powerful tool for downloading YouTube videos, audio, and playlists with
    advanced features including scheduled downloads, batch processing, storage
    management, and real-time process monitoring.

    \b
    Developed by DML Labs | Lead Engineer: @devmayank-official
    Version: {version}

    \b
    Quick Start:
      dml-stream download video --url <url>    Download a video
      dml-stream download audio --url <url>    Download audio only
      dml-stream info video <url>              Get video information
      dml-stream interactive                    Interactive mode

    \b
    Command Groups:
      info        Get information about videos, playlists, channels
      download    Download videos, audio, and playlists
      file-ops    File operations (convert, merge, extract, compress)
      storage     Storage management (status, analyze, clean-cache)
      config      Configuration management
      dev         Developer tools and debugging
      system      System diagnostics and maintenance
      service     Background services (daemon, scheduling, batch)
      history     View and manage download history

    Examples:

        # Download a video in 1080p
        dml-stream download video --url https://youtube.com/watch?v=... -q 1080p

        # Get video information before downloading
        dml-stream info video https://youtube.com/watch?v=...

        # List available formats
        dml-stream info formats https://youtube.com/watch?v=...

        # Download audio as MP3
        dml-stream download audio --url https://youtube.com/watch?v=... -f mp3

        # Check system health
        dml-stream system doctor

        # Clean cache and temp files
        dml-stream storage clean-cache

        # Run in daemon mode for scheduled downloads
        dml-stream service --daemon
    """.format(version=__version__)

    # Initialize context
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['config_path'] = config
    ctx.obj['config'] = Config.load_from_file(config) if config else Config()

    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(
        log_file=ctx.obj['config'].log_file_path,
        log_level=log_level,
        console_output=True,
        json_format=True
    )

    # Show help if no command provided
    if ctx.invoked_subcommand is None:
        console.print(
            Panel(
                "[bold blue]DML Stream v2.5[/bold blue]\n\n"
                "[dim]Enterprise-Level Terminal-Based Video Download Solution[/dim]\n\n"
                "Run [bold]dml-stream --help[/bold] for available commands.\n\n"
                "Quick start: [bold]dml-stream interactive[/bold]",
                border_style="blue"
            )
        )


@cli.command()
@click.pass_context
def interactive(ctx: click.Context) -> None:
    """
    Start interactive mode with a menu-driven interface.

    Provides an easy-to-use menu for all download operations
    with real-time progress tracking.
    """
    from dml_stream.cli.interactive import InteractiveApp

    console.print(
        Panel.fit(
            "[bold blue]DML Stream[/bold blue] - Interactive Mode\n\n"
            "[dim]Starting interactive interface...[/dim]",
            border_style="blue"
        )
    )

    app = InteractiveApp(config=ctx.obj['config'])
    app.run()


@cli.command()
def version() -> None:
    """Show version information."""
    rprint(f"[bold blue]DML Stream[/bold blue] v{__version__}")
    rprint(f"[dim]Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}[/dim]")


# =============================================================================
# IMPORT AND REGISTER COMMAND GROUPS
# =============================================================================

from dml_stream.cli.commands import (
    info,
    download,
    file_ops,
    storage,
    config,
    dev,
    system,
)

# Import standalone commands
from dml_stream.cli.commands import (
    download_video_alias,
    download_audio_alias,
    download_playlist_alias,
)
from dml_stream.cli.commands.history import history
from dml_stream.cli.commands.service import service

# Register command groups
cli.add_command(info, "info")
cli.add_command(download, "download")  # v2.5 download group (video, audio, playlist subcommands)
cli.add_command(file_ops, "file-ops")
cli.add_command(storage, "storage")
cli.add_command(config, "config")
cli.add_command(dev, "dev")
cli.add_command(system, "system")

# Register standalone commands
cli.add_command(history, "history")
cli.add_command(service, "service")
cli.add_command(service, "daemon")  # Alias for service --daemon
cli.add_command(service, "schedule")  # Alias for service --schedule
cli.add_command(interactive, "interactive")
cli.add_command(version, "version")

# Register backward compatibility aliases (hidden) - v2.0 commands
# These are aliases for the old flat structure
cli.add_command(download_video_alias, "download-legacy")  # Hidden, for v2.0 compatibility
cli.add_command(download_audio_alias, "audio")      # v2.0 'audio' command
cli.add_command(download_playlist_alias, "playlist")  # v2.0 'playlist' command


def main() -> None:
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)
    except SystemExit as e:
        # Preserve exit codes from commands
        raise
    except Exception as e:
        console.print(f"\n[bold red]Fatal Error:[/bold red] {str(e)}")
        if console.is_terminal:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
