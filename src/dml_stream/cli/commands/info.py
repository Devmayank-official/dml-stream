"""
Info commands for DML Stream.

This module provides commands for retrieving video information:
- info video: Get video details
- info formats: List available formats
- info thumbnail: Preview/download thumbnail
- info subtitle: List subtitles
- info metadata: Full metadata dump
- info channel: Channel information
"""

import json
import logging
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from dml_stream.config.settings import Config
from dml_stream.services.download_service import DownloadService
from dml_stream.utilities.file_utils import format_duration, format_file_size

logger = logging.getLogger(__name__)
console = Console()


@click.group("info")
@click.pass_context
def info(ctx: click.Context) -> None:
    """
    Get information about YouTube videos, playlists, and channels.

    Examples:

        dml-stream info video <url>

        dml-stream info formats <url>

        dml-stream info thumbnail <url>

        dml-stream info subtitle <url>

        dml-stream info metadata <url>

        dml-stream info channel <url>
    """
    ctx.ensure_object(dict)
    ctx.obj['config'] = ctx.obj.get('config', Config())


@info.command("video")
@click.argument("url", required=True)
@click.option(
    "--json", "as_json",
    is_flag=True,
    help="Output as JSON"
)
@click.pass_context
def info_video(ctx: click.Context, url: str, as_json: bool) -> None:
    """
    Get detailed information about a YouTube video.

    Shows title, duration, views, channel, upload date, and description.

    URL: YouTube video URL

    Examples:

        dml-stream info video https://youtube.com/watch?v=...

        dml-stream info video <url> --json
    """
    try:
        service = DownloadService()
        yt = service.get_video_info(url)

        if as_json:
            data = {
                'title': yt.title,
                'url': url,
                'video_id': yt.video_id,
                'duration': yt.length,
                'duration_formatted': format_duration(yt.length) if yt.length else "Unknown",
                'views': yt.views,
                'author': yt.author,
                'publish_date': yt.publish_date.isoformat() if yt.publish_date else None,
                'description': yt.description[:500] + "..." if yt.description and len(yt.description) > 500 else yt.description,
                'thumbnail_url': yt.thumbnail_url,
            }
            console.print_json(json.dumps(data, indent=2))
        else:
            # Create info panel
            info_text = Text()
            info_text.append("Title: ", style="bold cyan")
            info_text.append(f"{yt.title}\n", style="bold white")
            info_text.append("\nVideo ID: ", style="bold cyan")
            info_text.append(f"{yt.video_id}\n", style="white")
            info_text.append("\nDuration: ", style="bold cyan")
            info_text.append(f"{format_duration(yt.length) if yt.length else 'Unknown'}\n", style="white")
            info_text.append("\nViews: ", style="bold cyan")
            info_text.append(f"{yt.views:,}\n", style="white")
            info_text.append("\nChannel: ", style="bold cyan")
            info_text.append(f"{yt.author}\n", style="white")
            info_text.append("\nUpload Date: ", style="bold cyan")
            info_text.append(f"{yt.publish_date.strftime('%Y-%m-%d') if yt.publish_date else 'Unknown'}\n", style="white")
            info_text.append("\nThumbnail: ", style="bold cyan")
            info_text.append(f"{yt.thumbnail_url}\n", style="dim white")

            if yt.description:
                info_text.append("\nDescription: ", style="bold cyan")
                desc = yt.description[:300] + "..." if len(yt.description) > 300 else yt.description
                info_text.append(f"{desc}\n", style="dim white")

            console.print(
                Panel(
                    info_text,
                    title="[bold blue]Video Information[/bold blue]",
                    border_style="blue"
                )
            )

        logger.info(f"Retrieved video info: {yt.title}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Failed to get video info: {str(e)}")
        raise SystemExit(1)


