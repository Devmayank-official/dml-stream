"""
File operation commands for DML Stream.

This module provides file manipulation commands:
- convert: Format conversion via FFmpeg
- merge: Mux video and audio streams
- extract-audio: Extract audio from video
- compress: Reduce file size
"""

import logging
import os
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn
from rich.table import Table

from dml_stream.config.settings import Config
from dml_stream.services.conversion_service import ConversionService
from dml_stream.utilities.file_utils import format_file_size, get_file_info

logger = logging.getLogger(__name__)
console = Console()


@click.group("file-ops")
@click.pass_context
def file_ops(ctx: click.Context) -> None:
    """
    File operations for media conversion and manipulation.

    Examples:

        dml-stream file-ops convert <file> --to mp4

        dml-stream file-ops merge --video <file> --audio <file>

        dml-stream file-ops extract-audio <video-file>

        dml-stream file-ops compress <file> --quality medium
    """
    ctx.ensure_object(dict)
    ctx.obj['config'] = ctx.obj.get('config', Config())


@file_ops.command("convert")
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--to", "output_format",
    type=click.Choice(['mp4', 'mkv', 'avi', 'mov', 'webm', 'mp3', 'm4a', 'flac', 'wav', 'aac']),
    required=True,
    help="Target format"
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Output file path"
)
@click.option(
    "--quality",
    type=click.Choice(['low', 'medium', 'high', 'lossless']),
    default='high',
    help="Quality preset"
)
@click.option(
    "--video-codec",
    type=str,
    help="Video codec (e.g., h264, hevc)"
)
@click.option(
    "--audio-codec",
    type=str,
    help="Audio codec (e.g., aac, mp3)"
)
@click.pass_context
def convert(
    ctx: click.Context,
    input_file: str,
    output_format: str,
    output: Optional[str],
    quality: str,
    video_codec: Optional[str],
    audio_codec: Optional[str]
) -> None:
    """
    Convert a media file to a different format.

    Uses FFmpeg for format conversion with quality presets.

    INPUT_FILE: Path to input file

    Examples:

        dml-stream file-ops convert video.mkv --to mp4

        dml-stream file-ops convert video.mp4 --to mp3 --quality high

        dml-stream file-ops convert video.mov --to mp4 --quality lossless
    """
    try:
        service = ConversionService()

        # Check FFmpeg
        if not service.has_ffmpeg():
            console.print("[bold red]Error:[/bold red] FFmpeg is required for conversion")
            console.print("[dim]Install FFmpeg: https://ffmpeg.org/download.html[/dim]")
            raise SystemExit(1)

        # Show file info
        file_info = get_file_info(input_file)
        console.print(Panel.fit(
            f"[bold]Converting File[/bold]\n\n"
            f"[cyan]Input:[/cyan] {os.path.basename(input_file)}\n"
            f"[cyan]Size:[/cyan] {file_info.get('size_formatted', 'Unknown')}\n"
            f"[cyan]To:[/cyan] {output_format.upper()}\n"
            f"[cyan]Quality:[/cyan] {quality}"
        ))

        # Generate output path if not provided
        if not output:
            base, _ = os.path.splitext(input_file)
            output = f"{base}.{output_format}"

        console.print("[cyan]Starting conversion...[/cyan]")

        # Convert with progress simulation
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "•",
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Converting...", total=100)

            # Start conversion (blocking)
            import threading
            result = [None, None]  # [output_path, error]

            def convert_thread():
                try:
                    result[0] = service.convert(
                        input_path=input_file,
                        output_path=output,
                        output_format=output_format,
                        video_codec=video_codec,
                        audio_codec=audio_codec,
                        quality=quality
                    )
                except Exception as e:
                    result[1] = e

            thread = threading.Thread(target=convert_thread)
            thread.start()

            # Update progress
            import time
            elapsed = 0
            while thread.is_alive():
                progress.update(task, completed=min(elapsed * 10, 95))
                time.sleep(0.5)
                elapsed += 0.5

            thread.join()

            if result[1]:
                raise result[1]

            progress.update(task, completed=100)

        # Show result
        output_info = get_file_info(result[0])
        console.print(f"[bold green]✓ Conversion completed![/bold green]")
        console.print(f"[dim]Output: {result[0]}[/dim]")
        console.print(f"[dim]Size: {output_info.get('size_formatted', 'Unknown')}[/dim]")

        logger.info(f"Converted: {input_file} -> {result[0]} ({output_format})")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Conversion failed: {str(e)}")
        raise SystemExit(1)


