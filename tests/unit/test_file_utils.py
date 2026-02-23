"""
Unit tests for file utilities.
"""

import os
import tempfile
import unittest
from dml_stream.utilities.file_utils import (
    safe_filename,
    ensure_dir,
    format_file_size,
    format_duration,
    get_available_disk_space,
)


class TestSafeFilename(unittest.TestCase):
    """Tests for safe_filename function."""
    
    def test_basic_filename(self):
        """Test basic filename sanitization."""
        result = safe_filename("My Video.mp4")
        self.assertEqual(result, "My.Video.mp4")
    
    def test_invalid_characters(self):
        """Test removal of invalid characters."""
        result = safe_filename("My<Video>.mp4")
        self.assertNotIn('<', result)
        self.assertNotIn('>', result)
    
    def test_unicode_filename(self):
        """Test Unicode filename handling."""
        result = safe_filename("Видео.mp4")
        self.assertTrue(result.endswith('.mp4'))
    
    def test_long_filename(self):
        """Test filename truncation."""
        long_name = "a" * 300 + ".mp4"
        result = safe_filename(long_name)
        self.assertLess(len(result), 250)
    
    def test_empty_filename(self):
        """Test empty filename."""
        result = safe_filename("")
        self.assertEqual(result, "unnamed")
    
    def test_filename_with_spaces(self):
        """Test filename with multiple spaces."""
        result = safe_filename("My   Video   File.mp4")
        # Multiple spaces should be reduced
        self.assertNotIn('   ', result)
    
    def test_filename_without_extension(self):
        """Test filename without extension."""
        result = safe_filename("MyVideo")
        self.assertEqual(result, "MyVideo")


class TestEnsureDir(unittest.TestCase):
    """Tests for ensure_dir function."""
    
    def test_create_new_directory(self):
        """Test creating a new directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = os.path.join(tmpdir, "new_folder")
            result = ensure_dir(new_dir)
            self.assertTrue(os.path.isdir(result))
    
    def test_existing_directory(self):
        """Test with existing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = ensure_dir(tmpdir)
            self.assertTrue(os.path.isdir(result))
    
    def test_nested_directories(self):
        """Test creating nested directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested = os.path.join(tmpdir, "a", "b", "c")
            result = ensure_dir(nested)
            self.assertTrue(os.path.isdir(result))


class TestFormatFileSize(unittest.TestCase):
    """Tests for format_file_size function."""
    
    def test_bytes(self):
        """Test bytes formatting."""
        result = format_file_size(500)
        self.assertEqual(result, "500 B")
    
    def test_kilobytes(self):
        """Test kilobytes formatting."""
        result = format_file_size(1536)
        self.assertEqual(result, "1.50 KB")
    
    def test_megabytes(self):
        """Test megabytes formatting."""
        result = format_file_size(1572864)
        self.assertEqual(result, "1.50 MB")
    
    def test_gigabytes(self):
        """Test gigabytes formatting."""
        result = format_file_size(1610612736)
        self.assertEqual(result, "1.50 GB")
    
    def test_zero_bytes(self):
        """Test zero bytes."""
        result = format_file_size(0)
        self.assertEqual(result, "0 B")
    
    def test_negative_bytes(self):
        """Test negative bytes."""
        result = format_file_size(-100)
        self.assertEqual(result, "Invalid size")


class TestFormatDuration(unittest.TestCase):
    """Tests for format_duration function."""
    
    def test_seconds_only(self):
        """Test duration in seconds."""
        result = format_duration(45)
        self.assertEqual(result, "45s")
    
    def test_minutes_and_seconds(self):
        """Test duration in minutes and seconds."""
        result = format_duration(125)
        self.assertEqual(result, "2m 5s")
    
    def test_hours_minutes_seconds(self):
        """Test duration in hours, minutes, and seconds."""
        result = format_duration(3665)
        self.assertEqual(result, "1h 1m 5s")
    
    def test_minutes_only(self):
        """Test duration in minutes only."""
        result = format_duration(120)
        self.assertEqual(result, "2m")
    
    def test_zero_duration(self):
        """Test zero duration."""
        result = format_duration(0)
        self.assertEqual(result, "0s")
    
    def test_negative_duration(self):
        """Test negative duration."""
        result = format_duration(-10)
        self.assertEqual(result, "Invalid duration")


class TestGetAvailableDiskSpace(unittest.TestCase):
    """Tests for get_available_disk_space function."""
    
    def test_current_directory(self):
        """Test getting disk space for current directory."""
        space = get_available_disk_space(".")
        # Should return a non-negative number or -1 if unable to determine
        self.assertGreaterEqual(space, -1)
    
    def test_temp_directory(self):
        """Test getting disk space for temp directory."""
        space = get_available_disk_space(tempfile.gettempdir())
        self.assertGreaterEqual(space, -1)


if __name__ == "__main__":
    unittest.main()
