"""
Service commands for DML Stream.

This module provides service and automation commands:
- daemon mode for scheduled downloads
- batch processing
- process monitoring

Preserved from v2.0 with enhancements for v2.5.
"""

import logging
import time
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from dml_stream.config.settings import Config

logger = logging.getLogger(__name__)
console = Console()


@click.command("service")
@click.option(
    "--daemon",
    is_flag=True,
    help="Run in daemon mode for scheduled downloads"
)
@click.option(
    "--schedule",
    is_flag=True,
    help="Schedule a new download"
)
@click.option(
    "--list-scheduled",
    is_flag=True,
    help="List all scheduled downloads"
)
@click.option(
    "--cancel-scheduled",
    type=str,
    help="Cancel a scheduled download by ID"
)
@click.option(
    "--batch",
    type=str,
    help="Create a new batch download with given name"
)
@click.option(
    "--list-batch",
    is_flag=True,
    help="List all batch downloads"
)
@click.option(
    "--view-processes",
    is_flag=True,
    help="View all tracked processes"
)
@click.pass_context
def service(
    ctx: click.Context,
    daemon: bool,
    schedule: bool,
    list_scheduled: bool,
    cancel_scheduled: str,
    batch: str,
    list_batch: bool,
    view_processes: bool
) -> None:
    """
    Service commands for automation and background operations.

    Provides daemon mode, scheduling, and batch management commands.

    Examples:

        dml-stream service --daemon

        dml-stream service --list-scheduled

        dml-stream service --batch "My Playlist Batch"
    """
    from dml_stream.managers.batch_manager import BatchManager
    from dml_stream.managers.process_manager import ProcessManager
    from dml_stream.managers.schedule_manager import ScheduleManager

    config = ctx.obj.get('config', Config())

    if daemon:
        from dml_stream.managers.schedule_manager import ScheduleManager
        
        console.print("[bold blue]Starting daemon mode...[/bold blue]")
        console.print("[dim]Processing scheduled downloads in background[/dim]")
        console.print("[dim]Press Ctrl+C to stop[/dim]")

        def execute_scheduled_download(scheduled: "ScheduledDownload") -> None:
            """
            Execute a scheduled download with FULL implementation.
            
            Supports:
            - Video downloads (all formats)
            - Audio downloads (all formats)
            - Playlist downloads (sequential)
            
            Args:
                scheduled: ScheduledDownload object to execute.
            
            Raises:
                Exception: Re-raises any download errors for status update.
            """
            from pytubefix import YouTube
            from pytubefix.contrib.playlist import Playlist
            
            from dml_stream.services.download_service import DownloadService
            from dml_stream.services.playlist_service import PlaylistService
            
            try:
                if scheduled.download_type == "video":
                    # === VIDEO DOWNLOAD ===
                    yt = YouTube(scheduled.url)
                    service = DownloadService()
                    
                    console.print(f"[dim]📹 Downloading video: {yt.title}[/dim]")
                    
                    result_path = service.download_video(
                        yt=yt,
                        output_folder=scheduled.output_folder,
                        output_format=scheduled.output_format or "mp4",
                        method=scheduled.method
                    )
                    
                    console.print(f"[green]✓ Video downloaded: {result_path}[/green]")
                    logger.info(f"Video download completed: {result_path}")
                    
                elif scheduled.download_type == "audio":
                    # === AUDIO DOWNLOAD ===
                    yt = YouTube(scheduled.url)
                    service = DownloadService()
                    
                    console.print(f"[dim]🎵 Downloading audio: {yt.title}[/dim]")
                    
                    result_path = service.download_audio(
                        yt=yt,
                        output_folder=scheduled.output_folder,
                        output_format=scheduled.output_format or "mp3",
                        method=scheduled.method
                    )
                    
                    console.print(f"[green]✓ Audio downloaded: {result_path}[/green]")
                    logger.info(f"Audio download completed: {result_path}")
                    
                elif scheduled.download_type == "playlist":
                    # === PLAYLIST DOWNLOAD ===
                    playlist = Playlist(scheduled.url)
                    
                    console.print(f"[dim]📋 Downloading playlist: {playlist.title}[/dim]")
                    console.print(f"[dim]  Videos: {len(playlist.video_urls)}[/dim]")
                    
                    # Download playlist sequentially (daemon-safe)
                    downloaded_count = 0
                    failed_count = 0
                    
                    for i, video_url in enumerate(playlist.video_urls, 1):
                        try:
                            console.print(f"[dim]  [{i}/{len(playlist.video_urls)}] Downloading...[/dim]")
                            
                            yt = YouTube(video_url)
                            service = DownloadService()
                            
                            # Determine if audio or video based on format
                            if scheduled.output_format in ["mp3", "m4a", "flac", "wav", "aac"]:
                                result_path = service.download_audio(
                                    yt=yt,
                                    output_folder=scheduled.output_folder,
                                    output_format=scheduled.output_format or "mp3",
                                    method=scheduled.method
                                )
                            else:
                                result_path = service.download_video(
                                    yt=yt,
                                    output_folder=scheduled.output_folder,
                                    output_format=scheduled.output_format or "mp4",
                                    method=scheduled.method
                                )
                            
                            downloaded_count += 1
                            console.print(f"[green]    ✓ Downloaded[/green]")
                            
                        except Exception as e:
                            failed_count += 1
                            console.print(f"[red]    ✗ Failed: {str(e)}[/red]")
                            logger.warning(f"Playlist video failed: {video_url} - {str(e)}")
                    
                    console.print(f"[bold]Playlist complete: {downloaded_count} succeeded, {failed_count} failed[/bold]")
                    logger.info(f"Playlist download completed: {downloaded_count}/{len(playlist.video_urls)}")
                    
                else:
                    logger.error(f"Unknown download type: {scheduled.download_type}")
                    raise ValueError(f"Unknown download type: {scheduled.download_type}")
                    
            except Exception as e:
                console.print(f"[red]✗ Download failed: {str(e)}[/red]")
                logger.error(f"Scheduled download failed: {scheduled.url} - {str(e)}")
                raise  # Re-raise for status update in daemon
        
        manager = ScheduleManager(
            db_path=config.database_path,
            execute_callback=execute_scheduled_download
        )
        manager.start_daemon()

        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            manager.stop_daemon()
            console.print("\n[yellow]Daemon stopped[/yellow]")

    elif list_scheduled:
        manager = ScheduleManager(
            db_path=config.database_path
        )
        scheduled = manager.get_all_scheduled()

        if not scheduled:
            console.print("[yellow]No scheduled downloads[/yellow]")
        else:
            table = Table(title="Scheduled Downloads")
            table.add_column("ID", style="dim")
            table.add_column("URL")
            table.add_column("Type")
            table.add_column("Time")
            table.add_column("Status")

            for s in scheduled:
                table.add_row(
                    s.id[:8] + "...",
                    s.url[:40] + "..." if len(s.url) > 40 else s.url,
                    s.download_type,
                    s.scheduled_time,
                    s.status
                )

            console.print(table)

    elif cancel_scheduled:
        manager = ScheduleManager(
            db_path=config.database_path
        )
        if manager.cancel_scheduled(cancel_scheduled):
            console.print(f"[green]✓ Cancelled scheduled download {cancel_scheduled}[/green]")
        else:
            console.print(f"[red]Scheduled download not found: {cancel_scheduled}[/red]")

    elif batch:
        manager = BatchManager(
            persist_path=config.batch_downloads_file_path
        )
        batch_download = manager.create_batch(batch)
        console.print(f"[green]✓ Created batch:[/green] {batch} (ID: {batch_download.id})")

    elif list_batch:
        manager = BatchManager(
            persist_path=config.batch_downloads_file_path
        )
        batches = manager.get_all_batches()

        if not batches:
            console.print("[yellow]No batch downloads[/yellow]")
        else:
            table = Table(title="Batch Downloads")
            table.add_column("ID", style="dim")
            table.add_column("Name")
            table.add_column("Items")
            table.add_column("Status")

            for b in batches:
                table.add_row(
                    b.id[:8] + "...",
                    b.name,
                    str(len(b.items)),
                    b.status
                )

            console.print(table)

    elif view_processes:
        manager = ProcessManager()
        processes = manager.get_all_processes()

        if not processes:
            console.print("[yellow]No tracked processes[/yellow]")
        else:
            table = Table(title="Tracked Processes")
            table.add_column("Name")
            table.add_column("URL")
            table.add_column("Type")
            table.add_column("Status")
            table.add_column("Progress")

            for p in processes:
                table.add_row(
                    p.name,
                    p.url[:30] + "..." if len(p.url) > 30 else p.url,
                    p.download_type,
                    p.status,
                    f"{p.progress:.1f}%"
                )

            console.print(table)

    elif schedule:
        from dml_stream.managers.schedule_manager import ScheduleManager
        
        console.print(
            Panel(
                "[bold]Schedule Download[/bold]\n\n"
                "Interactive scheduling interface",
                border_style="blue"
            )
        )
        
        # Get URL from user
        url = click.prompt("Enter YouTube URL", type=str)
        
        # Get download type
        download_type = click.prompt(
            "Download type",
            type=click.Choice(['video', 'audio', 'playlist']),
            default='video'
        )
        
        # Get output folder
        output_folder = click.prompt(
            "Output folder",
            type=str,
            default=config.default_output_folder
        )
        
        # Get scheduled time
        scheduled_time = click.prompt(
            "Schedule time (HH:MM or YYYY-MM-DD HH:MM:SS)",
            type=str
        )
        
        # Get download method
        method = click.prompt(
            "Download method",
            type=click.Choice(['normal', 'fast']),
            default='normal'
        )
        
        # Get threads
        threads = click.prompt(
            "Number of threads",
            type=int,
            default=config.default_threads
        )
        
        # Get format (optional)
        output_format = click.prompt(
            "Output format (optional, press Enter to skip)",
            type=str,
            default=''
        )
        
        # Create schedule manager with correct config path
        manager = ScheduleManager(
            db_path=config.database_path
        )
        
        scheduled = manager.schedule_download(
            url=url,
            download_type=download_type,
            output_folder=output_folder,
            scheduled_time=scheduled_time,
            method=method,
            threads=threads,
            output_format=output_format or None
        )
        
        console.print(
            Panel(
                f"[green]✓ Successfully scheduled download![/green]\n\n"
                f"[bold]URL:[/bold] {url}\n"
                f"[bold]Type:[/bold] {download_type}\n"
                f"[bold]Time:[/bold] {scheduled_time}\n"
                f"[bold]Output:[/bold] {output_folder}\n"
                f"[bold]ID:[/bold] {scheduled.id}\n\n"
                f"[dim]File: {config.scheduled_downloads_file_path}[/dim]",
                border_style="green"
            )
        )
        
        logger.info(f"Scheduled download: {url} at {scheduled_time}")

    else:
        console.print(
            Panel(
                "[bold]Service Commands[/bold]\n\n"
                "  --daemon           Run in daemon mode\n"
                "  --schedule         Schedule a download\n"
                "  --list-scheduled   List scheduled downloads\n"
                "  --cancel-scheduled Cancel a scheduled download\n"
                "  --batch            Create a batch download\n"
                "  --list-batch       List batch downloads\n"
                "  --view-processes   View tracked processes",
                border_style="blue"
            )
        )