@info.command("formats")
@click.argument("url", required=True)
@click.option(
    "--type", "stream_type",
    type=click.Choice(['all', 'progressive', 'video', 'audio']),
    default='all',
    help="Filter by stream type"
)
@click.option(
    "--json", "as_json",
    is_flag=True,
    help="Output as JSON"
)
@click.pass_context
def info_formats(ctx: click.Context, url: str, stream_type: str, as_json: bool) -> None:
    """
    List all available download formats for a video.

    Shows quality, codec, filesize, and format ID for each stream.

    URL: YouTube video URL

    Examples:

        dml-stream info formats <url>

        dml-stream info formats <url> --type progressive

        dml-stream info formats <url> --json
    """
    try:
        service = DownloadService()
        yt = service.get_video_info(url)
        candidates = service.list_streams(yt)

        # Filter by type
        if stream_type != 'all':
            candidates = [c for c in candidates if c.type == stream_type]

        if not candidates:
            console.print("[yellow]No streams found[/yellow]")
            return

        if as_json:
            data = []
            for c in candidates:
                data.append({
                    'itag': c.itag,
                    'type': c.type,
                    'mime': c.mime,
                    'resolution': c.resolution,
                    'abr': c.abr,
                    'filesize': c.filesize,
                    'filesize_formatted': c.get_size_formatted(),
                })
            console.print_json(json.dumps(data, indent=2))
        else:
            table = Table(
                title=f"Available Formats for: {yt.title[:50]}...",
                show_header=True,
                header_style="bold magenta",
                border_style="blue"
            )

            table.add_column("ID", style="dim", width=6)
            table.add_column("Type", style="cyan")
            table.add_column("Quality", style="green")
            table.add_column("Codec", style="yellow")
            table.add_column("Audio", style="cyan")
            table.add_column("Size", style="white", justify="right")

            for c in candidates:
                # Extract codec from mime type
                codec = c.mime.split('/')[-1] if c.mime else 'unknown'

                table.add_row(
                    str(c.itag),
                    c.type.upper(),
                    c.resolution or 'N/A',
                    codec,
                    c.abr or 'N/A',
                    c.get_size_formatted()
                )

            console.print(table)
            console.print(f"\n[dim]Total: {len(candidates)} streams available[/dim]")

        logger.info(f"Listed {len(candidates)} formats for video: {yt.video_id}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Failed to list formats: {str(e)}")
        raise SystemExit(1)


@info.command("thumbnail")
@click.argument("url", required=True)
@click.option(
    "--download", "-d",
    is_flag=True,
    help="Download thumbnail to file"
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Output path for downloaded thumbnail"
)
@click.pass_context
def info_thumbnail(ctx: click.Context, url: str, download: bool, output: Optional[str]) -> None:
    """
    Preview or download video thumbnail.

    Shows thumbnail URL and optionally downloads it.

    URL: YouTube video URL

    Examples:

        dml-stream info thumbnail <url>

        dml-stream info thumbnail <url> --download

        dml-stream info thumbnail <url> -o thumb.jpg
    """
    try:
        service = DownloadService()
        yt = service.get_video_info(url)
        thumbnail_url = yt.thumbnail_url

        if download:
            import requests

            # Determine output path
            if not output:
                output = f"{yt.video_id}_thumbnail.jpg"

            console.print(f"[cyan]Downloading thumbnail...[/cyan]")

            response = requests.get(thumbnail_url, timeout=30)
            response.raise_for_status()

            with open(output, 'wb') as f:
                f.write(response.content)

            console.print(f"[bold green]✓[/bold green] Thumbnail saved to: [dim]{output}[/dim]")
            logger.info(f"Downloaded thumbnail to: {output}")
        else:
            # Show thumbnail info
            info_table = Table(title="Thumbnail Information", border_style="blue")
            info_table.add_column("Property", style="cyan")
            info_table.add_column("Value", style="white")

            info_table.add_row("Video", yt.title[:50] + "..." if len(yt.title) > 50 else yt.title)
            info_table.add_row("Video ID", yt.video_id)
            info_table.add_row("Thumbnail URL", thumbnail_url)

            console.print(info_table)

            # Show different resolution options
            resolutions = [
                ("Default", thumbnail_url),
                ("High Quality", thumbnail_url.replace("default", "hqdefault")),
                ("Medium Quality", thumbnail_url.replace("default", "mqdefault")),
                ("Standard Quality", thumbnail_url.replace("default", "sddefault")),
                ("Max Resolution", thumbnail_url.replace("default", "maxresdefault")),
            ]

            res_table = Table(title="Available Resolutions", border_style="blue")
            res_table.add_column("Quality", style="cyan")
            res_table.add_column("URL", style="dim white")

            for name, res_url in resolutions:
                res_table.add_row(name, res_url)

            console.print(res_table)

        logger.info(f"Retrieved thumbnail info for: {yt.video_id}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Failed to get thumbnail info: {str(e)}")
        raise SystemExit(1)


