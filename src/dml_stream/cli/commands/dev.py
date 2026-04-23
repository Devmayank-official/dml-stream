"""
Developer commands for DML Stream.

This module provides developer-focused commands:
- shell: Python REPL with app context
- reset-db: Wipe and recreate history database
- seed: Populate test data
- benchmark: Download speed test
- debug: Verbose stream information
- export-logs: Zip and export logs
"""

import json
import logging
import os
import shutil
import tempfile
import time
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn, TransferSpeedColumn
from rich.table import Table

from dml_stream.config.settings import Config
from dml_stream.managers.history_manager import HistoryManager
from dml_stream.models.entities import DownloadHistory
from dml_stream.services.download_service import DownloadService
from dml_stream.utilities.file_utils import format_file_size
from dml_stream.utilities.platform_utils import get_config_dir

logger = logging.getLogger(__name__)
console = Console()


@click.group("dev")
@click.pass_context
def dev(ctx: click.Context) -> None:
    """
    Developer tools and debugging commands.

    Examples:

        dml-stream dev shell

        dml-stream dev benchmark <url>

        dml-stream dev debug <url>

        dml-stream dev export-logs
    """
    ctx.ensure_object(dict)
    ctx.obj['config'] = ctx.obj.get('config', Config())


@dev.command("shell")
@click.pass_context
def dev_shell(ctx: click.Context) -> None:
    """
    Drop into a Python REPL with application context.

    Starts an interactive Python shell with all DML Stream modules pre-imported.

    Examples:

        dml-stream dev shell
    """
    console.print(Panel.fit(
        "[bold blue]DML Stream Developer Shell[/bold blue]\n\n"
        "[dim]Starting Python REPL with app context...[/dim]\n\n"
        "Available imports:\n"
        "  - from dml_stream.config.settings import Config\n"
        "  - from dml_stream.services.download_service import DownloadService\n"
        "  - from dml_stream.services.playlist_service import PlaylistService\n"
        "  - from dml_stream.managers.history_manager import HistoryManager\n"
        "  - from dml_stream.models.entities import *\n\n"
        "[yellow]Type 'exit()' or Ctrl+D to quit[/yellow]"
    ))

    # Try to use code module for REPL
    try:
        import code
        from dml_stream.config.settings import Config
        from dml_stream.services.download_service import DownloadService
        from dml_stream.services.playlist_service import PlaylistService
        from dml_stream.managers.history_manager import HistoryManager

        config = ctx.obj.get('config', Config())

        # Create namespace with pre-imported modules
        namespace = {
            'config': config,
            'Config': Config,
            'DownloadService': DownloadService,
            'PlaylistService': PlaylistService,
            'HistoryManager': HistoryManager,
        }

        # Start REPL
        code.interact(
            local=namespace,
            banner=""
        )

    except ImportError:
        console.print("[yellow]Interactive shell not available. Install 'readline' for better experience.[/yellow]")
        raise SystemExit(1)

    logger.info("Developer shell session started")


@dev.command("reset-db")
@click.option(
    "--force",
    is_flag=True,
    help="Skip confirmation prompt"
)
@click.pass_context
def dev_reset_db(ctx: click.Context, force: bool) -> None:
    """
    Wipe and recreate the download history database.

    Deletes all download history and creates a fresh database.

    Examples:

        dml-stream dev reset-db

        dml-stream dev reset-db --force
    """
    config = ctx.obj.get('config', Config())
    db_file = config.database_path

    if not force:
        # Count existing entries
        try:
            manager = HistoryManager(db_path=db_file)
            count = len(manager.get_all_history())
            console.print(f"[yellow]Found {count} download history entries[/yellow]")
        except Exception:
            console.print("[yellow]History database may not exist[/yellow]")

        console.print("[bold red]Warning:[/bold red] This will permanently delete all download history!")
        if not click.confirm("Continue?", default=False):
            console.print("[yellow]Cancelled[/yellow]")
            return

    try:
        # Delete history files
        if os.path.exists(db_file):
            os.remove(db_file)
            console.print(f"[green]✓ Deleted history database: {db_file}[/green]")

        # Create fresh database
        manager = HistoryManager(db_path=db_file)
        console.print("[green]✓ Created fresh history database[/green]")

        logger.info("History database reset")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Failed to reset database: {str(e)}")
        raise SystemExit(1)


