import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Dict, Optional, Union, Any


class AppLogger:
    """
    Singleton logger class that provides consistent logging across the application.
    Creates log files with date stamps and supports multiple logging levels.
    """
    _instances: Dict[str, 'AppLogger'] = {}

    @classmethod
    def get_instance(cls, name: str, log_dir: str = 'logs',
                     log_level: int = logging.INFO,
                     enable_console: bool = True,
                     max_file_size: int = 10 * 1024 * 1024,  # 10 MB
                     backup_count: int = 5) -> 'AppLogger':
        """
        Get or create a logger instance with the given name.

        Args:
            name: Logger name, typically __name__ of the calling module
            log_dir: Directory where log files will be stored
            log_level: Logging level (e.g., logging.INFO)
            enable_console: Whether to also log to console
            max_file_size: Maximum size of log files before rotation
            backup_count: Number of backup files to keep

        Returns:
            AppLogger instance
        """
        if name not in cls._instances:
            instance = cls(name, log_dir, log_level, enable_console, max_file_size, backup_count)
            cls._instances[name] = instance
        return cls._instances[name]

    def __init__(self, name: str, log_dir: str, log_level: int,
                 enable_console: bool, max_file_size: int, backup_count: int):
        """Initialize the logger instance."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        # Only configure handlers if none exist
        if not self.logger.handlers:
            try:
                # Create log directory
                log_dir_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), log_dir)
                os.makedirs(log_dir_path, exist_ok=True)

                # Configure formatters
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )

                # Set up file handler with rotation
                log_file = os.path.join(log_dir_path, f'app_{datetime.now().strftime("%Y%m%d")}.log')
                file_handler = RotatingFileHandler(
                    log_file,
                    maxBytes=max_file_size,
                    backupCount=backup_count
                )
                file_handler.setLevel(log_level)
                file_handler.setFormatter(file_formatter)
                self.logger.addHandler(file_handler)

                # Add console handler if enabled
                if enable_console:
                    console_handler = logging.StreamHandler()
                    console_handler.setLevel(log_level)
                    console_handler.setFormatter(file_formatter)
                    self.logger.addHandler(console_handler)

            except Exception as e:
                # Fallback to basic console logging if file setup fails
                print(f"Error setting up logger: {e}")
                console_handler = logging.StreamHandler()
                console_handler.setLevel(log_level)
                self.logger.addHandler(console_handler)

    def get_logger(self) -> logging.Logger:
        """Return the configured logger instance."""
        return self.logger