"""
Python library for controlling laboratory power supplies.

This module provides a standardized interface for communicating with various
lab power supplies using a proper object-oriented design.

Supported devices:
- Agilent E3631A (Triple output, ±25V/±1A, 6V/5A)
- Agilent E3632A (Single output, 0-15V/7A or 0-30V/4A)
- Keysight E3649A (Dual output, 0-35V/0.8A or 0-60V/0.5A)
- Keysight E36313A (Triple output, 6V/5A, 25V/1A, 25V/1A)
- Keysight E36234A (Quad output, 0-30V/1A*2, 0-6V/5A, 0-25V/1A)
"""

import pyvisa
import sys
import time
import logging
import numpy as np
from typing import Dict, List, Union, Optional, Callable, Type, Any, Tuple
from abc import ABC, abstractmethod
from .base import LibraryTemplate

# Setup module logger
logger = logging.getLogger(__name__)


class PowerSupplyBase(ABC):
    """Abstract base class for all power supply devices.
    
    This class defines the common interface for all power supplies.
    Specific implementations inherit from this class.
    """

    def __init__(self, connection, device_name: str):
        """Initialize with an open connection.
        
        Args:
            connection: Open PyVISA connection to the instrument
            device_name: Name of the specific device
        """
        self.connection = connection
        self.device_name = device_name
        
        # Set the instrument to remote control mode
        self._initialize_remote()
    
    def _initialize_remote(self):
        """Initialize instrument in remote control mode."""
        # Default implementation - override in subclasses if needed
        try:
            # Set to remote control mode if the device supports it
            self.connection.write("SYST:REM")
        except Exception:
            # Not all devices support/need this command
            pass
    
    @abstractmethod
    def set_voltage(self, voltage: float, current_limit: float, channel: int = 1) -> None:
        """Set the output voltage and current limit.
        
        Args:
            voltage: Target voltage in volts
            current_limit: Current limit in amperes
            channel: Output channel number
        """
        pass
    
    @abstractmethod
    def get_voltage(self, channel: int = 1) -> float:
        """Get the set voltage value.
        
        Args:
            channel: Output channel number
            
        Returns:
            float: The voltage setting in volts
        """
        pass
    
    @abstractmethod
    def measure_voltage(self, channel: int = 1) -> float:
        """Measure the actual output voltage.
        
        Args:
            channel: Output channel number
            
        Returns:
            float: The measured voltage in volts
        """
        pass
    
    @abstractmethod
    def measure_current(self, channel: int = 1) -> float:
        """Measure the actual output current.
        
        Args:
            channel: Output channel number
            
        Returns:
            float: The measured current in amperes
        """
        pass
    
    @abstractmethod
    def enable_output(self, channel: Optional[int] = None) -> None:
        """Enable the output.
        
        Args:
            channel: Output channel number (if None, enable all channels)
        """
        pass
    
    @abstractmethod
    def disable_output(self, channel: Optional[int] = None) -> None:
        """Disable the output.
        
        Args:
            channel: Output channel number (if None, disable all channels)
        """
        pass
    
    def get_output_state(self, channel: int = 1) -> bool:
        """Get the output state.
        
        Args:
            channel: Output channel number
            
        Returns:
            bool: True if output is enabled, False otherwise
        """
        try:
            response = self.connection.query(f"OUTP? (@{channel})").strip()
            return response == "1" or response.upper() == "ON"
        except Exception as e:
            logger.warning(f"Error getting output state: {str(e)}")
            # Default implementation that works for many power supplies
            try:
                response = self.connection.query(f"OUTP?").strip()
                return response == "1" or response.upper() == "ON"
            except Exception:
                logger.error("Could not determine output state")
                return False
    
    def reset(self) -> None:
        """Reset the instrument to default settings."""
        try:
            self.connection.write("*RST")
            logger.info(f"Reset {self.device_name}")
        except Exception as e:
            logger.error(f"Error resetting {self.device_name}: {str(e)}")