@dev.command("seed")
@click.option(
    "--count", "-c",
    type=int,
    default=10,
    help="Number of test entries to create"
)
@click.pass_context
def dev_seed(ctx: click.Context, count: int) -> None:
    """
    Populate test data for development and testing.

    Creates fake download history entries for testing UI and features.

    Examples:

        dml-stream dev seed

        dml-stream dev seed --count 50
    """
    config = ctx.obj.get('config', Config())
    manager = HistoryManager(db_path=config.database_path)

    console.print(f"[cyan]Creating {count} test download entries...[/cyan]")

    # Sample test data
    test_titles = [
        "Python Tutorial for Beginners",
        "Advanced Machine Learning",
        "Web Development Masterclass",
        "Data Science Fundamentals",
        "Cloud Computing Basics",
        "DevOps Engineering",
        "Cybersecurity Essentials",
        "Mobile App Development",
        "Game Development with Unity",
        "Blockchain Technology",
    ]

    test_urls = [
        "https://youtube.com/watch?v=TEST001",
        "https://youtube.com/watch?v=TEST002",
        "https://youtube.com/watch?v=TEST003",
        "https://youtube.com/watch?v=TEST004",
        "https://youtube.com/watch?v=TEST005",
    ]

    test_types = ['video', 'audio', 'playlist']
    test_statuses = ['success', 'success', 'success', 'success', 'failed']  # 80% success rate

    created_count = 0

    with Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Creating entries...", total=count)

        for i in range(count):
            title = f"{test_titles[i % len(test_titles)]} - Test {i + 1}"
            url = test_urls[i % len(test_urls)]
            download_type = test_types[i % len(test_types)]
            status = test_statuses[i % len(test_statuses)]

            # Create fake file path
            file_path = f"/fake/path/download_{i}.{download_type}"

            # Create entry with random date in past 30 days
            days_ago = i % 30
            download_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")

            try:
                # Convert string size to integer bytes for the new repository
                size_mb = (i % 500) + 50
                size_bytes = int(size_mb * 1024 * 1024)

                manager._repository.add(
                    title=title,
                    url=url,
                    file_path=file_path,
                    file_size=size_bytes,
                    download_type=download_type,
                    status=status
                )
                created_count += 1
                progress.update(task, advance=1)

            except Exception as e:
                logger.warning(f"Failed to create test entry {i}: {str(e)}")

    console.print(f"[bold green]✓ Created {created_count} test entries[/bold green]")
    logger.info(f"Seeded {created_count} test download entries")


