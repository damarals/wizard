"""
Configuration management for CAPES Research Wizard.
"""

import json
import os
import sys

from wizard.utils.logger import get_logger

logger = get_logger(__name__)


class Config:
    """
    Manages application configuration settings.

    This class handles loading, accessing, and saving application settings
    to a JSON configuration file.
    """

    def __init__(self, config_path=None):
        """
        Initialize configuration manager.

        Args:
            config_path: Optional path to config file
        """
        self.data = {}

        # Determine config directory and file path
        if config_path:
            self.config_file = config_path
        else:
            self.config_file = self._get_default_config_path()

        # Load configuration
        self.load()

        # Set defaults if not present
        self._set_defaults()

    def _get_default_config_path(self):
        """Get the default path for the config file based on platform."""
        if sys.platform == "win32":
            # Windows: %APPDATA%\CAPES Research Wizard\config.json
            app_data = os.environ.get("APPDATA", "")
            base_dir = os.path.join(app_data, "CAPES Research Wizard")
        elif sys.platform == "darwin":
            # macOS: ~/Library/Application Support/CAPES Research Wizard
            base_dir = os.path.expanduser("~/Library/Application Support/CAPES Research Wizard")
        else:
            # Linux/Unix: ~/.config/capes-wizard
            base_dir = os.path.expanduser("~/.config/capes-wizard")

        # Create directory if it doesn't exist
        os.makedirs(base_dir, exist_ok=True)

        return os.path.join(base_dir, "config.json")

    def _set_defaults(self):
        """Set default configuration values if not present."""
        defaults = {
            "max_workers": 3,
            "request_delay": 2.0,
            "max_pages": 5,
            "fetch_details": True,
            "use_advanced_search": True,
            "auto_resize_columns": True,
            "alternate_row_colors": True,
            "export_filename": "capes_articles.csv",
            "window_width": 1200,
            "window_height": 800,
            "splitter_sizes": [650, 350],
        }

        for key, value in defaults.items():
            if key not in self.data:
                self.data[key] = value

    def load(self):
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                logger.debug(f"Configuration loaded from {self.config_file}")
            else:
                logger.debug(f"Configuration file not found at {self.config_file}, using defaults")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}", exc_info=True)
            self.data = {}

    def save(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
            logger.debug(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}", exc_info=True)

    def get(self, key, default=None):
        """
        Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key doesn't exist

        Returns:
            Configuration value or default
        """
        return self.data.get(key, default)

    def set(self, key, value):
        """
        Set a configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        self.data[key] = value

    def clear(self):
        """Clear all configuration data."""
        self.data = {}
        self._set_defaults()