class AgilentE3631A(PowerSupplyBase):
    """Controller for Agilent E3631A Triple Output Power Supply.
    
    This power supply has three outputs:
    - P6V: 0-6V, 0-5A
    - P25V: 0-25V, 0-1A
    - N25V: 0 to -25V, 0-1A
    """
    
    # Map logical channels to actual outputs
    _channel_map = {1: "P6V", 2: "P25V", 3: "N25V"}
    
    def set_voltage(self, voltage: float, current_limit: float, channel: int = 1) -> None:
        """Set the output voltage and current limit.
        
        Args:
            voltage: Target voltage in volts
            current_limit: Current limit in amperes
            channel: Output channel (1=P6V, 2=P25V, 3=N25V)
        """
        try:
            if channel not in self._channel_map:
                logger.error(f"Invalid channel {channel} for {self.device_name}")
                return
                
            output = self._channel_map[channel]
            self.connection.write(f"INST:SEL {output}")
            self.connection.write(f"VOLT {voltage:.4f}")
            self.connection.write(f"CURR {current_limit:.4f}")
            logger.info(f"Set {output} to {voltage:.4f}V with {current_limit:.4f}A limit")
        except Exception as e:
            logger.error(f"Error setting voltage/current: {str(e)}")
    
    def get_voltage(self, channel: int = 1) -> float:
        """Get the set voltage value.
        
        Args:
            channel: Output channel (1=P6V, 2=P25V, 3=N25V)
            
        Returns:
            float: The voltage setting in volts
        """
        try:
            if channel not in self._channel_map:
                logger.error(f"Invalid channel {channel} for {self.device_name}")
                return 0.0
                
            output = self._channel_map[channel]
            self.connection.write(f"INST:SEL {output}")
            response = self.connection.query("VOLT?").strip()
            return float(response)
        except Exception as e:
            logger.error(f"Error getting voltage setting: {str(e)}")
            return 0.0
    
    def measure_voltage(self, channel: int = 1) -> float:
        """Measure the actual output voltage.
        
        Args:
            channel: Output channel (1=P6V, 2=P25V, 3=N25V)
            
        Returns:
            float: The measured voltage in volts
        """
        try:
            if channel not in self._channel_map:
                logger.error(f"Invalid channel {channel} for {self.device_name}")
                return 0.0
                
            output = self._channel_map[channel]
            self.connection.write(f"INST:SEL {output}")
            response = self.connection.query("MEAS:VOLT?").strip()
            return float(response)
        except Exception as e:
            logger.error(f"Error measuring voltage: {str(e)}")
            return 0.0
    
    def measure_current(self, channel: int = 1) -> float:
        """Measure the actual output current.
        
        Args:
            channel: Output channel (1=P6V, 2=P25V, 3=N25V)
            
        Returns:
            float: The measured current in amperes
        """
        try:
            if channel not in self._channel_map:
                logger.error(f"Invalid channel {channel} for {self.device_name}")
                return 0.0
                
            output = self._channel_map[channel]
            self.connection.write(f"INST:SEL {output}")
            response = self.connection.query("MEAS:CURR?").strip()
            return float(response)
        except Exception as e:
            logger.error(f"Error measuring current: {str(e)}")
            return 0.0
    
    def enable_output(self, channel: Optional[int] = None) -> None:
        """Enable the output.
        
        For E3631A, this enables all outputs (device doesn't support individual control).
        
        Args:
            channel: Ignored for this model
        """
        try:
            self.connection.write("OUTP ON")
            logger.info(f"Enabled output on {self.device_name}")
        except Exception as e:
            logger.error(f"Error enabling output: {str(e)}")
    
    def disable_output(self, channel: Optional[int] = None) -> None:
        """Disable the output.
        
        For E3631A, this disables all outputs (device doesn't support individual control).
        
        Args:
            channel: Ignored for this model
        """
        try:
            self.connection.write("OUTP OFF")
            logger.info(f"Disabled output on {self.device_name}")
        except Exception as e:
            logger.error(f"Error disabling output: {str(e)}")


