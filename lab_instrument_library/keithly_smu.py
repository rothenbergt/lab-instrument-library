"""
Python library containing general functions to control Keithley SMUs.

This module provides functions for controlling Keithley 228 and 238 Source Measure Units.
"""

from .base import LibraryTemplate
from .utils import visa_exception_handler
from typing import Dict, Optional, Union, List, Any
import logging
import inspect

# Setup module logger
logger = logging.getLogger(__name__)

class Keithly228(LibraryTemplate):
    """Class for interfacing with Keithley 228 Source Measure Unit.
    
    This class provides methods for basic source and measurement operations 
    with Keithley 228 SMUs.
    """   
    
    def __init__(self, instrument_address: str, nickname: str = None, identify: bool = True):
        """Initialize the Keithley 228 SMU instance.
        
        Args:
            instrument_address (str): The VISA address of the instrument.
            nickname (str, optional): User-defined name for the instrument.
            identify (bool): Whether to query the instrument ID on connection.
        """
        super().__init__(instrument_address, nickname, identify)
        logger.info(f"Initialized Keithley 228 SMU at {instrument_address}")
        
    @visa_exception_handler(module_logger=logger)
    def set_voltage(self, voltage: float) -> None:
        """Set the output voltage of the SMU.
        
        Args:
            voltage (float): The desired output voltage.
        """
        logger.debug(f"Setting voltage to {voltage}V")
        self.write(f"SOUR:VOLT {voltage}")
        
    @visa_exception_handler(module_logger=logger)
    def set_current(self, current: float) -> None:
        """Set the output current of the SMU.
        
        Args:
            current (float): The desired output current.
        """
        logger.debug(f"Setting current to {current}A")
        self.write(f"SOUR:CURR {current}")
        
    @visa_exception_handler(module_logger=logger)
    def measure_voltage(self) -> float:
        """Measure the output voltage of the SMU.
        
        Returns:
            float: The measured output voltage.
        """
        response = self.query("MEAS:VOLT?")
        result = float(response.strip())
        logger.debug(f"Measured voltage: {result}V")
        return result
        
    @visa_exception_handler(module_logger=logger)
    def measure_current(self) -> float:
        """Measure the output current of the SMU.
        
        Returns:
            float: The measured output current.
        """
        response = self.query("MEAS:CURR?")
        result = float(response.strip())
        logger.debug(f"Measured current: {result}A")
        return result
        
    @visa_exception_handler(module_logger=logger)
    def enable_output(self) -> None:
        """Enable the output of the SMU."""
        logger.info("Enabling SMU output")
        self.write("OUTP ON")
        
    @visa_exception_handler(module_logger=logger)
    def disable_output(self) -> None:
        """Disable the output of the SMU."""
        logger.info("Disabling SMU output")
        self.write("OUTP OFF")
        
    def reset(self) -> bool:
        """Reset the instrument to factory settings.
        
        Returns:
            bool: True if reset succeeded, False otherwise.
        """
        logger.info("Resetting Keithley 228 SMU")
        return super().reset()
    
    def clear(self) -> bool:
        """Clear the instrument's status registers and error queue.
        
        Returns:
            bool: True if clear succeeded, False otherwise.
        """
        logger.info("Clearing Keithley 228 SMU status")
        return super().clear()
    
    def close(self) -> None:
        """Close the connection to the SMU.
        
        Ensures output is disabled before closing.
        """
        try:
            self.disable_output()
        except Exception as e:
            logger.warning(f"Error disabling output during close: {str(e)}")
        
        logger.info("Closing Keithley 228 SMU connection")
        super().close_connection()
        
    @visa_exception_handler(module_logger=logger)
    def perform_voltage_sweep(self, start: float, stop: float, steps: int, 
                            compliance: float = 0.1, delay: float = 0.1) -> List[Dict[str, float]]:
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
        import numpy as np
        import time
        
        # Create voltage points
        voltages = np.linspace(start, stop, steps)
        results = []
        
        # Configure sweep
        self.write(f"SOUR:CURR:COMP {compliance}")
        
        try:
            for voltage in voltages:
                # Set voltage
                self.set_voltage(voltage)
                time.sleep(delay)
                
                # Measure
                measured_v = self.measure_voltage()
                measured_i = self.measure_current()
                
                results.append({
                    "voltage": measured_v,
                    "current": measured_i
                })
                
            return results
        except Exception as e:
            logger.error(f"Error during voltage sweep: {str(e)}")
            # Set voltage to 0 for safety
            self.set_voltage(0)
            return results
    
    @visa_exception_handler(module_logger=logger)
    def configure_output_mode(self, mode: str) -> None:
        """Configure the output mode of the SMU.
        
        Args:
            mode: Output mode ('VOLT', 'CURR')
        """
        if mode.upper() not in ['VOLT', 'CURR']:
            logger.warning(f"Invalid mode: {mode}. Use 'VOLT' or 'CURR'")
            return
            
        self.write(f"SOUR:FUNC:MODE {mode}")
        logger.info(f"Set source function to {mode}")

