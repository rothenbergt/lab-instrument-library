"""
Python library containing general functions to control Keithley SMUs.

This module provides functions for controlling Keithley 228 and 238 Source Measure Units.
These instruments are commonly used for precision sourcing and measurement of voltage
and current in semiconductor testing and characterization applications.

Supported devices:
- Keithley 228 Voltage/Current Source
- Keithley 238 High Current Source Measure Unit

Documentation references:
- Keithley 236/237/238 Operator's Manual: https://cores.research.asu.edu/sites/default/files/2021-04/Keithley%20237%20Operations%20Manual_0.pdf
- Keithley 228 Manual (Tektronix): https://www.tek.com/en/manual/keithley-model-228-voltage-current-source-instruction-manual-rev-c
"""

import logging
import time
from abc import ABC
from typing import Any, Dict, List, Tuple, TypeVar

import numpy as np

from .base import LibraryTemplate
from .utils.decorators import parameter_validator, visa_exception_handler

# Setup module logger
logger = logging.getLogger(__name__)

# Type variable for the Keithley classes
T = TypeVar('T', bound='KeithlyBaseSMU')


class KeithlyBaseSMU(LibraryTemplate, ABC):
    """Base class for Keithley Source Measure Units.

    This abstract base class provides common functionality for different Keithley SMU models.
    It implements methods for basic source and measurement operations that are shared across
    various Keithley SMU instruments.

    Attributes:
        instrument_address: The VISA address of the connected SMU.
        connection: The PyVISA resource connection object.
        instrumentID: The identification string of the connected instrument.
        nickname: A user-provided name for the instrument (optional).
        voltage_range: Current voltage range setting
        current_range: Current current range setting
        is_output_enabled: Whether the output is currently enabled
    """

    # Default limits - should be overridden by subclasses
    MAX_VOLTAGE = 100.0  # Default max voltage in volts
    MAX_CURRENT = 1.0  # Default max current in amps

    def __init__(self, instrument_address: str, nickname: str = None, identify: bool = True):
        """Initialize a connection to the Keithley SMU.

        Args:
            instrument_address: VISA address of the instrument.
            nickname: User-defined name for the instrument.
            identify: Whether to identify the instrument with *IDN?.
        """
        super().__init__(instrument_address, nickname, identify)
        logger.info(f"Initialized Keithley SMU at {instrument_address}")

        # Track instrument state
        self.voltage_range = None
        self.current_range = None
        self.is_output_enabled = False

        # Set longer timeout for some operations
        self.connection.timeout = 10000

    @parameter_validator(voltage=lambda v: abs(v) <= KeithlyBaseSMU.MAX_VOLTAGE)
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_voltage(self, voltage: float) -> None:
        """Set the output voltage of the SMU.

        Args:
            voltage: The desired output voltage (must be within the instrument's limits).

        Raises:
            ValueError: If voltage exceeds instrument limits.
        """
        logger.debug(f"Setting voltage to {voltage}V")
        self.write(f"SOUR:VOLT {voltage}")

    @parameter_validator(current=lambda i: abs(i) <= KeithlyBaseSMU.MAX_CURRENT)
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_current(self, current: float) -> None:
        """Set the output current of the SMU.

        Args:
            current: The desired output current (must be within the instrument's limits).

        Raises:
            ValueError: If current exceeds instrument limits.
        """
        logger.debug(f"Setting current to {current}A")
        self.write(f"SOUR:CURR {current}")

    @visa_exception_handler(default_return_value=0.0, module_logger=logger)
    def measure_voltage(self) -> float:
        """Measure the output voltage of the SMU.

        Returns:
            float: The measured output voltage or 0.0 on error.
        """
        response = self.query("MEAS:VOLT?")
        result = float(response.strip())
        logger.debug(f"Measured voltage: {result}V")
        return result

    @visa_exception_handler(default_return_value=0.0, module_logger=logger)
    def measure_current(self) -> float:
        """Measure the output current of the SMU.

        Returns:
            float: The measured output current or 0.0 on error.
        """
        response = self.query("MEAS:CURR?")
        result = float(response.strip())
        logger.debug(f"Measured current: {result}A")
        return result

    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def enable_output(self) -> None:
        """Enable the output of the SMU."""
        logger.info("Enabling SMU output")
        self.write("OUTP ON")
        self.is_output_enabled = True

    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def disable_output(self) -> None:
        """Disable the output of the SMU."""
        logger.info("Disabling SMU output")
        self.write("OUTP OFF")
        self.is_output_enabled = False

    @visa_exception_handler(default_return_value=False, module_logger=logger)
    def reset(self) -> bool:
        """Reset the instrument to factory settings.

        Returns:
            bool: True if reset succeeded, False otherwise.
        """
        logger.info(f"Resetting {self.__class__.__name__}")
        success = super().reset()
        if success:
            # Reset tracking variables after successful reset
            self.is_output_enabled = False
        return success

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
        """Close the connection to the SMU.

        Ensures output is disabled before closing for safety.
        """
        try:
            if self.is_output_enabled:
                self.disable_output()
        except Exception as e:
            logger.warning(f"Error disabling output during close: {str(e)}")

        logger.info(f"Closing {self.__class__.__name__} connection")
        super().close_connection()

    @parameter_validator(
        start=lambda v: abs(v) <= KeithlyBaseSMU.MAX_VOLTAGE,
        stop=lambda v: abs(v) <= KeithlyBaseSMU.MAX_VOLTAGE,
        steps=lambda s: s > 0,
        compliance=lambda c: c > 0,
        delay=lambda d: d >= 0,
    )
    @visa_exception_handler(default_return_value=[], module_logger=logger)
    def perform_voltage_sweep(
        self, start: float, stop: float, steps: int, compliance: float = 0.1, delay: float = 0.1
    ) -> List[Dict[str, float]]:
        """Perform a voltage sweep and measure current at each point.

        Args:
            start: Start voltage
            stop: Stop voltage
            steps: Number of steps
            compliance: Current compliance limit
            delay: Delay between points in seconds

        Returns:
            List of dictionaries with voltage and current measurements
        """
        # Create voltage points
        voltages = np.linspace(start, stop, steps)
        results = []

        # Store current state
        original_state = self._save_state()

        # Configure sweep
        self.write(f"SOUR:CURR:COMP {compliance}")

        try:
            # Enable output if it's not already on
            if not self.is_output_enabled:
                self.enable_output()

            for voltage in voltages:
                # Set voltage
                self.set_voltage(voltage)
                time.sleep(delay)

                # Measure
                measured_v = self.measure_voltage()
                measured_i = self.measure_current()

                results.append({"voltage": measured_v, "current": measured_i, "timestamp": time.time()})

            return results
        except Exception as e:
            logger.error(f"Error during voltage sweep: {str(e)}")
            # Set voltage to 0 for safety
            self.set_voltage(0)
            return results
        finally:
            # Restore original state
            self._restore_state(original_state)

    @parameter_validator(mode=lambda m: m.upper() in ['VOLT', 'CURR'])
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def configure_output_mode(self, mode: str) -> None:
        """Configure the output mode of the SMU.

        Args:
            mode: Output mode ('VOLT' for voltage source, 'CURR' for current source)

        Raises:
            ValueError: If mode is not 'VOLT' or 'CURR'
        """
        self.write(f"SOUR:FUNC:MODE {mode.upper()}")
        logger.info(f"Set source function to {mode.upper()}")

    @parameter_validator(voltage_limit=lambda v: v > 0, current_limit=lambda i: i > 0)
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def configure_limits(self, voltage_limit: float, current_limit: float) -> None:
        """Configure the voltage and current limits.

        Args:
            voltage_limit: Maximum allowed voltage
            current_limit: Maximum allowed current
        """
        self.write(f"SENS:VOLT:PROT {voltage_limit}")
        self.write(f"SENS:CURR:PROT {current_limit}")
        logger.info(f"Set limits: voltage={voltage_limit}V, current={current_limit}A")

    @visa_exception_handler(default_return_value=(0.0, 0.0), module_logger=logger)
    def measure_both(self) -> Tuple[float, float]:
        """Measure both voltage and current.

        Returns:
            Tuple containing (voltage, current) measurements
        """
        voltage = self.measure_voltage()
        current = self.measure_current()
        return voltage, current

    def _save_state(self) -> Dict[str, Any]:
        """Save the current state of the instrument.

        Returns:
            Dictionary containing current state parameters
        """
        state = {"output_enabled": self.is_output_enabled}
        return state

    def _restore_state(self, state: Dict[str, Any]) -> None:
        """Restore a previously saved state.

        Args:
            state: Dictionary containing state parameters
        """
        # Restore output state
        if state["output_enabled"] and not self.is_output_enabled:
            self.enable_output()
        elif not state["output_enabled"] and self.is_output_enabled:
            self.disable_output()

    def __str__(self) -> str:
        """Return a string representation of the SMU.

        Returns:
            String representation with model and address
        """
        return f"{self.__class__.__name__} at {self.instrument_address} ({self.instrumentID if self.instrumentID else 'Not identified'})"


