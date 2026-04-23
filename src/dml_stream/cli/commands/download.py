"""
Download commands for DML Stream.

This module provides all download-related commands:
- download video: Download single video
- download audio: Download audio only
- download playlist: Download playlist

Backward Compatibility:
- Old 'download' command works as alias for 'download video'
- Old 'audio' command works as alias for 'download audio'
- Old 'playlist' command works as alias for 'download playlist'
"""

import logging
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn, TransferSpeedColumn
from rich.table import Table

from dml_stream.config.settings import Config
from dml_stream.managers.history_manager import HistoryManager
from dml_stream.models.entities import DownloadProgress
from dml_stream.services.download_service import DownloadService
from dml_stream.services.playlist_service import PlaylistService

logger = logging.getLogger(__name__)
console = Console()


@click.group("download")
@click.pass_context
def download(ctx: click.Context) -> None:
    """
    Download videos, audio, and playlists from YouTube.

    Examples:

        dml-stream download video <url>

        dml-stream download audio <url>

        dml-stream download playlist <url>
    """
    ctx.ensure_object(dict)
    ctx.obj['config'] = ctx.obj.get('config', Config())


@download.command("video")
@click.option(
    "--url", "-u",
    required=True,
    help="YouTube video URL"
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Output folder path"
)
@click.option(
    "--format", "-f",
    "output_format",
    type=click.Choice(['mp4', 'mkv', 'avi', 'mov', 'webm']),
    help="Output video format"
)
@click.option(
    "--quality", "-q",
    type=click.Choice(['1080p', '720p', '480p', '360p']),
    help="Video quality"
)
@click.option(
    "--fast",
    is_flag=True,
    help="Use fast multi-threaded download"
)
@click.option(
    "--threads", "-t",
    type=int,
    default=4,
    help="Number of download threads (for fast mode)"
)
@click.option(
    "--speed-limit",
    type=float,
    help="Maximum download speed in bytes/second"
)
@click.pass_context
def download_video_cmd(
    ctx: click.Context,
    url: str,
    output: str,
    output_format: str,
    quality: str,
    fast: bool,
    threads: int,
    speed_limit: float
) -> None:
    """
    Download a YouTube video.

    Downloads a single YouTube video with optional quality and format settings.

    Examples:

        dml-stream download video --url https://youtube.com/watch?v=...

        dml-stream download video -u URL -f mp4 -q 1080p --fast
    """
    config = ctx.obj.get('config', Config())

    console.print(Panel.fit(f"[bold blue]Downloading Video[/bold blue]\n\n[dim]{url}[/dim]"))

    try:
        service = DownloadService(
            output_folder=output or config.default_output_folder,
            threads=threads if fast else 1,
            max_speed=speed_limit,
        )

        # Get video info
        console.print("[cyan]Fetching video info...[/cyan]")
        yt = service.get_video_info(url)
        console.print(f"[green]✓[/green] {yt.title}")

        # Download
        method = "fast" if fast else "normal"
        console.print(f"[cyan]Starting download (method: {method})...[/cyan]")

        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "•",
            TransferSpeedColumn(),
            "•",
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Downloading...", total=100)

            def update_progress(p: DownloadProgress):
                progress.update(task, completed=p.percentage)

            service.progress_callback = update_progress

            file_path = service.download_video(
                yt,
                output_folder=output,
                output_format=output_format,
                method=method
            )

        # Record in history
        history_manager = HistoryManager(db_path=config.database_path)
        history_manager.record_download(
            title=yt.title,
            url=url,
            file_path=file_path,
            download_type="video",
            status="success"
        )

        console.print("[bold green]✓ Download completed![/bold green]")
        console.print(f"[dim]Saved to: {file_path}[/dim]")
        logger.info(f"Downloaded video: {yt.title} -> {file_path}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Download failed: {str(e)}")
        raise SystemExit(1)


@download.command("audio")
@click.option(
    "--url", "-u",
    required=True,
    help="YouTube video URL"
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Output folder path"
)
@click.option(
    "--format", "-f",
    "output_format",
    type=click.Choice(['mp3', 'm4a', 'flac', 'wav', 'aac']),
    default='mp3',
    help="Output audio format"
)
@click.option(
    "--fast",
    is_flag=True,
    help="Use fast multi-threaded download"
)
@click.option(
    "--threads", "-t",
    type=int,
    default=4,
    help="Number of download threads"
)
@click.pass_context
def download_audio_cmd(
    ctx: click.Context,
    url: str,
    output: str,
    output_format: str,
    fast: bool,
    threads: int
) -> None:
    """
    Download audio from a YouTube video.

    Extracts and downloads audio from a YouTube video in the specified format.

    Examples:

        dml-stream download audio --url https://youtube.com/watch?v=...

        dml-stream download audio -u URL -f flac --fast
    """
    config = ctx.obj.get('config', Config())

    console.print(Panel.fit(f"[bold green]Downloading Audio[/bold green]\n\n[dim]{url}[/dim]"))

    try:
        service = DownloadService(
            output_folder=output or config.default_output_folder,
            threads=threads if fast else 1,
        )

        # Get video info
        console.print("[cyan]Fetching video info...[/cyan]")
        yt = service.get_video_info(url)
        console.print(f"[green]✓[/green] {yt.title}")

        # Download audio
        method = "fast" if fast else "normal"
        console.print(f"[cyan]Extracting audio (format: {output_format})...[/cyan]")

        file_path = service.download_audio(
            yt,
            output_folder=output,
            output_format=output_format,
            method=method
        )

        # Record in history
        history_manager = HistoryManager(db_path=config.database_path)
        history_manager.record_download(
            title=yt.title,
            url=url,
            file_path=file_path,
            download_type="audio",
            status="success"
        )

        console.print("[bold green]✓ Audio download completed![/bold green]")
        console.print(f"[dim]Saved to: {file_path}[/dim]")
        logger.info(f"Downloaded audio: {yt.title} -> {file_path}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Audio download failed: {str(e)}")
        raise SystemExit(1)


