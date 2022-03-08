"""  ____
    / __ \___  ____  ___  _________ ______
   / /_/ / _ \/ __ \/ _ \/ ___/ __ `/ ___/
  / _, _/  __/ / / /  __(__  ) /_/ (__  )
 /_/ |_|\___/_/ /_/\___/____/\__,_/____/
 ----------------------------------------
Python library containing general functions to control lab supplies.

    The current methods available within the module are:

    Class Methods:
        check_for_errors()
        clear()
        disable_output()
        enable_output()
        exception_handler()
        get_voltage_range()
        identify()
        make_connection()
        measure_current()
        measure_voltage()
        query()
        query_ascii_values()
        reset()
        select_output1()
        select_output2()
        select_output3()
        set_range()
        set_voltage()
        write()

    Typical usage example:

        supply = Supply()
        supply_voltage = foo.set_voltage(voltage = 1, current = 1)

  ----------------------------------------------------------------------------------------------------------------- |
  | COMPANY     MODEL   DOCUMENT      LINK                                                                          |
  ----------------------------------------------------------------------------------------------------------------  |
  | Agilent     E3631A  Users Guide   http://ece-research.unm.edu/jimp/650/instr_docs/AgilentE3631A.pdf             |
  | Agilent     E3632A  Users Guide   https://www.keysight.com/us/en/assets/9018-01309/user-manuals/9018-01309.pdf  |
  | Keysight    E3649A  Users Guide   https://www.keysight.com/us/en/assets/9018-01166/user-manuals/9018-01166.pdf  |
  | Keysight    E36313A Users Guide   https://www.keysight.com/us/en/assets/9018-04576/user-manuals/9018-04576.pdf  |
  | Keysight    E36234A Users Guide   https://www.keysight.com/us/en/assets/9018-04838/user-manuals/9018-04838.pdf  |
  ----------------------------------------------------------------------------------------------------------------- |
"""

import pyvisa
import sys
import time
import numpy as np
import inspect


