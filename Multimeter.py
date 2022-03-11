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
    clear()
    exception_handler()
    fetch()
    fetch_current()
    fetch_current_AC()
    fetch_resistance()
    fetch_voltage()
    fetch_voltage_AC()
    get_error()
    get_function()
    get_range()
    get_thermocouple_type()
    get_voltage_range()
    identify()
    initiate()
    make_connection()
    measure_current()
    measure_current_AC()
    measure_function()
    measure_resistance()
    measure_voltage()
    measure_voltage_AC()
    query()
    query_ascii_values()
    read_current()
    read_current_AC()
    read_function()
    read_resistance()
    read_voltage()
    read_voltage_AC()
    reset()
    set_function()
    set_range()
    set_thermocouple_type()
    set_thermocouple_unit()
    set_voltage_range()
    turn_off_auto_range()
    write()

  Typical usage example:

  mult = Multimeter("GPIB0::15::INSTR")
  measured_voltage = mult.read_voltage()

  OR

  mult = Multimeter("GPIB0::15::INSTR", identify = False, nickname = "Keithly 2000")
  measured_voltage = mult.read_voltage()
  
  --------------------------------------------------------------------------------------------------- |
  | COMPANY     MODEL   DOCUMENT      LINK                                                            |
  --------------------------------------------------------------------------------------------------- |
  | HP          34401A  Users Guide   https://engineering.purdue.edu/~aae520/hp34401manual.pdf        |
  | Keithly     2000    Users Guide   https://download.tek.com/manual/2000-900_J-Aug2010_User.pdf     |
  | Keithly     2110    Users Guide   https://download.tek.com/manual/2110-901-01(C-Aug2013)(Ref).pdf |
  | Tektronix   DMM4050 Users Guide   https://download.tek.com/manual/077036300web_0.pdf              |
  --------------------------------------------------------------------------------------------------- |