class Keithly228(KeithlyBaseSMU):
    """Class for interfacing with Keithley 228 Source Measure Unit.

    This class provides methods for basic source and measurement operations
    with Keithley 228 SMUs.

    The Keithley 228 is designed for precision voltage/current source/measure
    applications requiring high accuracy.
    """

    # Override with model-specific limits
    MAX_VOLTAGE = 100.0  # Maximum output voltage in volts
    MAX_CURRENT = 1.0  # Maximum output current in amps

    def __init__(self, instrument_address: str, nickname: str = None, identify: bool = True):
        """Initialize the Keithley 228 SMU instance.

        Args:
            instrument_address: The VISA address of the instrument.
            nickname: User-defined name for the instrument.
            identify: Whether to query the instrument ID on connection.
        """
        super().__init__(instrument_address, nickname, identify)
        logger.info(f"Initialized Keithley 228 SMU at {instrument_address}")

        # Apply model-specific setup
        self.write("SYST:BEEP:STAT OFF")  # Disable beeper

    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_voltage_range(self, voltage_range: float) -> None:
        """Set the voltage measurement range.

        Args:
            voltage_range: Voltage range in volts
        """
        self.write(f"SENS:VOLT:RANG {voltage_range}")
        self.voltage_range = voltage_range
        logger.debug(f"Set voltage range to {voltage_range}V")

    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_current_range(self, current_range: float) -> None:
        """Set the current measurement range.

        Args:
            current_range: Current range in amps
        """
        self.write(f"SENS:CURR:RANG {current_range}")
        self.current_range = current_range
        logger.debug(f"Set current range to {current_range}A")

    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_auto_range(self, mode: str, state: bool = True) -> None:
        """Configure auto-ranging for voltage or current.

        Args:
            mode: 'VOLT' or 'CURR'
            state: True to enable auto-range, False to disable
        """
        if mode.upper() not in ['VOLT', 'CURR']:
            raise ValueError("Mode must be 'VOLT' or 'CURR'")

        self.write(f"SENS:{mode}:RANG:AUTO {1 if state else 0}")
        logger.debug(f"Set {mode} auto-range to {'ON' if state else 'OFF'}")


