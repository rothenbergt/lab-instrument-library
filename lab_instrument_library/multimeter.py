"""
Python library for controlling laboratory digital multimeters.

This module provides a standardized interface for working with various lab 
multimeters regardless of manufacturer or model differences. It supports
voltage, current, and resistance measurements in different modes.

Supported devices:
- HP 34401A
- Keithley 2000 
- Keithley 2110
- Tektronix DMM4050

Documentation references:
- HP 34401A: https://engineering.purdue.edu/~aae520/hp34401manual.pdf
- Keithley 2000: https://download.tek.com/manual/2000-900_J-Aug2010_User.pdf
- Keithley 2110: https://download.tek.com/manual/2110-901-01(C-Aug2013)(Ref).pdf
- Tektronix DMM4050: https://download.tek.com/manual/077036300web_0.pdf
"""
import inspect
import sys
import pyvisa
import logging
import time
import numpy as np
from typing import Optional, Union, Callable, Any, Dict, List, Tuple
from abc import ABC, abstractmethod
from .base import LibraryTemplate
from .utils.decorators import visa_exception_handler, parameter_validator, retry

# Setup module logger
logger = logging.getLogger(__name__)

# Valid measurement functions for all multimeters
VALID_FUNCTIONS = [
    "VOLT", "VOLT:DC", "VOLT:AC", 
    "CURR", "CURR:DC", "CURR:AC",
    "RES", "FRES", "FREQ", "CONT", "DIOD", "TEMP"
]

