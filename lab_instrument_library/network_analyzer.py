"""
Python library containing general functions to control network analyzers.

This module provides a standardized interface for working with network analyzers
to perform frequency sweeps, S-parameter measurements, and data acquisition.

Supported devices:
- Agilent/Keysight E5061B

Documentation references:
- Agilent/Keysight E5061B: https://www.keysight.com/us/en/assets/9018-04907/programming-guides/9018-04907.pdf
"""

import pyvisa
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
import time
from typing import Dict, List, Tuple, Optional, Union, Any
import PySimpleGUI as sg
from .base import LibraryTemplate
from .utils import visa_exception_handler

# Setup module logger
logger = logging.getLogger(__name__)

class NetworkAnalyzer(LibraryTemplate):
    """Class for interfacing with network analyzers such as Agilent/Keysight E5061B.
    
    This class provides methods to control network analyzers, perform frequency sweeps,
    measure S-parameters, and acquire data.
    
    Attributes:
        instrument_address: The VISA address of the connected network analyzer.
        connection: The PyVISA resource connection object.
        instrumentID: The identification string of the connected instrument.
        nickname: A user-provided name for the instrument (optional).
    """
    
    def __init__(self, instrument_address: str, nickname: Optional[str] = None, identify: bool = True):
        """Initialize a network analyzer connection.

        Args:
            instrument_address: VISA address of the instrument.
            nickname: User-defined name for the instrument.
            identify: Whether to identify the instrument with *IDN?.
        """      
        super().__init__(instrument_address, nickname, identify)
        # Configure instrument-specific settings if needed
        self.connection.timeout = 10000  # Longer timeout for measurements
        
    @visa_exception_handler(module_logger=logger)
    def set_sweep_parameters(self, start_freq: float, stop_freq: float, points: int = 401):
        """Set the frequency sweep parameters.
        
        Args:
            start_freq: Start frequency in Hz.
            stop_freq: Stop frequency in Hz.
            points: Number of frequency points.
        """
        self.write(f"SENS:FREQ:STAR {start_freq}")
        self.write(f"SENS:FREQ:STOP {stop_freq}")
        self.write(f"SENS:SWE:POIN {points}")
        logger.info(f"Set sweep from {start_freq/1e6:.2f} MHz to {stop_freq/1e6:.2f} MHz with {points} points")
        
    @visa_exception_handler(module_logger=logger)
    def set_power(self, power_level: float):
        """Set the output power level.
        
        Args:
            power_level: Power level in dBm.
        """
        self.write(f"SOUR:POW {power_level}")
        logger.info(f"Set output power to {power_level} dBm")
    
    @visa_exception_handler(module_logger=logger)
    def get_power(self) -> float:
        """Get the current output power level.
        
        Returns:
            float: Current power level in dBm.
        """
        return float(self.query("SOUR:POW?").strip())
    
    def setup_s_parameter_measurement(self, parameter: str = "S21"):
        """Set up S-parameter measurement.
        
        Args:
            parameter: S-parameter to measure (S11, S21, S12, S22)
        """
        # Select measurement parameter
        self.write(f"CALC:PAR:DEL:ALL")  # Delete all existing measurements
        self.write(f"CALC:PAR:DEF:EXT 'Meas1', {parameter}")
        self.write(f"CALC:PAR:SEL 'Meas1'")
        
        # Set measurement format (default to log magnitude)
        self.write("CALC:FORM MLOG")
        logger.info(f"Set up {parameter} measurement")
    
    def perform_sweep(self, wait: bool = True) -> bool:
        """Perform a frequency sweep.
        
        Args:
            wait: Whether to wait for the sweep to complete.
            
        Returns:
            bool: True if sweep completed successfully.
        """
        try:
            self.write("INIT:CONT OFF")  # Set to single sweep
            self.write("INIT:IMM")  # Trigger the sweep
            
            if wait:
                # Wait for the operation to complete
                return self.wait_for_operation_complete()
            
            logger.info("Sweep completed")
            return True
        except Exception as e:
            logger.error(f"Sweep failed: {str(e)}")
            return False
    
    def get_trace_data(self) -> Tuple[List[float], List[float]]:
        """Get the current trace data.
        
        Returns:
            Tuple containing frequency and measurement data arrays.
        """
        # Get frequency data
        self.write("SENS:X:VAL?")
        freq_data = self.connection.read_raw()
        frequencies = [float(v) for v in freq_data.decode().strip().split(',')]
        
        # Get measurement data
        self.write("CALC:DATA:FDAT?")
        meas_data = self.connection.read_raw()
        values = [float(v) for v in meas_data.decode().strip().split(',')]
        
        # Only return real values (every other value is imaginary)
        real_values = values[::2]
        
        return frequencies, real_values
    
    def measure_s_parameter(self, parameter: str = "S21") -> pd.DataFrame:
        """Measure a specific S-parameter across the frequency range.
        
        Args:
            parameter: S-parameter to measure (S11, S21, S12, S22)
            
        Returns:
            DataFrame containing frequency and measurement data.
        """
        self.setup_s_parameter_measurement(parameter)
        self.perform_sweep(wait=True)
        frequencies, values = self.get_trace_data()
        
        # Create a DataFrame with the results
        df = pd.DataFrame({
            'Frequency': frequencies,
            parameter: values
        })
        
        return df
    
    def measure_s_parameters(self) -> pd.DataFrame:
        """Measure all four S-parameters.
        
        Returns:
            DataFrame containing frequency and all S-parameters.
        """
        # Start with S11 to get the frequencies
        df_s11 = self.measure_s_parameter("S11")
        df = df_s11.rename(columns={"S11": "S11"})
        
        # Add the other S-parameters
        for param in ["S21", "S12", "S22"]:
            df_param = self.measure_s_parameter(param)
            df[param] = df_param[param]
        
        return df
    
    def plot_s_parameters(self, data: pd.DataFrame, params: List[str] = None):
        """Plot S-parameters.
        
        Args:
            data: DataFrame with frequency and S-parameter columns.
            params: List of S-parameters to plot (default: all available).
        """
        if params is None:
            # Plot all S-parameters in the DataFrame except Frequency
            params = [col for col in data.columns if col.startswith('S')]
        
        plt.figure(figsize=(10, 6))
        
        for param in params:
            if param in data.columns:
                plt.plot(data["Frequency"] / 1e6, data[param], label=param)
            else:
                logger.warning(f"S-parameter {param} not found in data")
        
        plt.xlabel("Frequency (MHz)")
        plt.ylabel("Magnitude (dB)")
        plt.title("S-Parameters")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        
        return plt.gcf()
    
    def save_s_parameters(self, data: pd.DataFrame, filename: str):
        """Save S-parameters to a CSV file.
        
        Args:
            data: DataFrame with frequency and S-parameter columns.
            filename: File to save the data to.
        """
        # Make sure the filename ends with .csv
        if not filename.lower().endswith('.csv'):
            filename += '.csv'
        
        data.to_csv(filename, index=False)
        logger.info(f"Saved S-parameters to {filename}")
        
    def load_s_parameters(self, filename: str) -> pd.DataFrame:
        """Load S-parameters from a CSV file.
        
        Args:
            filename: File to load the data from.
            
        Returns:
            DataFrame with frequency and S-parameter columns.
        """
        data = pd.read_csv(filename)
        logger.info(f"Loaded S-parameters from {filename}")
        return data

    def set_markers(self, frequencies: List[float]):
        """Set markers at specified frequencies.
        
        Args:
            frequencies: List of frequencies (Hz) to set markers at.
        """
        self.write("CALC:MARK:AOFF")  # Turn off all markers
        
        for i, freq in enumerate(frequencies, 1):
            if i > 9:  # Most network analyzers support up to 9 or 10 markers
                break
                
            self.write(f"CALC:MARK{i}:STAT ON")
            self.write(f"CALC:MARK{i}:X {freq}")
        
        logger.info(f"Set {min(len(frequencies), 9)} markers")
        
    @visa_exception_handler(module_logger=logger)
    def get_marker_values(self, marker_num: int = 1) -> Dict[str, float]:
        """Get values at a specific marker."""
        freq = float(self.query(f"CALC:MARK{marker_num}:X?").strip())
        value = float(self.query(f"CALC:MARK{marker_num}:Y?").strip())
        
        return {
            "frequency": freq,
            "value": value
        }

    def clear(self) -> bool:
        """Clear the instrument's status registers and error queue."""
        logger.info("Clearing network analyzer status")
        return super().clear()
    
    def reset(self) -> bool:
        """Reset the instrument to factory settings."""
        logger.info("Resetting network analyzer")
        success = super().reset()
        # Reset display format
        self.write("CALC:FORM MLOG")
        # Reset sweep parameters to defaults
        self.write("SENS:SWE:TYPE LIN")
        logger.info("Network analyzer successfully reset")
        return success
        
    def close(self) -> None:
        """Close the connection to the network analyzer safely."""
        logger.info("Closing network analyzer connection")
        super().close_connection()

    @visa_exception_handler(module_logger=logger)
    def save_screenshot(self, filename: str, format: str = "PNG") -> bool:
        """Save a screenshot of the analyzer display.
        
        Args:
            filename: File to save the screenshot to
            format: Image format (PNG, BMP, JPG)
            
        Returns:
            bool: True if successful
        """
        # Ensure proper extension
        if not filename.lower().endswith(f'.{format.lower()}'):
            filename += f'.{format.lower()}'

        self.write(f"HCOP:DEV:LANG {format}")
        self.write("HCOP:DEST 'MMEM'")
        self.write(f"MMEM:NAME '{filename}'")
        self.write("HCOP:IMM")
        
        logger.info(f"Screenshot saved to {filename}")
        return True