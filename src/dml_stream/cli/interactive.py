"""
Interactive mode application for YouTube Downloader.

This module provides a menu-driven interactive interface
using Rich for beautiful terminal output.
"""

import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from dml_stream.config.settings import Config

console = Console()


class InteractiveApp:
    """
    Interactive application for YouTube Downloader.
    
    Provides a menu-driven interface for all download operations.
    """

    def __init__(self, config: Optional[Config] = None) -> None:
        """
        Initialize the interactive application.
        
        Args:
            config: Application configuration.
        """
        self.config = config or Config()
        self.running = True

    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        console.clear()

    def show_header(self) -> None:
        """Display application header."""
        from dml_stream import __version__

        header = Panel.fit(
            f"[bold blue]YouTube Downloader[/bold blue] v{__version__}\n"
            f"[dim]Enterprise-Level Terminal-Based Video Download Solution[/dim]",
            border_style="blue",
            padding=(1, 2)
        )
        console.print(header)
        console.print()

    def show_menu(self) -> None:
        """Display main menu."""
        menu_items = [
            ("1", "🎥", "Download Video (single)"),
            ("2", "🎵", "Download Audio (single)"),
            ("3", "📺", "Download Playlist (videos)"),
            ("4", "🎵", "Download Playlist (audio only)"),
            ("5", "📋", "View Download History"),
            ("6", "🔄", "Retry Failed Downloads"),
            ("7", "⏰", "Schedule Download"),
            ("8", "📦", "Batch Download Manager"),
            ("9", "📅", "View Scheduled Downloads"),
            ("10", "📊", "View Batch Downloads"),
            ("11", "⚙️", "View All Processes"),
            ("12", "🏃", "View Running Processes"),
            ("13", "📝", "View Application Logs"),
            ("14", "⚙️", "Configuration Settings"),
            ("15", "🧹", "Clear Terminal"),
            ("0", "❌", "Exit"),
        ]

        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Key", style="bold cyan", width=4)
        table.add_column("Icon", width=4)
        table.add_column("Option", style="white")

        for key, icon, option in menu_items:
            table.add_row(key, icon, option)

        console.print(table)
        console.print()

    def run(self) -> None:
        """Run the interactive application."""
        self.clear_screen()
        self.show_header()

        while self.running:
            self.show_menu()
            choice = Prompt.ask(
                "[bold]Select an option[/bold]",
                default="0",
                show_default=False
            )

            self.handle_choice(choice)

    def handle_choice(self, choice: str) -> None:
        """Handle menu choice."""
        handlers = {
            "1": self.download_video,
            "2": self.download_audio,
            "3": self.download_playlist_video,
            "4": self.download_playlist_audio,
            "5": self.view_history,
            "6": self.retry_failed,
            "7": self.schedule_download,
            "8": self.batch_manager,
            "9": self.view_scheduled,
            "10": self.view_batch,
            "11": self.view_all_processes,
            "12": self.view_running_processes,
            "13": self.view_logs,
            "14": self.view_config,
            "15": self.clear_screen,
            "0": self.exit_app,
        }

        handler = handlers.get(choice)
        if handler:
            try:
                handler()
            except KeyboardInterrupt:
                console.print("\n[yellow]Operation cancelled[/yellow]")
            except Exception as e:
                console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        else:
            console.print("[red]Invalid option. Please try again.[/red]")

        if choice != "15":  # Don't pause after clear
            console.input("\n[dim]Press Enter to continue...[/dim]")

    def download_video(self) -> None:
        """Download a single video."""
        from rich.progress import (
            BarColumn,
            Progress,
            TextColumn,
            TimeRemainingColumn,
            TransferSpeedColumn,
        )

        from dml_stream.models.entities import DownloadProgress
        from dml_stream.services.download_service import DownloadService

        console.print("\n[bold blue]🎥 Download Video[/bold blue]\n")

        url = Prompt.ask("Enter YouTube video URL")
        if not url:
            return

        # Ask for quality
        quality = Prompt.ask(
            "Select quality",
            choices=["1080p", "720p", "480p", "360p", "best"],
            default="720p"
        )

        # Ask for format
        output_format = Prompt.ask(
            "Output format",
            choices=["mp4", "mkv", "webm", "avi"],
            default="mp4"
        )

        # Ask for download method
        method = Prompt.ask(
            "Download method",
            choices=["normal", "fast"],
            default="normal"
        )

        threads = 4
        if method == "fast":
            threads = int(Prompt.ask("Number of threads", default="4"))

        try:
            service = DownloadService(
                output_folder=self.config.default_output_folder,
                threads=threads if method == "fast" else 1,
            )

            # Get video info
            console.print("\n[cyan]Fetching video info...[/cyan]")
            yt = service.get_video_info(url)
            console.print(f"[green]✓[/green] {yt.title}")
            console.print(f"[dim]Duration: {yt.length} seconds[/dim]")

            # Confirm download
            if not Confirm.ask("\nStart download?", default=True):
                return

            # Download with progress
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
                    output_format=output_format,
                    method=method
                )

            console.print("\n[bold green]✓ Download completed![/bold green]")
            console.print(f"[dim]Saved to: {file_path}[/dim]")

        except Exception as e:
            console.print(f"\n[bold red]✗ Download failed:[/bold red] {str(e)}")

    def download_audio(self) -> None:
        """Download audio from a video."""
        from rich.progress import (
            BarColumn,
            Progress,
            TextColumn,
            TransferSpeedColumn,
        )

        from dml_stream.models.entities import DownloadProgress
        from dml_stream.services.download_service import DownloadService

        console.print("\n[bold green]🎵 Download Audio[/bold green]\n")

        url = Prompt.ask("Enter YouTube video URL")
        if not url:
            return

        output_format = Prompt.ask(
            "Output format",
            choices=["mp3", "m4a", "flac", "wav", "aac"],
            default="mp3"
        )

        method = Prompt.ask(
            "Download method",
            choices=["normal", "fast"],
            default="normal"
        )

        threads = 4
        if method == "fast":
            threads = int(Prompt.ask("Number of threads", default="4"))

        try:
            service = DownloadService(
                output_folder=self.config.default_output_folder,
                threads=threads if method == "fast" else 1,
            )

            console.print("\n[cyan]Fetching video info...[/cyan]")
            yt = service.get_video_info(url)
            console.print(f"[green]✓[/green] {yt.title}")

            if not Confirm.ask("\nStart audio download?", default=True):
                return

            with Progress(
                TextColumn("[bold green]{task.description}"),
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                "•",
                TransferSpeedColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("[cyan]Downloading audio...", total=100)

                def update_progress(p: DownloadProgress):
                    progress.update(task, completed=p.percentage)

                service.progress_callback = update_progress

                file_path = service.download_audio(
                    yt,
                    output_format=output_format,
                    method=method
                )

            console.print("\n[bold green]✓ Audio download completed![/bold green]")
            console.print(f"[dim]Saved to: {file_path}[/dim]")

        except Exception as e:
            console.print(f"\n[bold red]✗ Download failed:[/bold red] {str(e)}")

    def download_playlist_video(self) -> None:
        """Download playlist videos."""
        self._download_playlist(download_type="video")

    def download_playlist_audio(self) -> None:
        """Download playlist audio."""
        self._download_playlist(download_type="audio")

    def _download_playlist(self, download_type: str) -> None:
        """Download a playlist."""
        from dml_stream.services.playlist_service import PlaylistService

        emoji = "📺" if download_type == "video" else "🎵"
        title = "Playlist Videos" if download_type == "video" else "Playlist Audio"
        console.print(f"\n[bold magenta]{emoji} Download {title}[/bold magenta]\n")

        url = Prompt.ask("Enter YouTube playlist URL")
        if not url:
            return

        output_format = Prompt.ask(
            "Output format (press Enter for default)",
            default="mp4" if download_type == "video" else "mp3"
        )

        skip_existing = Confirm.ask("Skip videos that already exist?", default=True)

        try:
            service = PlaylistService(
                output_folder=self.config.default_output_folder,
            )

            console.print("\n[cyan]Fetching playlist info...[/cyan]")
            playlist_info = service.get_playlist_info(url)
            console.print(f"[green]✓[/green] {playlist_info['title']}")
            console.print(f"[dim]{playlist_info['video_count']} videos[/dim]")

            if not Confirm.ask(f"\nDownload all {playlist_info['video_count']} videos?", default=True):
                return

            console.print("\n[cyan]Starting download...[/cyan]\n")

            results = service.download_playlist(
                url=url,
                download_type=download_type,
                output_format=output_format,
                skip_existing=skip_existing
            )

            # Show summary
            summary = Table(title="Download Summary")
            summary.add_column("Metric", style="cyan")
            summary.add_column("Value", style="green")

            summary.add_row("Total", str(results['total_videos']))
            summary.add_row("Successful", str(results['successful']))
            summary.add_row("Failed", str(results['failed']))
            summary.add_row("Skipped", str(results['skipped']))

            console.print(summary)

        except Exception as e:
            console.print(f"\n[bold red]✗ Download failed:[/bold red] {str(e)}")

    def view_history(self) -> None:
        """View download history."""
        from dml_stream.managers.history_manager import HistoryManager

        console.print("\n[bold blue]📋 Download History[/bold blue]\n")

        manager = HistoryManager(persist_path=self.config.history_file_path)
        entries = manager.get_recent(20)

        if not entries:
            console.print("[yellow]No download history[/yellow]")
            return

        table = Table(title="Recent Downloads")
        table.add_column("Title", style="white", max_width=40)
        table.add_column("Type", style="cyan")
        table.add_column("Size", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Date", style="dim")

        for e in entries:
            status_style = "green" if e.status == "success" else "red"
            table.add_row(
                e.title[:40] + "..." if len(e.title) > 40 else e.title,
                e.download_type,
                e.file_size,
                f"[{status_style}]{e.status}[/{status_style}]",
                e.download_date
            )

        console.print(table)

    def retry_failed(self) -> None:
        """Retry failed downloads."""
        from dml_stream.managers.history_manager import HistoryManager

        console.print("\n[bold yellow]🔄 Retry Failed Downloads[/bold yellow]\n")

        manager = HistoryManager(persist_path=self.config.history_file_path)
        failed = manager.get_failed()

        if not failed:
            console.print("[green]No failed downloads to retry[/green]")
            return

        console.print(f"Found {len(failed)} failed download(s)\n")

        for i, entry in enumerate(failed[:10], 1):
            console.print(f"{i}. {entry.title}")
            console.print(f"   URL: {entry.url}\n")

        if Confirm.ask("Retry all failed downloads?", default=True):
            console.print("[cyan]Retrying downloads...[/cyan]")
            # Would implement retry logic here
            console.print("[green]Retry functionality would be implemented here[/green]")

    def schedule_download(self) -> None:
        """Schedule a download."""
        from dml_stream.managers.schedule_manager import ScheduleManager

        console.print("\n[bold cyan]⏰ Schedule Download[/bold cyan]\n")

        url = Prompt.ask("Enter YouTube URL")
        if not url:
            return

        download_type = Prompt.ask(
            "Download type",
            choices=["video", "audio", "playlist"],
            default="video"
        )

        scheduled_time = Prompt.ask(
            "Scheduled time (HH:MM or YYYY-MM-DD HH:MM)",
            default="12:00"
        )

        try:
            manager = ScheduleManager(
                persist_path=self.config.scheduled_downloads_file_path
            )

            manager.schedule_download(
                url=url,
                download_type=download_type,
                output_folder=self.config.default_output_folder,
                scheduled_time=scheduled_time
            )

            console.print(f"[green]✓ Download scheduled for {scheduled_time}[/green]")

        except Exception as e:
            console.print(f"[red]Failed to schedule: {str(e)}[/red]")

    def batch_manager(self) -> None:
        """Batch download manager."""
        from dml_stream.managers.batch_manager import BatchManager

        console.print("\n[bold magenta]📦 Batch Download Manager[/bold magenta]\n")

        action = Prompt.ask(
            "Select action",
            choices=["create", "list", "start", "delete", "back"],
            default="list"
        )

        manager = BatchManager(persist_path=self.config.batch_downloads_file_path)

        if action == "create":
            name = Prompt.ask("Enter batch name")
            batch = manager.create_batch(name)
            console.print(f"[green]✓ Created batch:[/green] {batch.name} (ID: {batch.id})")

            # Add URLs
            while Confirm.ask("Add a URL to this batch?", default=True):
                url = Prompt.ask("Enter YouTube URL")
                download_type = Prompt.ask("Type", choices=["video", "audio"], default="video")
                manager.add_item_to_batch(
                    batch_id=batch.id,
                    url=url,
                    download_type=download_type,
                    output_folder=self.config.default_output_folder
                )
                console.print("[green]✓ Added to batch[/green]")

        elif action == "list":
            batches = manager.get_all_batches()
            if not batches:
                console.print("[yellow]No batch downloads[/yellow]")
            else:
                table = Table(title="Batch Downloads")
                for b in batches:
                    table.add_row(b.name, str(len(b.items)), b.status)
                console.print(table)

        elif action == "start":
            batch_id = Prompt.ask("Enter batch ID")
            # Would implement batch execution here
            console.print("[yellow]Batch execution would start here[/yellow]")

        elif action == "delete":
            batch_id = Prompt.ask("Enter batch ID to delete")
            if manager.delete_batch(batch_id):
                console.print("[green]✓ Batch deleted[/green]")

    def view_scheduled(self) -> None:
        """View scheduled downloads."""
        from dml_stream.managers.schedule_manager import ScheduleManager

        console.print("\n[bold cyan]📅 Scheduled Downloads[/bold cyan]\n")

        manager = ScheduleManager(persist_path=self.config.scheduled_downloads_file_path)
        scheduled = manager.get_all_scheduled()

        if not scheduled:
            console.print("[yellow]No scheduled downloads[/yellow]")
            return

        table = Table(title="Scheduled Downloads")
        table.add_column("ID", style="dim")
        table.add_column("URL", max_width=40)
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

    def view_batch(self) -> None:
        """View batch downloads."""
        from dml_stream.managers.batch_manager import BatchManager

        console.print("\n[bold magenta]📊 Batch Downloads[/bold magenta]\n")

        manager = BatchManager(persist_path=self.config.batch_downloads_file_path)
        batches = manager.get_all_batches()

        if not batches:
            console.print("[yellow]No batch downloads[/yellow]")
            return

        table = Table(title="Batch Downloads")
        table.add_column("Name")
        table.add_column("Items")
        table.add_column("Status")
        table.add_column("Progress")

        for b in batches:
            table.add_row(
                b.name,
                str(len(b.items)),
                b.status,
                f"{b.get_progress():.1f}%"
            )

        console.print(table)

    def view_all_processes(self) -> None:
        """View all tracked processes."""
        from dml_stream.managers.process_manager import ProcessManager

        console.print("\n[bold yellow]⚙️ All Processes[/bold yellow]\n")

        manager = ProcessManager()
        processes = manager.get_all_processes()

        if not processes:
            console.print("[yellow]No tracked processes[/yellow]")
            return

        table = Table(title="Tracked Processes")
        table.add_column("Name")
        table.add_column("URL", max_width=30)
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

    def view_running_processes(self) -> None:
        """View running processes."""
        from dml_stream.managers.process_manager import ProcessManager

        console.print("\n[bold green]🏃 Running Processes[/bold green]\n")

        manager = ProcessManager()
        processes = manager.get_running_processes()

        if not processes:
            console.print("[green]No processes currently running[/green]")
            return

        table = Table(title="Running Processes")
        table.add_column("Name")
        table.add_column("URL", max_width=30)
        table.add_column("Type")
        table.add_column("Progress")
        table.add_column("Started")

        for p in processes:
            table.add_row(
                p.name,
                p.url[:30] + "..." if len(p.url) > 30 else p.url,
                p.download_type,
                f"{p.progress:.1f}%",
                p.start_time
            )

        console.print(table)

    def view_logs(self) -> None:
        """View application logs."""
        console.print("\n[bold blue]📝 Application Logs[/bold blue]\n")

        log_file = self.config.log_file_path

        try:
            with open(log_file) as f:
                lines = f.readlines()

            if not lines:
                console.print("[yellow]Log file is empty[/yellow]")
                return

            # Show last 50 lines
            for line in lines[-50:]:
                console.print(f"[dim]{line.strip()}[/dim]")

        except FileNotFoundError:
            console.print("[yellow]Log file not found[/yellow]")
        except Exception as e:
            console.print(f"[red]Error reading logs: {str(e)}[/red]")

    def view_config(self) -> None:
        """View configuration."""
        console.print("\n[bold yellow]⚙️ Configuration Settings[/bold yellow]\n")

        table = Table(title="Current Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        for field_name in self.config.__dataclass_fields__:
            value = getattr(self.config, field_name)
            table.add_row(field_name, str(value))

        console.print(table)

        if Confirm.ask("\nModify configuration?", default=False):
            key = Prompt.ask("Enter setting name to modify")
            if hasattr(self.config, key):
                value = Prompt.ask("Enter new value")
                try:
                    self.config.set(key, value)
                    self.config.save_to_file()
                    console.print("[green]✓ Configuration updated[/green]")
                except Exception as e:
                    console.print(f"[red]Error: {str(e)}[/red]")
            else:
                console.print(f"[red]Unknown setting: {key}[/red]")

    def exit_app(self) -> None:
        """Exit the application."""
        if Confirm.ask("Exit YouTube Downloader?", default=True):
            console.print("\n[bold blue]Goodbye! 👋[/bold blue]\n")
            self.running = False
            sys.exit(0)
