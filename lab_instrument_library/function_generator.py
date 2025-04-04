"""
Python library containing general functions to control Tektronix AFG3000 series.

This module provides a standardized interface for working with function generators
to generate various waveforms, set frequency, amplitude and other signal parameters.

Supported devices:
- Tektronix AFG3000 series (AFG3052C, etc.)

Documentation references:
- Tektronix AFG3000: https://www.tek.com/en/function-generator/afg3000-function-generator-manual/afg3000-series
"""

import sys
import inspect
import logging
from typing import Optional, Union, Dict, List, Any
from .base import LibraryTemplate
from .utils import visa_exception_handler

# Setup module logger
logger = logging.getLogger(__name__)

class AFG3000(LibraryTemplate):
    """Class for interfacing with Tektronix AFG3000 series function generators.
    
    This class provides methods to control Tektronix AFG3000 series function generators,
    including setting waveform type, frequency, amplitude, and other signal parameters.
    
    Attributes:
        instrument_address: The VISA address of the connected function generator.
        connection: The PyVISA resource connection object.
        instrumentID: The identification string of the connected instrument.
        nickname: A user-provided name for the instrument (optional).
    """
    
    def __init__(self, instrument_address: str, nickname: str = None, identify: bool = True):
        """Initialize a connection to the function generator.

        Args:
            instrument_address: VISA address of the instrument.
            nickname: User-defined name for the instrument.
            identify: Whether to identify the instrument with *IDN?.
        """      
        super().__init__(instrument_address, nickname, identify)
        logger.info(f"Initialized AFG3000 at {instrument_address}")
        
        # Set longer timeout for some operations
        self.connection.timeout = 10000

    @visa_exception_handler(module_logger=logger)
    def set_function(self, function: str, channel: int = 1) -> None:
        """Sets the waveform function for the specified channel.

        Args:
            function: The waveform function (e.g., "SIN", "SQU", "RAMP", "PULSE", "NOISE").
            channel: The output channel (1 or 2).
        """
        if channel not in [1, 2]:
            logger.warning(f"Invalid channel {channel}, must be 1 or 2")
            return
            
        logger.debug(f"Setting channel {channel} function to {function}")
        self.write(f"FUNCtion{channel} {function}")

    @visa_exception_handler(module_logger=logger)
    def set_frequency(self, channel: int, frequency: float) -> None:
        """Sets the frequency for the specified channel.

        Args:
            channel: The output channel (1 or 2).
            frequency: The frequency in Hz.
        """
        if channel not in [1, 2]:
            logger.warning(f"Invalid channel {channel}, must be 1 or 2")
            return
            
        logger.debug(f"Setting channel {channel} frequency to {frequency} Hz")
        self.write(f"FREQuency{channel} {frequency}")

    @visa_exception_handler(module_logger=logger)
    def set_amplitude(self, channel: int, amplitude: float) -> None:
        """Sets the amplitude for the specified channel.

        Args:
            channel: The output channel (1 or 2).
            amplitude: The amplitude in Vpp.
        """
        if channel not in [1, 2]:
            logger.warning(f"Invalid channel {channel}, must be 1 or 2")
            return
            
        logger.debug(f"Setting channel {channel} amplitude to {amplitude} Vpp")
        self.write(f"VOLTage{channel} {amplitude}")

    @visa_exception_handler(module_logger=logger)
    def set_offset(self, channel: int, offset: float) -> None:
        """Sets the offset for the specified channel.

        Args:
            channel: The output channel (1 or 2).
            offset: The offset in volts.
        """
        if channel not in [1, 2]:
            logger.warning(f"Invalid channel {channel}, must be 1 or 2")
            return
            
        logger.debug(f"Setting channel {channel} offset to {offset} V")
        self.write(f"VOLTage:OFFSet{channel} {offset}")

    @visa_exception_handler(module_logger=logger)
    def set_phase(self, channel: int, phase: float) -> None:
        """Sets the phase for the specified channel.

        Args:
            channel: The output channel (1 or 2).
            phase: The phase in degrees.
        """
        if channel not in [1, 2]:
            logger.warning(f"Invalid channel {channel}, must be 1 or 2")
            return
            
        logger.debug(f"Setting channel {channel} phase to {phase} degrees")
        self.write(f"PHASe{channel} {phase}")

    @visa_exception_handler(module_logger=logger)
    def enable_output(self, channel: int) -> None:
        """Enables the output for the specified channel.

        Args:
            channel: The output channel (1 or 2).
        """
        if channel not in [1, 2]:
            logger.warning(f"Invalid channel {channel}, must be 1 or 2")
            return
            
        logger.info(f"Enabling channel {channel} output")
        self.write(f"OUTPut{channel}:STATe ON")

    @visa_exception_handler(module_logger=logger)
    def disable_output(self, channel: int) -> None:
        """Disables the output for the specified channel.

        Args:
            channel: The output channel (1 or 2).
        """
        if channel not in [1, 2]:
            logger.warning(f"Invalid channel {channel}, must be 1 or 2")
            return
            
        logger.info(f"Disabling channel {channel} output")
        self.write(f"OUTPut{channel}:STATe OFF")

    @visa_exception_handler(module_logger=logger)
    def get_output_state(self, channel: int) -> str:
        """Gets the output state for the specified channel.

        Args:
            channel: The output channel (1 or 2).

        Returns:
            str: The output state ("ON" or "OFF").
        """
        if channel not in [1, 2]:
            logger.warning(f"Invalid channel {channel}, must be 1 or 2")
            return "OFF"
            
        response = self.query(f"OUTPut{channel}:STATe?").strip()
        logger.debug(f"Channel {channel} output state is {response}")
        return response

    @visa_exception_handler(module_logger=logger)
    def get_error(self) -> str:
        """Gets the first error in the error buffer.

        Returns:
            str: The error message or "0,No Error" if no errors.
        """
        response = self.query("SYSTem:ERRor?").strip("\n")
        if not response.startswith("0,"):
            logger.warning(f"Error in function generator: {response}")
        return response
    
    @visa_exception_handler(module_logger=logger)
    def set_duty_cycle(self, channel: int, duty_cycle: float) -> None:
        """Set the duty cycle for pulse/square waveforms.
        
        Args:
            channel: Output channel (1 or 2)
            duty_cycle: Duty cycle percentage (0-100)
        """
        if channel not in [1, 2]:
            logger.warning(f"Invalid channel {channel}, must be 1 or 2")
            return
            
        if not 0 <= duty_cycle <= 100:
            logger.warning(f"Invalid duty cycle {duty_cycle}, must be between 0-100%")
            return
            
        logger.debug(f"Setting channel {channel} duty cycle to {duty_cycle}%")
        self.write(f"PULS:DCYC{channel} {duty_cycle}")

    @visa_exception_handler(module_logger=logger)
    def set_sweep(self, channel: int, start_freq: float, stop_freq: float, sweep_time: float) -> None:
        """Configure a frequency sweep.
        
        Args:
            channel: Output channel (1 or 2)
            start_freq: Start frequency in Hz
            stop_freq: Stop frequency in Hz
            sweep_time: Sweep time in seconds
        """
        if channel not in [1, 2]:
            logger.warning(f"Invalid channel {channel}, must be 1 or 2")
            return
            
        logger.info(f"Setting up frequency sweep on channel {channel}")
        
        self.write(f"FREQ{channel}:STAR {start_freq}")
        self.write(f"FREQ{channel}:STOP {stop_freq}")
        self.write(f"SWE{channel}:TIME {sweep_time}")
        self.write(f"SWE{channel}:STAT ON")
        
        logger.info(f"Configured sweep from {start_freq} Hz to {stop_freq} Hz in {sweep_time} seconds")

    @visa_exception_handler(module_logger=logger)
    def output_arbitrary_waveform(self, channel: int, waveform_data: List[float], 
                                 sample_rate: float = 10e6) -> None:
        """Load and output an arbitrary waveform.
        
        Args:
            channel: Output channel (1 or 2)
            waveform_data: List of waveform points (-1.0 to 1.0)
            sample_rate: Sample rate in samples per second
        """
        if channel not in [1, 2]:
            logger.warning(f"Invalid channel {channel}, must be 1 or 2")
            return
        
        # Normalize data to ensure it's between -1 and 1
        max_val = max(max(waveform_data), abs(min(waveform_data)), 1)
        normalized_data = [val/max_val for val in waveform_data]
        
        # Convert to binary format
        binary_data = self.connection.write_binary_values(
            f"DATA:DAC{channel} VOLATILE,", normalized_data, datatype='f'
        )
        
        # Set to arbitrary function
        self.set_function("USER", channel)
        
        # Set sample rate
        self.write(f"FUNC{channel}:USER:FREQ {sample_rate}")
        
        logger.info(f"Loaded arbitrary waveform with {len(waveform_data)} points to channel {channel}")
    
    def reset(self) -> bool:
        """Reset the instrument to factory settings.
        
        Returns:
            bool: True if reset succeeded, False otherwise.
        """
        logger.info("Resetting function generator")
        return super().reset()
    
    def clear(self) -> bool:
        """Clear the instrument's status registers and error queue.
        
        Returns:
            bool: True if clear succeeded, False otherwise.
        """
        logger.info("Clearing function generator status")
        return super().clear()
    
    def close(self) -> None:
        """Close the connection to the function generator.
        
        Disables all outputs before closing for safety.
        """
        try:
            # Try to disable both channels before closing
            self.disable_output(1)
            self.disable_output(2)
        except Exception as e:
            logger.warning(f"Error disabling outputs during close: {str(e)}")
        
        logger.info("Closing function generator connection")
        super().close_connection()