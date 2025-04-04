"""
Python library containing general functions to control oscilloscopes.

This module provides a standardized interface for working with oscilloscopes
to capture waveforms, save images, and control display and acquisition settings.

Supported devices:
- Tektronix TBS1000/2000 Series
- Tektronix TDS1000/2000 Series
- Tektronix MSO/DPO2000/3000/4000 Series
- Tektronix MDO3000/4000 Series

Documentation references:
- TBS1000: https://download.tek.com/manual/TBS1000-TBS1000B-Programmer-Manual-077009811.pdf
- TDS2000: https://download.tek.com/manual/071125802.pdf
- MDO3000: https://download.tek.com/manual/MDO3000-Series-Programmer-077124004.pdf
"""

from struct import unpack
import io
import numpy as np
import os
import pandas as pd
import pylab
import pyvisa
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any, Union, TypeVar
from PIL import Image, ImageColor, ImageDraw
from .base import LibraryTemplate
from .utils.decorators import visa_exception_handler, parameter_validator

# Setup module logger
logger = logging.getLogger(__name__)

# Type variable for oscilloscope base class
T = TypeVar('T', bound='OscilloscopeBase')

class OscilloscopeBase(LibraryTemplate, ABC):
    """Base class for all oscilloscopes.
    
    This abstract base class provides common functionality for different oscilloscope models.
    It implements methods for basic waveform acquisition, display control, and
    measurement operations that are shared across various oscilloscope instruments.
    
    Attributes:
        instrument_address: The VISA address of the connected oscilloscope.
        connection: The PyVISA resource connection object.
        instrumentID: The identification string of the connected instrument.
        nickname: A user-provided name for the instrument (optional).
        max_channels: Maximum number of channels available on this oscilloscope.
    """
    
    # Class constants
    GRATICULE_MODES = ["GRID", "CROSS", "FRAME", "FULL"]
    DEFAULT_TIMEOUT = 10000  # 10 seconds
    
    def __init__(self, instrument_address: str, nickname: str = None, identify: bool = True, 
                max_channels: int = 4, timeout: int = DEFAULT_TIMEOUT):
        """Initialize the oscilloscope connection.

        Args:
            instrument_address: VISA address of the instrument.
            nickname: User-defined name for the instrument.
            identify: Whether to identify the instrument with *IDN?.
            max_channels: Maximum number of channels on this oscilloscope.
            timeout: Connection timeout in milliseconds.
        """      
        super().__init__(instrument_address, nickname, identify, timeout)
        self.max_channels = max_channels
        logger.info(f"Initialized {self.__class__.__name__} at {instrument_address}")

    @parameter_validator(channel=lambda c: c > 0)
    @visa_exception_handler(default_return_value=(np.array([]), np.array([])), module_logger=logger)
    def acquire(self, channel: int, show: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """Acquire waveform data from the specified channel.

        Args:
            channel: The channel number to acquire data from.
            show: Whether to display the acquired waveform.

        Returns:
            tuple: Time and voltage data arrays.
        """
        # Validate channel
        if channel > self.max_channels:
            logger.error(f"Channel {channel} is invalid. This oscilloscope has {self.max_channels} channels.")
            return np.array([]), np.array([])
            
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

    @visa_exception_handler(default_return_value=False, module_logger=logger)
    def save_image(self, filename: str) -> bool:
        """Save a screenshot of the oscilloscope display.

        Args:
            filename: The filename to save the image as.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        logger.info(f"Saving oscilloscope screenshot to {filename}")
        self.write("HARDCOPY START")
        
        # Increase timeout for image transfer
        with self.temporary_timeout(30000):  # 30 seconds
            data = self.connection.read_raw()
            
        try:
            with open(filename, 'wb') as f:
                f.write(data)
            logger.info(f"Screenshot saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving screenshot: {str(e)}")
            return False

    @parameter_validator(
        channel=lambda c: c > 0,
        label=lambda l: len(l) <= 32  # Most oscilloscopes limit label length
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_channel_label(self, channel: int, label: str) -> None:
        """Set the label for the specified channel.

        Args:
            channel: The channel number to set the label for.
            label: The label to set (max 32 chars).
            
        Raises:
            ValueError: If channel is invalid or label is too long.
        """
        # Validate channel
        if channel > self.max_channels:
            raise ValueError(f"Channel {channel} is invalid. This oscilloscope has {self.max_channels} channels.")
            
        logger.debug(f"Setting channel {channel} label to '{label}'")
        self.write(f"CH{channel}:LAB \"{label}\"")

    @parameter_validator(
        channel=lambda c: c > 0,
        scale=lambda s: s > 0
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_vertical_scale(self, channel: int, scale: float) -> None:
        """Set the vertical scale for the specified channel.

        Args:
            channel: The channel number to set the scale for.
            scale: The scale to set in volts/division (must be positive).
            
        Raises:
            ValueError: If channel is invalid or scale is not positive.
        """
        # Validate channel
        if channel > self.max_channels:
            raise ValueError(f"Channel {channel} is invalid. This oscilloscope has {self.max_channels} channels.")
            
        logger.debug(f"Setting channel {channel} vertical scale to {scale} V/div")
        self.write(f"CH{channel}:SCA {scale}")

    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def auto_set(self) -> None:
        """Automatically configure the oscilloscope for the current signal."""
        logger.info("Executing autoset command")
        self.write("AUTOSET EXECUTE")

    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def run(self) -> None:
        """Start acquisition."""
        logger.debug("Starting acquisition")
        self.write("ACQUIRE:STATE RUN")

    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def stop(self) -> None:
        """Stop acquisition."""
        logger.debug("Stopping acquisition")
        self.write("ACQUIRE:STATE STOP")

    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def show_message(self, message: str) -> None:
        """Display a message on the oscilloscope screen.

        Args:
            message: The message to display.
        """
        logger.debug(f"Displaying message: '{message}'")
        self.write(f"MESSage:SHOW \"{message}\"")

    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def remove_message(self) -> None:
        """Remove the displayed message from the oscilloscope screen."""
        logger.debug("Removing displayed message")
        self.write("MESSage:SHOW \"\"")

    @parameter_validator(graticule=lambda g: g.upper() in OscilloscopeBase.GRATICULE_MODES)
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def change_graticule(self, graticule: str) -> None:
        """Change the graticule display mode.

        Args:
            graticule: The graticule mode to set (e.g., "GRID", "CROSS", "FRAME", "FULL").
            
        Raises:
            ValueError: If graticule mode is invalid.
        """
        logger.debug(f"Changing graticule mode to {graticule.upper()}")
        self.write(f"DISPLAY:INTENSITY:GRATICULE {graticule.upper()}")

    @parameter_validator(intensity=lambda i: 0 <= i <= 100)
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def change_waveform_intensity(self, intensity: int) -> None:
        """Change the waveform intensity.

        Args:
            intensity: The intensity level to set (0-100).
            
        Raises:
            ValueError: If intensity is outside valid range.
        """
        logger.debug(f"Setting waveform intensity to {intensity}")
        self.write(f"DISplay:INTENSITY:WAVEFORM {intensity}")

    @parameter_validator(
        channel=lambda c: c > 0,
        filename=lambda f: True  # Any filename is valid
    )
    @visa_exception_handler(default_return_value=False, module_logger=logger)
    def export_waveform_to_csv(self, channel: int, filename: str) -> bool:
        """Export waveform data to a CSV file.
        
        Args:
            channel: Channel to acquire data from
            filename: File to save data to
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If channel is invalid.
        """
        # Validate channel
        if channel > self.max_channels:
            raise ValueError(f"Channel {channel} is invalid. This oscilloscope has {self.max_channels} channels.")
            
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

    @visa_exception_handler(default_return_value="ERROR: Unable to retrieve error status", module_logger=logger)
    def get_error(self) -> str:
        """Get the first error from the instrument's error queue.
        
        Returns:
            str: Error message or indication of no error.
        """
        error = self.query("EVENT?")
        return error.strip()

    @visa_exception_handler(default_return_value=False, module_logger=logger)
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
    
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def close(self) -> None:
        """Close the connection to the oscilloscope."""
        logger.info("Closing oscilloscope connection")
        super().close_connection()
    
    @parameter_validator(timebase=lambda t: t > 0)
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_horizontal_scale(self, timebase: float) -> None:
        """Set the horizontal scale (time base).

        Args:
            timebase: The timebase to set in seconds/division (must be positive).
            
        Raises:
            ValueError: If timebase is not positive.
        """
        logger.debug(f"Setting horizontal scale to {timebase} s/div")
        self.write(f"HORizontal:SCAle {timebase}")
    
    @parameter_validator(
        channel=lambda c: c > 0,
        coupling=lambda c: c.upper() in ["AC", "DC", "GND"]
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_coupling(self, channel: int, coupling: str) -> None:
        """Set the input coupling for the specified channel.

        Args:
            channel: The channel number.
            coupling: The coupling type (AC, DC, GND).
            
        Raises:
            ValueError: If channel or coupling is invalid.
        """
        # Validate channel
        if channel > self.max_channels:
            raise ValueError(f"Channel {channel} is invalid. This oscilloscope has {self.max_channels} channels.")
            
        logger.debug(f"Setting channel {channel} coupling to {coupling.upper()}")
        self.write(f"CH{channel}:COUPling {coupling.upper()}")
    
    @parameter_validator(
        channel=lambda c: c > 0,
        position=lambda p: -5 <= p <= 5  # Typical range for vertical position
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_vertical_position(self, channel: int, position: float) -> None:
        """Set the vertical position for the specified channel.

        Args:
            channel: The channel number.
            position: The vertical position (typically -5 to 5 divisions).
            
        Raises:
            ValueError: If channel or position is invalid.
        """
        # Validate channel
        if channel > self.max_channels:
            raise ValueError(f"Channel {channel} is invalid. This oscilloscope has {self.max_channels} channels.")
            
        logger.debug(f"Setting channel {channel} vertical position to {position}")
        self.write(f"CH{channel}:POSition {position}")
    
    @parameter_validator(
        trigger_source=lambda s: s.startswith("CH") or s in ["EXT", "LINE", "WGEN"]
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_trigger_source(self, trigger_source: str) -> None:
        """Set the trigger source.

        Args:
            trigger_source: The trigger source (CH1, CH2, EXT, etc.).
            
        Raises:
            ValueError: If trigger source is invalid.
        """
        logger.debug(f"Setting trigger source to {trigger_source}")
        self.write(f"TRIGger:A:EDGE:SOUrce {trigger_source}")
    
    @parameter_validator(
        trigger_level=lambda l: -1000 <= l <= 1000  # Wide range to accommodate various signal levels
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_trigger_level(self, trigger_level: float) -> None:
        """Set the trigger level.

        Args:
            trigger_level: The trigger level in volts.
            
        Raises:
            ValueError: If trigger level is outside valid range.
        """
        logger.debug(f"Setting trigger level to {trigger_level}V")
        self.write(f"TRIGger:A:LEVel {trigger_level}")
    
    @parameter_validator(
        acquisition_mode=lambda m: m.upper() in ["SAMPLE", "AVERAGE", "ENVELOPE", "PEAK", "HIRES"]
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_acquisition_mode(self, acquisition_mode: str) -> None:
        """Set the acquisition mode.

        Args:
            acquisition_mode: The acquisition mode (SAMPLE, AVERAGE, ENVELOPE, etc.).
            
        Raises:
            ValueError: If acquisition mode is invalid.
        """
        logger.debug(f"Setting acquisition mode to {acquisition_mode.upper()}")
        self.write(f"ACQuire:MODe {acquisition_mode.upper()}")
    

class TektronixTDS2000(OscilloscopeBase):
    """Class for Tektronix TDS2000 Series Digital Oscilloscopes.
    
    This class supports the TDS1000, TDS2000, TDS1000B, TDS2000B, and TDS1000C-EDU series.
    These are popular entry-level digital oscilloscopes with 2 channels.
    
    The TDS2000 series offers up to 100MHz bandwidth and 2GS/s sample rate.
    """
    
    def __init__(self, instrument_address: str, nickname: str = None, identify: bool = True):
        """Initialize connection to a Tektronix TDS2000 series oscilloscope.
        
        Args:
            instrument_address: VISA address of the instrument.
            nickname: User-defined name for the instrument.
            identify: Whether to identify the instrument with *IDN?.
        """
        # TDS2000 series typically has 2 channels
        super().__init__(instrument_address, nickname, identify, max_channels=2)
        logger.info(f"Initialized Tektronix TDS2000 series oscilloscope at {instrument_address}")
    
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def lock_front_panel(self) -> None:
        """Lock the front panel controls."""
        logger.debug("Locking front panel")
        self.write("LOCk ALL")
    
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def unlock_front_panel(self) -> None:
        """Unlock the front panel controls."""
        logger.debug("Unlocking front panel")
        self.write("UNLock ALL")


class TektronixDPO2000(OscilloscopeBase):
    """Class for Tektronix DPO/MSO2000 Series Digital Oscilloscopes.
    
    This class supports the DPO2000 and MSO2000 series. These are mid-range
    oscilloscopes with more advanced features than the TDS series.
    
    The DPO2000 series offers up to 200MHz bandwidth and 1GS/s sample rate with 4 channels.
    """
    
    def __init__(self, instrument_address: str, nickname: str = None, identify: bool = True):
        """Initialize connection to a Tektronix DPO/MSO2000 series oscilloscope.
        
        Args:
            instrument_address: VISA address of the instrument.
            nickname: User-defined name for the instrument.
            identify: Whether to identify the instrument with *IDN?.
        """
        # DPO2000 series typically has 4 channels
        super().__init__(instrument_address, nickname, identify, max_channels=4)
        logger.info(f"Initialized Tektronix DPO/MSO2000 series oscilloscope at {instrument_address}")
    
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def enable_channel(self, channel: int, state: bool = True) -> None:
        """Enable or disable a channel.
        
        Args:
            channel: Channel number
            state: True to enable, False to disable
        """
        # Validate channel
        if channel > self.max_channels:
            logger.error(f"Channel {channel} is invalid. This oscilloscope has {self.max_channels} channels.")
            return
            
        logger.debug(f"{'Enabling' if state else 'Disabling'} channel {channel}")
        self.write(f"SELECT:CH{channel} {1 if state else 0}")
    
    @visa_exception_handler(default_return_value={}, module_logger=logger)
    def get_measurement_statistics(self, measurement_type: str, channel: int) -> Dict[str, float]:
        """Get statistics for a measurement.
        
        Args:
            measurement_type: Type of measurement (MEAN, FREQUENCY, etc.)
            channel: Channel number
            
        Returns:
            Dictionary with statistics (mean, min, max, stddev)
        """
        # Validate channel
        if channel > self.max_channels:
            logger.error(f"Channel {channel} is invalid. This oscilloscope has {self.max_channels} channels.")
            return {}
            
        # Setup measurement
        self.write(f"MEASUrement:IMMed:SOUrce1 CH{channel}")
        self.write(f"MEASUrement:IMMed:TYPe {measurement_type}")
        self.write("MEASUrement:IMMed:STATistics:STATE ON")
        
        # Get statistics
        mean = float(self.query("MEASUrement:IMMed:STATistics:MEAN?"))
        minimum = float(self.query("MEASUrement:IMMed:STATistics:MINimum?"))
        maximum = float(self.query("MEASUrement:IMMed:STATistics:MAXimum?"))
        stddev = float(self.query("MEASUrement:IMMed:STATistics:STDdev?"))
        
        results = {
            "mean": mean,
            "min": minimum,
            "max": maximum,
            "stddev": stddev
        }
        
        logger.debug(f"Measurement statistics for {measurement_type} on CH{channel}: {results}")
        return results
        

class TektronixMDO3000(OscilloscopeBase):
    """Class for Tektronix MDO3000 Series Mixed Domain Oscilloscopes.
    
    This class supports the MDO3000 series, which are advanced oscilloscopes
    with integrated spectrum analyzer functionality.
    
    The MDO3000 series offers up to 1GHz bandwidth and 5GS/s sample rate.
    """
    
    def __init__(self, instrument_address: str, nickname: str = None, identify: bool = True):
        """Initialize connection to a Tektronix MDO3000 series oscilloscope.
        
        Args:
            instrument_address: VISA address of the instrument.
            nickname: User-defined name for the instrument.
            identify: Whether to identify the instrument with *IDN?.
        """
        # MDO3000 series typically has 4 channels
        super().__init__(instrument_address, nickname, identify, max_channels=4)
        logger.info(f"Initialized Tektronix MDO3000 series oscilloscope at {instrument_address}")
    
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_frequency_domain(self, state: bool = True) -> None:
        """Switch to frequency domain (spectrum analyzer) mode.
        
        Args:
            state: True to enable frequency domain, False for time domain
        """
        logger.debug(f"{'Enabling' if state else 'Disabling'} frequency domain")
        self.write(f"SPECTrum:STATE {1 if state else 0}")
    
    @parameter_validator(
        start_freq=lambda f: f > 0,
        stop_freq=lambda f: f > 0
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_frequency_span(self, start_freq: float, stop_freq: float) -> None:
        """Set the frequency span for spectrum analyzer mode.
        
        Args:
            start_freq: Start frequency in Hz
            stop_freq: Stop frequency in Hz
            
        Raises:
            ValueError: If frequencies are invalid
        """
        if start_freq >= stop_freq:
            raise ValueError("Start frequency must be less than stop frequency")
            
        logger.debug(f"Setting frequency span: {start_freq}Hz to {stop_freq}Hz")
        self.write(f"SPECTrum:FREQuency:STARt {start_freq}")
        self.write(f"SPECTrum:FREQuency:STOP {stop_freq}")
    
    @visa_exception_handler(default_return_value=(np.array([]), np.array([])), module_logger=logger)
    def acquire_spectrum(self, show: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """Acquire spectrum analyzer data.
        
        Args:
            show: Whether to display the spectrum
            
        Returns:
            tuple: Frequency and amplitude data arrays
        """
        logger.info("Acquiring spectrum data")
        
        # Ensure we're in frequency domain
        self.set_frequency_domain(True)
        
        # Get the data
        self.write("SPECTrum:SOURce CH1")  # Usually spectrum is from CH1
        self.write("DATa:SOUrce SPECTrum")
        self.write("DATa:ENCdg ASCIi")
        self.write("WFMOutpre:ENCdg ASCIi")
        self.write("CURVE?")
        
        data = self.connection.read_raw()
        header_len = 2 + int(data[1])
        values = data[header_len:-1]
        amplitudes = np.array([float(val) for val in values.split(b',')])
        
        # Get frequency axis
        start_freq = float(self.query("SPECTrum:FREQuency:STARt?"))
        stop_freq = float(self.query("SPECTrum:FREQuency:STOP?"))
        frequencies = np.linspace(start_freq, stop_freq, len(amplitudes))
        
        if show:
            pylab.figure()
            pylab.plot(frequencies / 1e6, amplitudes)  # Convert to MHz for display
            pylab.xlabel('Frequency (MHz)')
            pylab.ylabel('Amplitude (dBm)')
            pylab.title('Spectrum Analyzer')
            pylab.grid(True)
            pylab.show()
        
        logger.debug(f"Acquired {len(amplitudes)} spectrum points")
        return frequencies, amplitudes


class TektronixTBS1000(OscilloscopeBase):
    """Class for Tektronix TBS1000 Series Digital Oscilloscopes.
    
    This class supports the TBS1000, TBS1000B, and TBS1000B-EDU series.
    These are modern entry-level digital oscilloscopes with 2 channels.
    
    The TBS1000 series offers up to 100MHz bandwidth and 1GS/s sample rate.
    """
    
    def __init__(self, instrument_address: str, nickname: str = None, identify: bool = True):
        """Initialize connection to a Tektronix TBS1000 series oscilloscope.
        
        Args:
            instrument_address: VISA address of the instrument.
            nickname: User-defined name for the instrument.
            identify: Whether to identify the instrument with *IDN?.
        """
        # TBS1000 series typically has 2 channels
        super().__init__(instrument_address, nickname, identify, max_channels=2)
        logger.info(f"Initialized Tektronix TBS1000 series oscilloscope at {instrument_address}")
    
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_bandwidth_limit(self, channel: int, state: bool = True) -> None:
        """Enable or disable bandwidth limiting on a channel.
        
        Bandwidth limiting acts as a low-pass filter to reduce noise.
        
        Args:
            channel: Channel number
            state: True to enable bandwidth limiting, False to disable
        """
        # Validate channel
        if channel > self.max_channels:
            logger.error(f"Channel {channel} is invalid. This oscilloscope has {self.max_channels} channels.")
            return
            
        logger.debug(f"{'Enabling' if state else 'Disabling'} bandwidth limit on channel {channel}")
        self.write(f"CH{channel}:BANdwidth {20e6 if state else 0}")  # 20MHz BW limit or full bandwidth
        
    @parameter_validator(percent=lambda p: 0 <= p <= 100)
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_trigger_holdoff(self, percent: float) -> None:
        """Set trigger holdoff as a percentage of the maximum holdoff time.
        
        Args:
            percent: Percentage of maximum holdoff time (0-100)
            
        Raises:
            ValueError: If percentage is outside valid range
        """
        logger.debug(f"Setting trigger holdoff to {percent}% of maximum")
        self.write(f"TRIGger:HOLDoff:PERCent {percent}")


# For backward compatibility, default to the most common model
class Oscilloscope(TektronixTDS2000):
    """Legacy class for backward compatibility.
    
    This class inherits from TektronixTDS2000 to maintain compatibility
    with existing code. New code should use the specific model classes.
    """
    pass