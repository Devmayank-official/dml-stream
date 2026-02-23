"""
Unit tests for configuration.
"""

import os
import tempfile
import unittest

from dml_stream.config.settings import Config, ConfigManager
from dml_stream.core.exceptions import ConfigurationError


class TestConfig(unittest.TestCase):
    """Tests for Config class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_config_file = tempfile.mktemp(suffix='.json')

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()

        self.assertEqual(config.default_output_folder, "downloads")
        self.assertEqual(config.default_threads, 4)
        self.assertEqual(config.max_threads, 12)
        self.assertEqual(config.min_threads, 1)
        self.assertEqual(config.default_method, "normal")

    def test_config_validation(self):
        """Test configuration validation."""
        # Valid config
        config = Config()
        # Should not raise

        # Invalid thread range
        with self.assertRaises(ConfigurationError):
            Config(min_threads=10, max_threads=5)

        # Invalid default threads
        with self.assertRaises(ConfigurationError):
            Config(default_threads=20)

    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        config = Config(config_file_path=self.test_config_file)
        config.default_threads = 8
        config.save_to_file()

        # Verify file was created
        self.assertTrue(os.path.exists(self.test_config_file))

        # Load and verify
        loaded = Config.load_from_file(self.test_config_file)
        self.assertEqual(loaded.default_threads, 8)

    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = Config()
        config_dict = config.to_dict()

        self.assertIsInstance(config_dict, dict)
        self.assertIn('default_output_folder', config_dict)
        self.assertIn('default_threads', config_dict)

    def test_config_update(self):
        """Test updating configuration values."""
        config = Config()
        config.update(default_threads=8)
        self.assertEqual(config.default_threads, 8)

        # Update with invalid key
        with self.assertRaises(ConfigurationError):
            config.update(invalid_key=123)

    def test_config_get_set(self):
        """Test getting and setting configuration values."""
        config = Config()

        # Get existing value
        value = config.get('default_threads')
        self.assertEqual(value, 4)

        # Get with default
        value = config.get('nonexistent', 'default')
        self.assertEqual(value, 'default')

        # Set value
        config.set('default_threads', 8)
        self.assertEqual(config.default_threads, 8)

    def test_config_reset(self):
        """Test resetting configuration to defaults."""
        config = Config()
        config.default_threads = 8
        config.reset_to_defaults()
        self.assertEqual(config.default_threads, 4)


class TestConfigManager(unittest.TestCase):
    """Tests for ConfigManager singleton."""

    def setUp(self):
        """Reset ConfigManager state."""
        ConfigManager._instance = None
        ConfigManager._config = None

    def test_singleton_instance(self):
        """Test that ConfigManager is a singleton."""
        manager1 = ConfigManager.get_instance()
        manager2 = ConfigManager.get_instance()

        self.assertIs(manager1, manager2)

    def test_get_config(self):
        """Test getting configuration from manager."""
        config = ConfigManager.get_config()
        self.assertIsInstance(config, Config)

    def test_update_config(self):
        """Test updating configuration via manager."""
        ConfigManager.update_config(default_threads=8)
        config = ConfigManager.get_config()
        self.assertEqual(config.default_threads, 8)

    def test_save_and_load(self):
        """Test saving and loading via manager."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            test_file = f.name

        try:
            ConfigManager.update_config(default_threads=8)
            ConfigManager.save(test_file)

            ConfigManager.reset()
            ConfigManager.load(test_file)

            config = ConfigManager.get_config()
            self.assertEqual(config.default_threads, 8)
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)


if __name__ == "__main__":
    unittest.main()