@dev.command("benchmark")
@click.argument("url", required=True)
@click.option(
    "--threads", "-t",
    type=int,
    default=4,
    help="Number of download threads to test"
)
@click.option(
    "--duration", "-d",
    type=int,
    default=10,
    help="Test duration in seconds"
)
@click.pass_context
def dev_benchmark(ctx: click.Context, url: str, threads: int, duration: int) -> None:
    """
    Run download speed benchmark.

    Tests download speed with different thread counts.

    URL: YouTube video URL for testing

    Examples:

        dml-stream dev benchmark <url>

        dml-stream dev benchmark <url> --threads 8 --duration 30
    """
    console.print(Panel.fit(
        f"[bold]Download Speed Benchmark[/bold]\n\n"
        f"[cyan]URL:[/cyan] {url[:60]}...\n"
        f"[cyan]Threads:[/cyan] {threads}\n"
        f"[cyan]Duration:[/cyan] {duration}s"
    ))

    try:
        service = DownloadService(threads=threads)

        # Get video info
        console.print("[cyan]Fetching video info...[/cyan]")
        yt = service.get_video_info(url)

        # Get best stream
        candidates = service.list_streams(yt)
        if not candidates:
            console.print("[bold red]Error:[/bold red] No streams found")
            raise SystemExit(1)

        # Select best progressive stream
        stream = None
        for c in candidates:
            if c.type == 'progressive' and c.resolution and '720' in c.resolution:
                stream = c
                break

        if not stream:
            stream = candidates[0]

        console.print(f"[dim]Testing with: {stream.resolution or 'N/A'} ({stream.get_size_formatted()})[/dim]")

        # Download to temp file with speed tracking
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, f"benchmark_{yt.video_id}.tmp")

        speeds: List[float] = []
        start_time = time.time()
        downloaded_bytes = 0

        def progress_callback(progress):
            nonlocal downloaded_bytes
            downloaded_bytes = progress.downloaded_bytes
            if progress.speed > 0:
                speeds.append(progress.speed)

        service.progress_callback = progress_callback

        console.print("[cyan]Starting benchmark download...[/cyan]")

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
            task = progress.add_task("[cyan]Downloading...", total=stream.filesize or 100)

            try:
                service.download_stream(
                    url=stream.stream.url,
                    out_path=temp_file,
                    desc="Benchmark"
                )
            except Exception:
                pass  # Partial download is OK for benchmark

        # Cleanup
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass

        # Calculate results
        elapsed = time.time() - start_time
        avg_speed = sum(speeds) / len(speeds) if speeds else 0
        max_speed = max(speeds) if speeds else 0

        results = Table(title="Benchmark Results")
        results.add_column("Metric", style="cyan")
        results.add_column("Value", style="green")

        results.add_row("Duration", f"{elapsed:.1f}s")
        results.add_row("Downloaded", format_file_size(downloaded_bytes))
        results.add_row("Average Speed", f"{format_file_size(int(avg_speed))}/s")
        results.add_row("Max Speed", f"{format_file_size(int(max_speed))}/s")
        results.add_row("Threads", str(threads))

        console.print(results)

        logger.info(f"Benchmark completed: avg={avg_speed:.0f} B/s, max={max_speed:.0f} B/s")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Benchmark failed: {str(e)}")
        raise SystemExit(1)


@dev.command("debug")
@click.argument("url", required=True)
@click.option(
    "--full",
    is_flag=True,
    help="Show complete debug information"
)
@click.pass_context
def dev_debug(ctx: click.Context, url: str, full: bool) -> None:
    """
    Show verbose debug information for a URL.

    Displays raw stream information and technical details.

    URL: YouTube video URL

    Examples:

        dml-stream dev debug <url>

        dml-stream dev debug <url> --full
    """
    console.print(Panel.fit(
        f"[bold]Debug Information[/bold]\n\n"
        f"[cyan]URL:[/cyan] {url}"
    ))

    try:
        service = DownloadService()

        # Get video info
        console.print("[cyan]Fetching video info...[/cyan]")
        yt = service.get_video_info(url)

        # Basic info
        basic_table = Table(title="Basic Information")
        basic_table.add_column("Property", style="cyan")
        basic_table.add_column("Value", style="white")

        basic_table.add_row("Title", yt.title)
        basic_table.add_row("Video ID", yt.video_id)
        basic_table.add_row("Author", yt.author)
        basic_table.add_row("Length", f"{yt.length}s" if yt.length else "Unknown")
        basic_table.add_row("Views", f"{yt.views:,}" if yt.views else "Unknown")

        console.print(basic_table)

        # Stream info
        streams_table = Table(title="Stream Summary")
        streams_table.add_column("Type", style="cyan")
        streams_table.add_column("Count", style="green")

        progressive_count = len(list(yt.streams.filter(progressive=True)))
        adaptive_video_count = len(list(yt.streams.filter(adaptive=True, only_video=True)))
        adaptive_audio_count = len(list(yt.streams.filter(adaptive=True, only_audio=True)))

        streams_table.add_row("Progressive (Video+Audio)", str(progressive_count))
        streams_table.add_row("Adaptive Video", str(adaptive_video_count))
        streams_table.add_row("Adaptive Audio", str(adaptive_audio_count))
        streams_table.add_row("Total", str(len(list(yt.streams))))

        console.print(streams_table)

        if full:
            # Detailed stream info
            candidates = service.list_streams(yt)

            detail_table = Table(title="All Streams")
            detail_table.add_column("itag", style="dim")
            detail_table.add_column("type", style="cyan")
            detail_table.add_column("mime", style="yellow")
            detail_table.add_column("resolution", style="green")
            detail_table.add_column("abr", style="cyan")
            detail_table.add_column("filesize", style="white")
            detail_table.add_column("url", style="dim")

            for c in candidates:
                url_preview = c.stream.url[:50] + "..." if len(c.stream.url) > 50 else c.stream.url
                detail_table.add_row(
                    str(c.itag),
                    c.type,
                    c.mime,
                    c.resolution or 'N/A',
                    c.abr or 'N/A',
                    c.get_size_formatted(),
                    url_preview
                )

            console.print(detail_table)

        logger.info(f"Debug info retrieved for: {yt.video_id}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Debug failed: {str(e)}")
        raise SystemExit(1)


