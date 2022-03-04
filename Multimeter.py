"""  ____
    / __ \___  ____  ___  _________ ______
   / /_/ / _ \/ __ \/ _ \/ ___/ __ `/ ___/
  / _, _/  __/ / / /  __(__  ) /_/ (__  )
 /_/ |_|\___/_/ /_/\___/____/\__,_/____/
 ----------------------------------------
Python library containing general functions to control lab multimeters.

The current methods available within the module are:

  Class Methods:
    __init__()
    fetch_voltage()
    get_error()
    get_function()
    get_range()
    get_voltage_range()
    identify()
    initiate()
    make_connection()
    measure_voltage()
    read_voltage()
    set_function()
    set_range()
    set_voltage_range()

  Typical usage example:

  mult = Multimeter("GPIB0::15::INSTR")
  measured_voltage = mult.measure_voltage()

  OR

  mult = Multimeter("GPIB0::15::INSTR", identify = False, nickname = "Keithly 2000")
  measured_voltage = mult.measure_voltage()
  
  --------------------------------------------------------------------------------------------------- |
  | COMPANY     MODEL   DOCUMENT      LINK                                                            |
  --------------------------------------------------------------------------------------------------- |
  | HP          34401A  Users Guide   https://engineering.purdue.edu/~aae520/hp34401manual.pdf        |
  | Keithly     2000    Users Guide   https://download.tek.com/manual/2000-900_J-Aug2010_User.pdf     |
  | Keithly     2110    Users Guide   https://download.tek.com/manual/2110-901-01(C-Aug2013)(Ref).pdf |
  | Tektronix   DMM4050 Users Guide   https://download.tek.com/manual/077036300web_0.pdf              |
  --------------------------------------------------------------------------------------------------- |
"""
from LibraryTemplate import LibraryTemplate
import numpy as np
import time
import sys
import pyvisa
import inspect