class AgilentE3632A(PowerSupplyBase):
    """Controller for Agilent E3632A Single Output Power Supply.
    
    This power supply has a single output with two ranges:
    - Low: 0-15V/0-7A
    - High: 0-30V/0-4A
    """
    
    def set_voltage(self, voltage: float, current_limit: float, channel: int = 1) -> None:
        """Set the output voltage and current limit.
        
        Args:
            voltage: Target voltage in volts
            current_limit: Current limit in amperes
            channel: Ignored for this single-output model
        """
        try:
            # Select appropriate range automatically
            if voltage <= 15.0:
                self.connection.write("VOLT:RANG LOW")
            else:
                self.connection.write("VOLT:RANG HIGH")
                
            self.connection.write(f"VOLT {voltage:.4f}")
            self.connection.write(f"CURR {current_limit:.4f}")
            logger.info(f"Set output to {voltage:.4f}V with {current_limit:.4f}A limit")
        except Exception as e:
            logger.error(f"Error setting voltage/current: {str(e)}")
    
    def get_voltage(self, channel: int = 1) -> float:
        """Get the set voltage value.
        
        Args:
            channel: Ignored for this single-output model
            
        Returns:
            float: The voltage setting in volts
        """
        try:
            response = self.connection.query("VOLT?").strip()
            return float(response)
        except Exception as e:
            logger.error(f"Error getting voltage setting: {str(e)}")
            return 0.0
    
    def measure_voltage(self, channel: int = 1) -> float:
        """Measure the actual output voltage.
        
        Args:
            channel: Ignored for this single-output model
            
        Returns:
            float: The measured voltage in volts
        """
        try:
            response = self.connection.query("MEAS:VOLT?").strip()
            return float(response)
        except Exception as e:
            logger.error(f"Error measuring voltage: {str(e)}")
            return 0.0
    
    def measure_current(self, channel: int = 1) -> float:
        """Measure the actual output current.
        
        Args:
            channel: Ignored for this single-output model
            
        Returns:
            float: The measured current in amperes
        """
        try:
            response = self.connection.query("MEAS:CURR?").strip()
            return float(response)
        except Exception as e:
            logger.error(f"Error measuring current: {str(e)}")
            return 0.0
    
    def enable_output(self, channel: Optional[int] = None) -> None:
        """Enable the output.
        
        Args:
            channel: Ignored for this single-output model
        """
        try:
            self.connection.write("OUTP ON")
            logger.info(f"Enabled output on {self.device_name}")
        except Exception as e:
            logger.error(f"Error enabling output: {str(e)}")
    
    def disable_output(self, channel: Optional[int] = None) -> None:
        """Disable the output.
        
        Args:
            channel: Ignored for this single-output model
        """
        try:
            self.connection.write("OUTP OFF")
            logger.info(f"Disabled output on {self.device_name}")
        except Exception as e:
            logger.error(f"Error disabling output: {str(e)}")


class KeysightE3649A(PowerSupplyBase):
    """Controller for Keysight E3649A Dual Output Power Supply."""
    
    def set_voltage(self, voltage: float, current_limit: float, channel: int = 1) -> None:
        """Set the output voltage and current limit.
        
        Args:
            voltage: Target voltage in volts
            current_limit: Current limit in amperes
            channel: Output channel (1 or 2)
        """
        try:
            # Select channel first
            self.connection.write(f"INST:SEL OUT{channel}")
            
            # Set range based on voltage (0-35V/0.8A or 0-60V/0.5A)
            if voltage <= 35.0:
                self.connection.write("VOLT:RANG LOW")
            else:
                self.connection.write("VOLT:RANG HIGH")
                
            # Set voltage and current
            self.connection.write(f"VOLT {voltage:.4f}")
            self.connection.write(f"CURR {current_limit:.4f}")
            logger.info(f"Set channel {channel} to {voltage:.4f}V with {current_limit:.4f}A limit")
        except Exception as e:
            logger.error(f"Error setting voltage/current: {str(e)}")
    
    def get_voltage(self, channel: int = 1) -> float:
        """Get the set voltage value.
        
        Args:
            channel: Output channel (1 or 2)
            
        Returns:
            float: The voltage setting in volts
        """
        try:
            self.connection.write(f"INST:SEL OUT{channel}")
            response = self.connection.query("VOLT?").strip()
            return float(response)
        except Exception as e:
            logger.error(f"Error getting voltage setting: {str(e)}")
            return 0.0
    
    def measure_voltage(self, channel: int = 1) -> float:
        """Measure the actual output voltage.
        
        Args:
            channel: Output channel (1 or 2)
            
        Returns:
            float: The measured voltage in volts
        """
        try:
            self.connection.write(f"INST:SEL OUT{channel}")
            response = self.connection.query("MEAS:VOLT?").strip()
            return float(response)
        except Exception as e:
            logger.error(f"Error measuring voltage: {str(e)}")
            return 0.0
    
    def measure_current(self, channel: int = 1) -> float:
        """Measure the actual output current.
        
        Args:
            channel: Output channel (1 or 2)
            
        Returns:
            float: The measured current in amperes
        """
        try:
            self.connection.write(f"INST:SEL OUT{channel}")
            response = self.connection.query("MEAS:CURR?").strip()
            return float(response)
        except Exception as e:
            logger.error(f"Error measuring current: {str(e)}")
            return 0.0
    
    def enable_output(self, channel: Optional[int] = None) -> None:
        """Enable the output.
        
        Args:
            channel: Output channel (1, 2, or None for all)
        """
        try:
            if channel is None:
                # Enable all channels
                self.connection.write("OUTP ON")
                logger.info(f"Enabled all outputs on {self.device_name}")
            else:
                # Enable specific channel
                self.connection.write(f"INST:SEL OUT{channel}")
                self.connection.write("OUTP ON")
                logger.info(f"Enabled output {channel} on {self.device_name}")
        except Exception as e:
            logger.error(f"Error enabling output: {str(e)}")
    
    def disable_output(self, channel: Optional[int] = None) -> None:
        """Disable the output.
        
        Args:
            channel: Output channel (1, 2, or None for all)
        """
        try:
            if channel is None:
                # Disable all channels
                self.connection.write("OUTP OFF")
                logger.info(f"Disabled all outputs on {self.device_name}")
            else:
                # Disable specific channel
                self.connection.write(f"INST:SEL OUT{channel}")
                self.connection.write("OUTP OFF")
                logger.info(f"Disabled output {channel} on {self.device_name}")
        except Exception as e:
            logger.error(f"Error disabling output: {str(e)}")