@file_ops.command("merge")
@click.option(
    "--video", "-v",
    "video_file",
    type=click.Path(exists=True),
    required=True,
    help="Video file (no audio)"
)
@click.option(
    "--audio", "-a",
    "audio_file",
    type=click.Path(exists=True),
    required=True,
    help="Audio file"
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Output file path"
)
@click.option(
    "--format", "output_format",
    type=click.Choice(['mp4', 'mkv', 'avi']),
    default='mp4',
    help="Output format"
)
@click.pass_context
def merge(
    ctx: click.Context,
    video_file: str,
    audio_file: str,
    output: Optional[str],
    output_format: str
) -> None:
    """
    Merge separate video and audio files.

    Muxes video-only and audio-only streams into a single file.

    Examples:

        dml-stream file-ops merge --video video.mp4 --audio audio.m4a

        dml-stream file-ops merge -v video.mp4 -a audio.mp3 -o output.mkv
    """
    try:
        service = ConversionService()

        if not service.has_ffmpeg():
            console.print("[bold red]Error:[/bold red] FFmpeg is required")
            raise SystemExit(1)

        console.print(Panel.fit(
            f"[bold]Merging Audio + Video[/bold]\n\n"
            f"[cyan]Video:[/cyan] {os.path.basename(video_file)}\n"
            f"[cyan]Audio:[/cyan] {os.path.basename(audio_file)}\n"
            f"[cyan]Format:[/cyan] {output_format.upper()}"
        ))

        # Generate output path if not provided
        if not output:
            base, _ = os.path.splitext(video_file)
            output = f"{base}_merged.{output_format}"

        console.print("[cyan]Merging streams...[/cyan]")

        output_path = service.merge_audio_video(
            video_path=video_file,
            audio_path=audio_file,
            output_path=output,
            output_format=output_format
        )

        output_info = get_file_info(output_path)
        console.print(f"[bold green]✓ Merge completed![/bold green]")
        console.print(f"[dim]Output: {output_path}[/dim]")
        console.print(f"[dim]Size: {output_info.get('size_formatted', 'Unknown')}[/dim]")

        logger.info(f"Merged: {video_file} + {audio_file} -> {output_path}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Merge failed: {str(e)}")
        raise SystemExit(1)


@file_ops.command("extract-audio")
@click.argument("video_file", type=click.Path(exists=True))
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Output file path"
)
@click.option(
    "--format", "audio_format",
    type=click.Choice(['mp3', 'm4a', 'flac', 'wav', 'aac']),
    default='mp3',
    help="Output audio format"
)
@click.option(
    "--quality",
    type=click.Choice(['128k', '192k', '256k', '320k']),
    default='192k',
    help="Audio quality (bitrate)"
)
@click.pass_context
def extract_audio(
    ctx: click.Context,
    video_file: str,
    output: Optional[str],
    audio_format: str,
    quality: str
) -> None:
    """
    Extract audio from a video file.

    Strips audio track from video and saves as audio-only file.

    VIDEO_FILE: Path to video file

    Examples:

        dml-stream file-ops extract-audio video.mp4

        dml-stream file-ops extract-audio video.mkv --format flac --quality 320k
    """
    try:
        service = ConversionService()

        if not service.has_ffmpeg():
            console.print("[bold red]Error:[/bold red] FFmpeg is required")
            raise SystemExit(1)

        console.print(Panel.fit(
            f"[bold]Extracting Audio[/bold]\n\n"
            f"[cyan]Input:[/cyan] {os.path.basename(video_file)}\n"
            f"[cyan]Format:[/cyan] {audio_format.upper()}\n"
            f"[cyan]Quality:[/cyan] {quality}"
        ))

        # Generate output path if not provided
        if not output:
            base, _ = os.path.splitext(video_file)
            output = f"{base}.{audio_format}"

        console.print("[cyan]Extracting audio...[/cyan]")

        output_path = service.extract_audio(
            video_path=video_file,
            output_path=output,
            audio_format=audio_format,
            audio_quality=quality
        )

        output_info = get_file_info(output_path)
        console.print(f"[bold green]✓ Audio extracted![/bold green]")
        console.print(f"[dim]Output: {output_path}[/dim]")
        console.print(f"[dim]Size: {output_info.get('size_formatted', 'Unknown')}[/dim]")

        logger.info(f"Extracted audio: {video_file} -> {output_path}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Audio extraction failed: {str(e)}")
        raise SystemExit(1)