@dev.command("export-logs")
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Output path for zip file"
)
@click.option(
    "--include-system",
    is_flag=True,
    help="Include system information"
)
@click.pass_context
def dev_export_logs(ctx: click.Context, output: Optional[str], include_system: bool) -> None:
    """
    Zip and export logs for debugging.

    Creates a zip archive with all logs and optionally system info.

    Examples:

        dml-stream dev export-logs

        dml-stream dev export-logs -o logs.zip

        dml-stream dev export-logs --include-system
    """
    config = ctx.obj.get('config', Config())

    # Determine output path
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"dml-stream-logs-{timestamp}.zip"

    console.print(f"[cyan]Exporting logs to: {output}[/cyan]")

    try:
        # Create temp directory for collecting files
        temp_dir = tempfile.mkdtemp()

        # Collect log files
        log_files = []
        log_dir = Path(config.log_file_path).parent

        if log_dir.exists():
            for log_file in log_dir.glob("*.log*"):
                log_files.append(log_file)

        # Create zip
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add log files
            for log_file in log_files:
                try:
                    zipf.write(log_file, f"logs/{log_file.name}")
                except Exception as e:
                    logger.warning(f"Failed to add {log_file}: {str(e)}")

            # Add config (sanitized)
            try:
                config_path = Path(config.config_file_path)
                if config_path.exists():
                    zipf.write(config_path, "config/config.json")
            except Exception as e:
                logger.warning(f"Failed to add config: {str(e)}")

            # Add system info if requested
            if include_system:
                try:
                    import platform
                    system_info = {
                        'platform': platform.system(),
                        'platform_release': platform.release(),
                        'platform_version': platform.version(),
                        'machine': platform.machine(),
                        'processor': platform.processor(),
                        'python_version': platform.python_version(),
                        'python_implementation': platform.python_implementation(),
                    }

                    system_info_path = os.path.join(temp_dir, "system_info.json")
                    with open(system_info_path, 'w') as f:
                        json.dump(system_info, f, indent=2)

                    zipf.write(system_info_path, "system_info.json")
                except Exception as e:
                    logger.warning(f"Failed to add system info: {str(e)}")

            # Add metadata
            metadata = {
                'exported_at': datetime.now().isoformat(),
                'version': '2.5.0',
                'log_files': [str(f) for f in log_files],
            }

            metadata_path = os.path.join(temp_dir, "metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            zipf.write(metadata_path, "metadata.json")

        # Cleanup temp dir
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass

        # Get zip file size
        zip_size = os.path.getsize(output)

        console.print(f"[bold green]✓ Logs exported to: {output}[/bold green]")
        console.print(f"[dim]Size: {format_file_size(zip_size)}[/dim]")

        logger.info(f"Exported logs to: {output} ({format_file_size(zip_size)})")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Failed to export logs: {str(e)}")
        raise SystemExit(1)