class KeysightE36300(PowerSupplyBase):
    """Controller for Keysight E36300 Series (E36313A, E36234A) Multi-Output Power Supplies."""
    
    def set_voltage(self, voltage: float, current_limit: float, channel: int = 1) -> None:
        """Set the output voltage and current limit.
        
        Args:
            voltage: Target voltage in volts
            current_limit: Current limit in amperes
            channel: Output channel number
        """
        try:
            # Modern Keysight supplies use (@N) channel syntax
            self.connection.write(f"VOLT {voltage:.4f}, (@{channel})")
            self.connection.write(f"CURR {current_limit:.4f}, (@{channel})")
            logger.info(f"Set channel {channel} to {voltage:.4f}V with {current_limit:.4f}A limit")
        except Exception as e:
            logger.error(f"Error setting voltage/current: {str(e)}")
    
    def get_voltage(self, channel: int = 1) -> float:
        """Get the set voltage value.
        
        Args:
            channel: Output channel number
            
        Returns:
            float: The voltage setting in volts
        """
        try:
            response = self.connection.query(f"VOLT? (@{channel})").strip()
            return float(response)
        except Exception as e:
            logger.error(f"Error getting voltage setting: {str(e)}")
            return 0.0
    
    def measure_voltage(self, channel: int = 1) -> float:
        """Measure the actual output voltage.
        
        Args:
            channel: Output channel number
            
        Returns:
            float: The measured voltage in volts
        """
        try:
            response = self.connection.query(f"MEAS:VOLT? (@{channel})").strip()
            return float(response)
        except Exception as e:
            logger.error(f"Error measuring voltage: {str(e)}")
            return 0.0
    
    def measure_current(self, channel: int = 1) -> float:
        """Measure the actual output current.
        
        Args:
            channel: Output channel number
            
        Returns:
            float: The measured current in amperes
        """
        try:
            response = self.connection.query(f"MEAS:CURR? (@{channel})").strip()
            return float(response)
        except Exception as e:
            logger.error(f"Error measuring current: {str(e)}")
            return 0.0
    
    def enable_output(self, channel: Optional[int] = None) -> None:
        """Enable the output.
        
        Args:
            channel: Output channel number (if None, enable all channels)
        """
        try:
            if channel is None:
                # Enable all channels
                self.connection.write("OUTP ON, (@1,2,3)")
                logger.info(f"Enabled all outputs on {self.device_name}")
            else:
                # Enable specific channel
                self.connection.write(f"OUTP ON, (@{channel})")
                logger.info(f"Enabled output {channel} on {self.device_name}")
        except Exception as e:
            logger.error(f"Error enabling output: {str(e)}")
    
    def disable_output(self, channel: Optional[int] = None) -> None:
        """Disable the output.
        
        Args:
            channel: Output channel number (if None, disable all channels)
        """
        try:
            if channel is None:
                # Disable all channels
                self.connection.write("OUTP OFF, (@1,2,3)")
                logger.info(f"Disabled all outputs on {self.device_name}")
            else:
                # Disable specific channel
                self.connection.write(f"OUTP OFF, (@{channel})")
                logger.info(f"Disabled output {channel} on {self.device_name}")
        except Exception as e:
            logger.error(f"Error disabling output: {str(e)}")


