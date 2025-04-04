"""
Python library containing general functions to control Keysight B2902A SMU.

This module provides a standardized interface for working with Source Measure Units
to perform precision voltage/current sourcing and measurement.

Supported devices:
- Keysight B2902A
"""

from .base import LibraryTemplate
from .utils import visa_exception_handler
import numpy as np
import time
import sys
import pyvisa
import logging

# Setup module logger
logger = logging.getLogger(__name__)

class SMU(LibraryTemplate):
    """General SMU class for interfacing with Source Measure Units.

    This class provides a unified interface to control various SMU models
    through standard commands. It handles connection establishment, command sending,
    and measurement acquisition.

    Attributes:
        instrument_address: The VISA address of the connected SMU.
        connection: The PyVISA resource connection object.
        instrument_ID: The identification string of the connected instrument.
        nickname: A user-provided name for the instrument (optional).
    """
    
    def __init__(self, instrument_address: str, nickname: str = None, identify: bool = True):
        """Initalizes the instance with necessary information.

        Args:
        instrument_address: The selected channel
        nickname: string which allows naming of a device yourself. 
        identify: boolean which will either identify the instrument with *IDN? or not.
                  This is useful as some instruments do not have this command built in.

        Returns:
        The current selected function.

        Raises:
        Except: If the query fails.
        """      
        self.instrument_address = instrument_address
        self.rm = pyvisa.ResourceManager()
        self.connection = None
        self.instrument_ID = None
        self.nickname = nickname

        if (not self.make_connection(identify)):
            sys.exit()

        # Increase the timeout as some functions  
        # such as Voltage:AC take longer to process
        self.connection.timeout = 5000

    # Make the GPIB connection & set up the instrument
    def make_connection(self, identify: bool) -> bool:
        """Attempts to make a GPIB PyVISA connection with instrument .

        Args:
        instrument_address: The selected channel
        identify: boolean which will either identify the instrument with *IDN? or not.
                  This is useful as some instruments do not have this command built in. 

        Returns:
        boolean for if connection was made successfully

        Raises:
        Except: If the query fails.
        """
        # Make the connection
        try:
            # Make the connection and store it
            self.connection = self.rm.open_resource(self.instrument_address)
            
            # Display that the connection has been made
            if identify == True:              
                if (self.identify()):
                    print(f"Successfully established {self.instrument_address} connection with {self.instrument_ID}")
                    return True
                else:
                    return False
            else:
                if self.nickname == None:
                    print("If identify is false nickname must be set")
                    sys.exit()
                else:
                    self.instrument_ID = self.nickname

                print(f"Successfully established {self.instrument_address} connection with {self.instrument_ID}")
                return True
        
        except Exception as ex:
            print(f"General exception connecting to {self.instrument_address} connection.")
            print(ex)
            return False
            

    def identify(self) -> bool:
        """Identifies the instrument ID using *IDN? query.

        Args:
        none

        Returns:
        bool if the identification was successful or not

        Raises:
        Except: If the identification fails.
        """
        try:
            self.instrument_ID = self.connection.query("*IDN?")[:-1]
            return True
        except:
            print(f"{self.__class__.__name__} at {self.instrument_address} could not by identified using *IDN?")
            return False


    def initiate(self) -> bool:
        '''
        Change state of triggering system to wait for trigger state.
        '''
        """Gets the selected function.

        Args:
        minimum: The selected channel

        Returns:
        The current selected function.

        Raises:
        Except: If the query fails.
        """
        
        self.connection.write("INIT")
        return True

    
    @visa_exception_handler(module_logger=logger)
    def fetch(self, function : str = "VOLT") -> float:
        """Uses the FETCh? command to transfer the readings from the
        multimeters internal memory to the multimeters output buffer where
        you can read them into your bus controller.

        Args:
        none

        Returns:
        The return from instrument or sys.maxsize to indicate there was an error
        """
        # If the function is already set, we don't want to set it again.
        # The reason is that each time the function is set, the config
        # is also reset. An example is auto range. When the function is set
        # Autorange is automatically turned back to ON.
        if (self.get_function() != function):
            self.set_function(function)

        self.initiate()
        return float(self.connection.query("FETCh?"))


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

    def close(self):
        """Close the connection to the SMU.
        
        This method should be called when finished using the instrument.
        """
        super().close_connection()  # Use the parent's implementation


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