class Multimeter():
    """General Multimeter class.

    Attributes:
        lab_multimeters: A dictionary of the current lab multimeters.
        instrument_address:
        connection:
        instrument_ID:
        nickname:
    """
    lab_multimeters = {
        "1": "2000",
        "2": "2110",
        "3": "4050",
        "4": "34401A",
    }
    
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
        retval = sys.maxsize 
        
        try:
            if "2000" in self.instrument_ID:
                self.connection.write("INIT")
                return True

            elif "2110" in self.instrument_ID:
                self.connection.write("INIT")
                return True

            elif "4050" in self.instrument_ID:
                self.connection.write("INIT")
                return True

            elif "34401A":
                self.connection.write("INIT")
                return True
            else:
                print(f"Device {self.instrument_ID} not in library")
        
        except ValueError as ex:
            # print(f"Could not convert returned value from meter: {self.instrument_ID} at {self.instrument}")
            return retval
        except Exception as ex:
            # print(f"Could not fetch from meter: {self.instrument_ID} at {self.instrument}")
            return retval

    def fetch_voltage(self) -> float:
        """Uses the FETCh? command to transfer the readings from the
        multimeters internal memory to the multimeters output buffer where
        you can read them into your bus controller.

        Args:
        none

        Returns:
        The voltage or sys.maxsize to indicate there was an error

        Raises:
        ValueError: If the result from the multimeter couldn't be convereted to float.
        pyvisa.errors.VisaIOError: 
        pyvisa.errors.VisaIOErrorVI_ERROR_NLISTENERS:
        pyvisa.errors.VI_ERROR_TMO
        """
        retval = sys.maxsize 
        
        try:
            if "2000" in self.instrument_ID:
                retval = float(self.connection.query("FETCh?"))
                return retval

            elif "2110" in self.instrument_ID:
                retval = float(self.connection.query("FETCh?"))
                return retval

            elif "4050" in self.instrument_ID:
                retval = float(self.connection.query("FETCh?"))
                return retval
            elif "34401A":
                retval = float(self.connection.query("FETCh?"))
                return retval
            else:
                print(f"Device {self.instrument_ID} not in library")
                return retval
        
        except ValueError as ex:
            print(f"Could not convert returned value to float from meter: {self.instrument_ID} at {self.instrument} \n \
                    in class {self.__class__.__name__}, method {inspect.currentframe().f_code.co_name}")
            return retval

        except pyvisa.errors.VisaIOError as ex:
            
            if "VI_ERROR_NLISTENERS" in ex.abbreviation:
                print(f"Looks like the instrument at {self.instrument_address} isn't responding.. Are you sure this is the right GPIB address?.")
                return retval
            else:
                print(f"Input/Output error. Check your command in class {self.__class__.__name__}, method {inspect.currentframe().f_code.co_name}")
                return retval

        except pyvisa.errors.VI_ERROR_TMO as ex:
            print(f"Device {self.instrument_ID} timeout error in class {self.__class__.__name__}, method {inspect.currentframe().f_code.co_name}")
            return retval
    


    def read_voltage(self):
        """Gets the selected function.

        Args:
        minimum: The selected channel

        Returns:
        The current selected function.

        Raises:
        Except: If the query fails.
        """
        retval = sys.maxsize
        try:
            retval = float(self.connection.query("READ?"))
        except ValueError as ex:
            print(f"Could not convert returned value from meter: {self.instrument_ID} at {self.instrument}")
        except Exception as ex:
            print(f"Could not fetch from meter: {self.instrument_ID} at {self.instrument}")
        return retval


    def measure_voltage(self, function = "VOLTage:DC"):
        """Gets the selected function.

        Args:
        minimum: The selected channel

        Returns:
        The current selected function.

        Raises:
        Except: If the query fails.
        """
        retval = sys.maxsize
        
        try:
            retval = float(self.connection.query(f"MEASure:{function}?"))
        except ValueError as ex:
            print(f"Could not convert returned value from meter: {self.instrument_ID} at {self.instrument}")
        except TimeoutError as ex:
            print(f"Timeout error from meter: {self.instrument_ID} at {self.instrument}")
        except Exception as ex:
            print(f"Could not fetch from meter: {self.instrument_ID} at {self.instrument}")
        return retval

    def get_function(self):
        """Gets the selected function.

        Args:
        minimum: The selected channel

        Returns:
        The current selected function.

        Raises:
        Except: If the query fails.
        """
        try:
            current_function = self.connection.query("FUNCtion?")
            return current_function
        except:
            print(f"General Exception from meter: {self.instrument_ID} at {self.instrument}")

    def set_function(self, function: str):
        """Gets the selected function.

        Args:
        function: The selected channel
                                            VOLTage:AC"
                                            "VOLTage[:DC]"
                                            "VOLTage[:DC]:RATio"
                                            "CURRent:AC"
                                            "CURRent[:DC]"
                                            "FREQuency[:VOLT]"
                                            "FREQuency:CURR"
                                            "FRESistance"
                                            "PERiod[:VOLT]"
                                            "PERiod:CURR"
                                            "RESistance"
                                            "DIODe"
                                            "TCOuple"
                                            "TEMPerature"
                                            "CONTinuity"
        Returns:
        The current selected function.

        Raises:
        Except: If the query fails.
        """
        '''

        '''
        self.connection.write(f":conf:{function}")

        return self.get_function()

    def set_thermocouple_type(self, thermocouple_type: str):
        self.connection.write(f"TCOuple:TYPE {thermocouple_type}")


    def get_voltage_range():
        """Gets the selected function.

        Args:
        minimum: The selected channel

        Returns:
        The current selected function.

        Raises:
        Except: If the query fails.
        """
        get_range("VOLTage:DC")

    def get_range(self, function):
        """Gets the selected function.

        Args:
        minimum: The selected channel

        Returns:
        The current selected function.

        Raises:
        Except: If the query fails.
        """
        retval = sys.maxsize 
        
        try:
            if "2000" in self.instrument_ID:

                # Path to configure measurement range:
                # Select range (0 to 1010).
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
        
        except ValueError as ex:
            # print(f"Could not convert returned value from meter: {self.instrument_ID} at {self.instrument}")
            return retval
        except Exception as ex:
            # print(f"Could not fetch from meter: {self.instrument_ID} at {self.instrument}")
            return retval      

    def set_voltage_range(self, voltage_range):
        """Gets the selected function.

        Args:
        minimum: The selected channel

        Returns:
        The current selected function.

        Raises:
        Except: If the query fails.
        """
        self.set_range(voltage_range, "VOLTage:DC")


    def set_range(self, voltage_range: float, function):
        """Gets the selected function.

        Args:
        minimum: The selected channel

        Returns:
        The current selected function.

        Raises:
        Except: If the query fails.
        """
        retval = sys.maxsize 
        
        try:
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
        
        except ValueError as ex:
            # print(f"Could not convert returned value from meter: {self.instrument_ID} at {self.instrument}")
            return retval
        except Exception as ex:
            # print(f"Could not fetch from meter: {self.instrument_ID} at {self.instrument}")
            return retval


    def get_error(self):
        """Gets the selected function.

        Args:
        minimum: The selected channel

        Returns:
        The current selected function.

        Raises:
        Except: If the query fails.
        """
        try:
            # Get the error code from the multimeter
            error_string = self.connection.query("SYSTem:ERRor?").strip("\n")
            # If the error code is 0, we have no errors
            # If the error code is anything other than 0, we have errors
            
            # Attempt to lookup the errors from the dictionary
            return error_string
            
        except ValueError as ex:
            print(f"Could not convert returned value from meter: {self.instrument_ID} at {self.instrument}")        
        except Exception as ex:
            print(f"General Exception from meter: {self.instrument_ID} at {self.instrument}")

    def query(self, message):
        try:
            return self.connection.query(message)
        except pyvisa.errors.VisaIOError as ex:
            print(f"Input/Output error. Check your command in class {self.__class__.__name__}, method {inspect.currentframe().f_code.co_name}: {message}")
        except pyvisa.errors.VI_ERROR_TMO as ex:
            print(f"Device {self.instrument_ID} timeout error in class {self.__class__.__name__}, method {inspect.currentframe().f_code.co_name}")

