"""
Download service for YouTube videos and audio.

This service handles all download operations including:
- Single video downloads
- Audio extraction
- Multi-threaded downloads
- Speed limiting
- Resume capability
"""

import logging
import os
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import requests
from pytubefix import YouTube

from dml_stream.core.constants import (
    CHUNK_SIZE,
    TIMEOUT_SECONDS,
    DEFAULT_HEADERS,
    DOWNLOAD_CHUNK_SIZE,
    MIN_RESUME_SIZE,
)
from dml_stream.core.exceptions import (
    DownloadError,
    FFmpegNotFoundError,
    NoStreamsFoundError,
)
from dml_stream.core.validators import validate_youtube_url
from dml_stream.models.entities import DownloadProgress, StreamCandidate
from dml_stream.utilities.file_utils import safe_filename, ensure_dir

logger = logging.getLogger(__name__)


class DownloadService:
    """
    Service for handling YouTube video and audio downloads.
    
    Provides methods for downloading content with various options
    including quality selection, format conversion, and speed limiting.
    """
    
    def __init__(
        self,
        output_folder: str = "downloads",
        threads: int = 4,
        max_speed: Optional[float] = None,
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None
    ) -> None:
        """
        Initialize the download service.
        
        Args:
            output_folder: Default output folder for downloads.
            threads: Number of threads for multi-threaded downloads.
            max_speed: Maximum download speed in bytes/second (None for unlimited).
            progress_callback: Optional callback for progress updates.
        """
        self.output_folder = output_folder
        self.threads = max(1, min(threads, 12))  # Clamp between 1-12
        self.max_speed = max_speed
        self.progress_callback = progress_callback
        self._cancel_flag = threading.Event()
    
    def cancel(self) -> None:
        """Cancel current download operation."""
        self._cancel_flag.set()
    
    def _check_cancelled(self) -> None:
        """Check if download was cancelled and raise if so."""
        if self._cancel_flag.is_set():
            raise DownloadError("Download cancelled by user", retryable=False)
    
    def get_video_info(self, url: str) -> YouTube:
        """
        Get YouTube video information.
        
        Args:
            url: YouTube video URL.
            
        Returns:
            YouTube object with video information.
            
        Raises:
            InvalidURLError: If URL is invalid.
        """
        is_valid, error_msg = validate_youtube_url(url)
        if not is_valid:
            from dml_stream.core.exceptions import InvalidURLError
            raise InvalidURLError(url, error_msg)
        
        return YouTube(url)
    
    def list_streams(self, yt: YouTube) -> List[StreamCandidate]:
        """
        List all available stream options for a video.
        
        Args:
            yt: YouTube object.
            
        Returns:
            List of stream candidates.
        """
        streams = yt.streams
        candidates: List[StreamCandidate] = []
        
        # Progressive streams (video + audio combined)
        for s in streams.filter(progressive=True).order_by('resolution').desc():
            candidates.append(StreamCandidate(
                itag=s.itag,
                type='progressive',
                mime=s.mime_type,
                resolution=getattr(s, 'resolution', None),
                abr=getattr(s, 'abr', None),
                filesize=getattr(s, 'filesize', 0) or 0,
                stream=s
            ))
        
        # Adaptive video-only streams
        for s in streams.filter(adaptive=True, only_video=True).order_by('resolution').desc():
            candidates.append(StreamCandidate(
                itag=s.itag,
                type='video',
                mime=s.mime_type,
                resolution=getattr(s, 'resolution', None),
                abr=None,
                filesize=getattr(s, 'filesize', 0) or 0,
                stream=s
            ))
        
        # Adaptive audio-only streams
        for s in streams.filter(adaptive=True, only_audio=True).order_by('abr').desc():
            candidates.append(StreamCandidate(
                itag=s.itag,
                type='audio',
                mime=s.mime_type,
                resolution=None,
                abr=getattr(s, 'abr', None),
                filesize=getattr(s, 'filesize', 0) or 0,
                stream=s
            ))
        
        return candidates
    
    def download_stream(
        self,
        url: str,
        out_path: str,
        desc: Optional[str] = None,
        max_speed: Optional[float] = None,
        resume: bool = True
    ) -> str:
        """
        Download a file using a single stream with progress tracking.
        
        Args:
            url: URL to download from.
            out_path: Output path for the downloaded file.
            desc: Description for progress display.
            max_speed: Maximum download speed in bytes/second.
            resume: Whether to resume partial downloads.
            
        Returns:
            Path to the downloaded file.
            
        Raises:
            DownloadError: If download fails.
        """
        speed = max_speed or self.max_speed
        
        try:
            # Check for existing partial download
            total = 0
            start_pos = 0
            headers = {}
            mode = 'wb'
            
            if resume and os.path.exists(out_path):
                file_size = os.path.getsize(out_path)
                if file_size >= MIN_RESUME_SIZE:
                    # Get total size from server
                    response = requests.head(url, headers=DEFAULT_HEADERS, timeout=TIMEOUT_SECONDS)
                    total = int(response.headers.get('Content-Length', 0))
                    
                    if file_size < total:
                        start_pos = file_size
                        headers = {"Range": f"bytes={file_size}-"}
                        mode = 'ab'
                        logger.info(f"Resuming download from byte {file_size}")
                    else:
                        logger.info(f"File already complete: {out_path}")
                        return out_path
            
            # Get total size if not already known
            if not total:
                response = requests.head(url, headers=DEFAULT_HEADERS, timeout=TIMEOUT_SECONDS)
                total = int(response.headers.get('Content-Length', 0))
            
            # Download with progress tracking
            downloaded = start_pos
            last_update = time.time()
            speed_samples: List[float] = []
            
            with requests.get(url, stream=True, timeout=TIMEOUT_SECONDS, headers=headers) as r:
                r.raise_for_status()
                
                with open(out_path, mode) as f:
                    for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                        self._check_cancelled()
                        
                        if not chunk:
                            continue
                        
                        chunk_start = time.time()
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Calculate speed
                        elapsed = time.time() - chunk_start
                        if elapsed > 0:
                            instant_speed = len(chunk) / elapsed
                            speed_samples.append(instant_speed)
                            if len(speed_samples) > 10:
                                speed_samples.pop(0)
                            avg_speed = sum(speed_samples) / len(speed_samples)
                        else:
                            avg_speed = 0
                        
                        # Update progress
                        percentage = (downloaded / total * 100) if total > 0 else 0
                        eta = (total - downloaded) / avg_speed if avg_speed > 0 else 0
                        
                        progress = DownloadProgress(
                            total_bytes=total,
                            downloaded_bytes=downloaded,
                            speed=avg_speed,
                            eta_seconds=eta,
                            percentage=percentage,
                            status="downloading"
                        )
                        
                        if self.progress_callback:
                            self.progress_callback(progress)
                        
                        # Speed limiting
                        if speed:
                            expected_time = len(chunk) / speed
                            actual_time = time.time() - chunk_start
                            if actual_time < expected_time:
                                time.sleep(expected_time - actual_time)
            
            logger.info(f"Download completed: {out_path}")
            return out_path
            
        except requests.exceptions.Timeout as e:
            raise DownloadError(f"Download timeout: {str(e)}", url)
        except requests.exceptions.RequestException as e:
            raise DownloadError(f"Download failed: {str(e)}", url)
        except OSError as e:
            raise DownloadError(f"File system error: {str(e)}", url)
    
    def download_chunked(
        self,
        url: str,
        out_path: str,
        num_threads: int = 4,
        desc: Optional[str] = None,
        max_speed: Optional[float] = None
    ) -> str:
        """
        Download a file using multiple threads for faster speeds.
        
        Args:
            url: URL to download from.
            out_path: Output path.
            num_threads: Number of download threads.
            desc: Description for progress display.
            max_speed: Maximum download speed per thread.
            
        Returns:
            Path to downloaded file.
            
        Raises:
            DownloadError: If download fails.
        """
        speed = max_speed or self.max_speed
        
        try:
            # Get file size
            response = requests.head(url, headers=DEFAULT_HEADERS, timeout=TIMEOUT_SECONDS)
            total_size = int(response.headers.get('Content-Length', 0))
            
            if total_size == 0:
                # Fall back to single-threaded download
                logger.warning("Content-Length not available, using single-threaded download")
                return self.download_stream(url, out_path, desc, speed)
            
            # Check for existing file
            if os.path.exists(out_path):
                file_size = os.path.getsize(out_path)
                if file_size >= total_size:
                    logger.info(f"File already complete: {out_path}")
                    return out_path
            
            # Calculate chunk ranges
            chunk_size = total_size // num_threads
            chunks = []
            for i in range(num_threads):
                start = i * chunk_size
                end = total_size if i == num_threads - 1 else (i + 1) * chunk_size - 1
                chunks.append((start, end))
            
            # Create temporary directory for chunks
            temp_dir = f"{out_path}.parts"
            ensure_dir(temp_dir)
            
            # Download chunks in parallel
            downloaded_chunks: Dict[int, int] = {}
            lock = threading.Lock()
            errors: List[Exception] = []
            
            def download_chunk(chunk_idx: int, start: int, end: int) -> None:
                try:
                    self._check_cancelled()
                    
                    chunk_path = os.path.join(temp_dir, f"chunk_{chunk_idx:04d}")
                    headers = {"Range": f"bytes={start}-{end}"}
                    
                    response = requests.get(url, stream=True, headers=headers, timeout=TIMEOUT_SECONDS)
                    response.raise_for_status()
                    
                    chunk_downloaded = 0
                    with open(chunk_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                            self._check_cancelled()
                            if chunk:
                                f.write(chunk)
                                chunk_downloaded += len(chunk)
                    
                    with lock:
                        downloaded_chunks[chunk_idx] = chunk_downloaded
                        self._update_chunk_progress(downloaded_chunks, total_size)
                        
                except Exception as e:
                    with lock:
                        errors.append(e)
            
            threads = []
            for i, (start, end) in enumerate(chunks):
                t = threading.Thread(target=download_chunk, args=(i, start, end))
                threads.append(t)
                t.start()
            
            # Wait for all threads
            for t in threads:
                t.join()
            
            # Check for errors
            if errors:
                raise errors[0]
            
            # Merge chunks
            with open(out_path, 'wb') as outfile:
                for i in range(num_threads):
                    chunk_path = os.path.join(temp_dir, f"chunk_{i:04d}")
                    with open(chunk_path, 'rb') as infile:
                        outfile.write(infile.read())
            
            # Cleanup temp directory
            shutil.rmtree(temp_dir)
            
            logger.info(f"Chunked download completed: {out_path}")
            return out_path
            
        except Exception as e:
            if isinstance(e, DownloadError):
                raise
            raise DownloadError(f"Chunked download failed: {str(e)}", url)
    
    def _update_chunk_progress(self, downloaded_chunks: Dict[int, int], total_size: int) -> None:
        """Update progress during chunked download."""
        total_downloaded = sum(downloaded_chunks.values())
        percentage = (total_downloaded / total_size * 100) if total_size > 0 else 0
        
        progress = DownloadProgress(
            total_bytes=total_size,
            downloaded_bytes=total_downloaded,
            speed=0,  # Would need more complex tracking for multi-threaded
            eta_seconds=0,
            percentage=percentage,
            status="downloading"
        )
        
        if self.progress_callback:
            self.progress_callback(progress)
    
    def download_video(
        self,
        yt: YouTube,
        output_folder: Optional[str] = None,
        stream_candidate: Optional[StreamCandidate] = None,
        output_format: Optional[str] = None,
        method: str = "normal"
    ) -> str:
        """
        Download a video with optional audio merge.
        
        Args:
            yt: YouTube object.
            output_folder: Output folder (uses default if None).
            stream_candidate: Selected stream candidate.
            output_format: Optional output format for conversion.
            method: Download method ('normal' or 'fast').
            
        Returns:
            Path to downloaded video file.
        """
        folder = output_folder or os.path.join(self.output_folder, "videos")
        ensure_dir(folder)
        
        # Auto-select best stream if not provided
        if not stream_candidate:
            candidates = self.list_streams(yt)
            # Prefer 720p progressive
            for c in candidates:
                if c.type == 'progressive' and c.resolution and '720' in c.resolution:
                    stream_candidate = c
                    break
            if not stream_candidate:
                stream_candidate = candidates[0] if candidates else None
        
        if not stream_candidate:
            raise NoStreamsFoundError("No video streams available")
        
        # Download the stream
        filename = safe_filename(yt.title)
        ext = stream_candidate.stream.subtype or 'mp4'
        out_path = os.path.join(folder, f"{filename}.{ext}")
        
        url = stream_candidate.stream.url
        
        if method == "fast" and self.threads > 1:
            self.download_chunked(url, out_path, num_threads=self.threads, desc=yt.title)
        else:
            self.download_stream(url, out_path, desc=yt.title)
        
        # Convert format if requested
        if output_format and output_format != ext:
            from dml_stream.services.conversion_service import ConversionService
            converter = ConversionService()
            converted_path = os.path.join(folder, f"{filename}.{output_format}")
            out_path = converter.convert(out_path, converted_path, output_format)
        
        return out_path
    
    def download_audio(
        self,
        yt: YouTube,
        output_folder: Optional[str] = None,
        stream_candidate: Optional[StreamCandidate] = None,
        output_format: Optional[str] = None,
        method: str = "normal"
    ) -> str:
        """
        Download audio from a video.
        
        Args:
            yt: YouTube object.
            output_folder: Output folder.
            stream_candidate: Selected audio stream.
            output_format: Output format (default: mp3).
            method: Download method.
            
        Returns:
            Path to downloaded audio file.
        """
        folder = output_folder or os.path.join(self.output_folder, "audio")
        ensure_dir(folder)
        
        # Auto-select best audio stream if not provided
        if not stream_candidate:
            candidates = self.list_streams(yt)
            audio_candidates = [c for c in candidates if c.type == 'audio']
            if audio_candidates:
                stream_candidate = audio_candidates[0]  # Highest bitrate
            else:
                # Fall back to progressive with audio
                progressive = [c for c in candidates if c.type == 'progressive']
                if progressive:
                    stream_candidate = progressive[0]
        
        if not stream_candidate:
            raise NoStreamsFoundError("No audio streams available")
        
        # Download the stream
        filename = safe_filename(yt.title)
        ext = stream_candidate.stream.subtype or 'mp4'
        out_path = os.path.join(folder, f"{filename}.{ext}")
        
        url = stream_candidate.stream.url
        
        if method == "fast" and self.threads > 1:
            self.download_chunked(url, out_path, num_threads=self.threads, desc=f"🎵 {yt.title}")
        else:
            self.download_stream(url, out_path, desc=f"🎵 {yt.title}")
        
        # Convert format if requested
        target_format = output_format or 'mp3'
        if target_format and target_format != ext:
            from dml_stream.services.conversion_service import ConversionService
            converter = ConversionService()
            converted_path = os.path.join(folder, f"{filename}.{target_format}")
            out_path = converter.convert(out_path, converted_path, target_format)
        
        return out_path
