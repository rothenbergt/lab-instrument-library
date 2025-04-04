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
from typing import Optional, Union, Callable, Any, Dict, List
from .base import LibraryTemplate
from .utils import visa_exception_handler

# Setup module logger
logger = logging.getLogger(__name__)

class Multimeter(LibraryTemplate):
    """General multimeter interface for lab instruments.

    This class provides a unified interface to control various multimeter models
    through standard commands. It handles connection establishment, command sending,
    and measurement acquisition regardless of manufacturer differences.

    Attributes:
        lab_multimeters: Dictionary mapping of supported multimeter models.
        instrument_address: VISA address of the connected instrument.
        connection: PyVISA resource connection object.
        instrument_ID: Identification string of the connected instrument.
        nickname: User-provided name for the instrument (optional).
    """
    lab_multimeters = {
        "1": "2000",
        "2": "2110",
        "3": "4050",
        "4": "34401A",
    }
    
    # Map of model strings to identify manufacturers
    _manufacturers = {
        "33": "Agilent",
        "34": "HP/Agilent",
        "20": "Keithley",
        "21": "Keithley",
        "40": "Tektronix",
        "DMM": "Tektronix"
    }
    
    def __init__(self, instrument_address: str, nickname: Optional[str] = None, 
                 identify: bool = True, timeout: int = 5000):
        """Initialize the multimeter connection.

        Args:
            instrument_address: VISA address of the instrument.
            nickname: User-defined name for the instrument.
            identify: Whether to identify the instrument with *IDN?.
                      Set to False for instruments that don't support *IDN?.
            timeout: Connection timeout in milliseconds.

        Raises:
            SystemExit: If connection fails and no exception handler is in place.
        """      
        self.instrument_address = instrument_address
        self.rm = pyvisa.ResourceManager()
        self.connection = None
        self.instrument_ID = None
        self.nickname = nickname
        self.manufacturer = None
        self.model = None

        if not self.make_connection(identify):
            logger.error(f"Failed to connect to multimeter at {instrument_address}")
            sys.exit(1)

        # Configure instrument-specific settings
        self.connection.timeout = timeout
        
        # Detect manufacturer and model
        if self.instrument_ID:
            self._identify_manufacturer()

    def _identify_manufacturer(self) -> None:
        """Determine the manufacturer and model from the ID string."""
        if not self.instrument_ID:
            return
            
        # Extract model information
        parts = self.instrument_ID.split(',')
        if len(parts) >= 2:
            self.manufacturer = parts[0].strip()
            self.model = parts[1].strip()
            
        # For nickname behavior, also identify by model number
        for key, manufacturer in self._manufacturers.items():
            if self.model and key in self.model:
                self.manufacturer = manufacturer
                break

    def make_connection(self, identify: bool) -> bool:
        """Establish a connection to the multimeter.

        Args:
            identify: Whether to query the instrument ID.

        Returns:
            bool: True if connection was successful, False otherwise.
        """
        try:
            # Establish the connection
            self.connection = self.rm.open_resource(self.instrument_address)
            
            # Identify the instrument if requested
            if identify:              
                if self.identify():
                    logger.info(f"Connected to {self.instrument_ID} at {self.instrument_address}")
                    print(f"Successfully established {self.instrument_address} connection with {self.instrument_ID}")
                    return True
                else:
                    return False
            else:
                if self.nickname is None:
                    logger.error("Nickname must be set when identify=False")
                    print("If identify is false nickname must be set")
                    return False
                
                self.instrument_ID = self.nickname
                logger.info(f"Connected to {self.instrument_ID} at {self.instrument_address}")
                print(f"Successfully established {self.instrument_address} connection with {self.instrument_ID}")
                return True
        
        except pyvisa.errors.VisaIOError as ex:
            logger.error(f"VISA error connecting to {self.instrument_address}: {str(ex)}")
            print(f"VISA error connecting to {self.instrument_address}")
            print(ex)
            return False
        except Exception as ex:
            logger.error(f"Error connecting to {self.instrument_address}: {str(ex)}")
            print(f"General exception connecting to {self.instrument_address}")
            print(ex)
            return False
            
    def identify(self) -> bool:
        """Identify the instrument using the *IDN? query.

        Returns:
            bool: True if identification was successful, False otherwise.
        """
        try:
            self.instrument_ID = self.connection.query("*IDN?").strip()
            return True
        except Exception as ex:
            logger.error(f"Identification failed: {str(ex)}")
            print(f"{self.__class__.__name__} at {self.instrument_address} could not be identified using *IDN?")
            return False

    def initiate(self) -> bool:
        """Initiate a measurement (change to waiting-for-trigger state).
        
        This method prepares the multimeter to take a reading when triggered.

        Returns:
            bool: True if the command was sent successfully.
        """
        try:
            self.connection.write("INIT")
            return True
        except Exception as ex:
            logger.error(f"Error initiating measurement: {str(ex)}")
            return False
    
    @visa_exception_handler(default_return_value=sys.maxsize, module_logger=logger)
    def fetch(self, function: str = "VOLT") -> float:
        """Fetch the most recent measurement from the multimeter's buffer.

        This method retrieves a reading from the instrument's memory without
        initiating a new measurement. The instrument must have already taken
        a measurement or be in a continuous measurement mode.

        Args:
            function: The measurement function to use (e.g., "VOLT", "CURR").

        Returns:
            float: The measured value or sys.maxsize if an error occurred.
        """
        # Ensure the correct function is set
        current_function = self.get_function()
        if current_function != function:
            self.set_function(function)
            logger.debug(f"Changed function from {current_function} to {function}")

        self.initiate()
        response = self.connection.query("FETCh?")
        return float(response.strip())

    @visa_exception_handler(module_logger=logger)
    def fetch_voltage(self) -> float:
        """Fetch DC voltage reading

        Args:
        none

        Returns:
        The most recent DC voltage measurement
        """
        return self.fetch("VOLT")


    @visa_exception_handler(module_logger=logger)
    def fetch_voltage_AC(self) -> float:
        """Fetch AC voltage reading

        Args:
        none

        Returns:
        The most recent AC voltage measurement
        """
        return self.fetch("VOLT:AC")


    @visa_exception_handler(module_logger=logger)
    def fetch_current_AC(self) -> float:
        """Fetch AC current reading

        Args:
        none

        Returns:
        The most recent AC current measurement
        """
        return self.fetch("CURR:AC")


    @visa_exception_handler(module_logger=logger)
    def fetch_current(self) -> float:
        """Fetch DC current reading

        Args:
        none

        Returns:
        The most recent DC current measurement
        """
        return self.fetch("CURR")


    @visa_exception_handler(module_logger=logger)
    def fetch_resistance(self) -> float:
        """Fetch resistance reading

        Args:
        none

        Returns:
        The most recent resistance measurement
        """
        return self.fetch("RES")


    @visa_exception_handler(module_logger=logger)    
    def read_function(self, function : str = "VOLT") -> float:
        """Perform measurement and acquire reading.

        This method configures the multimeter for the specified measurement function
        if needed, then triggers a measurement and returns the result.

        Args:
            function: String containing the measurement function name.
                      Common values are "VOLT", "CURR", "RES", "VOLT:AC", "CURR:AC".

        Returns:
            float: The measured value.
        """

        # If the function is already set, we don't want to set it again.
        # The reason is that each time the function is set, the config
        # is also reset. An example is auto range. When the function is set
        # Autorange is automatically turned back to ON.
        if (self.get_function() != function):
            self.set_function(function)
        
        # If continuous initiation is enabled, then the :INITiate command 
        # generates an error and ignores the Command. 
        if "2000" in self.instrument_ID:
            self.connection.write(":INITiate:CONTinuous OFF")

        return float(self.connection.query("READ?"))


    @visa_exception_handler(module_logger=logger)    
    def read_voltage(self) -> float:
        """Perform DC voltage measurement and return the reading.

        Configures the multimeter for DC voltage measurement if needed,
        then triggers a measurement and returns the result.

        Args:
            None

        Returns:
            float: The measured DC voltage in volts.
        """
        return self.read_function("VOLT")


    @visa_exception_handler(module_logger=logger)    
    def read_voltage_AC(self) -> float:
        """Perform measurement and acquire reading.

        Args:
        none

        Returns:
        float: the current voltage
        """
        return self.read_function("VOLT:AC")


    @visa_exception_handler(module_logger=logger)    
    def read_current(self, function : str = "CURRent:DC") -> float:
        """Perform measurement and acquire reading.

        Args:
        none

        Returns:
        float: the current voltage
        """
        return self.read_function("CURR")


    @visa_exception_handler(module_logger=logger)    
    def read_current_AC(self, function : str = "CURRent:AC") -> float:
        """Perform measurement and acquire reading.

        Args:
        none

        Returns:
        float: the current voltage
        """
        return self.read_function("CURR:AC")


    @visa_exception_handler(module_logger=logger)    
    def read_resistance(self, function : str = "RESistance") -> float:
        """Perform measurement and acquire reading.

        Args:
        none

        Returns:
        float: the current voltage
        """
        return self.read_function("RES")


    @visa_exception_handler(module_logger=logger)    
    def measure_function(self, function : str = "VOLT") -> float:
        """This command combines all of the other signal 
           oriented measurement commands to perform a 
          “one-shot” measurement and acquire the reading.

        Args:
        function: a given function. VOLTage:DC by default

        Returns:
        float: The measurement result
        """

        # If the function is already set, we don't want to set it again.
        # The reason is that each time the function is set, the config
        # is also reset. An example is auto range. When the function is set
        # Autorange is automatically turned back to ON.
        if (self.get_function() != function):
            self.set_function(function)

        return float(self.connection.query(f"MEASure:{function}?"))


    @visa_exception_handler(module_logger=logger)    
    def measure_voltage(self) -> float:
        """Measures the DC voltage

        Args:
        none

        Returns:
        float: The measurement result
        """
        return self.measure_function("VOLT")


    @visa_exception_handler(module_logger=logger)    
    def measure_voltage_AC(self) -> float:
        """Measures the AC voltage

        Args:
        none

        Returns:
        float: The measurement result
        """
        return self.measure_function("VOLT:AC")


    @visa_exception_handler(module_logger=logger)    
    def measure_current(self) -> float:
        """Measures the DC current

        Args:
        none

        Returns:
        float: The measurement result
        """
        return self.measure_function("CURR")


    @visa_exception_handler(module_logger=logger)    
    def measure_current_AC(self, function : str = "CURRent:AC") -> float:
        """Measures the AC voltage

        Args:
        none

        Returns:
        float: The measurement result
        """
        return self.measure_function("CURR:AC")


    @visa_exception_handler(module_logger=logger)    
    def measure_resistance(self, function : str = "RESistance") -> float:
        """Measures the resistance

        Args:
        none

        Returns:
        float: The measurement result
        """
        return self.measure_function("RES")


    @visa_exception_handler(module_logger=logger)    
    def get_function(self) -> str:
        """Gets the selected function.

        Args:
        minimum: The selected channel

        Returns:
        str: The current selected function.
        """
        current_function = self.connection.query("FUNCtion?")
        return current_function.strip("\n").strip("\"")


    @visa_exception_handler(module_logger=logger)    
    def set_function(self, function: str) -> str:
        """Gets the selected function.

        Args:
        function: The selected channel
                                        VOLTage:AC
                                        VOLTage[:DC]
                                        VOLTage[:DC]:RATio
                                        CURRent:AC
                                        CURRent[:DC]
                                        FREQuency[:VOLT]
                                        FREQuency:CURR
                                        FRESistance
                                        PERiod[:VOLT]
                                        PERiod:CURR
                                        RESistance
                                        DIODe
                                        TCOuple
                                        TEMPerature
                                        CONTinuity
        Returns:
        The current selected function.

        Raises:
        Except: If the query fails.
        """
        self.connection.write(f":conf:{function}")

        return self.get_function()


    @visa_exception_handler(module_logger=logger)    
    def get_thermocouple_type(self) -> str:
        if "2000" in self.instrument_ID:
            retval = self.connection.query(f"TEMPerature:TCOUple:TYPE?")
            return retval.strip("\n")

        elif "2110" in self.instrument_ID:
            retval = self.connection.query(f"TCOuple:TYPE?")
            return retval

        elif "4050" in self.instrument_ID:
            return retval
        elif "34401A":
            return retval
        else:
            print(f"Device {self.instrument_ID} not in library")
            return retval     


    @visa_exception_handler(module_logger=logger)    
    def set_thermocouple_type(self, thermocouple_type: str) -> str:
        if "2000" in self.instrument_ID:
            self.connection.write(f"TEMPerature:TCOuple:TYPE {thermocouple_type}")
            retval = self.get_thermocouple_type()
            return retval

        elif "2110" in self.instrument_ID:
            self.connection.write(f"TCOuple:TYPE {thermocouple_type}")
            retval = self.get_thermocouple_type()
            return retval

        else:
            print(f"Device {self.instrument_ID} not in library")
            return retval


    @visa_exception_handler(module_logger=logger)    
    def turn_off_auto_range(self) -> str:
        self.connection.write("VOLTage:DC:RANGe:AUTO OFF")
        return self.get_auto_range_state()

    @visa_exception_handler(module_logger=logger)    
    def get_auto_range_state(self) -> str:
        return self.connection.query("VOLTage:DC:RANGe:AUTO?").strip("\n")


    @visa_exception_handler(module_logger=logger)    
    def set_thermocouple_unit(self, unit: str):
        """Identifies the instrument ID using *IDN? query.

        Args:
        unit: set the unit to one of the following:
            Cel, Far, K

        Returns:
        bool if the identification was successful or not
        """
        self.connection.write(f"UNIT {unit}")


    @visa_exception_handler(module_logger=logger)    
    def get_voltage_range(self):
        """Gets the selected function.

        Args:
        minimum: The selected channel

        Returns:
        The current selected function.
        """
        return self.get_range("VOLTage:DC")


    @visa_exception_handler(module_logger=logger)    
    def get_range(self, function):
        """Gets the selected function.

        Args:
        minimum: The selected channel

        Returns:
        The current selected function.
        """
        retval = sys.maxsize 
        
        if "2000" in self.instrument_ID:
            retval = self.connection.query(f"{function}:RANGe?")
            return float(retval)

        elif "2110" in self.instrument_ID:
            retval = self.connection.query(f"{function}:RANGe?")
            return float(retval)

        elif "4050" in self.instrument_ID:
            retval = self.connection.query(f"{function}:RANGe?")
            return float(retval)
        elif "34401A":
            retval = self.connection.query(f"{function}:RANGe?")
            return float(retval)
        else:
            print(f"Device {self.instrument_ID} not in library")
            return retval
        

    @visa_exception_handler(module_logger=logger)    
    def set_voltage_range(self, voltage_range):
        """Sets the voltage range .

        Args:
        voltage_range: the given range

        Returns:
        float: the current range
        """
        self.set_range(voltage_range, "VOLTage:DC")
        return self.get_voltage_range()


    @visa_exception_handler(module_logger=logger)    
    def set_range(self, voltage_range: float, function):
        """Gets the selected function.

        Args:
        minimum: The selected channel

        Returns:
        The current selected function.
        """
        retval = sys.maxsize 
        
        if "2000" in self.instrument_ID:

            # Path to configure measurement range:
            # Select range (0 to 1010).
            self.connection.write(f"{function}:RANGe {voltage_range}")

        elif "2110" in self.instrument_ID:
            self.connection.write(f"{function}:RANGe {voltage_range}")

        elif "4050" in self.instrument_ID:
            self.connection.write(f"{function}:RANGe {voltage_range}")

        elif "34401A":
            self.connection.write(f"{function}:RANGe {voltage_range}")

        else:
            print(f"Device {self.instrument_ID} not in library")
            return retval
        

    @visa_exception_handler(module_logger=logger)    
    def get_error(self) -> str:
        """Gets the first error in the error buffer.

        Args:
        none

        Returns:
        str: Either an error, or no error
        """
        # Get the error code from the multimeter
        error_string = self.connection.query("SYSTem:ERRor?").strip("\n")

        # If the error code is 0, we have no errors
        # If the error code is anything other than 0, we have errors
        
        return error_string
            

    @visa_exception_handler(module_logger=logger)    
    def reset(self):
        """Reset the instrument to factory settings.
        
        This sends the *RST command to the instrument and returns it to a known state.
        
        Returns:
            bool: True if reset succeeded, False otherwise.
        """
        return super().reset()

    @visa_exception_handler(module_logger=logger)    
    def clear(self):
        """Clear the instrument's status registers and error queue.
        
        This sends the *CLS command to the instrument.
        
        Returns:
            bool: True if clear succeeded, False otherwise.
        """
        return super().clear()

    def close(self) -> None:
        """Close the connection to the multimeter.
        
        This method should be called when finished using the instrument.
        """
        super().close_connection()
        # No need for additional try/except since the base class handles it


    """General PyVISA functions
        write
        query
        query_ascii_values
    """

    @visa_exception_handler(module_logger=logger)    
    def write(self, message : str) -> str:
        self.connection.write(message)


    @visa_exception_handler(module_logger=logger)    
    def query(self, message) -> str:
        return self.connection.query(message)


    @visa_exception_handler(module_logger=logger)    
    def query_ascii_values(self, message) -> list:
        return self.connection.query_ascii_values(message)

    @visa_exception_handler(module_logger=logger)
    def measure_statistics(self, function: str = "VOLT", samples: int = 10, delay: float = 0.1) -> Dict[str, float]:
        """Measure multiple samples and return statistics.
        
        Args:
            function: Measurement function ("VOLT", "CURR", etc.)
            samples: Number of samples to take
            delay: Delay between samples in seconds
            
        Returns:
            Dictionary of statistical values (min, max, mean, std_dev)
        """
        import time
        import numpy as np
        
        # Set the measurement function
        self.set_function(function)
        
        # Take measurements
        measurements = []
        for i in range(samples):
            value = self.read_function(function)
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

    @visa_exception_handler(module_logger=logger)
    def setup_trigger(self, source: str = "IMM", count: int = 1) -> None:
        """Configure trigger settings.
        
        Args:
            source: Trigger source ("IMM", "EXT", "BUS")
            count: Trigger count
        """
        self.write(f"TRIG:SOUR {source}")
        self.write(f"TRIG:COUN {count}")
        logger.info(f"Set trigger source to {source}, count to {count}")