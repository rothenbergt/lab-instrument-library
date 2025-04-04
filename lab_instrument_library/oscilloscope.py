"""
Python library containing general functions to control oscilloscopes.

This module provides a standardized interface for working with oscilloscopes
to capture waveforms, save images, and control display and acquisition settings.
"""

from struct import unpack
import PySimpleGUI as sg
import io
import numpy as np
import os
import pandas as pd
import pylab
import pyvisa
import shutil
import tempfile
import time
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from PIL import Image, ImageColor, ImageDraw
from .base import LibraryTemplate
from .utils import visa_exception_handler

# Setup module logger
logger = logging.getLogger(__name__)

class Oscilloscope(LibraryTemplate):
    """Oscilloscope class for interfacing with Tektronix and similar oscilloscopes.
    
    This class provides methods for waveform acquisition, display control, and
    measurement capabilities of oscilloscopes.
    
    Attributes:
        instrument_address: The VISA address of the connected oscilloscope.
        connection: The PyVISA resource connection object.
        instrumentID: The identification string of the connected instrument.
        nickname: A user-provided name for the instrument (optional).
    """
    
    def __init__(self, instrument_address: str, nickname: str = None, identify: bool = True):
        """Initialize the oscilloscope connection.

        Args:
            instrument_address: VISA address of the instrument.
            nickname: User-defined name for the instrument.
            identify: Whether to identify the instrument with *IDN?.
        """      
        super().__init__(instrument_address, nickname, identify)
        logger.info(f"Initialized oscilloscope at {instrument_address}")

    @visa_exception_handler(module_logger=logger)
    def acquire(self, channel: int, show: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """Acquire waveform data from the specified channel.

        Args:
            channel: The channel number to acquire data from.
            show: Whether to display the acquired waveform.

        Returns:
            tuple: Time and voltage data arrays.
        """
        logger.info(f"Acquiring waveform from channel {channel}")
        self.write(f"DATA:SOURCE CH{channel}")
        self.write("DATA:START 1")
        self.write("DATA:STOP 10000")
        self.write("WFMPRE:ENC ASCII")
        self.write("CURVE?")
        data = self.connection.read_raw()
        header_len = 2 + int(data[1])
        adc_wave = data[header_len:-1]
        adc_wave = np.array(unpack(f'{len(adc_wave)}B', adc_wave))
        volts_per_div = float(self.query("WFMPRE:YMULT?"))
        volts_offset = float(self.query("WFMPRE:YZERO?"))
        volts = (adc_wave - 127.5) * volts_per_div + volts_offset
        time_per_div = float(self.query("WFMPRE:XINCR?"))
        time_offset = float(self.query("WFMPRE:PT_OFF?"))
        time = np.arange(0, len(volts)) * time_per_div + time_offset

        if show:
            pylab.plot(time, volts)
            pylab.show()
            
        logger.debug(f"Acquired {len(volts)} waveform points from channel {channel}")
        return time, volts

    @visa_exception_handler(module_logger=logger)
    def save_image(self, filename: str) -> None:
        """Save a screenshot of the oscilloscope display.

        Args:
            filename: The filename to save the image as.
        """
        logger.info(f"Saving oscilloscope screenshot to {filename}")
        self.write("HARDCOPY START")
        data = self.connection.read_raw()
        with open(filename, 'wb') as f:
            f.write(data)
        logger.info(f"Screenshot saved to {filename}")

    @visa_exception_handler(module_logger=logger)
    def set_channel_label(self, channel: int, label: str) -> None:
        """Set the label for the specified channel.

        Args:
            channel: The channel number to set the label for.
            label: The label to set.
        """
        logger.debug(f"Setting channel {channel} label to '{label}'")
        self.write(f"CH{channel}:LAB \"{label}\"")

    @visa_exception_handler(module_logger=logger)
    def set_vertical_scale(self, channel: int, scale: float) -> None:
        """Set the vertical scale for the specified channel.

        Args:
            channel: The channel number to set the scale for.
            scale: The scale to set in volts/division.
        """
        logger.debug(f"Setting channel {channel} vertical scale to {scale} V/div")
        self.write(f"CH{channel}:SCA {scale}")

    # Keep old method as alias
    setVerticalScale = set_vertical_scale

    @visa_exception_handler(module_logger=logger)
    def auto_set(self) -> None:
        """Automatically configure the oscilloscope for the current signal."""
        logger.info("Executing autoset command")
        self.write("AUTOSET EXECUTE")

    # Keep old method as alias
    autoSet = auto_set

    @visa_exception_handler(module_logger=logger)
    def run(self) -> None:
        """Start acquisition."""
        logger.debug("Starting acquisition")
        self.write("ACQUIRE:STATE RUN")

    @visa_exception_handler(module_logger=logger)
    def stop(self) -> None:
        """Stop acquisition."""
        logger.debug("Stopping acquisition")
        self.write("ACQUIRE:STATE STOP")

    @visa_exception_handler(module_logger=logger)
    def show_message(self, message: str) -> None:
        """Display a message on the oscilloscope screen.

        Args:
            message: The message to display.
        """
        logger.debug(f"Displaying message: '{message}'")
        self.write(f"MESSage:SHOW \"{message}\"")

    @visa_exception_handler(module_logger=logger)
    def remove_message(self) -> None:
        """Remove the displayed message from the oscilloscope screen."""
        logger.debug("Removing displayed message")
        self.write("MESSage:SHOW \"\"")

    @visa_exception_handler(module_logger=logger)
    def change_graticule(self, graticule: str) -> None:
        """Change the graticule display mode.

        Args:
            graticule: The graticule mode to set (e.g., "GRID", "AXIS").
        """
        logger.debug(f"Changing graticule mode to {graticule}")
        self.write(f"GRAT:MODE {graticule}")

    # Keep old method as alias
    changeGraticule = change_graticule

    @visa_exception_handler(module_logger=logger)
    def change_waveform_intensity(self, intensity: int) -> None:
        """Change the waveform intensity.

        Args:
            intensity: The intensity level to set (0-100).
        """
        logger.debug(f"Setting waveform intensity to {intensity}")
        self.write(f"DISplay:INTENSITY:WAVEFORM {intensity}")

    # Keep old method as alias
    changeWaveFormIntensity = change_waveform_intensity

    @visa_exception_handler(module_logger=logger)
    def export_waveform_to_csv(self, channel: int, filename: str) -> bool:
        """Export waveform data to a CSV file.
        
        Args:
            channel: Channel to acquire data from
            filename: File to save data to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            time_data, voltage_data = self.acquire(channel, show=False)
            
            # Ensure filename has .csv extension
            if not filename.lower().endswith('.csv'):
                filename += '.csv'
                
            import csv
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Time (s)', 'Voltage (V)'])
                for t, v in zip(time_data, voltage_data):
                    writer.writerow([t, v])
                    
            logger.info(f"Exported waveform data to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error exporting waveform: {str(e)}")
            return False

    def reset(self) -> bool:
        """Reset the instrument to factory settings.
        
        Returns:
            bool: True if reset succeeded, False otherwise.
        """
        logger.info("Resetting oscilloscope to factory settings")
        result = super().reset()
        if result:
            logger.info("Reset successful")
        else:
            logger.warning("Reset failed")
        return result
    
    def close(self) -> None:
        """Close the connection to the oscilloscope."""
        logger.info("Closing oscilloscope connection")
        super().close_connection()

    # Add aliases for backward compatibility:
    saveImage = save_image
    setChannelLabel = set_channel_label