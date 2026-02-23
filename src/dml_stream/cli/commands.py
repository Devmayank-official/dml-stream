"""
CLI commands for YouTube Downloader.

This module defines all Click commands for the CLI.
"""

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

console = Console()


@click.command("download")
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
def download_video(
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
    
        dml-stream download --url https://youtube.com/watch?v=...
        
        dml-stream download -u URL -f mp4 -q 1080p --fast
    """
    config = ctx.obj.get('config', Config())

    console.print(Panel.fit(f"[bold blue]Downloading Video[/bold blue]\n\n[dim]{url}[/dim]"))

    try:
        # Create download service
        def progress_callback(progress: DownloadProgress):
            # This would update a Rich progress bar in a real implementation
            pass

        service = DownloadService(
            output_folder=output or config.default_output_folder,
            threads=threads if fast else 1,
            max_speed=speed_limit,
            progress_callback=progress_callback
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

        console.print("[bold green]✓ Download completed![/bold green]")
        console.print(f"[dim]Saved to: {file_path}[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise SystemExit(1)


@click.command("audio")
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
def download_audio(
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
    
        dml-stream audio --url https://youtube.com/watch?v=...
        
        dml-stream audio -u URL -f flac --fast
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

        console.print("[bold green]✓ Audio download completed![/bold green]")
        console.print(f"[dim]Saved to: {file_path}[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise SystemExit(1)


@click.command("playlist")
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
@click.pass_context
def download_playlist(
    ctx: click.Context,
    url: str,
    output: str,
    audio_only: bool,
    output_format: str,
    skip_existing: bool
) -> None:
    """
    Download all videos from a YouTube playlist.
    
    Downloads an entire playlist with progress tracking for each video.
    
    Examples:
    
        dml-stream playlist --url https://youtube.com/playlist?list=...
        
        dml-stream playlist -u URL --audio-only -f mp3
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
            skip_existing=skip_existing
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
            for error in results['errors'][:5]:  # Show first 5 errors
                console.print(f"  • {error['url']}: {error['error']}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise SystemExit(1)


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
    """
    from dml_stream.managers.batch_manager import BatchManager
    from dml_stream.managers.process_manager import ProcessManager
    from dml_stream.managers.schedule_manager import ScheduleManager

    config = ctx.obj.get('config', Config())

    if daemon:
        console.print("[bold blue]Starting daemon mode...[/bold blue]")
        console.print("[dim]Processing scheduled downloads in background[/dim]")

        manager = ScheduleManager(
            persist_path=config.scheduled_downloads_file_path
        )
        manager.start_daemon()

        try:
            import time
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            manager.stop_daemon()
            console.print("\n[yellow]Daemon stopped[/yellow]")

    elif list_scheduled:
        manager = ScheduleManager(
            persist_path=config.scheduled_downloads_file_path
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
            persist_path=config.scheduled_downloads_file_path
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

    else:
        console.print(
            Panel(
                "[bold]Service Commands[/bold]\n\n"
                "  --daemon          Run in daemon mode\n"
                "  --schedule        Schedule a download\n"
                "  --list-scheduled  List scheduled downloads\n"
                "  --cancel-scheduled Cancel a scheduled download\n"
                "  --batch           Create a batch download\n"
                "  --list-batch      List batch downloads\n"
                "  --view-processes  View tracked processes"
            )
        )


@click.command("history")
@click.option(
    "--recent", "-r",
    is_flag=True,
    help="Show recent downloads"
)
@click.option(
    "--limit", "-l",
    type=int,
    default=10,
    help="Number of entries to show"
)
@click.option(
    "--search", "-s",
    type=str,
    help="Search history by title or URL"
)
@click.option(
    "--failed",
    is_flag=True,
    help="Show failed downloads"
)
@click.option(
    "--stats",
    is_flag=True,
    help="Show download statistics"
)
@click.pass_context
def history(
    ctx: click.Context,
    recent: bool,
    limit: int,
    search: str,
    failed: bool,
    stats: bool
) -> None:
    """
    View and manage download history.
    
    Examples:
    
        dml-stream history --recent
        
        dml-stream history --stats
    """
    config = ctx.obj.get('config', Config())
    manager = HistoryManager(persist_path=config.history_file_path)

    if stats:
        statistics = manager.get_statistics()

        table = Table(title="Download Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Downloads", str(statistics['total_downloads']))
        table.add_row("Successful", str(statistics['successful']))
        table.add_row("Failed", str(statistics['failed']))
        table.add_row("Total Size", statistics['total_size'])

        if statistics['first_download']:
            table.add_row("First Download", statistics['first_download'])
        if statistics['last_download']:
            table.add_row("Last Download", statistics['last_download'])

        console.print(table)

    elif failed:
        entries = manager.get_failed()

        if not entries:
            console.print("[green]No failed downloads[/green]")
        else:
            table = Table(title="Failed Downloads")
            table.add_column("Title")
            table.add_column("URL")
            table.add_column("Date")

            for e in entries[:limit]:
                table.add_row(e.title, e.url, e.download_date)

            console.print(table)

    elif search:
        entries = manager.search(search)

        if not entries:
            console.print(f"[yellow]No results for '{search}'[/yellow]")
        else:
            table = Table(title=f"Search Results: {search}")
            table.add_column("Title")
            table.add_column("Type")
            table.add_column("Status")
            table.add_column("Date")

            for e in entries:
                status_color = "green" if e.status == "success" else "red"
                table.add_row(
                    e.title,
                    e.download_type,
                    f"[{status_color}]{e.status}[/{status_color}]",
                    e.download_date
                )

            console.print(table)

    else:
        # Show recent by default
        entries = manager.get_recent(limit)

        if not entries:
            console.print("[yellow]No download history[/yellow]")
        else:
            table = Table(title="Recent Downloads")
            table.add_column("Title")
            table.add_column("Type")
            table.add_column("Size")
            table.add_column("Status")
            table.add_column("Date")

            for e in entries:
                status_color = "green" if e.status == "success" else "red"
                table.add_row(
                    e.title[:40] + "..." if len(e.title) > 40 else e.title,
                    e.download_type,
                    e.file_size,
                    f"[{status_color}]{e.status}[/{status_color}]",
                    e.download_date
                )

            console.print(table)


@click.command("config")
@click.option(
    "--show",
    is_flag=True,
    help="Show current configuration"
)
@click.option(
    "--set",
    "set_value",
    type=(str, str),
    help="Set a configuration value"
)
@click.option(
    "--reset",
    is_flag=True,
    help="Reset configuration to defaults"
)
@click.pass_context
def config_command(
    ctx: click.Context,
    show: bool,
    set_value: tuple,
    reset: bool
) -> None:
    """
    View and modify configuration settings.
    
    Examples:
    
        dml-stream config --show
        
        dml-stream config --set default_threads 8
    """
    config = ctx.obj.get('config', Config())

    if show:
        table = Table(title="Current Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        for field_name in config.__dataclass_fields__:
            value = getattr(config, field_name)
            table.add_row(field_name, str(value))

        console.print(table)

    elif set_value:
        key, value = set_value

        if hasattr(config, key):
            # Try to convert value to appropriate type
            current_value = getattr(config, key)
            try:
                if isinstance(current_value, int):
                    value = int(value)
                elif isinstance(current_value, bool):
                    value = value.lower() in ('true', '1', 'yes')
            except ValueError:
                pass

            config.set(key, value)
            config.save_to_file()
            console.print(f"[green]✓ Set {key} = {value}[/green]")
        else:
            console.print(f"[red]Unknown configuration key: {key}[/red]")

    elif reset:
        config.reset_to_defaults()
        config.save_to_file()
        console.print("[green]✓ Configuration reset to defaults[/green]")

    else:
        # Show by default
        table = Table(title="Current Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        for field_name in config.__dataclass_fields__:
            value = getattr(config, field_name)
            table.add_row(field_name, str(value))

        console.print(table)
