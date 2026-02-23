"""
Playlist download service.

This service handles downloading entire YouTube playlists with
progress tracking and error handling for individual videos.
"""

import logging
import os
from typing import Callable, Dict, List, Optional

from pytubefix import Playlist

from dml_stream.core.constants import (
    DOWNLOAD_TYPE_AUDIO,
    DOWNLOAD_TYPE_VIDEO,
)
from dml_stream.models.entities import DownloadProgress
from dml_stream.services.download_service import DownloadService
from dml_stream.utilities.file_utils import ensure_dir, safe_filename

logger = logging.getLogger(__name__)


class PlaylistService:
    """
    Service for downloading YouTube playlists.
    
    Provides methods for downloading all videos from a playlist
    with configurable options for each video.
    """

    def __init__(
        self,
        output_folder: str = "downloads",
        threads: int = 4,
        max_speed: Optional[float] = None,
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None
    ) -> None:
        """
        Initialize the playlist service.
        
        Args:
            output_folder: Base output folder for downloads.
            threads: Number of threads for downloads.
            max_speed: Maximum download speed in bytes/second.
            progress_callback: Callback for progress updates.
        """
        self.output_folder = output_folder
        self.threads = threads
        self.max_speed = max_speed
        self.progress_callback = progress_callback
        self._cancel_flag = False

    def cancel(self) -> None:
        """Cancel current playlist download."""
        self._cancel_flag = True

    def reset(self) -> None:
        """Reset cancellation flag."""
        self._cancel_flag = False

    def get_playlist_info(self, url: str) -> Dict:
        """
        Get playlist information.
        
        Args:
            url: YouTube playlist URL.
            
        Returns:
            Dictionary with playlist information.
            
        Raises:
            ValueError: If URL is not a valid playlist.
        """
        try:
            playlist = Playlist(url)

            return {
                'title': playlist.title,
                'url': url,
                'video_count': len(playlist.video_urls),
                'videos': playlist.video_urls,
                'description': getattr(playlist, 'description', ''),
            }
        except Exception as e:
            raise ValueError(f"Failed to get playlist info: {str(e)}")

    def download_playlist(
        self,
        url: str,
        output_folder: Optional[str] = None,
        download_type: str = DOWNLOAD_TYPE_VIDEO,
        method: str = "normal",
        output_format: Optional[str] = None,
        skip_existing: bool = True
    ) -> Dict:
        """
        Download all videos from a playlist.
        
        Args:
            url: YouTube playlist URL.
            output_folder: Output folder for downloads.
            download_type: 'video' or 'audio'.
            method: Download method ('normal' or 'fast').
            output_format: Optional output format for conversion.
            skip_existing: Skip videos that already exist.
            
        Returns:
            Dictionary with download results.
            
        Raises:
            ValueError: If URL is not a valid playlist.
        """
        self.reset()

        try:
            playlist = Playlist(url)
        except Exception as e:
            raise ValueError(f"Invalid playlist URL: {str(e)}")

        # Setup output folder
        playlist_name = safe_filename(playlist.title or "Playlist")
        base_folder = output_folder or self.output_folder

        if download_type == DOWNLOAD_TYPE_AUDIO:
            folder = os.path.join(base_folder, "playlists", playlist_name, "audio")
        else:
            folder = os.path.join(base_folder, "playlists", playlist_name, "videos")

        ensure_dir(folder)

        # Track results
        results = {
            'playlist_title': playlist.title,
            'playlist_url': url,
            'total_videos': len(playlist.video_urls),
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'errors': [],
            'files': []
        }

        logger.info(f"Starting playlist download: {playlist.title}")
        logger.info(f"Total videos: {len(playlist.video_urls)}")

        # Download each video
        download_service = DownloadService(
            output_folder=folder,
            threads=self.threads,
            max_speed=self.max_speed,
            progress_callback=self.progress_callback
        )

        for i, video_url in enumerate(playlist.video_urls):
            if self._cancel_flag:
                logger.info("Playlist download cancelled by user")
                break

            try:
                logger.info(f"Downloading video {i+1}/{len(playlist.video_urls)}")

                # Get video info
                yt = playlist.videos[i]
                filename = safe_filename(yt.title)

                # Check if already exists
                if skip_existing:
                    existing_file = self._find_existing_file(folder, filename, output_format)
                    if existing_file:
                        logger.info(f"Skipping (already exists): {yt.title}")
                        results['skipped'] += 1
                        results['files'].append({
                            'title': yt.title,
                            'url': video_url,
                            'path': existing_file,
                            'status': 'skipped'
                        })
                        continue

                # Download video or audio
                if download_type == DOWNLOAD_TYPE_AUDIO:
                    file_path = download_service.download_audio(
                        yt,
                        output_folder=folder,
                        output_format=output_format,
                        method=method
                    )
                else:
                    file_path = download_service.download_video(
                        yt,
                        output_folder=folder,
                        output_format=output_format,
                        method=method
                    )

                results['successful'] += 1
                results['files'].append({
                    'title': yt.title,
                    'url': video_url,
                    'path': file_path,
                    'status': 'success'
                })

                logger.info(f"Successfully downloaded: {yt.title}")

            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'url': video_url,
                    'error': str(e)
                })
                logger.error(f"Failed to download {video_url}: {str(e)}")

        # Log summary
        logger.info("Playlist download completed")
        logger.info(f"Successful: {results['successful']}")
        logger.info(f"Failed: {results['failed']}")
        logger.info(f"Skipped: {results['skipped']}")

        return results

    def _find_existing_file(
        self,
        folder: str,
        filename: str,
        output_format: Optional[str] = None
    ) -> Optional[str]:
        """
        Check if a file already exists in the folder.
        
        Args:
            folder: Folder to search.
            filename: Base filename.
            output_format: Expected format extension.
            
        Returns:
            Path to existing file or None.
        """
        if output_format:
            path = os.path.join(folder, f"{filename}.{output_format}")
            if os.path.exists(path):
                return path

        # Check common formats
        for ext in ['mp4', 'mkv', 'webm', 'mp3', 'm4a', 'wav']:
            path = os.path.join(folder, f"{filename}.{ext}")
            if os.path.exists(path):
                return path

        return None

    def download_playlist_parallel(
        self,
        url: str,
        output_folder: Optional[str] = None,
        download_type: str = DOWNLOAD_TYPE_VIDEO,
        max_concurrent: int = 3,
        method: str = "normal",
        output_format: Optional[str] = None
    ) -> Dict:
        """
        Download playlist with parallel downloads.
        
        Note: This is a placeholder for future implementation.
        Currently downloads sequentially to avoid rate limiting.
        
        Args:
            url: YouTube playlist URL.
            output_folder: Output folder.
            download_type: 'video' or 'audio'.
            max_concurrent: Maximum concurrent downloads.
            method: Download method.
            output_format: Output format.
            
        Returns:
            Dictionary with download results.
        """
        # For now, just use sequential download
        # Parallel downloads could trigger rate limiting
        logger.warning("Parallel playlist download not yet implemented, using sequential")
        return self.download_playlist(
            url=url,
            output_folder=output_folder,
            download_type=download_type,
            method=method,
            output_format=output_format
        )

    def get_playlist_videos(self, url: str) -> List[Dict]:
        """
        Get list of videos in a playlist.
        
        Args:
            url: YouTube playlist URL.
            
        Returns:
            List of video information dictionaries.
        """
        try:
            playlist = Playlist(url)
            videos = []

            for video in playlist.videos:
                videos.append({
                    'title': video.title,
                    'url': video.watch_url,
                    'video_id': video.video_id,
                    'length': video.length,
                    'thumbnail': video.thumbnail_url,
                })

            return videos

        except Exception as e:
            logger.error(f"Failed to get playlist videos: {str(e)}")
            return []