class Supply(LibraryTemplate):
    """Factory class for creating appropriate power supply instances.
    
    This class creates and configures the appropriate controller subclass
    based on the selected instrument type.
    """
    
    # Dictionary mapping model names to controller classes
    _controller_classes = {
        "E3631A": AgilentE3631A,
        "E3632A": AgilentE3632A,
        "E3649A": KeysightE3649A,
        "E36313A": KeysightE36300,
        "E36234A": KeysightE36300
    }
    
    # Simplified names for user selection
    lab_supplies = {
        "1": "E3631A",
        "2": "E3632A",
        "3": "E3649A",
        "4": "E36313A",
        "5": "E36234A",
    }
    
    def __init__(self, instrument_address: str, selected_instrument: Optional[str] = None, 
                 nickname: Optional[str] = None, identify: bool = True):
        """Initialize and select appropriate power supply controller.
        
        Args:
            instrument_address: VISA address of the instrument.
            selected_instrument: Name of the selected instrument model.
            nickname: User-defined name for the instrument.
            identify: Attempt to identify the instrument with IDN query.
        """
        super().__init__(instrument_address, nickname, identify)
        self.supply = None
        self._create_controller(selected_instrument)
    
    def _create_controller(self, selected_instrument: Optional[str]) -> None:
        """Create the appropriate controller for the connected power supply.
        
        Args:
            selected_instrument: Explicit model name (optional)
        """
        # Determine the instrument model
        model = self._determine_model(selected_instrument)
        
        if model in self._controller_classes:
            controller_class = self._controller_classes[model]
            self.supply = controller_class(self.connection, model)
            logger.info(f"Created controller for {model}")
        else:
            # Use a default implementation
            logger.warning(f"No specific controller for {model}, using generic implementation")
            self.supply = AgilentE3632A(self.connection, model)
    
    def _determine_model(self, selected_instrument: Optional[str]) -> str:
        """Determine the power supply model.
        
        Args:
            selected_instrument: Explicit model name (optional)
            
        Returns:
            str: Model name
        """
        # If model is explicitly specified, use it
        if selected_instrument:
            return selected_instrument
            
        # Try to extract model from identification string
        if self.instrumentID:
            for model in self._controller_classes:
                if model in self.instrumentID:
                    logger.info(f"Detected {model} from identification")
                    return model
            
        # If we can't determine the model, ask the user
        print("Please select your power supply model:")
        for key, value in self.lab_supplies.items():
            print(f"{key}: {value}")
            
        try:
            choice = input("Choice: ")
            if choice in self.lab_supplies:
                model = self.lab_supplies[choice]
                logger.info(f"User selected {model}")
                return model
        except Exception:
            pass
            
        # Default to E3632A as a reasonable fallback
        logger.warning("Could not determine model, using E3632A as default")
        return "E3632A"
    
    # Forward methods to the controller
    def set_voltage(self, voltage: float, current_limit: float = 0.1, channel: int = 1) -> None:
        """Set the output voltage and current limit.
        
        Args:
            voltage: Target voltage in volts
            current_limit: Current limit in amperes
            channel: Output channel number
        """
        self.supply.set_voltage(voltage, current_limit, channel)
    
    def get_voltage(self, channel: int = 1) -> float:
        """Get the set voltage value.
        
        Args:
            channel: Output channel number
            
        Returns:
            float: The voltage setting in volts
        """
        return self.supply.get_voltage(channel)
    
    def measure_voltage(self, channel: int = 1) -> float:
        """Measure the actual output voltage.
        
        Args:
            channel: Output channel number
            
        Returns:
            float: The measured voltage in volts
        """
        return self.supply.measure_voltage(channel)
    
    def measure_current(self, channel: int = 1) -> float:
        """Measure the actual output current.
        
        Args:
            channel: Output channel number
            
        Returns:
            float: The measured current in amperes
        """
        return self.supply.measure_current(channel)
    
    def enable_output(self, channel: Optional[int] = None) -> None:
        """Enable the output.
        
        Args:
            channel: Output channel number (if None, enable all channels)
        """
        self.supply.enable_output(channel)
    
    def disable_output(self, channel: Optional[int] = None) -> None:
        """Disable the output.
        
        Args:
            channel: Output channel number (if None, disable all channels)
        """
        self.supply.disable_output(channel)
    
    def get_output_state(self, channel: int = 1) -> bool:
        """Get the output state.
        
        Args:
            channel: Output channel number
            
        Returns:
            bool: True if output is enabled, False otherwise
        """
        return self.supply.get_output_state(channel)
    
    def reset(self) -> None:
        """Reset the instrument to default settings."""
        # First reset using the base class method (sends *RST command)
        super().reset()
        # Then allow the specific controller to do any additional reset steps
        if hasattr(self.supply, 'reset'):
            self.supply.reset()

    def clear(self) -> None:
        """Clear the instrument's status registers and error queue."""
        # First clear using the base class method (sends *CLS command)
        super().clear()
        # Then allow the specific controller to do any additional clearing
        if hasattr(self.supply, 'clear'):
            self.supply.clear()

    # Legacy method aliases for backward compatibility
    def set_channel_voltage(self, voltage: float, channel: int = 1) -> None:
        """Set voltage for a specific channel (legacy method)."""
        self.set_voltage(voltage, 0.1, channel)  # Default current limit of 0.1A
        
    def measure_output_voltage(self, channel: int = 1) -> float:
        """Measure output voltage (legacy method)."""
        return self.measure_voltage(channel)
        
    def measure_output_current(self, channel: int = 1) -> float:
        """Measure output current (legacy method)."""
        return self.measure_current(channel)

    # Add any additional methods that would be useful for power supplies
    def set_voltage_current(self, voltage: float, current: float, channel: int = 1) -> None:
        """Convenience method to set both voltage and current in one call."""
        self.set_voltage(voltage, current, channel)

    def get_all_measurements(self, channel: int = 1) -> Dict[str, float]:
        """Get all measurements for a channel.
        
        Args:
            channel: Output channel number
            
        Returns:
            Dict with voltage and current measurements
        """
        return {
            "voltage": self.measure_voltage(channel),
            "current": self.measure_current(channel)
        }

    def voltage_sweep(self, start: float, stop: float, steps: int, 
                    current_limit: float = 0.1, channel: int = 1, 
                    delay: float = 0.5, callback = None) -> List[Dict[str, float]]:
        """Perform a voltage sweep and measure at each step.
        
        Args:
            start: Starting voltage
            stop: Ending voltage
            steps: Number of steps
            current_limit: Current limit in amps
            channel: Channel number
            delay: Delay between steps in seconds
            callback: Optional callback function(voltage, current, step)
            
        Returns:
            List of measurement dictionaries with voltage and current readings
        """
        import numpy as np
        import time
        
        # Calculate voltage steps
        voltages = np.linspace(start, stop, steps)
        results = []
        
        # Enable output
        self.enable_output(channel)
        
        try:
            print(f"Sweeping voltage from {start}V to {stop}V in {steps} steps")
            
            for i, voltage in enumerate(voltages):
                self.set_voltage(voltage, current_limit, channel)
                time.sleep(delay)  # Allow settling time
                
                # Measure
                measured_v = self.measure_voltage(channel)
                measured_i = self.measure_current(channel)
                
                # Store results
                result = {
                    'set_voltage': voltage,
                    'measured_voltage': measured_v,
                    'measured_current': measured_i
                }
                results.append(result)
                
                # Call callback if provided
                if callback:
                    callback(measured_v, measured_i, i)
                
                print(f"\rStep {i+1}/{steps}: {measured_v:.3f}V, {measured_i*1000:.3f}mA", end="")
                
            print("\nSweep complete")
            return results
            
        except Exception as e:
            logger.error(f"Error during voltage sweep: {str(e)}")
            print(f"\nError during voltage sweep: {str(e)}")
            return results
        finally:
            # Safety: return to a safe voltage
            self.set_voltage(0.0, current_limit, channel)