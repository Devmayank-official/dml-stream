"""
Integration tests for YouTube Downloader.

These tests require network access and may take longer to run.
"""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from dml_stream.core.validators import validate_youtube_url
from dml_stream.services.download_service import DownloadService
from dml_stream.services.playlist_service import PlaylistService
from dml_stream.models.entities import DownloadProgress


class TestDownloadServiceIntegration(unittest.TestCase):
    """Integration tests for DownloadService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_output = tempfile.mkdtemp()
        self.service = DownloadService(output_folder=self.test_output)
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.test_output):
            shutil.rmtree(self.test_output)
    
    @unittest.skip("Requires network access - run manually")
    def test_get_video_info(self):
        """Test fetching video information."""
        # Using a well-known test video
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        yt = self.service.get_video_info(url)
        
        self.assertIsNotNone(yt)
        self.assertIsNotNone(yt.title)
        self.assertIsNotNone(yt.length)
    
    @unittest.skip("Requires network access - run manually")
    def test_list_streams(self):
        """Test listing available streams."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        yt = self.service.get_video_info(url)
        streams = self.service.list_streams(yt)
        
        self.assertGreater(len(streams), 0)
        
        # Check stream properties
        for stream in streams:
            self.assertIsNotNone(stream.itag)
            self.assertIn(stream.type, ['progressive', 'video', 'audio'])


class TestPlaylistServiceIntegration(unittest.TestCase):
    """Integration tests for PlaylistService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_output = tempfile.mkdtemp()
        self.service = PlaylistService(output_folder=self.test_output)
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.test_output):
            shutil.rmtree(self.test_output)
    
    @unittest.skip("Requires network access - run manually")
    def test_get_playlist_info(self):
        """Test fetching playlist information."""
        # Using a public test playlist
        url = "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        info = self.service.get_playlist_info(url)
        
        self.assertIsNotNone(info)
        self.assertIn('title', info)
        self.assertIn('video_count', info)
        self.assertGreater(info['video_count'], 0)
    
    @unittest.skip("Requires network access - run manually")
    def test_get_playlist_videos(self):
        """Test getting playlist video list."""
        url = "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        videos = self.service.get_playlist_videos(url)
        
        self.assertIsInstance(videos, list)
        self.assertGreater(len(videos), 0)
        
        # Check video properties
        for video in videos:
            self.assertIn('title', video)
            self.assertIn('url', video)


class TestDownloadProgress(unittest.TestCase):
    """Tests for DownloadProgress model."""
    
    def test_progress_calculation(self):
        """Test progress percentage calculation."""
        progress = DownloadProgress()
        progress.update(
            downloaded_bytes=500,
            total_bytes=1000,
            speed=100
        )
        
        self.assertEqual(progress.percentage, 50.0)
    
    def test_eta_calculation(self):
        """Test ETA calculation."""
        progress = DownloadProgress()
        progress.update(
            downloaded_bytes=500,
            total_bytes=1000,
            speed=100
        )
        
        # Remaining: 500 bytes at 100 bytes/s = 5 seconds
        self.assertEqual(progress.eta_seconds, 5.0)
    
    def test_is_complete(self):
        """Test completion check."""
        progress = DownloadProgress()
        progress.update(
            downloaded_bytes=1000,
            total_bytes=1000,
            speed=100
        )
        
        self.assertTrue(progress.is_complete)
    
    def test_speed_formatted(self):
        """Test speed formatting."""
        progress = DownloadProgress()
        progress.speed = 1048576  # 1 MB/s
        
        self.assertEqual(progress.speed_mb, 1.0)


class TestValidatorsIntegration(unittest.TestCase):
    """Integration tests for validators."""
    
    def test_various_youtube_urls(self):
        """Test various YouTube URL formats."""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
            "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
        ]
        
        for url in valid_urls:
            is_valid, error = validate_youtube_url(url)
            self.assertTrue(is_valid, f"URL should be valid: {url}")
    
    def test_invalid_urls(self):
        """Test invalid URLs."""
        invalid_urls = [
            "https://example.com/video",
            "not a url",
            "",
            "https://youtube.com",
        ]
        
        for url in invalid_urls:
            is_valid, error = validate_youtube_url(url)
            self.assertFalse(is_valid, f"URL should be invalid: {url}")


if __name__ == "__main__":
    unittest.main()
