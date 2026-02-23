"""
Media conversion service using FFmpeg.

This service handles format conversion for video and audio files
using FFmpeg with various quality and codec options.

Fully cross-platform compatible: Windows, macOS, Linux
"""

import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from dml_stream.core.constants import AUDIO_FORMATS, VIDEO_FORMATS
from dml_stream.core.exceptions import FFmpegNotFoundError
from dml_stream.utilities.platform_utils import find_ffmpeg

logger = logging.getLogger(__name__)


class ConversionService:
    """
    Service for media format conversion using FFmpeg.

    Provides methods for converting between different video and
    audio formats with configurable quality settings.
    
    Cross-platform FFmpeg detection and execution.
    """

    def __init__(self, ffmpeg_path: Optional[str] = None) -> None:
        """
        Initialize the conversion service.

        Args:
            ffmpeg_path: Optional custom path to FFmpeg executable.
        """
        # Use provided path, or auto-detect FFmpeg
        if ffmpeg_path:
            self.ffmpeg_path = ffmpeg_path
        else:
            detected = find_ffmpeg()
            self.ffmpeg_path = detected or "ffmpeg"

        self._ffmpeg_available: Optional[bool] = None

    def has_ffmpeg(self) -> bool:
        """
        Check if FFmpeg is available.

        Returns:
            True if FFmpeg is found in PATH or at custom path.
        """
        if self._ffmpeg_available is not None:
            return self._ffmpeg_available

        # Try shutil.which first (works on all platforms)
        if shutil.which(self.ffmpeg_path):
            self._ffmpeg_available = True
            return True

        # If not in PATH, check if it's a valid path
        if Path(self.ffmpeg_path).exists():
            self._ffmpeg_available = True
            return True

        self._ffmpeg_available = False
        return False

    def check_ffmpeg(self) -> None:
        """
        Check if FFmpeg is available and raise if not.

        Raises:
            FFmpegNotFoundError: If FFmpeg is not found.
        """
        if not self.has_ffmpeg():
            # Provide helpful platform-specific installation instructions
            import platform
            system = platform.system()

            if system == 'Windows':
                hint = "Install with: choco install ffmpeg (Chocolatey) or scoop install ffmpeg"
            elif system == 'Darwin':
                hint = "Install with: brew install ffmpeg"
            else:
                hint = "Install with: sudo apt install ffmpeg (Ubuntu) or sudo dnf install ffmpeg (Fedora)"

            raise FFmpegNotFoundError(
                f"FFmpeg not found. {hint}"
            )

    def get_ffmpeg_version(self) -> Optional[str]:
        """
        Get FFmpeg version string.
        
        Returns:
            FFmpeg version or None if not available.
        """
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.split('\n')[0]
        except Exception:
            pass
        return None

    def get_supported_formats(self) -> Dict[str, List[str]]:
        """
        Get list of supported formats from FFmpeg.
        
        Returns:
            Dictionary with 'video' and 'audio' format lists.
        """
        if not self.has_ffmpeg():
            return {'video': VIDEO_FORMATS, 'audio': AUDIO_FORMATS}

        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-formats"],
                capture_output=True,
                text=True,
                timeout=10
            )

            video_formats = []
            audio_formats = []

            for line in result.stdout.split('\n'):
                if line.startswith(' '):
                    parts = line.split()
                    if len(parts) >= 2:
                        fmt = parts[0]
                        desc = ' '.join(parts[1:]).lower()

                        if 'video' in desc or 'muxer' in desc:
                            video_formats.append(fmt)
                        elif 'audio' in desc or 'muxer' in desc:
                            audio_formats.append(fmt)

            return {
                'video': list(set(video_formats + VIDEO_FORMATS)),
                'audio': list(set(audio_formats + AUDIO_FORMATS))
            }
        except Exception:
            return {'video': VIDEO_FORMATS, 'audio': AUDIO_FORMATS}

    def convert(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        output_format: Optional[str] = None,
        video_codec: Optional[str] = None,
        audio_codec: Optional[str] = None,
        quality: str = "high",
        overwrite: bool = True
    ) -> str:
        """
        Convert a media file to a different format.
        
        Args:
            input_path: Path to input file.
            output_path: Path to output file (auto-generated if None).
            output_format: Target format extension (e.g., 'mp4', 'mp3').
            video_codec: Video codec to use (e.g., 'h264', 'hevc').
            audio_codec: Audio codec to use (e.g., 'aac', 'mp3').
            quality: Quality preset ('low', 'medium', 'high', 'lossless').
            overwrite: Whether to overwrite existing output file.
            
        Returns:
            Path to converted file.
            
        Raises:
            FFmpegNotFoundError: If FFmpeg is not available.
            RuntimeError: If conversion fails.
        """
        self.check_ffmpeg()

        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Determine output path and format
        if output_format:
            output_format = output_format.lstrip('.')
        else:
            output_format = os.path.splitext(output_path or input_path)[1].lstrip('.')

        if not output_path:
            base, _ = os.path.splitext(input_path)
            output_path = f"{base}.{output_format}"

        # Build FFmpeg command
        cmd = [self.ffmpeg_path, "-y" if overwrite else "-n"]

        # Input file
        cmd.extend(["-i", input_path])

        # Quality presets
        if quality == "lossless":
            if output_format in ['mp4', 'mkv', 'avi']:
                cmd.extend(["-crf", "0"])
            elif output_format in ['mp3', 'aac', 'm4a']:
                cmd.extend(["-q:a", "0"])
        elif quality == "high":
            if output_format in ['mp4', 'mkv', 'avi']:
                cmd.extend(["-crf", "18"])
            elif output_format in ['mp3', 'aac', 'm4a']:
                cmd.extend(["-q:a", "2"])
        elif quality == "medium":
            if output_format in ['mp4', 'mkv', 'avi']:
                cmd.extend(["-crf", "23"])
            elif output_format in ['mp3', 'aac', 'm4a']:
                cmd.extend(["-q:a", "4"])
        elif quality == "low":
            if output_format in ['mp4', 'mkv', 'avi']:
                cmd.extend(["-crf", "28"])
            elif output_format in ['mp3', 'aac', 'm4a']:
                cmd.extend(["-q:a", "6"])

        # Video codec
        if video_codec:
            cmd.extend(["-c:v", video_codec])
        elif output_format in ['mp4', 'mkv']:
            cmd.extend(["-c:v", "libx264"])

        # Audio codec
        if audio_codec:
            cmd.extend(["-c:a", audio_codec])
        elif output_format in ['mp3']:
            cmd.extend(["-c:a", "libmp3lame", "-b:a", "192k"])
        elif output_format in ['aac', 'm4a']:
            cmd.extend(["-c:a", "aac", "-b:a", "192k"])
        elif output_format in ['flac']:
            cmd.extend(["-c:a", "flac"])
        elif output_format in ['opus']:
            cmd.extend(["-c:a", "libopus", "-b:a", "192k"])

        # Output file
        cmd.append(output_path)

        logger.info(f"Converting: {input_path} -> {output_path}")
        logger.debug(f"FFmpeg command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            if result.returncode != 0:
                error_msg = result.stderr or "Unknown conversion error"
                raise RuntimeError(f"FFmpeg conversion failed: {error_msg}")

            if not os.path.exists(output_path):
                raise RuntimeError("Conversion completed but output file not found")

            logger.info(f"Conversion completed: {output_path}")
            return output_path

        except subprocess.TimeoutExpired:
            raise RuntimeError("FFmpeg conversion timed out")
        except Exception as e:
            if isinstance(e, (FileNotFoundError, RuntimeError)):
                raise
            raise RuntimeError(f"Conversion failed: {str(e)}")

    def extract_audio(
        self,
        video_path: str,
        output_path: Optional[str] = None,
        audio_format: str = "mp3",
        audio_quality: str = "192k"
    ) -> str:
        """
        Extract audio from a video file.
        
        Args:
            video_path: Path to video file.
            output_path: Path to output audio file.
            audio_format: Output audio format.
            audio_quality: Audio bitrate (e.g., '128k', '192k', '320k').
            
        Returns:
            Path to extracted audio file.
        """
        self.check_ffmpeg()

        if not output_path:
            base, _ = os.path.splitext(video_path)
            output_path = f"{base}.{audio_format}"

        cmd = [
            self.ffmpeg_path,
            "-y",
            "-i", video_path,
            "-vn",  # No video
            "-acodec", "libmp3lame" if audio_format == "mp3" else audio_format,
            "-ab", audio_quality,
            output_path
        ]

        logger.info(f"Extracting audio: {video_path} -> {output_path}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode != 0:
                raise RuntimeError(f"Audio extraction failed: {result.stderr}")

            return output_path

        except subprocess.TimeoutExpired:
            raise RuntimeError("Audio extraction timed out")

    def merge_audio_video(
        self,
        video_path: str,
        audio_path: str,
        output_path: Optional[str] = None,
        output_format: str = "mp4"
    ) -> str:
        """
        Merge separate video and audio files.
        
        Args:
            video_path: Path to video file (no audio).
            audio_path: Path to audio file.
            output_path: Path to output file.
            output_format: Output format.
            
        Returns:
            Path to merged file.
        """
        self.check_ffmpeg()

        if not output_path:
            base, _ = os.path.splitext(video_path)
            output_path = f"{base}_merged.{output_format}"

        cmd = [
            self.ffmpeg_path,
            "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_path
        ]

        logger.info(f"Merging audio+video: {output_path}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode != 0:
                raise RuntimeError(f"Merge failed: {result.stderr}")

            return output_path

        except subprocess.TimeoutExpired:
            raise RuntimeError("Merge timed out")

    def get_media_info(self, file_path: str) -> dict:
        """
        Get media file information using FFprobe.
        
        Args:
            file_path: Path to media file.
            
        Returns:
            Dictionary with media information.
        """
        ffprobe_path = shutil.which("ffprobe") or self.ffmpeg_path.replace("ffmpeg", "ffprobe")

        if not shutil.which(ffprobe_path):
            return {"error": "ffprobe not found"}

        cmd = [
            ffprobe_path,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            file_path
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
        except Exception as e:
            logger.error(f"Failed to get media info: {str(e)}")

        return {"error": str(e)}
