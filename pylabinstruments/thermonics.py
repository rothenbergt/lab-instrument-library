"""
Python library for controlling temperature forcing systems.

This module provides a standardized interface for communicating with Thermonics
and other temperature control devices using a proper object-oriented design.

Supported devices:
- Thermonics T-2500SE
- Thermonics T-2420
- Laboratory Ovens
- X-Stream 4300

Documentation references:
- Thermonics T-2500SE User Manual: https://www.manualsdir.com/manuals/319832/atec-thermonics-t-2500se.html
- Thermonics T-2500SE Datasheet: https://www.atecorp.com/getmedia/51110e58-1f65-4c4c-9580-58511566b537/thermonics-t-2500se_datasheet_1.pdf
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Callable, List, Optional

import pyvisa

from .utils import visa_exception_handler

# Setup module logger
logger = logging.getLogger(__name__)


class TemperatureController(ABC):
    """Abstract base class for all temperature controller devices.

    This class defines the common interface for all temperature controllers.
    Specific implementations should inherit from this class.
    """

    # Standard temperature ranges
    FULL_INDUSTRIAL_RANGE = [25, 0, -40, 125, 85]
    INDUSTRIAL_RANGE = [25, 0, -40, 105, 55]

    def __init__(self, connection, device_name: str):
        """Initialize with an open connection.

        Args:
            connection: Open PyVISA connection to the instrument
            device_name: Name of the specific device
        """
        self.connection = connection
        self.device_name = device_name
        self._last_temperature = 25.0  # Default to room temperature
        self._stable_temperature = False

    @abstractmethod
    def set_temperature(self, temp: float) -> None:
        """Set the target temperature.

        Args:
            temp: Target temperature in °C.
        """
        pass

    @abstractmethod
    def get_temperature(self) -> float:
        """Get the current temperature.

        Returns:
            float: Current temperature in °C.
        """
        pass

    def check_temperature_stable(self, target_temp: float, tolerance: float = 1.0) -> bool:
        """Check if temperature has stabilized at the target value.

        Args:
            target_temp: Target temperature in °C.
            tolerance: Acceptable temperature deviation from target.

        Returns:
            bool: True if temperature is stable within tolerance.
        """
        try:
            current_temp = self.get_temperature()
            stable = abs(current_temp - target_temp) <= tolerance

            if stable and not self._stable_temperature:
                logger.info(f"Temperature stabilized at {current_temp}°C (target: {target_temp}°C)")
                self._stable_temperature = True
            elif not stable:
                self._stable_temperature = False

            return stable
        except Exception as e:
            logger.error(f"Error checking temperature stability: {str(e)}")
            return False

    def wait_for_temperature(
        self,
        target_temp: float,
        tolerance: float = 1.0,
        timeout: float = 300,
        check_interval: float = 5.0,
        callback: Optional[Callable[[float, float], None]] = None,
    ) -> bool:
        """Wait until temperature stabilizes at the target value.

        Args:
            target_temp: Target temperature in °C.
            tolerance: Acceptable temperature deviation from target.
            timeout: Maximum time to wait in seconds.
            check_interval: Time between temperature checks in seconds.
            callback: Optional callback function(current_temp, time_elapsed).

        Returns:
            bool: True if temperature stabilized within timeout.
        """
        self._stable_temperature = False
        start_time = time.time()
        elapsed = 0

        logger.info(f"Waiting for temperature to stabilize at {target_temp}°C (±{tolerance}°C)")
        print(f"Waiting for temperature to stabilize at {target_temp}°C (±{tolerance}°C)")

        try:
            while elapsed < timeout:
                current_temp = self.get_temperature()
                elapsed = time.time() - start_time

                # Call the callback function if provided
                if callback is not None:
                    try:
                        callback(current_temp, elapsed)
                    except Exception as e:
                        logger.warning(f"Error in callback: {str(e)}")

                # Print status
                print(
                    f"\rCurrent: {current_temp:.2f}°C, Target: {target_temp:.2f}°C, Elapsed: {int(elapsed)}s/{int(timeout)}s",
                    end="",
                )

                # Check if temperature is stable
                if abs(current_temp - target_temp) <= tolerance:
                    self._stable_temperature = True
                    logger.info(f"Temperature stabilized at {current_temp}°C after {int(elapsed)}s")
                    print(f"\nTemperature stabilized at {current_temp}°C after {int(elapsed)}s")
                    return True

                # Wait before checking again
                time.sleep(check_interval)

            # If we exit the while loop, we've timed out
            logger.warning(f"Timeout waiting for temperature to stabilize at {target_temp}°C")
            print(f"\nTimeout waiting for temperature to stabilize at {target_temp}°C")
            return False

        except KeyboardInterrupt:
            logger.info("Temperature stabilization cancelled by user")
            print("\nTemperature stabilization cancelled by user")
            return False
        except Exception as e:
            logger.error(f"Error waiting for temperature: {str(e)}")
            print(f"\nError waiting for temperature: {str(e)}")
            return False

    def close(self) -> None:
        """Close the connection safely."""
        pass  # Default implementation does nothing


class ThermocoupleOven(TemperatureController):
    """Controller for laboratory ovens that use thermocouples."""

    def set_temperature(self, temp: float) -> None:
        """Set the oven temperature.

        Args:
            temp: Target temperature in °C.
        """
        try:
            self.connection.write(f"{temp}C")
            logger.info(f"Set oven temperature to {temp}°C")
            self._last_temperature = temp
        except Exception as e:
            logger.error(f"Error setting oven temperature to {temp}°C: {str(e)}")

    def get_temperature(self) -> float:
        """Get the current oven temperature.

        Returns:
            float: Current temperature in °C.
        """
        try:
            temp = float(self.connection.query("T").strip())
            logger.debug(f"Current oven temperature: {temp}°C")
            return temp
        except Exception as e:
            logger.error(f"Error getting oven temperature: {str(e)}")
            return self._last_temperature


class ThermocoupleController(TemperatureController):
    """Base class for Thermonics temperature controllers."""

    def __init__(self, connection, device_name: str):
        """Initialize the Thermonics controller.

        Args:
            connection: Open PyVISA connection to the instrument
            device_name: Name of the specific device
        """
        super().__init__(connection, device_name)
        # Configure specific termination settings for Thermonics devices
        connection.write_termination = '\r\n'
        connection.read_termination = '\r\n'
        connection.baud_rate = 9600

    def set_temperature(self, temp: float) -> None:
        """Set the target temperature.

        Args:
            temp: Target temperature in °C.
        """
        try:
            logger.info(f"Setting temperature to {temp}°C")
            print(f"Setting temperature to: {temp}°C")

            # Thermonics has different commands for hot vs cold
            if temp <= 25.0:
                self.set_cold_temp(temp)
                self.select_cold()
            else:
                self.set_hot_temp(temp)
                self.select_hot()

            # Update last temperature
            self._last_temperature = temp
            self._stable_temperature = False
        except Exception as e:
            logger.error(f"Error setting temperature to {temp}°C: {str(e)}")
            print(f"Error setting temperature: {str(e)}")

    def get_temperature(self) -> float:
        """Get the current temperature.

        Returns:
            float: Current temperature in °C.
        """
        try:
            temp = float(self.connection.query("RA").strip())
            logger.debug(f"Current temperature: {temp}°C")
            return temp
        except Exception as e:
            logger.error(f"Error getting temperature: {str(e)}")
            return self._last_temperature

    def set_hot_temp(self, temp: float) -> None:
        """Set the hot air temperature.

        Args:
            temp: Target temperature in °C.
        """
        try:
            self.connection.write(f"TH{temp}")
            logger.info(f"Set hot temperature to {temp}°C")
        except Exception as e:
            logger.error(f"Error setting hot temperature to {temp}°C: {str(e)}")

    def set_cold_temp(self, temp: float) -> None:
        """Set the cold air temperature.

        Args:
            temp: Target temperature in °C.
        """
        try:
            self.connection.write(f"TC{temp}")
            logger.info(f"Set cold temperature to {temp}°C")
        except Exception as e:
            logger.error(f"Error setting cold temperature to {temp}°C: {str(e)}")

    def select_cold(self) -> None:
        """Select cold air."""
        try:
            self.connection.write("AC")
            logger.info("Selected cold air")
        except Exception as e:
            logger.error(f"Error selecting cold air: {str(e)}")

    def select_hot(self) -> None:
        """Select hot air."""
        try:
            self.connection.write("AH")
            logger.info("Selected hot air")
        except Exception as e:
            logger.error(f"Error selecting hot air: {str(e)}")

    def select_ambient(self) -> None:
        """Select ambient air (no heating/cooling)."""
        try:
            self.connection.write("AA")
            logger.info("Selected ambient air")
        except Exception as e:
            logger.error(f"Error selecting ambient air: {str(e)}")

    def select_ambient_forced(self) -> None:
        """Select forced ambient air."""
        try:
            self.connection.write("AF")
            logger.info("Selected ambient forced air")
        except Exception as e:
            logger.error(f"Error selecting ambient forced air: {str(e)}")

    def turn_off_compressor(self) -> None:
        """Turn off the compressor."""
        try:
            self.connection.write("CP")
            logger.info("Turned off compressor")
        except Exception as e:
            logger.error(f"Error turning off compressor: {str(e)}")

    def turn_on_compressor(self) -> None:
        """Turn on the compressor."""
        try:
            self.connection.write("CS")
            logger.info("Turned on compressor")
        except Exception as e:
            logger.error(f"Error turning on compressor: {str(e)}")

    def close(self) -> None:
        """Return to a safe state before closing."""
        try:
            self.select_ambient()
            logger.info("Set to ambient temperature before closing")
        except Exception as e:
            logger.error(f"Error setting to ambient before closing: {str(e)}")


class ThermocoupleT2500(ThermocoupleController):
    """Controller for Thermonics T-2500SE."""

    # T-2500SE-specific functionality can be added here
    pass


class ThermocoupleT2420(ThermocoupleController):
    """Controller for Thermonics T-2420."""

    # T-2420-specific functionality can be added here
    pass


class XStreamController(TemperatureController):
    """Controller for X-Stream 4300."""

    def set_temperature(self, temp: float) -> None:
        """Set the target temperature.

        Args:
            temp: Target temperature in °C.
        """
        logger.warning("Temperature setting not yet implemented for X-Stream 4300")
        print("Setting temperature is not yet implemented for X-Stream 4300")
        self._last_temperature = temp

    def get_temperature(self) -> float:
        """Get the current temperature.

        Returns:
            float: Current temperature in °C or last set temperature.
        """
        logger.warning("Temperature reading not yet implemented for X-Stream 4300")
        return self._last_temperature


class Thermonics:
    """Factory class for creating appropriate temperature controller instances.

    This class creates and configures the appropriate controller subclass based
    on the selected instrument type.
    """

    # Dictionary mapping names to controller classes
    _controller_classes = {
        "Oven": ThermocoupleOven,
        "Thermonics T-2500SE": ThermocoupleT2500,
        "Thermonics T-2420": ThermocoupleT2420,
        "X-Stream 4300": XStreamController,
    }

    # Simplified names for user selection
    instrument_dictionary = {"1": "Oven", "2": "Thermonics T-2500SE", "3": "Thermonics T-2420", "4": "X-Stream 4300"}

    # Standard test temperature points
    full_industrial_range = TemperatureController.FULL_INDUSTRIAL_RANGE
    industrial_range = TemperatureController.INDUSTRIAL_RANGE

    def __init__(
        self,
        instrument_address: str = "GPIB0::21::INSTR",
        selected_instrument: Optional[str] = None,
        identify: bool = False,
    ):
        """Initialize and select appropriate temperature controller.

        Args:
            instrument_address: VISA address of the instrument.
            selected_instrument: Name of the selected instrument (optional).
            identify: Attempt to identify the instrument with IDN query.
        """
        self.instrument_address = instrument_address
        self.rm = pyvisa.ResourceManager()
        self.connection = None
        self.controller = None

        # Connect to the instrument
        if not self._connect(selected_instrument, identify):
            logger.error(f"Failed to connect to temperature controller at {instrument_address}")
            raise ConnectionError(f"Could not connect to temperature controller at {instrument_address}")

    def _connect(self, selected_instrument: Optional[str], identify: bool) -> bool:
        """Establish connection and configure the appropriate controller.

        Args:
            selected_instrument: Name of the selected instrument.
            identify: Attempt to identify the instrument via IDN query.

        Returns:
            bool: True if connected successfully, False otherwise.
        """
        try:
            # Open the connection
            self.connection = self.rm.open_resource(self.instrument_address)
            self.connection.timeout = 2500

            # Determine the instrument type
            instrument_name = self._determine_instrument_type(selected_instrument, identify)
            if not instrument_name:
                return False

            # Create appropriate controller instance
            if instrument_name in self._controller_classes:
                controller_class = self._controller_classes[instrument_name]
                self.controller = controller_class(self.connection, instrument_name)
                logger.info(f"Successfully connected to {instrument_name} at {self.instrument_address}")
                print(f"Successfully established connection with {instrument_name}")
                return True
            else:
                logger.error(f"No controller available for {instrument_name}")
                print(f"No controller implemented for {instrument_name}")
                return False

        except Exception as e:
            logger.error(f"Error connecting to {self.instrument_address}: {str(e)}")
            print(f"Error connecting to {self.instrument_address}: {str(e)}")
            return False

    def _determine_instrument_type(self, selected_instrument: Optional[str], identify: bool) -> Optional[str]:
        """Determine the type of instrument connected.

        Args:
            selected_instrument: User-provided instrument name.
            identify: Whether to attempt identification via IDN query.

        Returns:
            str: The determined instrument name or None if not determined.
        """
        # If instrument is specified directly, use that
        if selected_instrument:
            if selected_instrument in self._controller_classes:
                return selected_instrument
            else:
                logger.warning(f"Unknown instrument: {selected_instrument}")

        # Try to identify using IDN query
        if identify:
            try:
                idn = self.connection.query("*IDN?").strip()
                logger.debug(f"IDN response: {idn}")
                # Match IDN with instrument type (this would need customization)
                if "2500" in idn:
                    return "Thermonics T-2500SE"
                elif "2420" in idn:
                    return "Thermonics T-2420"
                elif "X-Stream" in idn or "4300" in idn:
                    return "X-Stream 4300"
            except Exception:
                logger.warning("Could not identify instrument using *IDN?")

        # Ask the user to select
        print("Please select your temperature forcing system:")
        for key, value in self.instrument_dictionary.items():
            print(f"{key}: {value}")

        try:
            user_choice = input("Choice: ")
            if user_choice in self.instrument_dictionary:
                return self.instrument_dictionary[user_choice]
            else:
                logger.error(f"Invalid selection: {user_choice}")
                print("Not a valid choice!")
                return None
        except Exception as e:
            logger.error(f"Error during instrument selection: {str(e)}")
            return None

    # Forward methods to the controller
    @visa_exception_handler(default_return_value=False, module_logger=logger)
    def set_temperature(self, temp: float) -> bool:
        """Set the target temperature.

        Args:
            temp: Target temperature in °C.

        Returns:
            bool: True if successful, False otherwise
        """
        self.controller.set_temperature(temp)
        return True  # Return success after setting temperature

    def get_temperature(self) -> float:
        """Get the current temperature."""
        return self.controller.get_temperature()

    def check_temperature_stable(self, target_temp: float, tolerance: float = 1.0) -> bool:
        """Check if temperature has stabilized."""
        return self.controller.check_temperature_stable(target_temp, tolerance)

    def wait_for_temperature(
        self,
        target_temp: float,
        tolerance: float = 1.0,
        timeout: float = 300,
        check_interval: float = 5.0,
        callback: Optional[Callable[[float, float], None]] = None,
    ) -> bool:
        """Wait until temperature stabilizes."""
        return self.controller.wait_for_temperature(target_temp, tolerance, timeout, check_interval, callback)

    def select_ambient(self) -> None:
        """Select ambient air temperature."""
        if hasattr(self.controller, 'select_ambient'):
            self.controller.select_ambient()
        else:
            logger.warning("select_ambient not supported by this controller")
            print("Ambient air selection not supported by this controller")

    def select_cold(self) -> None:
        """Select cold air."""
        if hasattr(self.controller, 'select_cold'):
            self.controller.select_cold()
        else:
            logger.warning("select_cold not supported by this controller")
            print("Cold air selection not supported by this controller")

    def select_hot(self) -> None:
        """Select hot air."""
        if hasattr(self.controller, 'select_hot'):
            self.controller.select_hot()
        else:
            logger.warning("select_hot not supported by this controller")
            print("Hot air selection not supported by this controller")

    def select_ambient_forced(self) -> None:
        """Select forced ambient air."""
        if hasattr(self.controller, 'select_ambient_forced'):
            self.controller.select_ambient_forced()
        else:
            logger.warning("select_ambient_forced not supported by this controller")
            print("Forced ambient air selection not supported by this controller")

    def set_cold_temp(self, temp: float) -> None:
        """Set cold air temperature."""
        if hasattr(self.controller, 'set_cold_temp'):
            self.controller.set_cold_temp(temp)
        else:
            self.set_temperature(temp)  # Fall back to generic method

    def set_hot_temp(self, temp: float) -> None:
        """Set hot air temperature."""
        if hasattr(self.controller, 'set_hot_temp'):
            self.controller.set_hot_temp(temp)
        else:
            self.set_temperature(temp)  # Fall back to generic method

    def turn_on_compressor(self) -> None:
        """Turn on the compressor."""
        if hasattr(self.controller, 'turn_on_compressor'):
            self.controller.turn_on_compressor()
        else:
            logger.warning("turn_on_compressor not supported by this controller")
            print("Compressor control not supported by this controller")

    def turn_off_compressor(self) -> None:
        """Turn off the compressor."""
        if hasattr(self.controller, 'turn_off_compressor'):
            self.controller.turn_off_compressor()
        else:
            logger.warning("turn_off_compressor not supported by this controller")
            print("Compressor control not supported by this controller")

    def turn_off_air(self) -> None:
        """Turn off forced air."""
        self.select_ambient()  # Default implementation uses ambient

    def write(self, command: str) -> None:
        """Send a raw command to the instrument."""
        try:
            self.connection.write(command)
            logger.debug(f"Sent command: {command}")
        except Exception as e:
            logger.error(f"Error sending command '{command}': {str(e)}")

    @visa_exception_handler(default_return_value="", module_logger=logger)
    def query(self, command: str) -> str:
        """Send a query and return the response."""
        response = self.connection.query(command)
        logger.debug(f"Query: {command}, Response: {response.strip()}")
        return response

    def close(self) -> None:
        """Close the connection to the instrument."""
        try:
            if self.controller:
                self.controller.close()

            if self.connection:
                self.connection.close()

            logger.info("Connection to temperature controller closed")
        except Exception as e:
            logger.error(f"Error closing connection: {str(e)}")

    def cycle_temperature(self, temperatures: List[float], wait_times: List[int]) -> None:
        """Cycle through a list of temperatures with wait times.

        Args:
            temperatures: List of temperatures to cycle through
            wait_times: List of times (in seconds) to wait at each temperature
        """
        if len(temperatures) != len(wait_times):
            logger.error("Temperature list and wait times must be the same length")
            return

        logger.info(f"Beginning temperature cycling through {len(temperatures)} points")
        print(f"Beginning temperature cycling through {len(temperatures)} points")

        try:
            for i, (temp, wait) in enumerate(zip(temperatures, wait_times)):
                print(f"\nStep {i+1}/{len(temperatures)}: Setting {temp}°C for {wait} seconds")
                self.set_temperature(temp)
                self.wait_for_temperature(temp)
                print(f"Temperature reached {temp}°C, waiting {wait} seconds")

                # Display countdown
                from .utils import countdown

                countdown(wait, f"Time remaining at {temp}°C")

        except KeyboardInterrupt:
            print("\nTemperature cycling stopped by user")
            self.select_ambient()