@download.command("playlist")
@click.option(
    "--url", "-u",
    required=True,
    help="YouTube playlist URL"
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Output folder path"
)
@click.option(
    "--audio-only",
    is_flag=True,
    help="Download audio only from playlist videos"
)
@click.option(
    "--format", "-f",
    "output_format",
    help="Output format"
)
@click.option(
    "--skip-existing",
    is_flag=True,
    default=True,
    help="Skip videos that already exist"
)
@click.option(
    "--max-videos",
    type=int,
    help="Maximum number of videos to download"
)
@click.pass_context
def download_playlist_cmd(
    ctx: click.Context,
    url: str,
    output: str,
    audio_only: bool,
    output_format: str,
    skip_existing: bool,
    max_videos: Optional[int]
) -> None:
    """
    Download all videos from a YouTube playlist.

    Downloads an entire playlist with progress tracking for each video.

    Examples:

        dml-stream download playlist --url https://youtube.com/playlist?list=...

        dml-stream download playlist -u URL --audio-only -f mp3
    """
    config = ctx.obj.get('config', Config())

    console.print(Panel.fit(f"[bold magenta]Downloading Playlist[/bold magenta]\n\n[dim]{url}[/dim]"))

    try:
        service = PlaylistService(
            output_folder=output or config.default_output_folder,
            threads=config.default_threads,
        )

        # Get playlist info
        console.print("[cyan]Fetching playlist info...[/cyan]")
        playlist_info = service.get_playlist_info(url)
        console.print(f"[green]✓[/green] {playlist_info['title']}")
        console.print(f"[dim]{playlist_info['video_count']} videos[/dim]")

        # Download playlist
        download_type = "audio" if audio_only else "video"
        console.print(f"[cyan]Starting playlist download ({download_type})...[/cyan]")

        results = service.download_playlist(
            url=url,
            output_folder=output,
            download_type=download_type,
            output_format=output_format,
            skip_existing=skip_existing,
            max_videos=max_videos
        )

        # Show summary
        summary = Table(title="Download Summary")
        summary.add_column("Metric", style="cyan")
        summary.add_column("Value", style="green")

        summary.add_row("Total Videos", str(results['total_videos']))
        summary.add_row("Successful", str(results['successful']))
        summary.add_row("Failed", str(results['failed']))
        summary.add_row("Skipped", str(results['skipped']))

        console.print(summary)

        if results['errors']:
            console.print("\n[yellow]Errors:[/yellow]")
            for error in results['errors'][:5]:
                console.print(f"  • {error['url']}: {error['error']}")

        # Record in history
        history_manager = HistoryManager(db_path=config.database_path)
        history_manager.record_download(
            title=playlist_info['title'],
            url=url,
            file_path=output or config.default_output_folder,
            download_type="playlist",
            status="success" if results['failed'] == 0 else "partial"
        )

        logger.info(f"Downloaded playlist: {playlist_info['title']} ({results['successful']}/{results['total_videos']})")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Playlist download failed: {str(e)}")
        raise SystemExit(1)


# =============================================================================
# BACKWARD COMPATIBILITY ALIASES (v2.0 commands)
# =============================================================================

@click.command("download", hidden=True)
@click.option("--url", "-u", required=True, help="YouTube video URL")
@click.option("--output", "-o", type=click.Path(), help="Output folder path")
@click.option("--format", "-f", "output_format", type=click.Choice(['mp4', 'mkv', 'avi', 'mov', 'webm']), help="Output video format")
@click.option("--quality", "-q", type=click.Choice(['1080p', '720p', '480p', '360p']), help="Video quality")
@click.option("--fast", is_flag=True, help="Use fast multi-threaded download")
@click.option("--threads", "-t", type=int, default=4, help="Number of download threads")
@click.option("--speed-limit", type=float, help="Maximum download speed in bytes/second")
@click.pass_context
def download_video_alias(ctx: click.Context, **kwargs):
    """Legacy alias for 'download video' (v2.0 compatibility)."""
    ctx.invoke(download_video_cmd, **kwargs)


@click.command("audio", hidden=True)
@click.option("--url", "-u", required=True, help="YouTube video URL")
@click.option("--output", "-o", type=click.Path(), help="Output folder path")
@click.option("--format", "-f", "output_format", type=click.Choice(['mp3', 'm4a', 'flac', 'wav', 'aac']), default='mp3', help="Output audio format")
@click.option("--fast", is_flag=True, help="Use fast multi-threaded download")
@click.option("--threads", "-t", type=int, default=4, help="Number of download threads")
@click.pass_context
def download_audio_alias(ctx: click.Context, **kwargs):
    """Legacy alias for 'download audio' (v2.0 compatibility)."""
    ctx.invoke(download_audio_cmd, **kwargs)


@click.command("playlist", hidden=True)
@click.option("--url", "-u", required=True, help="YouTube playlist URL")
@click.option("--output", "-o", type=click.Path(), help="Output folder path")
@click.option("--audio-only", is_flag=True, help="Download audio only")
@click.option("--format", "-f", "output_format", help="Output format")
@click.option("--skip-existing", is_flag=True, default=True, help="Skip existing videos")
@click.pass_context
def download_playlist_alias(ctx: click.Context, **kwargs):
    """Legacy alias for 'download playlist' (v2.0 compatibility)."""
    ctx.invoke(download_playlist_cmd, **kwargs)
