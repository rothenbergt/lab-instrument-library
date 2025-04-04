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
from .utils.decorators import visa_exception_handler, parameter_validator, retry

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
    
    # Valid waveform functions for this instrument
    VALID_FUNCTIONS = ["SIN", "SQU", "RAMP", "PULSE", "NOIS", "DC", "USER"]
    
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

    @parameter_validator(
        function=lambda f: f.upper() in AFG3000.VALID_FUNCTIONS,
        channel=lambda c: c in [1, 2]
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_function(self, function: str, channel: int = 1) -> None:
        """Sets the waveform function for the specified channel.

        Args:
            function: The waveform function (e.g., "SIN", "SQU", "RAMP", "PULSE", "NOIS").
            channel: The output channel (1 or 2).
            
        Raises:
            ValueError: If an invalid function or channel is specified.
        """
        logger.debug(f"Setting channel {channel} function to {function}")
        self.write(f"FUNCtion{channel} {function.upper()}")

    @parameter_validator(
        channel=lambda c: c in [1, 2],
        frequency=lambda f: 0 < f < 100e6  # AFG3000 typically has a max frequency of 100MHz
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_frequency(self, channel: int, frequency: float) -> None:
        """Sets the frequency for the specified channel.

        Args:
            channel: The output channel (1 or 2).
            frequency: The frequency in Hz (must be positive and within the instrument's range).
            
        Raises:
            ValueError: If an invalid channel or frequency value is specified.
        """
        logger.debug(f"Setting channel {channel} frequency to {frequency} Hz")
        self.write(f"FREQuency{channel} {frequency}")

    @parameter_validator(
        channel=lambda c: c in [1, 2],
        amplitude=lambda a: 0 <= a <= 10  # AFG3000 typically has a max amplitude of 10Vpp
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_amplitude(self, channel: int, amplitude: float) -> None:
        """Sets the amplitude for the specified channel.

        Args:
            channel: The output channel (1 or 2).
            amplitude: The amplitude in Vpp (0-10V range for most AFG3000 models).
            
        Raises:
            ValueError: If an invalid channel or amplitude value is specified.
        """
        logger.debug(f"Setting channel {channel} amplitude to {amplitude} Vpp")
        self.write(f"VOLTage{channel} {amplitude}")

    @parameter_validator(
        channel=lambda c: c in [1, 2],
        offset=lambda o: -5 <= o <= 5  # Typical AFG3000 offset range
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_offset(self, channel: int, offset: float) -> None:
        """Sets the offset for the specified channel.

        Args:
            channel: The output channel (1 or 2).
            offset: The offset in volts (typically -5V to +5V for AFG3000).
            
        Raises:
            ValueError: If an invalid channel or offset value is specified.
        """
        logger.debug(f"Setting channel {channel} offset to {offset} V")
        self.write(f"VOLTage:OFFSet{channel} {offset}")

    @parameter_validator(
        channel=lambda c: c in [1, 2],
        phase=lambda p: 0 <= p < 360
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_phase(self, channel: int, phase: float) -> None:
        """Sets the phase for the specified channel.

        Args:
            channel: The output channel (1 or 2).
            phase: The phase in degrees (0-360).
            
        Raises:
            ValueError: If an invalid channel or phase value is specified.
        """
        logger.debug(f"Setting channel {channel} phase to {phase} degrees")
        self.write(f"PHASe{channel} {phase}")

    @parameter_validator(channel=lambda c: c in [1, 2])
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def enable_output(self, channel: int) -> None:
        """Enables the output for the specified channel.

        Args:
            channel: The output channel (1 or 2).
            
        Raises:
            ValueError: If an invalid channel is specified.
        """
        logger.info(f"Enabling channel {channel} output")
        self.write(f"OUTPut{channel}:STATe ON")

    @parameter_validator(channel=lambda c: c in [1, 2])
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def disable_output(self, channel: int) -> None:
        """Disables the output for the specified channel.

        Args:
            channel: The output channel (1 or 2).
            
        Raises:
            ValueError: If an invalid channel is specified.
        """
        logger.info(f"Disabling channel {channel} output")
        self.write(f"OUTPut{channel}:STATe OFF")

    @parameter_validator(channel=lambda c: c in [1, 2])
    @visa_exception_handler(default_return_value="OFF", module_logger=logger)
    def get_output_state(self, channel: int) -> str:
        """Gets the output state for the specified channel.

        Args:
            channel: The output channel (1 or 2).

        Returns:
            str: The output state ("ON" or "OFF").
            
        Raises:
            ValueError: If an invalid channel is specified.
        """
        response = self.query(f"OUTPut{channel}:STATe?").strip()
        logger.debug(f"Channel {channel} output state is {response}")
        return response

    @visa_exception_handler(default_return_value="0,No Error", module_logger=logger)
    def get_error(self) -> str:
        """Gets the first error in the error buffer.

        Returns:
            str: The error message or "0,No Error" if no errors.
        """
        response = self.query("SYSTem:ERRor?").strip("\n")
        if not response.startswith("0,"):
            logger.warning(f"Error in function generator: {response}")
        return response
    
    @parameter_validator(
        channel=lambda c: c in [1, 2],
        duty_cycle=lambda d: 0 <= d <= 100
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_duty_cycle(self, channel: int, duty_cycle: float) -> None:
        """Set the duty cycle for pulse/square waveforms.
        
        Args:
            channel: Output channel (1 or 2)
            duty_cycle: Duty cycle percentage (0-100)
            
        Raises:
            ValueError: If an invalid channel or duty cycle value is specified.
        """
        logger.debug(f"Setting channel {channel} duty cycle to {duty_cycle}%")
        self.write(f"PULS:DCYC{channel} {duty_cycle}")

    @parameter_validator(
        channel=lambda c: c in [1, 2],
        start_freq=lambda f: f > 0,
        stop_freq=lambda f: f > 0,
        sweep_time=lambda t: t > 0
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger, retry_count=1)
    def set_sweep(self, channel: int, start_freq: float, stop_freq: float, sweep_time: float) -> None:
        """Configure a frequency sweep.
        
        Args:
            channel: Output channel (1 or 2)
            start_freq: Start frequency in Hz (must be positive)
            stop_freq: Stop frequency in Hz (must be positive)
            sweep_time: Sweep time in seconds (must be positive)
            
        Raises:
            ValueError: If invalid channel or parameter values are specified.
        """
        logger.info(f"Setting up frequency sweep on channel {channel}")
        
        self.write(f"FREQ{channel}:STAR {start_freq}")
        self.write(f"FREQ{channel}:STOP {stop_freq}")
        self.write(f"SWE{channel}:TIME {sweep_time}")
        self.write(f"SWE{channel}:STAT ON")
        
        logger.info(f"Configured sweep from {start_freq} Hz to {stop_freq} Hz in {sweep_time} seconds")

    @parameter_validator(
        channel=lambda c: c in [1, 2],
        sample_rate=lambda s: s > 0
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger, retry_count=2, retry_delay=2.0)
    def output_arbitrary_waveform(self, channel: int, waveform_data: List[float], 
                                 sample_rate: float = 10e6) -> None:
        """Load and output an arbitrary waveform.
        
        Args:
            channel: Output channel (1 or 2)
            waveform_data: List of waveform points (-1.0 to 1.0)
            sample_rate: Sample rate in samples per second
            
        Raises:
            ValueError: If invalid channel or parameter values are specified.
        """
        if not waveform_data:
            raise ValueError("Waveform data cannot be empty")
        
        if len(waveform_data) < 2 or len(waveform_data) > 131072:  # Typical limit for AFG3000
            raise ValueError(f"Waveform length must be between 2 and 131072 points, got {len(waveform_data)}")
        
        # Normalize data to ensure it's between -1 and 1
        max_val = max(max(waveform_data), abs(min(waveform_data)), 1)
        normalized_data = [val/max_val for val in waveform_data]
        
        # Use temporary timeout for longer operation
        with self.temporary_timeout(30000):  # 30 seconds timeout for large waveforms
            try:
                # Convert to binary format
                self.connection.write_binary_values(
                    f"DATA:DAC{channel} VOLATILE,", normalized_data, datatype='f'
                )
                
                # Set to arbitrary function
                self.set_function("USER", channel)
                
                # Set sample rate
                self.write(f"FUNC{channel}:USER:FREQ {sample_rate}")
                
                logger.info(f"Loaded arbitrary waveform with {len(waveform_data)} points to channel {channel}")
            except Exception as e:
                logger.error(f"Failed to load arbitrary waveform: {str(e)}")
                raise
    
    @visa_exception_handler(default_return_value=False, module_logger=logger)
    def reset(self) -> bool:
        """Reset the instrument to factory settings.
        
        Returns:
            bool: True if reset succeeded, False otherwise.
        """
        logger.info("Resetting function generator")
        return super().reset()
    
    @visa_exception_handler(default_return_value=False, module_logger=logger)
    def clear(self) -> bool:
        """Clear the instrument's status registers and error queue.
        
        Returns:
            bool: True if clear succeeded, False otherwise.
        """
        logger.info("Clearing function generator status")
        return super().clear()
    
    @visa_exception_handler(default_return_value=None, module_logger=logger)
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
        
    def __str__(self) -> str:
        """Return a string representation of the function generator.
        
        Returns:
            str: String representation including address and ID.
        """
        return f"AFG3000 Function Generator at {self.instrument_address} ({self.instrumentID if self.instrumentID else 'Not identified'})"
        
    @parameter_validator(
        channel=lambda c: c in [1, 2],
        burst_count=lambda b: b > 0,
        burst_period=lambda p: p > 0
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def setup_burst_mode(self, channel: int, burst_count: int, burst_period: float) -> None:
        """Configure burst mode operation.
        
        Args:
            channel: Output channel (1 or 2)
            burst_count: Number of cycles in each burst (1 or more)
            burst_period: Burst period in seconds (must be positive)
            
        Raises:
            ValueError: If invalid parameters are specified.
        """
        logger.info(f"Setting up burst mode on channel {channel}")
        
        self.write(f"BURS{channel}:STAT ON")
        self.write(f"BURS{channel}:NCYC {burst_count}")
        self.write(f"BURS{channel}:INT:PER {burst_period}")
        
        logger.info(f"Configured burst mode with {burst_count} cycles and {burst_period}s period")