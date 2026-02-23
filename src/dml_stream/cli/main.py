"""
Main CLI entry point for DML Stream.

This module defines the main Click command group and orchestrates
all subcommands.
"""

import sys
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

from dml_stream import __version__
from dml_stream.config.settings import Config
from dml_stream.utilities.logging_utils import setup_logging

console = Console()


@click.group()
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
    DML Stream - Enterprise-Level Terminal-Based Video Download Solution

    A powerful tool for downloading YouTube videos, audio, and playlists with
    advanced features including scheduled downloads, batch processing, and
    real-time process monitoring.

    Developed by DML Labs | Lead Engineer: @devmayank-official

    Examples:

        # Download a video
        dml-stream download --url https://youtube.com/watch?v=...

        # Download audio only
        dml-stream audio --url https://youtube.com/watch?v=...

        # Download a playlist
        dml-stream playlist --url https://youtube.com/playlist?list=...

        # Run in daemon mode for scheduled downloads
        dml-stream service --daemon

        # Interactive mode
        dml-stream interactive
    """
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
            "[bold blue]YouTube Downloader[/bold blue] - Interactive Mode\n\n"
            "[dim]Starting interactive interface...[/dim]",
            border_style="blue"
        )
    )
    
    app = InteractiveApp(config=ctx.obj['config'])
    app.run()


@cli.command()
@click.pass_context
def version(ctx: click.Context) -> None:
    """Show version information."""
    from dml_stream import __version__
    
    rprint(f"[bold blue]YouTube Downloader[/bold blue] v{__version__}")
    rprint(f"[dim]Python {sys.version}[/dim]")


# Import and register subcommands
from dml_stream.cli.commands import (
    download_video,
    download_audio,
    download_playlist,
    service,
    history,
    config_command,
)

cli.add_command(download_video, "download")
cli.add_command(download_audio, "audio")
cli.add_command(download_playlist, "playlist")
cli.add_command(service, "service")
cli.add_command(history, "history")
cli.add_command(config_command, "config")
cli.add_command(interactive, "interactive")


def main() -> None:
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