@info.command("subtitle")
@click.argument("url", required=True)
@click.option(
    "--json", "as_json",
    is_flag=True,
    help="Output as JSON"
)
@click.pass_context
def info_subtitle(ctx: click.Context, url: str, as_json: bool) -> None:
    """
    List available subtitle/caption languages.

    Shows all available subtitle tracks with language codes.

    URL: YouTube video URL

    Examples:

        dml-stream info subtitle <url>

        dml-stream info subtitle <url> --json
    """
    try:
        service = DownloadService()
        yt = service.get_video_info(url)

        # Get subtitle tracks
        subtitles = getattr(yt, 'captions', None)
        tracks = []

        if subtitles and hasattr(subtitles, '_caption_tracks'):
            for track in subtitles._caption_tracks:
                tracks.append({
                    'code': track.code,
                    'name': track.name,
                    'language': getattr(track, 'language', 'Unknown'),
                })

        if not tracks:
            console.print("[yellow]No subtitles available for this video[/yellow]")
            return

        if as_json:
            console.print_json(json.dumps(tracks, indent=2))
        else:
            table = Table(
                title=f"Available Subtitles for: {yt.title[:50]}...",
                border_style="blue"
            )

            table.add_column("Code", style="cyan")
            table.add_column("Language", style="green")
            table.add_column("Name", style="white")

            for track in tracks:
                table.add_row(
                    track['code'],
                    track['language'],
                    track['name']
                )

            console.print(table)
            console.print(f"\n[dim]Total: {len(tracks)} subtitle tracks available[/dim]")

        logger.info(f"Listed {len(tracks)} subtitle tracks for: {yt.video_id}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Failed to get subtitle info: {str(e)}")
        raise SystemExit(1)


