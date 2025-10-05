"""
Python library for controlling Source Measure Units (SMUs) from various manufacturers.

This module provides a standardized interface for working with Source Measure Units
to perform precision voltage/current sourcing and measurement.

Supported devices:
- Keysight B2902A

Documentation references:
- Keysight B2902A Programming Guide: https://assets.testequity.com/te1/Documents/pdf/B2900A-prog.pdf
- Keysight B2902A User Guide: https://assets.testequity.com/te1/Documents/pdf/B2900A-ug.pdf
"""

from abc import ABC, abstractmethod
from .base import LibraryTemplate
from .utils import visa_exception_handler
from typing import Dict, Optional, Union, List, Any, Tuple, Callable
import numpy as np
import time
import sys
import logging
import re

# Setup module logger
logger = logging.getLogger(__name__)


class SMUBase(LibraryTemplate, ABC):
    """Base class for Source Measure Units.
    
    This abstract base class provides common functionality for different SMU models.
    It implements methods for basic source and measurement operations that are shared across
    various SMU instruments.
    
    Attributes:
        instrument_address (str): VISA address of the instrument
        connection: PyVISA resource connection to the instrument
        instrumentID (str): Identification string of the instrument
        nickname (str): Optional user-defined name for the instrument
    """
    
    # Default limits - should be overridden by subclasses
    MAX_VOLTAGE = 60.0  # Default max voltage in volts
    MAX_CURRENT = 3.0   # Default max current in amps
    
    def __init__(self, instrument_address: str, nickname: str = None, 
                identify: bool = True, timeout: int = 5000):
        """Initialize the SMU base class.
        
        Args:
            instrument_address: VISA address of the instrument
            nickname: User-defined name for the instrument
            identify: Whether to identify the instrument with *IDN?
            timeout: Connection timeout in milliseconds
        """
        super().__init__(instrument_address, nickname, identify, timeout)
        logger.info(f"Initialized SMU connection at {instrument_address}")
    
    @abstractmethod
    def set_voltage(self, voltage: float, current_limit: float = 0.1, channel: int = 1) -> None:
        """Set the output voltage and current limit.
        
        Args:
            voltage: Target voltage in volts
            current_limit: Current limit in amperes
            channel: Output channel (1 or 2)
        """
        pass
    
    @abstractmethod
    def set_current(self, current: float, voltage_limit: float = 10.0, channel: int = 1) -> None:
        """Set the output current and voltage limit.
        
        Args:
            current: Target current in amperes
            voltage_limit: Voltage limit in volts
            channel: Output channel (1 or 2)
        """
        pass
    
    @abstractmethod
    def measure_voltage(self, channel: int = 1) -> float:
        """Measure the actual output voltage.
        
        Args:
            channel: Output channel (1 or 2)
            
        Returns:
            float: The measured voltage in volts
        """
        pass
    
    @abstractmethod
    def measure_current(self, channel: int = 1) -> float:
        """Measure the actual output current.
        
        Args:
            channel: Output channel (1 or 2)
            
        Returns:
            float: The measured current in amperes
        """
        pass
    
    @abstractmethod
    def enable_output(self, channel: int = 1) -> None:
        """Enable the output of the specified channel.
        
        Args:
            channel: Output channel (1 or 2)
        """
        pass
    
    @abstractmethod
    def disable_output(self, channel: int = 1) -> None:
        """Disable the output of the specified channel.
        
        Args:
            channel: Output channel (1 or 2)
        """
        pass
    
    # Common implementations that might work across SMU types
    
    def get_all_measurements(self, channel: int = 1) -> Dict[str, float]:
        """Get all measurements for a channel.
        
        Args:
            channel: Output channel (1 or 2)
            
        Returns:
            Dict with voltage, current, resistance and power measurements
        """
        voltage = self.measure_voltage(channel)
        current = self.measure_current(channel)
        
        # Calculate resistance and power
        if abs(current) > 1e-12:  # Avoid division by zero
            resistance = voltage / current
        else:
            resistance = float('inf')
            
        power = voltage * current
        
        return {
            "voltage": voltage,
            "current": current,
            "resistance": resistance,
            "power": power
        }
    
    def measure_resistance(self, channel: int = 1) -> float:
        """Measure resistance using V/I calculation.
        
        Args:
            channel: Channel number (1 or 2)
            
        Returns:
            float: Resistance in ohms
        """
        voltage = self.measure_voltage(channel)
        current = self.measure_current(channel)
        
        if abs(current) > 1e-12:  # Avoid division by zero
            resistance = voltage / current
        else:
            resistance = float('inf')
            
        logger.debug(f"Measured resistance on channel {channel}: {resistance} ohms")
        return resistance
    
    def measure_power(self, channel: int = 1) -> float:
        """Measure power using V*I calculation.
        
        Args:
            channel: Channel number (1 or 2)
            
        Returns:
            float: Power in watts
        """
        voltage = self.measure_voltage(channel)
        current = self.measure_current(channel)
        power = voltage * current
        
        logger.debug(f"Measured power on channel {channel}: {power} watts")
        return power
    
    def close(self) -> None:
        """Close the connection to the instrument safely.
        
        This disables outputs before closing to ensure safety.
        """
        try:
            # Try to disable outputs for safety
            self.disable_output(1)
            try:
                # Some SMUs might have a second channel
                self.disable_output(2)
            except Exception:
                pass
            logger.info("Disabled all outputs")
        except Exception as e:
            logger.warning(f"Error disabling outputs: {str(e)}")
            
        # Close the connection
        super().close_connection()
        logger.info("Closed connection to SMU")