"""
import inspect
import sys
import pyvisa

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
    
    def exception_handler(func):
        """Handles the exceptions which might occur during a visa transaction.

        Args:
        func: the function which is being called

        Returns:
        The return value from the function

        Raises:
        ValueError: If the result couldn't be convereted to float.
        pyvisa.errors.VisaIOError: 
        pyvisa.errors.VisaIOErrorVI_ERROR_NLISTENERS:
        pyvisa.errors.VI_ERROR_TMO:
        """
        def inner_function(self, *args, **kw):

            retval = sys.maxsize
            try:
                return func(self, *args, **kw)
            except ValueError as ex:
                print(f"Could not convert returned value to float from meter: {self.instrument_ID} at {self.instrument} \n \
                        in class {self.__class__.__name__}, method {func.__name__}")
                return retval
            except TypeError as ex:
                print("Wrong param Type")
                return retval
            except pyvisa.errors.VisaIOError as ex:
                print(f"Exception {type(ex)} {ex.abbreviation}")

                if "VI_ERROR_NLISTENERS" in ex.abbreviation:
                    print(f"Looks like the instrument at {self.instrument_address} isn't responding.. Are you sure this is the right GPIB address?.")

                if "VI_ERROR_TMO" in ex.abbreviation:
                    print(f"Looks like the instrument at {self.instrument_address} is timing out.. Are you sure this is the right GPIB address?.")

                if "VI_ERROR_RSRC_NFOUND" in ex.abbreviation:
                    print("Resource not found")

                return retval
            except Exception as ex:
                print(f"This was an exception we were not prepared for {type(ex)}, {ex}")
                return retval

        return inner_function


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

    @exception_handler
    def fetch(self, function : str = "VOLTage:DC") -> float:
        """Uses the FETCh? command to transfer the readings from the
        multimeters internal memory to the multimeters output buffer where
        you can read them into your bus controller.

        Args:
        none

        Returns:
        The return from instrument or sys.maxsize to indicate there was an error
        """
        retval = sys.maxsize 
        self.set_function(function)
        self.initiate()
        retval = float(self.connection.query("FETCh?"))
        return retval

    @exception_handler
    def fetch_voltage_AC(self, function : str = "VOLTage:AC") -> float:
        """Fetch AC voltage reading

        Args:
        str: function

        Returns:
        The return from instrument or sys.maxsize to indicate there was an error
        """
        return self.fetch(function)

    @exception_handler
    def fetch_current_AC(self, function : str = "CURRent:AC") -> float:
        """Fetch AC voltage reading

        Args:
        str: function

        Returns:
        The return from instrument or sys.maxsize to indicate there was an error
        """
        return self.fetch(function)


    @exception_handler
    def fetch_current(self, function : str = "CURRent:DC") -> float:
        """Fetch AC voltage reading

        Args:
        str: function

        Returns:
        The return from instrument or sys.maxsize to indicate there was an error
        """
        return self.fetch(function)

    @exception_handler
    def fetch_resistance(self, function : str = "RESistance") -> float:
        """Fetch AC voltage reading

        Args:
        str: function

        Returns:
        The return from instrument or sys.maxsize to indicate there was an error
        """
        return self.fetch(function)


    @exception_handler
    def fetch_voltage(self, function : str = "VOLTage:DC") -> float:
        """Uses the FETCh? command to transfer the readings from the
        multimeters internal memory to the multimeters output buffer where
        you can read them into your bus controller.

        Args:
        none

        Returns:
        The voltage or sys.maxsize to indicate there was an error
        """
        return self.fetch(function)

        
    @exception_handler    
    def read_function(self, function : str = "VOLTage:DC") -> float:
        """Perform measurement and acquire reading.

        Args:
        none

        Returns:
        float: the current voltage
        """
        retval = sys.maxsize
        self.set_function(function)
        
        # If continuous initiation is enabled, then the :INITiate command 
        # generates an error and ignores the Command. 
        if "2000" in self.instrument_ID:
            self.connection.write(":INITiate:CONTinuous OFF")

        retval = float(self.connection.query("READ?"))
        return retval

    @exception_handler    
    def read_voltage(self, function : str = "VOLT") -> float:
        """Perform measurement and acquire reading.

        Args:
        none

        Returns:
        float: the current voltage
        """
        retval = sys.maxsize
        
        if (self.get_function() != "VOLT"):
            self.set_function(function)

        # If continuous initiation is enabled, then the :INITiate command 
        # generates an error and ignores the Command. 
        if "2000" in self.instrument_ID:
            self.connection.write(":INITiate:CONTinuous OFF")

        retval = float(self.connection.query("READ?"))
        return retval


    @exception_handler    
    def read_voltage_AC(self, function : str = "VOLT:AC") -> float:
        """Perform measurement and acquire reading.

        Args:
        none

        Returns:
        float: the current voltage
        """
        retval = sys.maxsize

        if (self.get_function() != "VOLT:AC"):
            self.set_function(function)
        
        # If continuous initiation is enabled, then the :INITiate command 
        # generates an error and ignores the Command. 
        if "2000" in self.instrument_ID:
            self.connection.write(":INITiate:CONTinuous OFF")

        retval = float(self.connection.query("READ?"))
        return retval


    @exception_handler    
    def read_current(self, function : str = "CURRent:DC") -> float:
        """Perform measurement and acquire reading.

        Args:
        none

        Returns:
        float: the current voltage
        """
        retval = sys.maxsize
        self.set_function(function)
        
        # If continuous initiation is enabled, then the :INITiate command 
        # generates an error and ignores the Command. 
        if "2000" in self.instrument_ID:
            self.connection.write(":INITiate:CONTinuous OFF")

        retval = float(self.connection.query("READ?"))
        return retval


    @exception_handler    
    def read_current_AC(self, function : str = "CURRent:AC") -> float:
        """Perform measurement and acquire reading.

        Args:
        none

        Returns:
        float: the current voltage
        """
        retval = sys.maxsize
        self.set_function(function)
        
        # If continuous initiation is enabled, then the :INITiate command 
        # generates an error and ignores the Command. 
        if "2000" in self.instrument_ID:
            self.connection.write(":INITiate:CONTinuous OFF")

        retval = float(self.connection.query("READ?"))
        return retval

    @exception_handler    
    def read_resistance(self, function : str = "RESistance") -> float:
        """Perform measurement and acquire reading.

        Args:
        none

        Returns:
        float: the current voltage
        """
        retval = sys.maxsize
        self.set_function(function)
        
        # If continuous initiation is enabled, then the :INITiate command 
        # generates an error and ignores the Command. 
        if "2000" in self.instrument_ID:
            self.connection.write(":INITiate:CONTinuous OFF")

        retval = float(self.connection.query("READ?"))
        return retval

    @exception_handler    
    def measure_function(self, function : str = "VOLT") -> float:
        """This command combines all of the other signal 
           oriented measurement commands to perform a 
          “one-shot” measurement and acquire the reading.

        Args:
        function: a given function. VOLTage:DC by default

        Returns:
        float: The measurement result
        """
        retval = sys.maxsize

        if (self.get_function() != function):
            self.set_function(function)

        retval = float(self.connection.query(f"MEASure:{function}?"))
        return retval


    @exception_handler    
    def measure_voltage(self, function : str = "VOLTage:DC") -> float:
        """Measures the DC voltage

        Args:
        function: a given function. VOLTage:DC by default

        Returns:
        float: The measurement result
        """
        retval = sys.maxsize
        retval = float(self.connection.query(f"MEASure:{function}?"))
        return retval


    @exception_handler    
    def measure_voltage_AC(self, function : str = "VOLTage:AC") -> float:
        """Measures the AC voltage

        Args:
        function: a given function. VOLTage:DC by default

        Returns:
        float: The measurement result
        """
        retval = sys.maxsize
        self.set_function(function)
        retval = float(self.connection.query(f"MEASure:{function}?"))
        return retval


    @exception_handler    
    def measure_current(self, function : str = "CURRent:DC") -> float:
        """Measures the DC current

        Args:
        function: a given function. VOLTage:DC by default

        Returns:
        float: The measurement result
        """
        retval = sys.maxsize
        self.set_function(function)
        retval = float(self.connection.query(f"MEASure:{function}?"))
        return retval


    @exception_handler    
    def measure_current_AC(self, function : str = "CURRent:AC") -> float:
        """Measures the AC voltage

        Args:
        function: a given function. VOLTage:DC by default

        Returns:
        float: The measurement result
        """
        retval = sys.maxsize
        self.set_function(function)
        retval = float(self.connection.query(f"MEASure:{function}?"))
        return retval


    @exception_handler    
    def measure_resistance(self, function : str = "RESistance") -> float:
        """Measures the resistance

        Args:
        function: a given function. VOLTage:DC by default

        Returns:
        float: The measurement result
        """
        retval = sys.maxsize
        self.set_function(function)
        retval = float(self.connection.query(f"MEASure:{function}?"))
        return retval


    @exception_handler    
    def get_function(self) -> str:
        """Gets the selected function.

        Args:
        minimum: The selected channel

        Returns:
        str: The current selected function.
        """
        current_function = self.connection.query("FUNCtion?")
        return current_function.strip("\n").strip("\"")

    @exception_handler    
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


    @exception_handler    
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

    @exception_handler    
    def set_thermocouple_type(self, thermocouple_type: str) -> str:
        if "2000" in self.instrument_ID:
            self.connection.write(f"TEMPerature:TCOuple:TYPE {thermocouple_type}")
            retval = self.get_thermocouple_type()
            return retval

        elif "2110" in self.instrument_ID:
            self.connection.write(f"TCOuple:TYPE {thermocouple_type}")
            retval = self.get_thermocouple_type()
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


    @exception_handler    
    def turn_off_auto_range(self):
        self.connection.write("VOLTage:DC:RANGe:AUTO OFF")

    @exception_handler    
    def get_auto_range_state(self):
        return self.connection.query("VOLTage:DC:RANGe:AUTO?").strip("\n")


    @exception_handler    
    def set_thermocouple_unit(self, unit: str):
        """Identifies the instrument ID using *IDN? query.

        Args:
        unit: set the unit to one of the following:
            Cel, Far, K

        Returns:
        bool if the identification was successful or not
        """
        self.connection.write(f"UNIT {unit}")


    @exception_handler    
    def get_voltage_range(self):
        """Gets the selected function.

        Args:
        minimum: The selected channel

        Returns:
        The current selected function.

        Raises:
        Except: If the query fails.
        """
        return self.get_range("VOLTage:DC")


    @exception_handler    
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
        

    @exception_handler    
    def set_voltage_range(self, voltage_range):
        """Sets the voltage range .

        Args:
        voltage_range: the given range

        Returns:
        float: the current range
        """
        self.set_range(voltage_range, "VOLTage:DC")
        return self.get_voltage_range()


    @exception_handler    
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
        

    @exception_handler    
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
            

    @exception_handler    
    def reset(self):
        self.connection.write("*RST")
        return True
        

    @exception_handler    
    def clear(self):
        self.connection.write("*CLS")
        return True


    """General PyVISA functions

        write
        query
        query_ascii_values
    """

    @exception_handler    
    def write(self, message : str) -> str:
        self.connection.write(message)


    @exception_handler    
    def query(self, message) -> str:
        return self.connection.query(message)


    @exception_handler    
    def query_ascii_values(self, message) -> list:
        return self.connection.query_ascii_values(message)