@file_ops.command("compress")
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Output file path"
)
@click.option(
    "--quality",
    type=click.Choice(['low', 'medium', 'high']),
    default='medium',
    help="Target quality"
)
@click.option(
    "--max-size",
    type=str,
    help="Maximum output size (e.g., 50MB, 100MB)"
)
@click.pass_context
def compress(
    ctx: click.Context,
    input_file: str,
    output: Optional[str],
    quality: str,
    max_size: Optional[str]
) -> None:
    """
    Compress a video file to reduce size.

    Uses FFmpeg to reduce file size while maintaining quality.

    INPUT_FILE: Path to video file

    Examples:

        dml-stream file-ops compress video.mp4 --quality medium

        dml-stream file-ops compress video.mkv --max-size 50MB
    """
    try:
        service = ConversionService()

        if not service.has_ffmpeg():
            console.print("[bold red]Error:[/bold red] FFmpeg is required")
            raise SystemExit(1)

        # Get input file size
        input_info = get_file_info(input_file)
        input_size = input_info.get('size', 0)

        console.print(Panel.fit(
            f"[bold]Compressing Video[/bold]\n\n"
            f"[cyan]Input:[/cyan] {os.path.basename(input_file)}\n"
            f"[cyan]Original Size:[/cyan] {input_info.get('size_formatted', 'Unknown')}\n"
            f"[cyan]Quality:[/cyan] {quality}"
        ))

        # Generate output path if not provided
        if not output:
            base, ext = os.path.splitext(input_file)
            output = f"{base}_compressed{ext}"

        console.print("[cyan]Compressing...[/cyan]")

        # Map quality to CRF values
        quality_map = {
            'low': '28',
            'medium': '23',
            'high': '18',
        }
        crf = quality_map.get(quality, '23')

        # Build FFmpeg command
        import subprocess
        cmd = [
            service.ffmpeg_path,
            '-y',
            '-i', input_file,
            '-c:v', 'libx264',
            '-crf', crf,
            '-c:a', 'aac',
            '-b:a', '128k',
            output
        ]

        logger.debug(f"Compress command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600
        )

        if result.returncode != 0:
            raise RuntimeError(f"Compression failed: {result.stderr}")

        # Show result
        output_info = get_file_info(output)
        output_size = output_info.get('size', 0)
        reduction = ((input_size - output_size) / input_size * 100) if input_size > 0 else 0

        summary = Table(title="Compression Results")
        summary.add_column("Metric", style="cyan")
        summary.add_column("Value", style="green")

        summary.add_row("Original Size", input_info.get('size_formatted', 'Unknown'))
        summary.add_row("Compressed Size", output_info.get('size_formatted', 'Unknown'))
        summary.add_row("Reduction", f"{reduction:.1f}%")

        console.print(summary)
        console.print(f"[bold green]✓ Compression completed![/bold green]")
        console.print(f"[dim]Output: {output}[/dim]")

        logger.info(f"Compressed: {input_file} -> {output} ({reduction:.1f}% reduction)")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Compression failed: {str(e)}")
        raise SystemExit(1)