@info.command("metadata")
@click.argument("url", required=True)
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Save metadata to file"
)
@click.option(
    "--format", "output_format",
    type=click.Choice(['json', 'table']),
    default='table',
    help="Output format"
)
@click.pass_context
def info_metadata(ctx: click.Context, url: str, output: Optional[str], output_format: str) -> None:
    """
    Get full metadata dump for a video.

    Shows complete video metadata in JSON or table format.

    URL: YouTube video URL

    Examples:

        dml-stream info metadata <url>

        dml-stream info metadata <url> --format json

        dml-stream info metadata <url> -o metadata.json
    """
    try:
        service = DownloadService()
        yt = service.get_video_info(url)

        # Build comprehensive metadata
        metadata = {
            'basic': {
                'title': yt.title,
                'video_id': yt.video_id,
                'url': url,
                'duration': yt.length,
                'duration_formatted': format_duration(yt.length) if yt.length else None,
            },
            'channel': {
                'author': yt.author,
                'channel_id': yt.channel_id,
                'channel_url': yt.channel_url,
            },
            'stats': {
                'views': yt.views,
                'rating': yt.rating,
            },
            'media': {
                'thumbnail_url': yt.thumbnail_url,
                'description': yt.description,
            },
            'technical': {
                'publish_date': yt.publish_date.isoformat() if yt.publish_date else None,
                'upload_date': getattr(yt, 'upload_date', None) or (yt.publish_date.strftime('%Y%m%d') if yt.publish_date else None),
                'age_restricted': getattr(yt, 'age_restricted', False),
                'is_live': getattr(yt, 'is_live', False),
                'is_live_content': getattr(yt, 'is_live_content', False),
                'keywords': getattr(yt, 'keywords', []),
                'categories': getattr(yt, 'categories', []),
            },
            'streams': {
                'progressive': len(list(yt.streams.filter(progressive=True))),
                'adaptive_video': len(list(yt.streams.filter(adaptive=True, only_video=True))),
                'adaptive_audio': len(list(yt.streams.filter(adaptive=True, only_audio=True))),
                'total': len(list(yt.streams)),
            }
        }

        if output_format == 'json' or output:
            json_str = json.dumps(metadata, indent=2, default=str)

            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(json_str)
                console.print(f"[bold green]✓[/bold green] Metadata saved to: [dim]{output}[/dim]")
            else:
                console.print_json(json_str)
        else:
            # Display as formatted tables
            sections = [
                ("Basic Information", metadata['basic']),
                ("Channel", metadata['channel']),
                ("Statistics", metadata['stats']),
                ("Technical Details", metadata['technical']),
                ("Stream Summary", metadata['streams']),
            ]

            for section_title, data in sections:
                table = Table(title=section_title, border_style="blue")
                table.add_column("Field", style="cyan")
                table.add_column("Value", style="white")

                for key, value in data.items():
                    if value is not None and value != []:
                        table.add_row(
                            key.replace('_', ' ').title(),
                            str(value)
                        )

                console.print(table)
                console.print()

            # Description panel
            if metadata['media']['description']:
                desc = metadata['media']['description']
                if len(desc) > 500:
                    desc = desc[:500] + "...\n\n[dim](truncated)[/dim]"

                console.print(
                    Panel(
                        desc,
                        title="[bold]Description[/bold]",
                        border_style="dim"
                    )
                )

        logger.info(f"Retrieved metadata for: {yt.video_id}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Failed to get metadata: {str(e)}")
        raise SystemExit(1)


@info.command("channel")
@click.argument("url", required=True)
@click.option(
    "--json", "as_json",
    is_flag=True,
    help="Output as JSON"
)
@click.pass_context
def info_channel(ctx: click.Context, url: str, as_json: bool) -> None:
    """
    Get channel information and statistics.

    Shows channel details, video count, and recent uploads.

    URL: YouTube channel URL or video URL (extracts channel)

    Examples:

        dml-stream info channel https://youtube.com/channel/...

        dml-stream info channel <video_url>

        dml-stream info channel <url> --json
    """
    try:
        service = DownloadService()
        yt = service.get_video_info(url)

        # Extract channel info
        channel_info = {
            'name': yt.author,
            'channel_id': yt.channel_id,
            'channel_url': yt.channel_url,
        }

        if as_json:
            console.print_json(json.dumps(channel_info, indent=2))
        else:
            info_table = Table(title="Channel Information", border_style="blue")
            info_table.add_column("Property", style="cyan")
            info_table.add_column("Value", style="white")

            info_table.add_row("Channel Name", channel_info['name'])
            info_table.add_row("Channel ID", channel_info['channel_id'])
            info_table.add_row("Channel URL", channel_info['channel_url'])

            console.print(info_table)

            console.print(
                Panel(
                    f"[dim]Note: Detailed channel statistics require channel URL directly.\n"
                    f"This shows info extracted from the video.[/dim]",
                    border_style="yellow"
                )
            )

        logger.info(f"Retrieved channel info: {channel_info['name']}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Failed to get channel info: {str(e)}")
        raise SystemExit(1)