class KeysightB2902A(SMUBase):
    """Enhanced controller for Keysight B2902A Source Measure Unit.
    
    This class extends the basic SMU functionality with advanced features
    specific to the Keysight B2902A, including arbitrary waveform generation,
    pulse mode, advanced triggering, sweeps, and digitization capabilities.
    
    Attributes:
        instrument_address (str): VISA address of the instrument
        connection: PyVISA resource connection to the instrument
        instrumentID (str): Identification string of the instrument
        nickname (str): Optional user-defined name for the instrument
    """
    
    def __init__(self, instrument_address: str, nickname: str = None, identify: bool = True):
        """Initialize the Keysight B2902A SMU instance.
        
        Args:
            instrument_address: VISA address of the instrument
            nickname: User-defined name for the instrument
            identify: Whether to identify the instrument with *IDN?
        """
        super().__init__(instrument_address, nickname, identify)
        logger.info(f"Initialized Keysight B2902A SMU at {instrument_address}")
        
        # Increase timeout for longer operations
        self.connection.timeout = 10000  # 10 seconds
        
        # Store the current function mode for each channel
        self._function_mode = {1: "VOLT", 2: "VOLT"}
        
    #-----------------------------------------------------------------------
    # Basic Functions (Setting voltage/current, enabling outputs, etc.)
    #-----------------------------------------------------------------------
    
    @visa_exception_handler(module_logger=logger)
    def set_voltage(self, voltage: float, current_limit: float = 0.1, channel: int = 1) -> None:
        """Set the output voltage and current limit.
        
        Args:
            voltage: Target voltage in volts
            current_limit: Current limit in amperes
            channel: Output channel (1 or 2)
        """
        logger.debug(f"Setting channel {channel} voltage to {voltage}V with {current_limit}A limit")
        self.write(f"SOUR{channel}:VOLT {voltage}")
        self.write(f"SOUR{channel}:CURR:LIMIT {current_limit}")
        self._function_mode[channel] = "VOLT"
    
    @visa_exception_handler(module_logger=logger)
    def set_current(self, current: float, voltage_limit: float = 10.0, channel: int = 1) -> None:
        """Set the output current and voltage limit.
        
        Args:
            current: Target current in amperes
            voltage_limit: Voltage limit in volts
            channel: Output channel (1 or 2)
        """
        logger.debug(f"Setting channel {channel} current to {current}A with {voltage_limit}V limit")
        self.write(f"SOUR{channel}:CURR {current}")
        self.write(f"SOUR{channel}:VOLT:LIMIT {voltage_limit}")
        self._function_mode[channel] = "CURR"
    
    @visa_exception_handler(module_logger=logger)
    def get_voltage(self, channel: int = 1) -> float:
        """Get the set voltage value.
        
        Args:
            channel: Output channel (1 or 2)
            
        Returns:
            float: The set voltage in volts
        """
        response = self.query(f"SOUR{channel}:VOLT?")
        return float(response.strip())
    
    @visa_exception_handler(module_logger=logger)
    def get_current(self, channel: int = 1) -> float:
        """Get the set current value.
        
        Args:
            channel: Output channel (1 or 2)
            
        Returns:
            float: The set current in amperes
        """
        response = self.query(f"SOUR{channel}:CURR?")
        return float(response.strip())
    
    @visa_exception_handler(module_logger=logger)
    def measure_voltage(self, channel: int = 1) -> float:
        """Measure the actual output voltage.
        
        Args:
            channel: Output channel (1 or 2)
            
        Returns:
            float: The measured voltage in volts
        """
        response = self.query(f"MEAS:VOLT? (@{channel})")
        return float(response.strip())
    
    @visa_exception_handler(module_logger=logger)
    def measure_current(self, channel: int = 1) -> float:
        """Measure the actual output current.
        
        Args:
            channel: Output channel (1 or 2)
            
        Returns:
            float: The measured current in amperes
        """
        response = self.query(f"MEAS:CURR? (@{channel})")
        return float(response.strip())
    
    @visa_exception_handler(module_logger=logger)
    def get_all_measurements(self, channel: int = 1) -> Dict[str, float]:
        """Get all measurements for a channel.
        
        Args:
            channel: Output channel (1 or 2)
            
        Returns:
            Dict with voltage, current, resistance and power measurements
        """
        voltage = self.measure_voltage(channel)
        current = self.measure_current(channel)
        
        # Calculate resistance and power
        if abs(current) > 1e-12:  # Avoid division by zero
            resistance = voltage / current
        else:
            resistance = float('inf')
            
        power = voltage * current
        
        return {
            "voltage": voltage,
            "current": current,
            "resistance": resistance,
            "power": power
        }
    
    @visa_exception_handler(module_logger=logger)
    def ch1_on(self) -> None:
        """Enable the output of channel 1."""
        self.enable_output(1)
    
    @visa_exception_handler(module_logger=logger)
    def ch2_on(self) -> None:
        """Enable the output of channel 2."""
        self.enable_output(2)
    
    @visa_exception_handler(module_logger=logger)
    def ch1_off(self) -> None:
        """Disable the output of channel 1."""
        self.disable_output(1)
    
    @visa_exception_handler(module_logger=logger)
    def ch2_off(self) -> None:
        """Disable the output of channel 2."""
        self.disable_output(2)
    
    @visa_exception_handler(module_logger=logger)
    def enable_output(self, channel: int = 1) -> None:
        """Enable the output of the specified channel.
        
        Args:
            channel: Output channel (1 or 2)
        """
        logger.info(f"Enabling output on channel {channel}")
        self.write(f"OUTP{channel} ON")
    
    @visa_exception_handler(module_logger=logger)
    def disable_output(self, channel: int = 1) -> None:
        """Disable the output of the specified channel.
        
        Args:
            channel: Output channel (1 or 2)
        """
        logger.info(f"Disabling output on channel {channel}")
        self.write(f"OUTP{channel} OFF")
    
    @visa_exception_handler(module_logger=logger)
    def get_output_state(self, channel: int = 1) -> bool:
        """Get the output state of the specified channel.
        
        Args:
            channel: Output channel (1 or 2)
            
        Returns:
            bool: True if output is enabled, False otherwise
        """
        response = self.query(f"OUTP{channel}?")
        return int(response.strip()) == 1
    
    @visa_exception_handler(module_logger=logger)
    def set_function(self, function: str, channel: int = 1) -> None:
        """Set the function (voltage or current source).
        
        Args:
            function: Function to set ("VOLT" or "CURR")
            channel: Output channel (1 or 2)
        """
        if function.upper() not in ["VOLT", "CURR"]:
            logger.warning(f"Invalid function: {function}. Using VOLT.")
            function = "VOLT"
            
        logger.debug(f"Setting channel {channel} function to {function}")
        self.write(f"SOUR{channel}:FUNC:MODE {function}")
        self._function_mode[channel] = function.upper()
    
    @visa_exception_handler(module_logger=logger)
    def get_function(self, channel: int = 1) -> str:
        """Get the function (voltage or current source).
        
        Args:
            channel: Output channel (1 or 2)
            
        Returns:
            str: The current function ("VOLT" or "CURR")
        """
        response = self.query(f"SOUR{channel}:FUNC:MODE?")
        mode = response.strip()
        self._function_mode[channel] = mode
        return mode
    
    @visa_exception_handler(module_logger=logger)
    def set_mode(self, channel: int, mode: str) -> None:
        """Set the operating mode.
        
        Args:
            channel: Output channel (1 or 2)
            mode: Operating mode ("VOLT", "CURR", "LIST", "SWE")
        """
        valid_modes = ["VOLT", "CURR", "CURR:DC", "VOLT:DC", "LIST", "SWE"]
        if mode.upper() not in valid_modes:
            logger.warning(f"Invalid mode: {mode}. Using VOLT.")
            mode = "VOLT"
            
        logger.debug(f"Setting channel {channel} mode to {mode}")
        self.write(f"SOUR{channel}:FUNC:MODE {mode}")
        if mode.upper() in ["VOLT", "CURR", "CURR:DC", "VOLT:DC"]:
            self._function_mode[channel] = mode.upper().split(':')[0]
    
    @visa_exception_handler(module_logger=logger)
    def set_ch1_mode(self, mode: str) -> None:
        """Set the operating mode for channel 1.
        
        Args:
            mode: Operating mode ("VOLT", "CURR", "LIST", "SWE")
        """
        self.set_mode(1, mode)
    
    @visa_exception_handler(module_logger=logger)
    def set_ch2_mode(self, mode: str) -> None:
        """Set the operating mode for channel 2.
        
        Args:
            mode: Operating mode ("VOLT", "CURR", "LIST", "SWE")
        """
        self.set_mode(2, mode)
    
    @visa_exception_handler(module_logger=logger)
    def set_mode_voltage_limit(self, channel: int, mode: str, voltage: float, limit: float) -> None:
        """Set the mode, voltage, and current limit in one command.
        
        Args:
            channel: Output channel (1 or 2)
            mode: Operating mode ("VOLT" or "CURR")
            voltage: Voltage value or limit
            limit: Current limit (for VOLT mode) or voltage limit (for CURR mode)
        """
        self.set_mode(channel, mode)
        
        if mode.upper() == "VOLT":
            self.set_voltage(voltage, limit, channel)
        else:  # mode is CURR
            self.set_current(voltage, limit, channel)
    
    @visa_exception_handler(module_logger=logger)
    def set_output_hiz(self, channel: int) -> None:
        """Set the output to high impedance mode.
        
        Args:
            channel: Output channel (1 or 2)
        """
        logger.info(f"Setting channel {channel} to high impedance mode")
        self.write(f"OUTP{channel}:HIMPEDANCE ON")
    
    @visa_exception_handler(module_logger=logger)
    def set_output_normal(self, channel: int) -> None:
        """Set the output to normal impedance mode.
        
        Args:
            channel: Output channel (1 or 2)
        """
        logger.info(f"Setting channel {channel} to normal impedance mode")
        self.write(f"OUTP{channel}:HIMPEDANCE OFF")
    
    #-----------------------------------------------------------------------
    # Advanced Functions (Pulse, List, Sweep, Trigger, etc.)
    #-----------------------------------------------------------------------
    
    @visa_exception_handler(module_logger=logger)
    def configure_pulse(self, channel: int, width: float, delay: float = 0.0, 
                       count: int = 1) -> None:
        """Configure pulse parameters.
        
        Args:
            channel: Output channel (1 or 2)
            width: Pulse width in seconds
            delay: Delay between pulses in seconds
            count: Number of pulses to generate
        """
        logger.info(f"Configuring pulse on channel {channel}: width={width}s, delay={delay}s, count={count}")
        
        # Set pulse parameters
        self.write(f"SOUR{channel}:FUNC:SHAP PULS")
        self.write(f"SOUR{channel}:PULS:WIDTH {width}")
        self.write(f"SOUR{channel}:PULS:DEL {delay}")
        self.write(f"SOUR{channel}:PULS:COUN {count}")
    
    @visa_exception_handler(module_logger=logger)
    def set_pulse(self, channel: int, level: float, width: float, 
                 base_level: float = 0.0, mode: str = "VOLT") -> None:
        """Set a single pulse.
        
        Args:
            channel: Output channel (1 or 2)
            level: Pulse level (V or A)
            width: Pulse width in seconds
            base_level: Base level (V or A)
            mode: "VOLT" for voltage or "CURR" for current
        """
        # Set the mode
        self.set_function(mode, channel)
        
        # Configure the pulse
        self.write(f"SOUR{channel}:FUNC:SHAP PULS")
        self.write(f"SOUR{channel}:PULS:WIDTH {width}")
        
        # Set pulse levels
        if mode.upper() == "VOLT":
            self.write(f"SOUR{channel}:VOLT {level}")
            self.write(f"SOUR{channel}:VOLT:BATT {base_level}")
        else:  # mode is CURR
            self.write(f"SOUR{channel}:CURR {level}")
            self.write(f"SOUR{channel}:CURR:BATT {base_level}")
            
        logger.info(f"Set {mode} pulse on channel {channel}: level={level}, width={width}s, base={base_level}")
    
    @visa_exception_handler(module_logger=logger)
    def set_pulse_train(self, channel: int, levels: List[float], widths: List[float],
                       delays: Optional[List[float]] = None, mode: str = "VOLT") -> None:
        """Set a pulse train using list mode.
        
        Args:
            channel: Output channel (1 or 2)
            levels: List of pulse levels (V or A)
            widths: List of pulse widths in seconds
            delays: Optional list of delays after each pulse in seconds
            mode: "VOLT" for voltage or "CURR" for current
        """
        if len(levels) != len(widths):
            raise ValueError("The number of levels must match the number of widths")
            
        if delays is not None and len(delays) != len(levels):
            raise ValueError("The number of delays must match the number of levels")
            
        # Configure list mode
        self.set_list_sweep(channel, levels, delays, mode=mode)
        
        # Set widths for each point
        widths_str = ",".join([f"{w}" for w in widths])
        self.write(f"LIST:WIDT {widths_str}, (@{channel})")
        
        logger.info(f"Set {mode} pulse train on channel {channel} with {len(levels)} pulses")
    
    @visa_exception_handler(module_logger=logger)
    def set_list_sweep(self, channel: int, values: List[float], 
                      delays: Optional[List[float]] = None,
                      points: Optional[int] = None,
                      mode: str = "VOLT") -> None:
        """Configure and set up a list sweep (arbitrary waveform).
        
        Args:
            channel: Output channel (1 or 2)
            values: List of voltage/current values to output
            delays: Optional list of delay times between points in seconds
            points: Optional number of points if different from len(values)
            mode: "VOLT" for voltage source or "CURR" for current source
        """
        if not points:
            points = len(values)
        
        # Configure the function mode (voltage or current)
        self.set_function(mode, channel)
        
        # Clear any existing list
        self.write(f"LIST:CLE (@{channel})")
        
        # Set the list points
        value_str = ",".join([f"{v}" for v in values])
        self.write(f"LIST:{mode} {value_str}, (@{channel})")
        
        # Set delays if provided
        if delays:
            delay_str = ",".join([f"{d}" for d in delays])
            self.write(f"LIST:DEL {delay_str}, (@{channel})")
        
        # Configure list count (number of repetitions)
        self.write(f"LIST:COUN 1, (@{channel})")
        
        # Set to list mode
        self.write(f"SOUR{channel}:FUNC:MODE LIST")
        
        logger.info(f"Configured list sweep with {points} points on channel {channel}")
    
    @visa_exception_handler(module_logger=logger)
    def configure_sweep(self, channel: int, start: float, stop: float, 
                       points: int, mode: str = "LIN", dual: bool = False,
                       function: str = "VOLT") -> None:
        """Configure a sweep measurement.
        
        Args:
            channel: Output channel (1 or 2)
            start: Start value (V or A)
            stop: Stop value (V or A)
            points: Number of points
            mode: "LIN" for linear or "LOG" for logarithmic
            dual: If True, performs a dual sweep (there and back)
            function: "VOLT" for voltage or "CURR" for current
        """
        # Set up the sweep
        self.write(f"SOUR{channel}:SWE:SPAC {mode}")
        self.write(f"SOUR{channel}:SWE:RANG FIX")
        self.write(f"SOUR{channel}:SWE:DIR UP")
        self.write(f"SOUR{channel}:{function}:STAR {start}")
        self.write(f"SOUR{channel}:{function}:STOP {stop}")
        self.write(f"SOUR{channel}:SWE:POIN {points}")
        
        # Set dual sweep if requested
        if dual:
            self.write(f"SOUR{channel}:SWE:STA DOUB")
        else:
            self.write(f"SOUR{channel}:SWE:STA SING")
            
        # Set to sweep mode
        self.write(f"SOUR{channel}:FUNC:MODE SWE")
        self.write(f"SOUR{channel}:FUNC:SHAP {function}")
        
        logger.info(f"Configured {function} sweep on channel {channel}: {start} to {stop}, {points} points, {mode} spacing")
    
    @visa_exception_handler(module_logger=logger)
    def execute_sweep(self, channel: int, wait: bool = True, timeout: float = 30.0) -> bool:
        """Execute a sweep and optionally wait for completion.
        
        Args:
            channel: Output channel (1 or 2)
            wait: Whether to wait for sweep completion
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if sweep completed successfully, False otherwise
        """
        # Ensure output is enabled
        self.enable_output(channel)
        
        # Initiate the sweep
        self.write(f"INIT (@{channel})")
        logger.info(f"Initiated sweep on channel {channel}")
        
        if wait:
            start_time = time.time()
            try:
                while time.time() - start_time < timeout:
                    # Check if operation is complete
                    response = self.query("*OPC?")
                    if int(response.strip()) == 1:
                        logger.info(f"Sweep on channel {channel} completed")
                        return True
                    time.sleep(0.1)  # Small delay to avoid flooding the instrument
                
                logger.warning(f"Sweep timeout after {timeout} seconds")
                return False
            except Exception as e:
                logger.error(f"Error during sweep execution: {str(e)}")
                return False
        
        return True
    
    @visa_exception_handler(module_logger=logger)
    def configure_digitize(self, channel: int, sample_count: int, 
                         interval: float) -> None:
        """Configure digitizing measurement.
        
        Args:
            channel: Channel number (1 or 2)
            sample_count: Number of samples to acquire
            interval: Time interval between samples in seconds
        """
        # Configure digitization parameters
        self.write(f"SENS{channel}:FUNC 'CURR:DC'")  # Can also be 'VOLT:DC'
        self.write(f"SENS{channel}:CURR:APER {interval}")
        self.write(f"SENS{channel}:CURR:DIG:COUN {sample_count}")
        
        logger.info(f"Configured digitizer on channel {channel}: {sample_count} samples at {interval}s interval")
    
    @visa_exception_handler(module_logger=logger)
    def digitize(self, channel: int) -> List[float]:
        """Perform a digitizing measurement.
        
        Args:
            channel: Channel number (1 or 2)
            
        Returns:
            List of measured values
        """
        # Start digitizing
        self.write(f"INIT:IMM (@{channel})")
        
        # Wait for completion
        self.wait_for_operation_complete()
        
        # Fetch the data
        data_str = self.query(f"FETC:ARR? (@{channel})")
        
        # Parse the data
        data_points = [float(x) for x in data_str.strip().split(',')]
        
        logger.info(f"Digitized {len(data_points)} points from channel {channel}")
        return data_points
    
    @visa_exception_handler(module_logger=logger)
    def configure_trigger(self, channel: int, source: str = "AUTO", 
                         count: int = 1, delay: float = 0.0) -> None:
        """Configure the trigger system.
        
        Args:
            channel: Output channel (1 or 2)
            source: Trigger source ("AUTO", "BUS", "EXT", "IMM")
            count: Trigger count
            delay: Trigger delay in seconds
        """
        # Configure ARM (outer) trigger
        self.write(f"ARM:SOUR {source}, (@{channel})")
        self.write(f"ARM:COUN 1, (@{channel})")
        
        # Configure TRIG (inner) trigger
        self.write(f"TRIG:SOUR {source}, (@{channel})")
        self.write(f"TRIG:COUN {count}, (@{channel})")
        self.write(f"TRIG:DEL {delay}, (@{channel})")
        
        logger.info(f"Configured triggers on channel {channel}: source={source}, count={count}, delay={delay}s")
    
    @visa_exception_handler(module_logger=logger)
    def trigger(self, channel: Optional[int] = None) -> None:
        """Send a trigger command to the specified channel(s).
        
        Args:
            channel: Channel number (1, 2, or None for all)
        """
        if channel is None:
            # Trigger all channels
            self.write("INIT (@1,2)")
            logger.info("Triggered all channels")
        else:
            # Trigger specified channel
            self.write(f"INIT (@{channel})")
            logger.info(f"Triggered channel {channel}")
    
    @visa_exception_handler(module_logger=logger)
    def abort(self, channel: Optional[int] = None) -> None:
        """Abort the current operation on the specified channel(s).
        
        Args:
            channel: Channel number (1, 2, or None for all)
        """
        if channel is None:
            # Abort all channels
            self.write("ABOR (@1,2)")
            logger.info("Aborted all channels")
        else:
            # Abort specified channel
            self.write(f"ABOR (@{channel})")
            logger.info(f"Aborted channel {channel}")
    
    #-----------------------------------------------------------------------
    # Measurement Configuration
    #-----------------------------------------------------------------------
    
    @visa_exception_handler(module_logger=logger)
    def set_nplc(self, channel: int, nplc: float) -> None:
        """Set the integration time in power line cycles.
        
        Args:
            channel: Channel number (1 or 2)
            nplc: Integration time in power line cycles
                  (0.01 to 10, lower is faster but noisier)
        """
        if nplc < 0.01 or nplc > 10:
            logger.warning(f"NPLC value {nplc} out of range (0.01-10), clipping")
            nplc = max(0.01, min(nplc, 10))
            
        # Set for both current and voltage measurements
        self.write(f"SENS{channel}:CURR:NPLC {nplc}")
        self.write(f"SENS{channel}:VOLT:NPLC {nplc}")
        
        logger.info(f"Set NPLC to {nplc} on channel {channel}")
    
    @visa_exception_handler(module_logger=logger)
    def configure_average(self, channel: int, count: int, enabled: bool = True) -> None:
        """Configure measurement averaging.
        
        Args:
            channel: Channel number
            count: Number of readings to average
            enabled: Whether to enable averaging
        """
        if enabled:
            self.write(f"SENS{channel}:AVER:COUN {count}")
            self.write(f"SENS{channel}:AVER:STAT ON")
            logger.info(f"Enabled averaging on channel {channel} with count {count}")
        else:
            self.write(f"SENS{channel}:AVER:STAT OFF")
            logger.info(f"Disabled averaging on channel {channel}")
    
    @visa_exception_handler(module_logger=logger)
    def set_measurement_speed(self, channel: int, speed: str) -> None:
        """Set the measurement speed.
        
        Args:
            channel: Channel number (1 or 2)
            speed: Speed setting ("FAST", "MED", "NORM", "HI-ACCURACY")
        """
        speed_map = {
            "FAST": 0.01,
            "MED": 0.1,
            "NORM": 1,
            "HI-ACCURACY": 10
        }
        
        if speed.upper() not in speed_map:
            logger.warning(f"Invalid speed setting: {speed}. Using NORM.")
            speed = "NORM"
            
        nplc = speed_map[speed.upper()]
        self.set_nplc(channel, nplc)
        
        logger.info(f"Set measurement speed to {speed} on channel {channel}")
    
    @visa_exception_handler(module_logger=logger)
    def set_bandwidth_filter(self, channel: int, state: bool, frequency: float = 20.0) -> None:
        """Set the bandwidth filter.
        
        The bandwidth filter reduces noise by averaging multiple samples.
        
        Args:
            channel: Channel number (1 or 2)
            state: True to enable, False to disable
            frequency: Filter bandwidth in Hz (0.1 to 100.0)
        """
        if state:
            self.write(f"SENS{channel}:CURR:BAND {frequency}")
            self.write(f"SENS{channel}:VOLT:BAND {frequency}")
            self.write(f"SENS{channel}:CURR:BAND:AUTO OFF")
            self.write(f"SENS{channel}:VOLT:BAND:AUTO OFF")
            logger.info(f"Enabled bandwidth filter on channel {channel} at {frequency} Hz")
        else:
            self.write(f"SENS{channel}:CURR:BAND:AUTO ON")
            self.write(f"SENS{channel}:VOLT:BAND:AUTO ON")
            logger.info(f"Disabled bandwidth filter on channel {channel}")
    
    @visa_exception_handler(module_logger=logger)
    def set_auto_zero(self, channel: int, auto_zero: bool) -> None:
        """Enable or disable auto-zero function.
        
        Auto-zero improves accuracy but slows down measurements.
        
        Args:
            channel: Channel number (1 or 2)
            auto_zero: True to enable, False to disable
        """
        if auto_zero:
            self.write(f"SENS{channel}:CURR:AZER ON")
            self.write(f"SENS{channel}:VOLT:AZER ON")
            logger.info(f"Enabled auto-zero on channel {channel}")
        else:
            self.write(f"SENS{channel}:CURR:AZER OFF")
            self.write(f"SENS{channel}:VOLT:AZER OFF")
            logger.info(f"Disabled auto-zero on channel {channel}")
    
    @visa_exception_handler(module_logger=logger)
    def measure_resistance(self, channel: int = 1) -> float:
        """Measure resistance using V/I calculation.
        
        Args:
            channel: Channel number (1 or 2)
            
        Returns:
            float: Resistance in ohms
        """
        voltage = self.measure_voltage(channel)
        current = self.measure_current(channel)
        
        if abs(current) > 1e-12:  # Avoid division by zero
            resistance = voltage / current
        else:
            resistance = float('inf')
            
        logger.debug(f"Measured resistance on channel {channel}: {resistance} ohms")
        return resistance
    
    @visa_exception_handler(module_logger=logger)
    def measure_power(self, channel: int = 1) -> float:
        """Measure power using V*I calculation.
        
        Args:
            channel: Channel number (1 or 2)
            
        Returns:
            float: Power in watts
        """
        voltage = self.measure_voltage(channel)
        current = self.measure_current(channel)
        power = voltage * current
        
        logger.debug(f"Measured power on channel {channel}: {power} watts")
        return power
    
    #-----------------------------------------------------------------------
    # IV Characterization Functions
    #-----------------------------------------------------------------------
    
    @visa_exception_handler(module_logger=logger)
    def measure_iv_curve(self, channel: int, start_v: float, stop_v: float, 
                       points: int, current_limit: float = 0.1, 
                       dual: bool = False) -> Tuple[List[float], List[float]]:
        """Measure an IV curve using voltage sweep.
        
        Args:
            channel: Output channel (1 or 2)
            start_v: Start voltage in volts
            stop_v: Stop voltage in volts
            points: Number of measurement points
            current_limit: Current limit in amperes
            dual: Whether to perform a dual sweep (forward and backward)
            
        Returns:
            Tuple of (voltage_list, current_list)
        """
        # Set up the sweep
        self.configure_sweep(channel, start_v, stop_v, points, 
                           mode="LIN", dual=dual, function="VOLT")
                           
        # Set the current limit
        self.write(f"SOUR{channel}:CURR:LIMIT {current_limit}")
        
        # Enable data collection
        self.write(f"SENS{channel}:FUNC 'CURR'")
        
        # Execute the sweep
        success = self.execute_sweep(channel, wait=True)
        
        if not success:
            logger.warning("IV curve measurement timed out or failed")
            return [], []
            
        # Fetch the measured data
        voltage_data = np.linspace(start_v, stop_v, points)
        if dual:
            # For dual sweep, include the backward sweep
            voltage_data = np.append(voltage_data, np.linspace(stop_v, start_v, points))
            
        current_data_str = self.query(f"FETC:ARR? (@{channel})")
        current_data = [float(x) for x in current_data_str.strip().split(',')]
        
        logger.info(f"Measured IV curve with {len(voltage_data)} points")
        return voltage_data.tolist(), current_data
    
    @visa_exception_handler(module_logger=logger)
    def four_wire_mode(self, channel: int, enable: bool = True) -> None:
        """Enable or disable 4-wire (remote sense) measurement mode.
        
        Args:
            channel: Channel number (1 or 2)
            enable: True to enable, False to disable
        """
        if enable:
            self.write(f"SENS{channel}:REM ON")
            logger.info(f"Enabled 4-wire mode on channel {channel}")
        else:
            self.write(f"SENS{channel}:REM OFF")
            logger.info(f"Disabled 4-wire mode on channel {channel}")
    
    @visa_exception_handler(module_logger=logger)
    def voltage_sweep(self, start: float, stop: float, steps: int,
                    compliance: float = 0.1, channel: int = 1,
                    delay: float = 0.1, callback = None) -> List[Dict[str, float]]:
        """Perform a voltage sweep and measure at each step.
        
        Args:
            start: Starting voltage
            stop: Ending voltage
            steps: Number of steps
            compliance: Current compliance limit in amps
            channel: Channel number
            delay: Delay between steps in seconds
            callback: Optional callback function(voltage, current, step)
            
        Returns:
            List of measurement dictionaries with voltage and current readings
        """
        # Configure the sweep
        self.configure_sweep(channel, start, stop, steps, mode="LIN", function="VOLT")
        
        # Set the current limit
        self.write(f"SOUR{channel}:CURR:LIMIT {compliance}")
        
        # Configure measurement and triggering
        self.write(f"SENS{channel}:FUNC 'CURR'")
        self.configure_trigger(channel, source="AUTO", count=steps)
        
        # Create data arrays
        voltages = np.linspace(start, stop, steps)
        results = []
        
        # Enable output
        self.enable_output(channel)
        
        try:
            print(f"Sweeping voltage from {start}V to {stop}V in {steps} steps")
            
            # Execute the sweep
            self.execute_sweep(channel, wait=True)
            
            # Fetch the data
            current_data_str = self.query(f"FETC:ARR? (@{channel})")
            current_values = [float(x) for x in current_data_str.strip().split(',')]
            
            # Process the results
            for i, (voltage, current) in enumerate(zip(voltages, current_values)):
                # Store results
                result = {
                    'set_voltage': voltage,
                    'measured_current': current,
                    'measured_power': voltage * current
                }
                results.append(result)
                
                # Call callback if provided
                if callback:
                    callback(voltage, current, i)
                
                print(f"\rStep {i+1}/{steps}: {voltage:.3f}V, {current*1000:.3f}mA", end="")
                
            print("\nSweep complete")
            return results
            
        except Exception as e:
            logger.error(f"Error during voltage sweep: {str(e)}")
            print(f"\nError during voltage sweep: {str(e)}")
            return results
        finally:
            # Safety: return to a safe voltage
            self.set_voltage(0.0, compliance, channel)
    
    #-----------------------------------------------------------------------
    # System and Error Handling Functions
    #-----------------------------------------------------------------------
    
    @visa_exception_handler(module_logger=logger)
    def get_error(self) -> str:
        """Get the first error from the error queue.
        
        Returns:
            str: Error message or "0,No error" if no errors
        """
        response = self.query("SYST:ERR?")
        if response.startswith("0,"):
            # No error
            return "0,No error"
        else:
            # Error found
            logger.warning(f"Error in SMU: {response}")
            return response
    
    @visa_exception_handler(module_logger=logger)
    def get_all_errors(self) -> List[str]:
        """Get all errors from the error queue.
        
        Returns:
            List of error messages
        """
        errors = []
        while True:
            error = self.get_error()
            if error.startswith("0,"):
                break
            errors.append(error)
        return errors
    
    @visa_exception_handler(module_logger=logger)
    def clear_errors(self) -> None:
        """Clear the error queue."""
        # Read all errors until empty
        while True:
            error = self.get_error()
            if error.startswith("0,"):
                break
        logger.info("Cleared error queue")
    
    @visa_exception_handler(module_logger=logger)
    def self_test(self) -> Tuple[bool, str]:
        """Run the instrument self-test.
        
        Returns:
            Tuple of (success, message)
        """
        response = self.query("*TST?")
        if int(response.strip()) == 0:
            logger.info("Self-test passed")
            return True, "Self-test passed"
        else:
            message = f"Self-test failed with code {response}"
            logger.warning(message)
            return False, message
    
    @visa_exception_handler(module_logger=logger)
    def reset(self) -> bool:
        """Reset the instrument to default settings.
        
        Returns:
            bool: True if reset succeeded, False otherwise
        """
        self.write("*RST")
        self.write("*CLS")
        logger.info("Reset instrument")
        return True
    
    @visa_exception_handler(module_logger=logger)
    def clear(self) -> bool:
        """Clear the instrument status registers.
        
        Returns:
            bool: True if clear succeeded, False otherwise
        """
        self.write("*CLS")
        logger.info("Cleared instrument status")
        return True
    
    def close(self) -> None:
        """Close the connection to the instrument safely.
        
        This disables outputs before closing to ensure safety.
        """
        try:
            # Disable outputs
            self.disable_output(1)
            self.disable_output(2)
            logger.info("Disabled all outputs")
        except Exception as e:
            logger.warning(f"Error disabling outputs: {str(e)}")
            
        # Close the connection
        super().close_connection()
        logger.info("Closed connection to SMU")