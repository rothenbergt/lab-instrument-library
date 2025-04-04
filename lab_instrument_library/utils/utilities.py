"""
Utility functions for the lab instrument library.

This module contains various utility functions used throughout the library for tasks
like directory management, instrument discovery, data type conversion, and user interfaces.
"""

import pyvisa
import os
import time
import logging
import re
import PySimpleGUI as sg
from typing import List, Union, Optional, Tuple, Dict, Any

# Setup module logger
logger = logging.getLogger(__name__)


def create_run_folder(base_path: str) -> str:
    """Create a new run folder with incrementing number.
    
    Creates a standardized folder structure for a new test run. This function
    finds the highest numbered existing run folder and creates the next one
    with subdirectories for data and pictures.
    
    Args:
        base_path: Base directory path where run folders will be created.
        
    Returns:
        Path to the newly created run folder with trailing slash.
        
    Raises:
        OSError: If directory creation fails.
    """
    # Ensure base_path exists
    os.makedirs(base_path, exist_ok=True)
    
    try:
        # Extract run numbers from existing folders
        max_num = 0
        run_pattern = re.compile(r'run(\d+)$')
        
        for item in os.listdir(base_path):
            if os.path.isdir(os.path.join(base_path, item)):
                match = run_pattern.match(item)
                if match:
                    num = int(match.group(1))
                    max_num = max(max_num, num)
        
        # Create new run folder and its subdirectories
        new_run_num = max_num + 1
        run_dir = os.path.join(base_path, f"run{new_run_num}")
        
        logger.info(f"Creating run folder {new_run_num}")
        print(f"Creating folder run{new_run_num}")
        
        # Create the directory structure
        os.makedirs(run_dir, exist_ok=True)
        os.makedirs(os.path.join(run_dir, "data"), exist_ok=True)
        os.makedirs(os.path.join(run_dir, "pictures"), exist_ok=True)
        
        # Ensure trailing slash for returned path
        run_path = os.path.join(run_dir, "")
        return run_path
        
    except OSError as e:
        logger.error(f"Error creating run folders: {str(e)}")
        print(f"Error creating run folders: {str(e)}")
        # Create a fallback directory structure
        run_dir = os.path.join(base_path, "run1")
        os.makedirs(run_dir, exist_ok=True)
        os.makedirs(os.path.join(run_dir, "data"), exist_ok=True)
        os.makedirs(os.path.join(run_dir, "pictures"), exist_ok=True)
        return os.path.join(run_dir, "")


def save_recent_directory(directory: str) -> None:
    """Save a directory path to the recent directories file.
    
    Args:
        directory: Directory path to save.
    """
    try:
        current_dir = os.getcwd()
        recent_file = os.path.join(current_dir, "recentDirectories.txt")
        
        # Read existing entries
        recent_dirs = []
        if os.path.exists(recent_file):
            with open(recent_file, 'r') as f:
                recent_dirs = [line.strip() for line in f.readlines()]
        
        # Add new directory if not already in list
        if directory not in recent_dirs:
            recent_dirs.append(directory)
            
            # Keep only the 10 most recent directories
            if len(recent_dirs) > 10:
                recent_dirs = recent_dirs[-10:]
                
            # Write back to file
            with open(recent_file, 'w') as f:
                for dir_path in recent_dirs:
                    f.write(f"{dir_path}\n")
    except Exception as e:
        logger.warning(f"Failed to save recent directory: {str(e)}")


def get_directory() -> Optional[str]:
    """Display a GUI for selecting a directory.
    
    Shows a GUI dialog that allows the user to browse for a directory or
    select from recently used directories.
    
    Returns:
        Selected directory path or None if canceled.
    """
    current_dir = os.getcwd()
    recent_dirs = []
    
    # Try to load recent directories
    try:
        recent_file = os.path.join(current_dir, "recentDirectories.txt")
        if os.path.exists(recent_file):
            with open(recent_file, 'r') as f:
                recent_dirs = [line.strip() for line in f.readlines()]
                # Remove duplicates while preserving order
                seen = set()
                recent_dirs = [x for x in recent_dirs if not (x in seen or seen.add(x))]
    except Exception as e:
        logger.warning(f"Failed to load recent directories: {str(e)}")

    # Create the layout for the directory selection dialog
    layout = [
        [sg.Text("Recent Directories:", visible=bool(recent_dirs))],
        [sg.Listbox(values=recent_dirs, size=(70, min(5, len(recent_dirs))), 
                   key="-LIST-", enable_events=True, visible=bool(recent_dirs))],
        [sg.Text("Choose a folder to save your data:")],
        [sg.InputText(key="-INPUT-", size=(60, 1)), 
         sg.FolderBrowse(key="-BROWSE-")],
        [sg.Button("OK", bind_return_key=True), sg.Button("Cancel")]
    ]

    window = sg.Window('Select Directory', layout, finalize=True)
    
    # Event loop
    while True:
        event, values = window.read()
        
        if event in (sg.WIN_CLOSED, "Cancel"):
            window.close()
            return None
            
        if event == "-LIST-" and values["-LIST-"]:
            # Update the input field with the selected directory
            window["-INPUT-"].update(values["-LIST-"][0])
            
        if event == "OK":
            selected_dir = values["-INPUT-"] or (values["-LIST-"][0] if values["-LIST-"] else "")
            
            if not selected_dir:
                sg.popup("Please select a directory", title="No Directory Selected")
                continue
                
            if not os.path.isdir(selected_dir):
                sg.popup(f"'{selected_dir}' is not a valid directory", title="Invalid Directory")
                continue
                
            window.close()
            # Save this directory for future use
            save_recent_directory(selected_dir)
            return selected_dir

    window.close()
    return None