class MultimeterBase(LibraryTemplate, ABC):
    """Base class for all multimeters.
    
    This abstract base class provides common functionality for different multimeter models.
    It implements methods for basic measurement operations that are shared across
    various laboratory multimeter instruments.
    
    Attributes:
        instrument_address: The VISA address of the connected multimeter.
        connection: The PyVISA resource connection object.
        instrumentID: The identification string of the connected instrument.
        nickname: A user-provided name for the instrument (optional).
    """
    
    def __init__(self, instrument_address: str, nickname: Optional[str] = None,
                identify: bool = True, timeout: int = 5000):
        """Initialize a connection to the multimeter.

        Args:
            instrument_address: VISA address of the instrument.
            nickname: User-defined name for the instrument.
            identify: Whether to identify the instrument with *IDN?.
            timeout: Connection timeout in milliseconds.
        """
        super().__init__(instrument_address, nickname, identify, timeout)
        logger.info(f"Initialized {self.__class__.__name__} at {instrument_address}")
    
    @parameter_validator(function=lambda f: f.upper() in [fn.upper() for fn in VALID_FUNCTIONS])
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_function(self, function: str) -> str:
        """Set the measurement function.

        Args:
            function: The measurement function to set (e.g., "VOLT", "CURR", "RES").
                    Common functions: "VOLT" (DC voltage), "VOLT:AC" (AC voltage),
                    "CURR" (DC current), "CURR:AC" (AC current), "RES" (resistance).
            
        Returns:
            str: The current selected function.
        
        Raises:
            ValueError: If function is not supported.
        """
        self.write(f":CONF:{function}")
        return self.get_function()
    
    @visa_exception_handler(default_return_value="VOLT", module_logger=logger)
    def get_function(self) -> str:
        """Get the currently selected measurement function.

        Returns:
            str: The current selected function.
        """
        current_function = self.query("FUNC?")
        return current_function.strip("\n").strip("\"")

    @parameter_validator(function=lambda f: f.upper() in [fn.upper() for fn in VALID_FUNCTIONS])
    @visa_exception_handler(default_return_value=0.0, module_logger=logger)
    def measure(self, function: str) -> float:
        """Perform a measurement using the specified function.
        
        This method configures the multimeter for the specified measurement function,
        triggers a measurement and returns the result.
        
        Args:
            function: The measurement function (e.g., "VOLT", "CURR", "RES").
            
        Returns:
            float: The measured value or 0.0 if an error occurred.
        """
        # If the function is already set, we don't need to set it again
        current_function = self.get_function()
        if current_function.upper() != function.upper():
            self.set_function(function)
        
        # Use MEASure command for a complete measurement
        response = self.query(f"MEAS:{function}?")
        return float(response.strip())
        
    @visa_exception_handler(default_return_value=0.0, module_logger=logger)
    def read(self, function: Optional[str] = None) -> float:
        """Perform measurement and acquire reading.
        
        Unlike measure(), this method reuses the current configuration
        and just triggers a new reading.
        
        Args:
            function: Optional function to set before reading.
            
        Returns:
            float: The measured value or 0.0 if an error occurred.
        """
        # Set function if specified
        if function:
            current_function = self.get_function()
            if current_function.upper() != function.upper():
                self.set_function(function)
        
        # Get a reading
        response = self.query("READ?")
        return float(response.strip())
        
    @visa_exception_handler(default_return_value=0.0, module_logger=logger)
    def fetch(self, function: Optional[str] = None) -> float:
        """Fetch the latest reading without triggering a new measurement.
        
        Args:
            function: Optional function to set before fetching.
            
        Returns:
            float: The measured value or 0.0 if an error occurred.
        """
        # Set function if specified
        if function:
            current_function = self.get_function()
            if current_function.upper() != function.upper():
                self.set_function(function)
        
        # Initiate a measurement
        self.initiate()
        
        # Fetch the result
        response = self.query("FETC?")
        return float(response.strip())
    
    @visa_exception_handler(default_return_value=False, module_logger=logger)
    def initiate(self) -> bool:
        """Initiate a measurement (change to waiting-for-trigger state).
        
        Returns:
            bool: True if the command was sent successfully.
        """
        self.write("INIT")
        return True
    
    # Convenience methods for common measurements
    
    @visa_exception_handler(default_return_value=0.0, module_logger=logger)
    def measure_voltage(self) -> float:
        """Measure DC voltage.
        
        Returns:
            float: The measured DC voltage in volts.
        """
        return self.measure("VOLT")
    
    @visa_exception_handler(default_return_value=0.0, module_logger=logger)
    def measure_voltage_ac(self) -> float:
        """Measure AC voltage.
        
        Returns:
            float: The measured AC voltage in volts.
        """
        return self.measure("VOLT:AC")
    
    @visa_exception_handler(default_return_value=0.0, module_logger=logger)
    def measure_current(self) -> float:
        """Measure DC current.
        
        Returns:
            float: The measured DC current in amps.
        """
        return self.measure("CURR")
    
    @visa_exception_handler(default_return_value=0.0, module_logger=logger)
    def measure_current_ac(self) -> float:
        """Measure AC current.
        
        Returns:
            float: The measured AC current in amps.
        """
        return self.measure("CURR:AC")
    
    @visa_exception_handler(default_return_value=0.0, module_logger=logger)
    def measure_resistance(self) -> float:
        """Measure resistance.
        
        Returns:
            float: The measured resistance in ohms.
        """
        return self.measure("RES")
    
    @parameter_validator(
        function=lambda f: f.upper() in [fn.upper() for fn in VALID_FUNCTIONS],
        samples=lambda s: s > 0,
        delay=lambda d: d >= 0
    )
    @visa_exception_handler(default_return_value={}, module_logger=logger)
    def measure_statistics(self, function: str = "VOLT", samples: int = 10, 
                         delay: float = 0.1) -> Dict[str, float]:
        """Measure multiple samples and return statistics.
        
        Args:
            function: Measurement function ("VOLT", "CURR", etc.)
            samples: Number of samples to take
            delay: Delay between samples in seconds
            
        Returns:
            Dictionary of statistical values (min, max, mean, std_dev)
        """
        # Set the measurement function
        self.set_function(function)
        
        # Take measurements
        measurements = []
        for _ in range(samples):
            value = self.read()
            measurements.append(value)
            time.sleep(delay)
            
        # Calculate statistics
        measurements = np.array(measurements)
        result = {
            "min": float(np.min(measurements)),
            "max": float(np.max(measurements)),
            "mean": float(np.mean(measurements)),
            "std_dev": float(np.std(measurements)),
            "samples": samples
        }
        
        logger.info(f"Measured {samples} {function} readings, mean: {result['mean']}, std_dev: {result['std_dev']}")
        return result
    
    @parameter_validator(
        function=lambda f: f.upper() in [fn.upper() for fn in VALID_FUNCTIONS],
        range_value=lambda r: r > 0
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_range(self, function: str, range_value: float) -> None:
        """Set the measurement range for the specified function.
        
        Args:
            function: Measurement function ("VOLT", "CURR", etc.)
            range_value: Range value in appropriate units
        """
        self.write(f"{function}:RANG {range_value}")
        logger.debug(f"Set {function} range to {range_value}")
    
    @parameter_validator(function=lambda f: f.upper() in [fn.upper() for fn in VALID_FUNCTIONS])
    @visa_exception_handler(default_return_value=0.0, module_logger=logger)
    def get_range(self, function: str) -> float:
        """Get the current measurement range for the specified function.
        
        Args:
            function: Measurement function ("VOLT", "CURR", etc.)
            
        Returns:
            float: The current range setting
        """
        response = self.query(f"{function}:RANG?")
        return float(response.strip())
    
    @parameter_validator(
        function=lambda f: f.upper() in [fn.upper() for fn in VALID_FUNCTIONS],
        state=lambda s: isinstance(s, bool)
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_auto_range(self, function: str, state: bool = True) -> None:
        """Enable or disable auto-ranging for the specified function.
        
        Args:
            function: Measurement function ("VOLT", "CURR", etc.)
            state: True to enable auto-range, False to disable
        """
        self.write(f"{function}:RANG:AUTO {1 if state else 0}")
        logger.debug(f"Set {function} auto-range to {'ON' if state else 'OFF'}")
    
    @parameter_validator(function=lambda f: f.upper() in [fn.upper() for fn in VALID_FUNCTIONS])
    @visa_exception_handler(default_return_value=False, module_logger=logger)
    def get_auto_range_state(self, function: str) -> bool:
        """Get the current auto-range state for the specified function.
        
        Args:
            function: Measurement function ("VOLT", "CURR", etc.)
            
        Returns:
            bool: True if auto-range is enabled, False otherwise
        """
        response = self.query(f"{function}:RANG:AUTO?").strip()
        return response == "1" or response.upper() == "ON"
    
    @parameter_validator(
        source=lambda s: s.upper() in ["IMM", "EXT", "BUS"],
        count=lambda c: c > 0
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def setup_trigger(self, source: str = "IMM", count: int = 1) -> None:
        """Configure trigger settings.
        
        Args:
            source: Trigger source ("IMM", "EXT", "BUS")
            count: Trigger count
        """
        self.write(f"TRIG:SOUR {source}")
        self.write(f"TRIG:COUN {count}")
        logger.info(f"Set trigger source to {source}, count to {count}")
    
    @visa_exception_handler(default_return_value="0,No Error", module_logger=logger)
    def get_error(self) -> str:
        """Get the first error from the error queue.
        
        Returns:
            str: Error message or "0,No Error" if no errors.
        """
        response = self.query("SYST:ERR?").strip("\n")
        if not response.startswith("0,"):
            logger.warning(f"Error in multimeter: {response}")
        return response
    
    @visa_exception_handler(default_return_value=False, module_logger=logger)
    def reset(self) -> bool:
        """Reset the instrument to factory settings.
        
        Returns:
            bool: True if reset succeeded, False otherwise.
        """
        logger.info(f"Resetting {self.__class__.__name__}")
        return super().reset()
    
    @visa_exception_handler(default_return_value=False, module_logger=logger)
    def clear(self) -> bool:
        """Clear the instrument's status registers and error queue.
        
        Returns:
            bool: True if clear succeeded, False otherwise.
        """
        logger.info(f"Clearing {self.__class__.__name__} status")
        return super().clear()
    
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def close(self) -> None:
        """Close the connection to the multimeter.
        
        This method should be called when finished using the instrument.
        """
        logger.info(f"Closing connection to {self.__class__.__name__}")
        super().close_connection()


class HP34401A(MultimeterBase):
    """Class for HP 34401A Digital Multimeter.
    
    The HP 34401A is a 6½-digit, high-performance digital multimeter
    with fast autoranging and high precision measurements.
    """
    
    def __init__(self, instrument_address: str, nickname: Optional[str] = None,
                identify: bool = True, timeout: int = 5000):
        """Initialize connection to an HP 34401A multimeter.
        
        Args:
            instrument_address: VISA address of the instrument.
            nickname: User-defined name for the instrument.
            identify: Whether to identify the instrument with *IDN?.
            timeout: Connection timeout in milliseconds.
        """
        super().__init__(instrument_address, nickname, identify, timeout)
        
        # Apply model-specific configuration
        self.write("DISP:TEXT:CLE")  # Clear the display
        logger.info(f"Initialized HP 34401A multimeter at {instrument_address}")
    
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def display_text(self, text: str) -> None:
        """Display text on the multimeter's front panel.
        
        Args:
            text: The text to display (up to 12 characters)
        """
        # Truncate text if needed - HP 34401A has a 12-character limit
        if len(text) > 12:
            text = text[:12]
        
        self.write(f'DISP:TEXT "{text}"')
        logger.debug(f"Displayed text: {text}")
    
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def clear_display(self) -> None:
        """Clear the custom text from the display."""
        self.write("DISP:TEXT:CLE")
        logger.debug("Cleared display text")
    
    @parameter_validator(nplc=lambda n: 0.02 <= n <= 100)
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_integration_time(self, nplc: float) -> None:
        """Set the integration time for measurements.
        
        Args:
            nplc: Number of power line cycles (0.02 to 100)
                Higher values give more accuracy but slower measurements
                
        Raises:
            ValueError: If NPLC is out of range
        """
        # Get the current function
        current_function = self.get_function()
        
        # Set integration time for current function
        self.write(f"{current_function}:NPLC {nplc}")
        logger.debug(f"Set integration time to {nplc} NPLC for {current_function}")
        
    @parameter_validator(
        samples=lambda s: 1 <= s <= 512,
        count=lambda c: 1 <= c <= 50000
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def setup_data_logging(self, samples: int = 10, count: int = 1, delay: float = 0.0) -> None:
        """Configure built-in data logging (useful for autonomous operation).
        
        Args:
            samples: Number of samples per trigger (1-512)
            count: Number of triggers (1-50000) 
            delay: Delay between samples in seconds
            
        Raises:
            ValueError: If parameters are out of range
        """
        self.write(f"TRIG:COUN {count}")
        self.write(f"SAMP:COUN {samples}")
        
        if delay > 0:
            self.write(f"SAMP:TIM {delay}")
        
        logger.debug(f"Setup data logging: {samples} samples, {count} triggers, {delay}s delay")


class Keithley2000(MultimeterBase):
    """Class for Keithley 2000 Digital Multimeter.
    
    The Keithley 2000 is a 6½-digit high-performance digital multimeter 
    with extensive measurement capabilities.
    """
    
    def __init__(self, instrument_address: str, nickname: Optional[str] = None,
                identify: bool = True, timeout: int = 5000):
        """Initialize connection to a Keithley 2000 multimeter.
        
        Args:
            instrument_address: VISA address of the instrument.
            nickname: User-defined name for the instrument.
            identify: Whether to identify the instrument with *IDN?.
            timeout: Connection timeout in milliseconds.
        """
        super().__init__(instrument_address, nickname, identify, timeout)
        
        # Disable beeper for less noise in the lab
        self.write("SYST:BEEP:STAT OFF")
        logger.info(f"Initialized Keithley 2000 multimeter at {instrument_address}")
        
    @visa_exception_handler(default_return_value=0.0, module_logger=logger)
    def read(self, function: Optional[str] = None) -> float:
        """Perform measurement and acquire reading.
        
        Keithley 2000-specific implementation that handles continuous initiation.
        
        Args:
            function: Optional function to set before reading.
            
        Returns:
            float: The measured value or 0.0 if an error occurred.
        """
        # Set function if specified
        if function:
            current_function = self.get_function()
            if current_function.upper() != function.upper():
                self.set_function(function)
        
        # Disable continuous initiation for Keithley 2000
        self.write(":INIT:CONT OFF")
        
        # Get a reading
        response = self.query("READ?")
        return float(response.strip())
    
    @parameter_validator(
        state=lambda s: isinstance(s, bool),
        type=lambda t: t.upper() in ['MOV', 'REP'],
        count=lambda c: 1 <= c <= 100
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_filter(self, state: bool = True, type: str = "MOV", count: int = 10) -> None:
        """Configure the measurement filter.
        
        Args:
            state: True to enable filter, False to disable
            type: Filter type ('MOV' for moving average, 'REP' for repeating)
            count: Number of readings to average (1-100)
            
        Raises:
            ValueError: If parameters are invalid
        """
        self.write(f"SENS:AVER:TCON {type}")
        self.write(f"SENS:AVER:COUN {count}")
        self.write(f"SENS:AVER {'ON' if state else 'OFF'}")
        
        logger.debug(f"Set filter: {'enabled' if state else 'disabled'}, type={type}, count={count}")
    
    @parameter_validator(
        thermocouple_type=lambda t: t.upper() in ['J', 'K', 'T', 'E', 'R', 'S', 'B', 'N']
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_thermocouple_type(self, thermocouple_type: str) -> None:
        """Set the thermocouple type for temperature measurements.
        
        Args:
            thermocouple_type: Thermocouple type (J, K, T, E, R, S, B, N)
            
        Raises:
            ValueError: If thermocouple_type is invalid
        """
        self.write(f"TEMP:TC:TYPE {thermocouple_type}")
        logger.debug(f"Set thermocouple type to {thermocouple_type}")
    
    @visa_exception_handler(default_return_value="K", module_logger=logger)
    def get_thermocouple_type(self) -> str:
        """Get the current thermocouple type setting.
        
        Returns:
            str: The thermocouple type
        """
        return self.query("TEMP:TC:TYPE?").strip()


class Keithley2110(MultimeterBase):
    """Class for Keithley 2110 Digital Multimeter.
    
    The Keithley 2110 is a 5½-digit digital multimeter designed for 
    general purpose bench or systems applications.
    """
    
    def __init__(self, instrument_address: str, nickname: Optional[str] = None,
                identify: bool = True, timeout: int = 5000):
        """Initialize connection to a Keithley 2110 multimeter.
        
        Args:
            instrument_address: VISA address of the instrument.
            nickname: User-defined name for the instrument.
            identify: Whether to identify the instrument with *IDN?.
            timeout: Connection timeout in milliseconds.
        """
        super().__init__(instrument_address, nickname, identify, timeout)
        
        # Disable beeper for less noise in the lab
        self.write("SYST:BEEP:STAT OFF")
        logger.info(f"Initialized Keithley 2110 multimeter at {instrument_address}")
    
    @parameter_validator(
        state=lambda s: isinstance(s, bool),
        type=lambda t: t.upper() in ['MOV', 'REP'],
        count=lambda c: 1 <= c <= 100
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_filter(self, state: bool = True, type: str = "MOV", count: int = 10) -> None:
        """Configure the measurement filter.
        
        Args:
            state: True to enable filter, False to disable
            type: Filter type ('MOV' for moving average, 'REP' for repeating)
            count: Number of readings to average (1-100)
            
        Raises:
            ValueError: If parameters are invalid
        """
        self.write(f"SENS:AVER:TCON {type}")
        self.write(f"SENS:AVER:COUN {count}")
        self.write(f"SENS:AVER {'ON' if state else 'OFF'}")
        
        logger.debug(f"Set filter: {'enabled' if state else 'disabled'}, type={type}, count={count}")
    
    @parameter_validator(
        thermocouple_type=lambda t: t.upper() in ['J', 'K', 'T', 'E', 'R', 'S', 'B', 'N']
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_thermocouple_type(self, thermocouple_type: str) -> None:
        """Set the thermocouple type for temperature measurements.
        
        Args:
            thermocouple_type: Thermocouple type (J, K, T, E, R, S, B, N)
            
        Raises:
            ValueError: If thermocouple_type is invalid
        """
        self.write(f"TC:TYPE {thermocouple_type}")
        logger.debug(f"Set thermocouple type to {thermocouple_type}")
    
    @visa_exception_handler(default_return_value="K", module_logger=logger)
    def get_thermocouple_type(self) -> str:
        """Get the current thermocouple type setting.
        
        Returns:
            str: The thermocouple type
        """
        return self.query("TC:TYPE?").strip()
        
    @parameter_validator(
        unit=lambda u: u.upper() in ['C', 'CEL', 'F', 'FAR', 'K']
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_temperature_unit(self, unit: str) -> None:
        """Set the temperature measurement unit.
        
        Args:
            unit: Temperature unit ('C'/'CEL' for Celsius, 
                                   'F'/'FAR' for Fahrenheit, 
                                   'K' for Kelvin)
                                   
        Raises:
            ValueError: If the unit is invalid
        """
        # Standardize input
        if unit.upper() in ['C', 'CEL']:
            std_unit = 'CEL'
        elif unit.upper() in ['F', 'FAR']:
            std_unit = 'FAR'
        else:
            std_unit = 'K'
            
        self.write(f"UNIT:TEMP {std_unit}")
        logger.debug(f"Set temperature unit to {std_unit}")


class TektronixDMM4050(MultimeterBase):
    """Class for Tektronix DMM4050 Digital Multimeter.
    
    The Tektronix DMM4050 is a 6½-digit precision digital multimeter with
    extensive measurement and analysis capabilities.
    """
    
    def __init__(self, instrument_address: str, nickname: Optional[str] = None,
                identify: bool = True, timeout: int = 5000):
        """Initialize connection to a Tektronix DMM4050 multimeter.
        
        Args:
            instrument_address: VISA address of the instrument.
            nickname: User-defined name for the instrument.
            identify: Whether to identify the instrument with *IDN?.
            timeout: Connection timeout in milliseconds.
        """
        super().__init__(instrument_address, nickname, identify, timeout)
        logger.info(f"Initialized Tektronix DMM4050 multimeter at {instrument_address}")
    
    @parameter_validator(
        primary_function=lambda f: f.upper() in [fn.upper() for fn in VALID_FUNCTIONS],
        secondary_function=lambda f: f.upper() in [fn.upper() for fn in VALID_FUNCTIONS]
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def enable_dual_display(self, primary_function: str, secondary_function: str) -> None:
        """Configure the dual display mode.
        
        Args:
            primary_function: Primary measurement function
            secondary_function: Secondary measurement function
            
        Raises:
            ValueError: If function names are invalid
        """
        self.set_function(primary_function)
        self.write(f"SENS:FUNC2 \"{secondary_function}\"")
        self.write("DISP:WIND2:STAT ON")
        
        logger.debug(f"Enabled dual display: primary={primary_function}, secondary={secondary_function}")
    
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def disable_dual_display(self) -> None:
        """Disable the dual display mode."""
        self.write("DISP:WIND2:STAT OFF")
        logger.debug("Disabled dual display")
    
    @visa_exception_handler(default_return_value=(0.0, 0.0), module_logger=logger)
    def read_dual_display(self) -> Tuple[float, float]:
        """Read both primary and secondary measurements.
        
        Returns:
            tuple: (primary_value, secondary_value)
        """
        # Initiate and fetch primary measurement
        primary = self.read()
        
        # Fetch secondary measurement
        secondary = float(self.query("SENS:DATA2?").strip())
        
        return primary, secondary
    
    @parameter_validator(
        rjunction_type=lambda t: t.upper() in ['INT', 'EXT', 'SIM']
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_temperature_reference_junction(self, rjunction_type: str, sim_value: float = 0.0) -> None:
        """Set the reference junction type for thermocouple measurements.
        
        Args:
            rjunction_type: Reference junction type ('INT', 'EXT', or 'SIM')
            sim_value: Simulated junction temperature value (when using 'SIM')
            
        Raises:
            ValueError: If junction type is invalid
        """
        self.write(f"TEMP:TRAN:TC:RJUN:TYPE {rjunction_type}")
        
        if rjunction_type.upper() == 'SIM':
            self.write(f"TEMP:TRAN:TC:RJUN:SIM {sim_value}")
            
        logger.debug(f"Set reference junction to {rjunction_type}")
