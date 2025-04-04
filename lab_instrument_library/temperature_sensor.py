"""
Python library for controlling temperature measurement devices.

This module provides a standardized interface for communicating with various
temperature measurement devices like thermometers and thermocouples, using
a proper object-oriented design.

Supported devices:
- Generic thermometers (FETCH? command)
- Thermocouples with multiple channels
- Custom temperature sensors
"""

import logging
import sys
from typing import Dict, List, Union, Optional, Any, Tuple
from abc import ABC, abstractmethod
from .base import LibraryTemplate

# Setup module logger
logger = logging.getLogger(__name__)


class TemperatureSensorBase(ABC):
    """Abstract base class for all temperature sensor devices.
    
    This class defines the common interface for all temperature sensors.
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
        
    @abstractmethod
    def get_temperature(self, channel: int = 1) -> float:
        """Get the current temperature reading.
        
        Args:
            channel: Channel number (defaults to 1)
            
        Returns:
            float: The current temperature.
        """
        pass
    
    def set_units(self, unit: str) -> None:
        """Set the temperature units.
        
        Args:
            unit: Units to use ('C', 'F', or 'K')
        """
        # Default implementation - override in subclasses if needed
        try:
            if unit.upper() in ['C', 'CEL', 'CELSIUS']:
                self.connection.write("UNIT:TEMP C")
            elif unit.upper() in ['F', 'FAR', 'FAHRENHEIT']:
                self.connection.write("UNIT:TEMP F")
            elif unit.upper() in ['K', 'KELVIN']:
                self.connection.write("UNIT:TEMP K")
            else:
                logger.warning(f"Unsupported unit: {unit}")
        except Exception as e:
            logger.error(f"Error setting units to {unit}: {str(e)}")


class SimpleFetchThermometer(TemperatureSensorBase):
    """Simple thermometer that uses the FETCH? command."""
    
    def get_temperature(self, channel: int = 1) -> float:
        """Get the current temperature reading.
        
        Args:
            channel: Not used in this implementation
            
        Returns:
            float: The current temperature or sys.maxsize on error.
        """
        try:
            response = self.connection.query("FETCH?").strip()
            return float(response)
        except Exception as e:
            logger.error(f"Error reading temperature: {str(e)}")
            return sys.maxsize


class MeasureThermometer(TemperatureSensorBase):
    """Thermometer that uses the MEAS? command with channel support."""
    
    def get_temperature(self, channel: int = 1) -> float:
        """Get the current temperature reading from the specified channel.
        
        Args:
            channel: Channel number to read from
            
        Returns:
            float: The current temperature or sys.maxsize on error.
        """
        try:
            response = self.connection.query(f"MEAS?{channel}").strip()
            return float(response)
        except Exception as e:
            logger.error(f"Error reading temperature from channel {channel}: {str(e)}")
            try:
                # Retry once
                response = self.connection.query(f"MEAS?{channel}").strip()
                return float(response)
            except Exception as retry_e:
                logger.error(f"Retry failed: {str(retry_e)}")
                return sys.maxsize


class TCoupleThermometer(TemperatureSensorBase):
    """Thermocouple with type setting capability."""
    
    def get_temperature(self, channel: int = 1) -> float:
        """Get the current temperature reading from the specified channel.
        
        Args:
            channel: Channel number to read from
            
        Returns:
            float: The current temperature or sys.maxsize on error.
        """
        try:
            response = self.connection.query(f"MEAS?{channel}").strip()
            return float(response)
        except Exception as e:
            logger.error(f"Error reading temperature from channel {channel}: {str(e)}")
            return sys.maxsize
    
    def set_type(self, channel: int, type_code: str = "T") -> None:
        """Set the thermocouple type.
        
        Args:
            channel: Channel number
            type_code: Thermocouple type ('B', 'E', 'J', 'K', 'N', 'R', 'S', 'T')
        """
        try:
            self.connection.write(f"TTYP {channel},{type_code}")
            logger.info(f"Set channel {channel} to type {type_code}")
        except Exception as e:
            logger.error(f"Error setting thermocouple type: {str(e)}")


class TemperatureSensor(LibraryTemplate):
    """Factory class for creating appropriate temperature sensor instances.
    
    This class creates and configures the appropriate sensor subclass based
    on the selected instrument type.
    """
    
    # Dictionary mapping sensor types to classes
    _sensor_classes = {
        "ThermometerFetch": SimpleFetchThermometer,
        "ThermometerMeasure": MeasureThermometer,
        "Thermocouple": TCoupleThermometer
    }
    
    # Simplified names for user selection
    sensor_types = {
        "1": "ThermometerFetch",
        "2": "ThermometerMeasure",
        "3": "Thermocouple"
    }
    
    def __init__(self, instrument_address: str, sensor_type: Optional[str] = None, 
                 nickname: Optional[str] = None, identify: bool = True):
        """Initialize and select appropriate temperature sensor.
        
        Args:
            instrument_address: VISA address of the instrument.
            sensor_type: Type of temperature sensor.
            nickname: User-defined name for the instrument.
            identify: Attempt to identify the instrument with IDN query.
        """
        super().__init__(instrument_address, nickname, identify)
        self.sensor_type = sensor_type
        self.sensor = self._create_sensor(sensor_type)
    
    def _create_sensor(self, sensor_type: Optional[str]) -> TemperatureSensorBase:
        """Create the appropriate sensor instance.
        
        Args:
            sensor_type: Type of temperature sensor to create.
            
        Returns:
            An instance of the appropriate sensor class.
        """
        # Determine sensor type if not specified
        if not sensor_type:
            sensor_type = self._determine_sensor_type()
        
        # Create sensor instance
        if sensor_type in self._sensor_classes:
            sensor_class = self._sensor_classes[sensor_type]
            return sensor_class(self.connection, sensor_type)
        else:
            # Default to simple thermometer
            logger.warning(f"Unknown sensor type: {sensor_type}. Using default.")
            return SimpleFetchThermometer(self.connection, "Unknown")
    
    def _determine_sensor_type(self) -> str:
        """Determine the type of sensor connected.
        
        This method tries to detect the appropriate sensor type, or asks
        the user to select one.
        
        Returns:
            str: The determined sensor type.
        """
        # Try to determine from instrument ID if available
        if self.instrumentID:
            if "THERMO" in self.instrumentID.upper():
                return "Thermocouple"
            # Add more detection logic here
        
        # Ask user to select
        print("Please select your temperature sensor type:")
        for key, value in self.sensor_types.items():
            print(f"{key}: {value}")
        
        try:
            choice = input("Choice: ")
            if choice in self.sensor_types:
                return self.sensor_types[choice]
        except Exception:
            pass
        
        # Default choice if all else fails
        return "ThermometerFetch"
    
    def get_temperature(self, channel: int = 1) -> float:
        """Get the current temperature reading.
        
        Args:
            channel: Channel number (defaults to 1)
            
        Returns:
            float: The current temperature.
        """
        return self.sensor.get_temperature(channel)
    
    def get_temperature_channel(self, channel: int) -> float:
        """Get temperature from specified channel.
        
        Alias for get_temperature with explicit channel parameter.
        
        Args:
            channel: Channel number to read from
            
        Returns:
            float: The temperature reading from the channel.
        """
        return self.get_temperature(channel)
    
    def set_type(self, channel: int, type_code: str = "T") -> None:
        """Set the thermocouple type if supported by the device.
        
        Args:
            channel: Channel number
            type_code: Thermocouple type code
        """
        if hasattr(self.sensor, 'set_type'):
            self.sensor.set_type(channel, type_code)
        else:
            logger.warning("This temperature sensor does not support type setting")
    
    def set_units(self, unit: str) -> None:
        """Set the temperature units.
        
        Args:
            unit: Units to use ('C', 'F', or 'K')
        """
        self.sensor.set_units(unit)

    def reset(self) -> bool:
        """Reset the instrument to default settings.
        
        This method first calls the base class reset implementation and
        then performs any temperature sensor specific reset operations.
        
        Returns:
            bool: True if reset succeeded, False otherwise.
        """
        success = super().reset()
        # Allow sensor-specific reset if supported
        if hasattr(self.sensor, 'reset'):
            sensor_success = self.sensor.reset()
            return success and sensor_success
        return success

    def close(self) -> None:
        """Close the connection to the instrument.
        
        This method ensures both the sensor-specific cleanup and 
        the base PyVISA connection closure are performed.
        """
        # First do any sensor-specific cleanup
        if hasattr(self.sensor, 'close'):
            try:
                self.sensor.close()
            except Exception as e:
                logger.warning(f"Error during sensor cleanup: {str(e)}")
        
        # Then close the underlying connection
        super().close_connection()
    
    def get_all_temperatures(self, channels: List[int]) -> Dict[int, float]:
        """Get temperatures from multiple channels at once.
        
        Args:
            channels: List of channel numbers to read
            
        Returns:
            Dict mapping channel numbers to temperature readings
        """
        results = {}
        for channel in channels:
            results[channel] = self.get_temperature(channel)
        return results
    
    def monitor_temperature(self, channel: int = 1, duration: int = 60, interval: int = 5) -> List[Tuple[float, float]]:
        """Monitor temperature over a specified duration.
        
        Args:
            channel: Channel to monitor
            duration: Monitoring duration in seconds
            interval: Sampling interval in seconds
            
        Returns:
            List of (timestamp, temperature) tuples
        """
        import time
        
        start_time = time.time()
        end_time = start_time + duration
        readings = []
        
        print(f"Monitoring temperature for {duration} seconds...")
        try:
            while time.time() < end_time:
                current_time = time.time() - start_time
                temp = self.get_temperature(channel)
                readings.append((current_time, temp))
                print(f"\rTime: {current_time:.1f}s, Temperature: {temp:.2f}°C", end="")
                time.sleep(interval)
            print("\nMonitoring complete")
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
            
        return readings


# Legacy classes for backwards compatibility
class Thermometer(TemperatureSensor):
    """Legacy thermometer class for backward compatibility.
    
    This class inherits from TemperatureSensor and defaults to the
    SimpleFetchThermometer implementation.
    """
    
    def __init__(self, instrument_address: str, nickname: Optional[str] = None, identify: bool = True):
        """Initialize a legacy thermometer instance.
        
        Args:
            instrument_address: VISA address of the instrument.
            nickname: User-defined name for the instrument.
            identify: Whether to identify the instrument with IDN query.
        """
        super().__init__(instrument_address, "ThermometerFetch", nickname, identify)


class Thermocouple(TemperatureSensor):
    """Legacy thermocouple class for backward compatibility.
    
    This class inherits from TemperatureSensor and defaults to the
    TCoupleThermometer implementation.
    """
    
    def __init__(self, instrument_address: str, nickname: Optional[str] = None, identify: bool = True):
        """Initialize a legacy thermocouple instance.
        
        Args:
            instrument_address: VISA address of the instrument.
            nickname: User-defined name for the instrument.
            identify: Whether to identify the instrument with IDN query.
        """
        super().__init__(instrument_address, "Thermocouple", nickname, identify)
    
    def get_temperature_2(self) -> float:
        """Legacy method to get temperature from channel 2.
        
        Returns:
            float: The temperature reading from channel 2.
        """
        return self.get_temperature(channel=2)
    
    def setType(self, ch: int, mnem: str = "T") -> None:
        """Legacy method to set thermocouple type.
        
        Args:
            ch: Channel number
            mnem: Thermocouple type mnemonic
        """
        self.set_type(ch, mnem)