def countdown(seconds: int, message: str = "Time remaining") -> None:
    """Display a countdown timer in the console.
    
    Shows a countdown timer with optional message, updating in-place
    on the console. Allows early termination with Ctrl+C.
    
    Args:
        seconds: Number of seconds to count down from.
        message: Optional message to display with the countdown.
    """
    try:
        for remaining in range(seconds, 0, -1):
            mins, secs = divmod(remaining, 60)
            hours, mins = divmod(mins, 60)
            
            if hours > 0:
                time_format = f"{hours:02d}:{mins:02d}:{secs:02d}"
            else:
                time_format = f"{mins:02d}:{secs:02d}"
                
            print(f"\r{message}: {time_format} (Ctrl+C to end early)", end="")
            time.sleep(1)
            
        print("\rCountdown complete!                            ")
        
    except KeyboardInterrupt:
        print("\rCountdown terminated by user                   ")


def scan_gpib_devices(start: int = 0, end: int = 32, timeout: int = 1000) -> Dict[int, str]:
    """Scan GPIB bus for connected instruments.
    
    Scans the specified range of GPIB addresses and attempts to identify
    instruments at each address.
    
    Args:
        start: Starting GPIB address to scan.
        end: Ending GPIB address to scan.
        timeout: Communication timeout in milliseconds.
        
    Returns:
        Dictionary mapping GPIB addresses to instrument identification strings.
    """
    devices = {}
    rm = pyvisa.ResourceManager()
    
    print(f"Scanning GPIB addresses {start}-{end}...")
    print("-" * 60)
    print(f"{'Address':<8} {'Connected':<12} {'Identification'}")
    print("-" * 60)
    
    for address in range(start, end + 1):
        resource_name = f'GPIB0::{address}::INSTR'
        print(f"{address:<8}", end=" ")
        
        try:
            # Attempt to open the resource with a short timeout
            instrument = rm.open_resource(resource_name)
            instrument.timeout = timeout
            print(f"{'Connected':<12}", end=" ")
            
            # Try to get identification
            try:
                idn = instrument.query("*IDN?").strip()
                devices[address] = idn
                print(f"{idn}")
            except Exception:
                print("(No identification available)")
                devices[address] = "Unknown instrument"
                
            # Close the connection
            instrument.close()
            
        except Exception:
            print("No device")
    
    print("-" * 60)
    return devices


def getAllLiveUnits() -> Dict[int, str]:
    """Find all live GPIB instruments.
    
    Legacy wrapper for scan_gpib_devices().
    
    Returns:
        Dictionary mapping GPIB addresses to instrument identification strings.
    """
    return scan_gpib_devices()


def parse_numeric(string: str) -> Union[int, float]:
    """Extract and parse a numeric value from a string.
    
    This function extracts numeric characters (and decimal points)
    from a string and attempts to parse them as either an integer
    or a float.
    
    Args:
        string: String containing numeric values.
        
    Returns:
        int or float: The parsed numeric value.
        
    Raises:
        ValueError: If no numeric value could be extracted.
    """
    # Extract digits and decimal points
    numeric_chars = [c for c in string if c.isdigit() or c == '.']
    
    if not numeric_chars:
        raise ValueError(f"No numeric value found in string: '{string}'")
        
    number_str = ''.join(numeric_chars)
    
    # Try to convert to numeric value
    try:
        # If there's a decimal point, return as float
        if '.' in number_str:
            return float(number_str)
        # Otherwise return as integer
        return int(number_str)
    except ValueError:
        raise ValueError(f"Failed to convert '{number_str}' to a numeric value")


def stringToInt(string: str) -> int:
    """Extract and convert numeric characters from a string to an integer.
    
    Args:
        string: String containing numbers.
        
    Returns:
        int: The extracted integer value.
    """
    try:
        return int(parse_numeric(string))
    except ValueError:
        # For backward compatibility, just log error and return 0
        logger.error(f"Failed to convert '{string}' to integer")
        return 0


def stringToFloat(string: str) -> float:
    """Extract and convert numeric characters from a string to a float.
    
    Args:
        string: String containing numbers.
        
    Returns:
        float: The extracted float value.
    """
    try:
        return float(parse_numeric(string))
    except ValueError:
        # For backward compatibility, just log error and return 0.0
        logger.error(f"Failed to convert '{string}' to float")
        return 0.0


def is_valid_ip(ip_address: str) -> bool:
    """Check if a string is a valid IP address.
    
    Args:
        ip_address: String to check.
        
    Returns:
        bool: True if the string is a valid IP address, False otherwise.
    """
    pattern = re.compile(
        r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    )
    return bool(pattern.match(ip_address))


def format_bytes(bytes: int) -> str:
    """Format byte count into human-readable string.
    
    Args:
        bytes: Number of bytes.
        
    Returns:
        Human-readable string representation (e.g., "1.23 MB").
    """
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024**2:
        return f"{bytes/1024:.2f} KB"
    elif bytes < 1024**3:
        return f"{bytes/1024**2:.2f} MB"
    else:
        return f"{bytes/1024**3:.2f} GB"
