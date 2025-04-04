"""
Logging utility for lab instrument experiments.

This module provides a configurable logging utility that writes messages
to both the console and a log file with timestamps and severity levels.
It supports multiple log levels and customizable formatting.
"""

import os
import sys
from datetime import datetime
import logging
from typing import Optional, Union, Any, TextIO, Dict, List

class Logger:
    """Logger class for instrument operations and experiments.
    
    This class provides methods to log messages with timestamps to both
    the console and a file, with support for different log levels and
    customizable formatting.
    
    Attributes:
        directory (str): Directory where log files are stored.
        log_file (str): Name of the log file.
        log_level (int): Current logging level (0-3).
        console_output (bool): Whether to print messages to console.
        timestamp_format (str): Format string for timestamps.
    """

    # Log levels
    INFO = 0
    WARNING = 1
    ERROR = 2
    DEBUG = 3
    
    # Level names for display
    _LEVEL_NAMES = {
        INFO: "INFO",
        WARNING: "WARNING",
        ERROR: "ERROR",
        DEBUG: "DEBUG"
    }

    def __init__(self, directory: str = ".", log_file: str = "log.txt", 
                log_level: int = INFO, console_output: bool = True,
                timestamp_format: str = "%Y-%m-%d %H:%M:%S"):
        """Initialize a new Logger.
        
        Args:
            directory: Directory where log files will be stored.
            log_file: Name of the log file.
            log_level: Logging level (0=INFO, 1=WARNING, 2=ERROR, 3=DEBUG).
            console_output: Whether to print messages to console.
            timestamp_format: Format string for timestamps.
        """
        self.directory = directory
        self.log_file = log_file
        self.log_level = log_level
        self.console_output = console_output
        self.timestamp_format = timestamp_format
        
        # Ensure directory has a trailing slash
        if not self.directory.endswith('/') and not self.directory.endswith('\\'):
            self.directory += os.path.sep
            
        # Ensure directory exists
        if not os.path.exists(self.directory):
            try:
                os.makedirs(self.directory)
                print(f"Created log directory: {self.directory}")
            except Exception as e:
                print(f"Warning: Could not create log directory: {str(e)}")

        # Initialize the log file with a header
        self._log_header()

    def _get_log_file(self, mode: str = "a") -> Optional[TextIO]:
        """Get a file handle for the log file.
        
        Args:
            mode: File open mode ('a' for append, 'w' for write).
            
        Returns:
            File handle or None if file couldn't be opened.
        """
        try:
            log_path = os.path.join(self.directory, self.log_file)
            return open(log_path, mode, encoding='utf-8')
        except Exception as e:
            if self.console_output:
                print(f"Warning: Could not open log file: {str(e)}")
            return None
    
    def _log_header(self) -> None:
        """Write a header to the log file."""
        f = self._get_log_file(mode='a')
        if f:
            try:
                start_time = datetime.now().strftime(self.timestamp_format)
                f.write(f"{'='*80}\n")
                f.write(f"Log started at {start_time}\n")
                f.write(f"{'='*80}\n")
            finally:
                f.close()

    def print(self, message: Any, level: int = INFO) -> None:
        """Log a message to both console and file.
        
        Args:
            message: The message to log.
            level: Log level for this message (0=INFO, 1=WARNING, 2=ERROR, 3=DEBUG).
        """
        # Skip if message level is higher than the current log level
        if level > self.log_level:
            return
            
        # Get current timestamp
        timestamp = datetime.now().strftime(self.timestamp_format)
        
        # Determine log level prefix
        level_name = self._LEVEL_NAMES.get(level, "INFO")
            
        # Format message
        if isinstance(message, str):
            formatted_message = f"{timestamp} [{level_name}] {message}"
        else:
            formatted_message = f"{timestamp} [{level_name}] {str(message)}"
            
        # Print to console if enabled
        if self.console_output:
            if level == self.ERROR:
                print(f"\033[91m{formatted_message}\033[0m")  # Red text for errors
            elif level == self.WARNING:
                print(f"\033[93m{formatted_message}\033[0m")  # Yellow text for warnings
            elif level == self.DEBUG:
                print(f"\033[94m{formatted_message}\033[0m")  # Blue text for debug
            else:
                print(formatted_message)
            
        # Write to file
        f = self._get_log_file()
        if f:
            try:
                f.write(f"{formatted_message}\n")
            finally:
                f.close()

    def info(self, message: Any) -> None:
        """Log an informational message.
        
        Args:
            message: The message to log.
        """
        self.print(message, self.INFO)
        
    def warning(self, message: Any) -> None:
        """Log a warning message.
        
        Args:
            message: The message to log.
        """
        self.print(message, self.WARNING)
        
    def error(self, message: Any) -> None:
        """Log an error message.
        
        Args:
            message: The message to log.
        """
        self.print(message, self.ERROR)
        
    def debug(self, message: Any) -> None:
        """Log a debug message.
        
        Args:
            message: The message to log.
        """
        self.print(message, self.DEBUG)
        
    def separator(self, char: str = '-', length: int = 80) -> None:
        """Log a separator line.
        
        Args:
            char: Character to use for the separator.
            length: Length of the separator line.
        """
        self.info(char * length)

    def clear(self) -> None:
        """Clear the current log file."""
        f = self._get_log_file(mode='w')
        if f:
            try:
                timestamp = datetime.now().strftime(self.timestamp_format)
                f.write(f"Log cleared at {timestamp}\n")
                if self.console_output:
                    print("Log file cleared.")
            finally:
                f.close()
        elif self.console_output:
            print("There is no log to clear.")
            
    def set_level(self, level: int) -> None:
        """Set the current logging level.
        
        Args:
            level: New logging level (0=INFO, 1=WARNING, 2=ERROR, 3=DEBUG).
        """
        if 0 <= level <= 3:
            self.log_level = level
            self.debug(f"Log level set to {self._LEVEL_NAMES.get(level, 'UNKNOWN')}")
        else:
            self.warning(f"Invalid log level: {level}. Using INFO level.")
            self.log_level = self.INFO
            
    def get_level_name(self) -> str:
        """Get the name of the current logging level.
        
        Returns:
            str: The name of the current logging level.
        """
        return self._LEVEL_NAMES.get(self.log_level, "UNKNOWN")
        
    def export_log(self, destination: str) -> bool:
        """Export the log file to another location.
        
        Args:
            destination: Path to export the log file to.
            
        Returns:
            bool: True if export succeeded, False otherwise.
        """
        source_path = os.path.join(self.directory, self.log_file)
        if not os.path.exists(source_path):
            if self.console_output:
                print(f"Log file {source_path} does not exist")
            return False
            
        try:
            with open(source_path, 'r', encoding='utf-8') as source, \
                 open(destination, 'w', encoding='utf-8') as dest:
                dest.write(source.read())
            if self.console_output:
                print(f"Log exported to {destination}")
            return True
        except Exception as e:
            if self.console_output:
                print(f"Error exporting log: {str(e)}")
            return False
