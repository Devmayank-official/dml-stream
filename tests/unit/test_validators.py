"""
Unit tests for validators.
"""

import unittest
from dml_stream.core.validators import (
    validate_youtube_url,
    validate_threads,
    validate_output_folder,
    validate_video_id,
    validate_download_speed,
)
from dml_stream.config.settings import Config


class TestValidateYouTubeUrl(unittest.TestCase):
    """Tests for validate_youtube_url function."""
    
    def test_valid_standard_url(self):
        """Test valid standard YouTube URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        is_valid, error = validate_youtube_url(url)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_valid_short_url(self):
        """Test valid youtu.be short URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        is_valid, error = validate_youtube_url(url)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_valid_playlist_url(self):
        """Test valid playlist URL."""
        url = "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        is_valid, error = validate_youtube_url(url)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_invalid_url(self):
        """Test invalid URL."""
        url = "https://example.com/video"
        is_valid, error = validate_youtube_url(url)
        self.assertFalse(is_valid)
        self.assertNotEqual(error, "")
    
    def test_empty_url(self):
        """Test empty URL."""
        is_valid, error = validate_youtube_url("")
        self.assertFalse(is_valid)
    
    def test_url_with_extra_params(self):
        """Test URL with additional parameters."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s&list=abc"
        is_valid, error = validate_youtube_url(url)
        self.assertTrue(is_valid)


class TestValidateThreads(unittest.TestCase):
    """Tests for validate_threads function."""
    
    def test_valid_threads(self):
        """Test valid thread count."""
        is_valid, error = validate_threads(4)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_min_threads(self):
        """Test minimum thread count."""
        is_valid, error = validate_threads(1)
        self.assertTrue(is_valid)
    
    def test_max_threads(self):
        """Test maximum thread count."""
        is_valid, error = validate_threads(12)
        self.assertTrue(is_valid)
    
    def test_too_few_threads(self):
        """Test too few threads."""
        is_valid, error = validate_threads(0)
        self.assertFalse(is_valid)
    
    def test_too_many_threads(self):
        """Test too many threads."""
        is_valid, error = validate_threads(20)
        self.assertFalse(is_valid)
    
    def test_invalid_type(self):
        """Test invalid type."""
        is_valid, error = validate_threads("4")
        self.assertFalse(is_valid)


class TestValidateOutputFolder(unittest.TestCase):
    """Tests for validate_output_folder function."""
    
    def test_valid_folder_path(self):
        """Test valid folder path."""
        import tempfile
        # Use existing temp directory
        is_valid, error = validate_output_folder(tempfile.gettempdir())
        self.assertTrue(is_valid, f"Should be valid: {error}")
    
    def test_create_new_folder_path(self):
        """Test creating new folder path."""
        import tempfile
        import os
        tmpdir = tempfile.mkdtemp()
        try:
            test_path = os.path.join(tmpdir, "new_folder")
            is_valid, error = validate_output_folder(test_path)
            self.assertTrue(is_valid, f"Should be valid: {error}")
        finally:
            os.rmdir(tmpdir)
    
    def test_invalid_characters(self):
        """Test path with invalid characters."""
        is_valid, error = validate_output_folder("downloads<invalid>")
        self.assertFalse(is_valid)
    
    def test_empty_path(self):
        """Test empty path."""
        is_valid, error = validate_output_folder("")
        self.assertFalse(is_valid)


class TestValidateVideoId(unittest.TestCase):
    """Tests for validate_video_id function."""
    
    def test_valid_video_id(self):
        """Test valid video ID."""
        video_id = "dQw4w9WgXcQ"
        is_valid, error = validate_video_id(video_id)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_invalid_length(self):
        """Test invalid length."""
        video_id = "short"
        is_valid, error = validate_video_id(video_id)
        self.assertFalse(is_valid)
    
    def test_invalid_characters(self):
        """Test invalid characters."""
        video_id = "dQw4w9WgXc!"
        is_valid, error = validate_video_id(video_id)
        self.assertFalse(is_valid)


class TestValidateDownloadSpeed(unittest.TestCase):
    """Tests for validate_download_speed function."""
    
    def test_valid_speed(self):
        """Test valid speed."""
        is_valid, error = validate_download_speed(102400)
        self.assertTrue(is_valid)
    
    def test_none_speed(self):
        """Test None speed (no limit)."""
        is_valid, error = validate_download_speed(None)
        self.assertTrue(is_valid)
    
    def test_zero_speed(self):
        """Test zero speed."""
        is_valid, error = validate_download_speed(0)
        self.assertFalse(is_valid)
    
    def test_negative_speed(self):
        """Test negative speed."""
        is_valid, error = validate_download_speed(-100)
        self.assertFalse(is_valid)


if __name__ == "__main__":
    unittest.main()