class Keithly238(KeithlyBaseSMU):
    """Class for interfacing with Keithley 238 Source Measure Unit.

    This class provides methods for basic source and measurement operations
    with Keithley 238 SMUs.

    The Keithley 238 is a high current source-measure unit designed for
    high precision current and voltage sourcing and measurement.
    """

    # Override with model-specific limits
    MAX_VOLTAGE = 110.0  # Maximum output voltage in volts
    MAX_CURRENT = 1.5  # Maximum output current in amps

    def __init__(self, instrument_address: str, nickname: str = None, identify: bool = True):
        """Initialize the Keithley 238 SMU instance.

        Args:
            instrument_address: The VISA address of the instrument.
            nickname: User-defined name for the instrument.
            identify: Whether to query the instrument ID on connection.
        """
        super().__init__(instrument_address, nickname, identify)
        logger.info(f"Initialized Keithley 238 SMU at {instrument_address}")

        # Apply model-specific setup
        self.write("SYST:BEEP:STAT OFF")  # Disable beeper

    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def set_integration_time(self, nplc: float) -> None:
        """Set the measurement integration time.

        Args:
            nplc: Integration time in number of power line cycles (0.01-10)
                Higher values give more accuracy but slower measurements
        """
        if not 0.01 <= nplc <= 10:
            raise ValueError("NPLC must be between 0.01 and 10")

        self.write(f"SENS:NPLC {nplc}")
        logger.debug(f"Set integration time to {nplc} NPLC")

    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def configure_filter(self, count: int = 10, mode: str = "MOV") -> None:
        """Configure the measurement filter.

        Args:
            count: Number of readings to average (1-100)
            mode: Filter mode ('MOV' for moving average, 'REP' for repeating)
        """
        if not 1 <= count <= 100:
            raise ValueError("Count must be between 1 and 100")

        if mode.upper() not in ['MOV', 'REP']:
            raise ValueError("Mode must be 'MOV' or 'REP'")

        self.write(f"SENS:AVER:COUN {count}")
        self.write(f"SENS:AVER:TCON {mode}")
        self.write("SENS:AVER ON")

        logger.debug(f"Configured filter: mode={mode}, count={count}")

    @parameter_validator(
        start=lambda v: abs(v) <= Keithly238.MAX_VOLTAGE,
        stop=lambda v: abs(v) <= Keithly238.MAX_VOLTAGE,
        steps=lambda s: s > 0,
    )
    @visa_exception_handler(default_return_value=None, module_logger=logger, retry_count=1)
    def configure_built_in_sweep(self, start: float, stop: float, steps: int) -> None:
        """Configure the instrument's built-in sweep functionality.

        The Keithley 238 has built-in sweep capability that can be more
        efficient than manually stepping through voltages.

        Args:
            start: Start voltage
            stop: Stop voltage
            steps: Number of steps
        """
        self.write(f"SOUR:VOLT:STAR {start}")
        self.write(f"SOUR:VOLT:STOP {stop}")
        self.write(f"SOUR:VOLT:STEP {(stop-start)/(steps-1 if steps > 1 else 1)}")
        self.write("SOUR:VOLT:MODE SWE")

        logger.info(f"Configured built-in sweep from {start}V to {stop}V in {steps} steps")