class Keithly238(LibraryTemplate):
    """Class for interfacing with Keithley 238 Source Measure Unit.
    
    This class provides methods for basic source and measurement operations 
    with Keithley 238 SMUs.
    """
    
    def __init__(self, instrument_address: str, nickname: str = None, identify: bool = True):
        """Initialize the Keithley 238 SMU instance.
        
        Args:
            instrument_address (str): The VISA address of the instrument.
            nickname (str, optional): User-defined name for the instrument.
            identify (bool): Whether to query the instrument ID on connection.
        """
        super().__init__(instrument_address, nickname, identify)
        logger.info(f"Initialized Keithley 238 SMU at {instrument_address}")
        
    @visa_exception_handler(module_logger=logger)
    def set_voltage(self, voltage: float) -> None:
        """Set the output voltage of the SMU.
        
        Args:
            voltage (float): The desired output voltage.
        """
        logger.debug(f"Setting voltage to {voltage}V")
        self.write(f"SOUR:VOLT {voltage}")
        
    @visa_exception_handler(module_logger=logger)
    def set_current(self, current: float) -> None:
        """Set the output current of the SMU.
        
        Args:
            current (float): The desired output current.
        """
        logger.debug(f"Setting current to {current}A")
        self.write(f"SOUR:CURR {current}")
        
    @visa_exception_handler(module_logger=logger)
    def measure_voltage(self) -> float:
        """Measure the output voltage of the SMU.
        
        Returns:
            float: The measured output voltage.
        """
        response = self.query("MEAS:VOLT?")
        result = float(response.strip())
        logger.debug(f"Measured voltage: {result}V")
        return result
        
    @visa_exception_handler(module_logger=logger)
    def measure_current(self) -> float:
        """Measure the output current of the SMU.
        
        Returns:
            float: The measured output current.
        """
        response = self.query("MEAS:CURR?")
        result = float(response.strip())
        logger.debug(f"Measured current: {result}A")
        return result
        
    @visa_exception_handler(module_logger=logger)
    def enable_output(self) -> None:
        """Enable the output of the SMU."""
        logger.info("Enabling SMU output")
        self.write("OUTP ON")
        
    @visa_exception_handler(module_logger=logger)
    def disable_output(self) -> None:
        """Disable the output of the SMU."""
        logger.info("Disabling SMU output")
        self.write("OUTP OFF")
    
    def reset(self) -> bool:
        """Reset the instrument to factory settings.
        
        Returns:
            bool: True if reset succeeded, False otherwise.
        """
        logger.info("Resetting Keithley 238 SMU")
        return super().reset()
    
    def clear(self) -> bool:
        """Clear the instrument's status registers and error queue.
        
        Returns:
            bool: True if clear succeeded, False otherwise.
        """
        logger.info("Clearing Keithley 238 SMU status")
        return super().clear()
    
    def close(self) -> None:
        """Close the connection to the SMU.
        
        Ensures output is disabled before closing.
        """
        try:
            self.disable_output()
        except Exception as e:
            logger.warning(f"Error disabling output during close: {str(e)}")
        
        logger.info("Closing Keithley 238 SMU connection")
        super().close_connection()