class Supply():
    """General Supply class.

    Attributes:
        lab_supplies: A dictionary of the current lab multimeters.
        instrument_address:
        connection:
        instrument_ID:
        nickname:
    """

    lab_supplies = {
        "1": "E3631A",
        "2": "E3632A",
        "3": "E3649A",
        "3": "E36313A",
        "4": "E36234A",
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
            try:
                return func(self, *args, **kw)
            except ValueError as ex:
                print(f"Could not convert returned value to float from meter: {self.instrument_ID} at {self.instrument} \n \
                        in class {self.__class__.__name__}, method {func.__name__}")
                return retval
            except TypeError as ex:
                print("Wrong param Type")
            except pyvisa.errors.VisaIOError as ex:
                print(f"Exception {type(ex)} {ex.abbreviation}")

                if "VI_ERROR_NLISTENERS" in ex.abbreviation:
                    print(f"Looks like the instrument at {self.instrument_address} isn't responding.. Are you sure this is the right GPIB address?.")

                if "VI_ERROR_TMO" in ex.abbreviation:
                    print(f"Looks like the instrument at {self.instrument_address} is timing out.. Are you sure this is the right GPIB address?.")

                return sys.maxsize
            except Exception as ex:
                print(f"This was an exception we were not prepared for {type(ex)}, {ex}")

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


    @exception_handler
    def get_output_state(self) -> int:
        """For the selected channel, check the output state

        Args:
        none

        Returns:
        the output state
        """
        
        retval = sys.maxsize

        if "E3631A" in self.instrument_ID:
            retval = self.connection.query("OUTPut?")
        elif "E3632A" in self.instrument_ID:
            retval = self.connection.query("OUTPut?")
        elif "E3649A" in self.instrument_ID:
            retval = self.connection.query("OUTPut?")
        elif "E36313A" in self.instrument_ID:
            retval = self.connection.query("OUTPut?")
        elif "E36234A" in self.instrument_ID:
            retval = self.connection.query("OUTPut?")
        else:
            print(f"Device {self.instrument_ID} not in library")

        return int(retval)


    @exception_handler
    def enable_output(self) -> bool:
        #TODO union the return function
        """Enables the output of the power supply

        Args:
        minimum: The selected channel

        Returns:
        The current selected function.

        Raises:
        Except: If the query fails.
        """
        if "E3631A" in self.instrument_ID:
            self.connection.write("OUTPut ON")
            return self.get_output_state()
        elif "E3632A" in self.instrument_ID:
            self.connection.write("OUTPut ON")
            return self.get_output_state()
        elif "E3649A" in self.instrument_ID:
            self.connection.write("OUTPut ON")     
            return self.get_output_state()
        elif "E36313A" in self.instrument_ID:
            self.connection.write("OUTPut ON")    
            return self.get_output_state()
        elif "E36234A" in self.instrument_ID:
            self.connection.write("OUTPut ON")    
            return self.get_output_state()
        else:
            print(f"Device {self.instrument_ID} not in library")
    
        return False



    @exception_handler    
    def disable_output(self) -> bool:
        """Disables the output of the power supply

        Args:

        Returns:
        bool: if the disable went through or not.

        Raises:
        Except: If the query fails.
        """
        if "E3631A" in self.instrument_ID:
            self.connection.write("OUTPut OFF")
            return True
        elif "E3632A" in self.instrument_ID:
            self.connection.write("OUTPut OFF")
            return True
        elif "E3649A" in self.instrument_ID:
            self.connection.write("OUTPut OFF")    
            return True
        elif "E36313A" in self.instrument_ID:
            self.connection.write("OUTPut OFF")  
            return True
        elif "E36234A" in self.instrument_ID:
            self.connection.write("OUTPut OFF")  
            return True
        else:
            print(f"Device {self.instrument_ID} not in library")
        
        return False

    @exception_handler    
    def select_output1(self) -> bool:
        '''
        Selects Output 1
        '''
        if "E3631A" in self.instrument_ID:
            self.connection.write("INSTrument:NSELect 1")   
            return True
        elif "E3632A" in self.instrument_ID:
            print(f"Device {self.instrument_ID} does not use {inspect.currentframe().f_code.co_name}")
            return False 
        elif "E3649A" in self.instrument_ID:
            self.connection.write("INSTrument:SELect OUTPut1")   
            return True
        elif "E36313A" in self.instrument_ID:
            self.connection.write("INSTrument:NSELect 1")
            return True
        elif "E36234A" in self.instrument_ID:
            self.connection.write("INSTrument:NSELect 1")
            return True            
        else:
            print(f"Device {self.instrument_ID} not in library")
        
        return False   

    @exception_handler    
    def select_output2(self) -> bool:
        '''
        Selects Output 2
        '''
        if "E3631A" in self.instrument_ID:
            self.connection.write("INSTrument:NSELect 2")   
            return True
        elif "E3632A" in self.instrument_ID:
            print(f"Device {self.instrument_ID} does not use {inspect.currentframe().f_code.co_name}")
            return False 
        elif "E3649A" in self.instrument_ID:
            self.connection.write("INSTrument:SELect OUTPut2")   
            return True
        elif "E36313A" in self.instrument_ID:
            self.connection.write("INSTrument:NSELect 2")
            return True
        elif "E36234A" in self.instrument_ID:
            self.connection.write("INSTrument:NSELect 2")
            return True            
        else:
            print(f"Device {self.instrument_ID} not in library")
        
        return False       

    @exception_handler    
    def select_output3(self) -> bool:
        '''
        Selects Output 3
        '''
        if "E3631A" in self.instrument_ID:
            self.connection.write("INSTrument:NSELect 3")   
            return True
        elif "E3632A" in self.instrument_ID:
            print(f"Device {self.instrument_ID} does not use {inspect.currentframe().f_code.co_name}")
            return False 
        elif "E3649A" in self.instrument_ID:
            self.connection.write("INSTrument:SELect OUTPut3")   
            return True
        elif "E36313A" in self.instrument_ID:
            self.connection.write("INSTrument:NSELect 3")
            return True
        elif "E36234A" in self.instrument_ID:
            self.connection.write("INSTrument:NSELect 3")
            return True            
        else:
            print(f"Device {self.instrument_ID} not in library")
        
        return False     

    @exception_handler    
    def set_voltage(self, voltage: float, current = "MAX") -> bool:
        '''
        Sets a voltage on the power supply
        '''
        try:
            if "E3631A" in self.instrument_ID: 
                self.connection.write(f"VOLT {voltage}")
                self.connection.write(f"CURR {current}")
            elif "E3632A" in self.instrument_ID:
                self.connection.write(f"APPLy {voltage},{current}")
            elif "E3649A" in self.instrument_ID:
                self.connection.write(f"APPLy {voltage},{current}")
            elif "E36313A" in self.instrument_ID:
                self.connection.write(f"VOLT {voltage}")
                self.connection.write(f"CURR {current}")            
            elif "E36234A" in self.instrument_ID:
                self.connection.write(f"VOLT {voltage}")
                self.connection.write(f"CURR {current}")  
            else:
                print(f"Device {self.instrument_ID} not in library")
        
            return True
        except:
            return False
    
    @exception_handler    
    def set_range(self, voltage) -> bool:
        '''
        Sets the voltage range on the power supply
        '''
        if "E3631A" in self.instrument_ID:
            print(f"Device {self.instrument_ID} does not use {inspect.currentframe().f_code.co_name}")

        elif "E3632A" in self.instrument_ID:

            if type(voltage) is str:
                print(f"E3632A only accepts int/float in {inspect.currentframe().f_code.co_name}")
                return False

            self.connection.write(f"VOLTage:RANGe P{voltage}V")

        elif "E3649A" in self.instrument_ID:
            
            if type(voltage) is not str:
                print(f"E3649A cant take int/float in {inspect.currentframe().f_code.co_name}")
                return False                

            self.connection.write(f"VOLTage:RANGe {voltage}")
        
        else:
            print(f"Device {self.instrument_ID} not in library")
        
    

    @exception_handler            
    def get_voltage_range(self):
        '''
        Gets the current voltage range
        '''
        retval = sys.maxsize

        if "E3631A" in self.instrument_ID:
            print(f"Device {self.instrument_ID} does not use {inspect.currentframe().f_code.co_name}")
        elif "E3632A" in self.instrument_ID:
            retval = self.connection.query("VOLTage:RANGe?")
        elif "E3649A" in self.instrument_ID:
            retval = self.connection.query("VOLTage:RANGe?")
        else:
            print(f"Device {self.instrument_ID} not in library")
        
        return retval


    @exception_handler    
    def measure_voltage(self):
        '''
        Measures the voltage
        '''

        retval = sys.maxsize

        if "E3631A" in self.instrument_ID:
            retval = self.connection.query("MEASure:VOLTage:DC?")
        elif "E3632A" in self.instrument_ID:
            retval = self.connection.query("MEASure:VOLTage:DC?")
        elif "E3649A" in self.instrument_ID:
            retval = self.connection.query("MEASure:VOLTage:DC?")
        else:
            print(f"Device {self.instrument_ID} not in library")
        
        return float(retval)


    @exception_handler    
    def measure_current(self):
        '''
        Measures the current
        '''

        retval = sys.maxsize

        if "E3631A" in self.instrument_ID:
            retval = self.connection.query("MEASure:CURRent:DC?")
        elif "E3632A" in self.instrument_ID:
            retval = self.connection.query("MEASure:CURRent:DC?")
        elif "E3649A" in self.instrument_ID:
            retval = self.connection.query("MEASure:CURRent:DC?")
        else:
            print(f"Device {self.instrument_ID} not in library")
        
        return float(retval)


    @exception_handler    
    def check_for_errors(self) -> bool:
        '''
        Pull an error from the error buffer
        '''
        print(self.connection.query("SYSTem:ERROR?"))

    @exception_handler    
    def reset(self):
        self.connection.write("*RST")
        return True
        
    @exception_handler    
    def clear(self):
        self.connection.write("*CLS")
        return True

    @exception_handler    
    def write(self, message : str) -> str:
        self.connection.write(message)

    @exception_handler    
    def query(self, message) -> str:
        return self.connection.query(message)

    @exception_handler    
    def query_ascii_values(self, message) -> list:
        return self.connection.query_ascii_values(message)