# TODO :init:cont off for 2000



# mult_2000 = Multimeter("GPIB0::3::INSTR", identify = False, nickname = "2000")
# print(mult_2000.fetch_voltage())
# mult_2000 = Multimeter("GPIB0::13::INSTR", identify = False, nickname = "2000")
# print(mult_2000.fetch_voltage())
mult_2110 = Multimeter("USB0::0x05E6::0x2110::8015791::INSTR")
# mult_4050 = Multimeter("GPIB0::2::INSTR")
# mult_34401A = Multimeter("GPIB0::1::INSTR")


# # mult_2000.initiate()
# # mult_2110.initiate()
# # mult_4050.initiate()
# # mult_34401A.initiate()

# # print(mult_2000.fetch_voltage())
# # print(mult_2110.fetch_voltage())
# # print(mult_4050.fetch_voltage())
# # print(mult_34401A.fetch_voltage())

# print(mult_2000.set_function('volt:dc'))
# print(mult_2000.set_function('TCOuple'))

print(mult_2110.set_function('TCOuple'))
mult_2110.set_thermocouple_type("T")
# print(mult_4050.set_function('volt:dc'))
# print(mult_34401A.set_function('volt:dc'))

mult_2110.initiate()
print(mult_2110.fetch_voltage())

# print(mult_2000.set_voltage_range(2))
# print(mult_2110.set_voltage_range(2))
# print(mult_4050.set_voltage_range(2))
# print(mult_34401A.set_voltage_range(2))

# print(mult_2000.get_range("VOLTage:DC"))
# print(mult_2110.get_range("VOLTage:DC"))
# print(mult_4050.get_range("VOLTage:DC"))
# print(mult_34401A.get_range("VOLTage:DC"))


# print(mult_2000.measure_voltage())
# print(mult_2110.measure_voltage())
# print(mult_4050.measure_voltage())
# print(mult_34401A.measure_voltage())


# print(mult_2000.get_error())
# print(mult_2110.get_error())
# print(mult_4050.get_error())
# print(mult_34401A.get_error())
