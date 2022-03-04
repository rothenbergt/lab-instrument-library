"""  ____
    / __ \___  ____  ___  _________ ______
   / /_/ / _ \/ __ \/ _ \/ ___/ __ `/ ___/
  / _, _/  __/ / / /  __(__  ) /_/ (__  )
 /_/ |_|\___/_/ /_/\___/____/\__,_/____/
 ----------------------------------------
Python library containing general functions to control lab supplies.

  Typical usage example:

  supply = Supply()
  supply_voltage = foo.set_voltage(voltage = 1)

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
    """Summary of class here.

    Longer class information....
    Longer class information....

    Attributes:
        likes_spam: A boolean indicating if we like SPAM or not.
        eggs: An integer count of the eggs we have laid.
    """

    supplyDictionary = {
        "1": "E3631A",
        "2": "E3632A",
        "3": "E3649A",
    }
    
    def __init__(self, instrument_address = "GPIB0::20::INSTR", nickname = None, identify = True):
        """Inits SampleClass with blah."""
        self.instrument_address = instrument_address
        self.rm = pyvisa.ResourceManager()
        self.connection = None
        self.instrumentID = None
        self.nickname = nickname
        self.make_connection(instrument_address, identify)    

    # Make the GPIB connection & set up the instrument
    def make_connection(self, instrument_address, identify):
        '''
        Identifies the instrument
        '''
        """Gets the selected function.

        Args:
        minimum: The selected channel

        Returns:
        The current selected function.

        Raises:
        Except: If the query fails.
        """
        # Make the connection
        try:
            # Make the connection and store it
            self.connection = self.rm.open_resource(instrument_address)
            
            # Increase the timeout
            # self.connection.timeout = 5000          
            
            # Display that the connection has been made
            if identify == True:              
                self.identify()
                print(f"Successfully established {self.instrument_address} connection with {self.instrumentID}")
            else:
                print(f"Successfully established {self.instrument_address} connection with {self.nickname}")
        
        except:
            print(f"Failed to establish {self.instrument_address} connection.")
            

    def identify(self):
        '''
        Identifies the instrument
        '''
        """Gets the selected function.

        Args:
        minimum: The selected channel

        Returns:
        The current selected function.

        Raises:
        Except: If the query fails.
        """
        try:
            self.instrumentID = self.connection.query("*IDN?")[:-1]
        except:
            print("Unit could not by identified using *IDN? command")


    
    def enable_output(self) -> bool:
        """Enables the output of the power supply

        Args:
        minimum: The selected channel

        Returns:
        The current selected function.

        Raises:
        Except: If the query fails.
        """
        try:
            if "E3631A" in self.instrumentID:
                self.connection.write("OUTPut ON")
            elif "E3632A" in self.instrumentID:
                self.connection.write("OUTPut ON")
            elif "E3649A" in self.instrumentID:
                self.connection.write("OUTPut ON")     
            elif "E36313A" in self.instrumentID:
                self.connection.write("OUTPut ON")     
            elif "E36234A" in self.instrumentID:
                self.connection.write("OUTPut ON")     
            else:
                print(f"Device {self.instrumentID} not in library")
        
            return True
        except:
            return False
    
    def disable_output(self) -> bool:
        """Disables the output of the power supply

        Args:
        minimum: The selected channel

        Returns:
        The current selected function.

        Raises:
        Except: If the query fails.
        """
        try:
            if "E3631A" in self.instrumentID:
                self.connection.write("OUTPut OFF")
            elif "E3632A" in self.instrumentID:
                self.connection.write("OUTPut OFF")
            elif "E3649A" in self.instrumentID:
                self.connection.write("OUTPut OFF")     
            elif "E36313A" in self.instrumentID:
                self.connection.write("OUTPut OFF")     
            elif "E36234A" in self.instrumentID:
                self.connection.write("OUTPut OFF")  
            else:
                print(f"Device {self.instrumentID} not in library")
        
            return True
        except:
            return False


    def select_output1(self) -> bool:
        '''
        Selects Output 1
        '''
        try:
            if "E3631A" in self.instrumentID:
                self.connection.write("INSTrument:NSELect 1")     
            elif "E3632A" in self.instrumentID:
                print(f"Device {self.instrumentID} does not use {inspect.currentframe().f_code.co_name}")
                return False 
            elif "E3649A" in self.instrumentID:
                self.connection.write("INSTrument:SELect OUTPut1")     
            elif "E36313A" in self.instrumentID:
                self.connection.write("INSTrument:NSELect 1")
            elif "E36234A" in self.instrumentID:
                self.connection.write("INSTrument:NSELect 1")
            else:
                print(f"Device {self.instrumentID} not in library")
            return True
        except:
            return False   

    def select_output2(self) -> bool:
        '''
        Selects Output 2
        '''
        try:
            if "E3631A" in self.instrumentID:
                self.connection.write("INSTrument:NSELect 2")     
            elif "E3632A" in self.instrumentID:
                print(f"Device {self.instrumentID} does not use {inspect.currentframe().f_code.co_name}")
                return False 
            elif "E3649A" in self.instrumentID:
                self.connection.write("INSTrument:SELect OUTPut2")     
            elif "E36313A" in self.instrumentID:
                self.connection.write("INSTrument:NSELect 2")
            elif "E36234A" in self.instrumentID:
                self.connection.write("INSTrument:NSELect 2")
            else:
                print(f"Device {self.instrumentID} not in library")
            return True
        except:
            return False      

    def select_output3(self) -> bool:
        '''
        Selects Output 3
        '''
        try:
            if "E3631A" in self.instrumentID:
                self.connection.write("INSTrument:NSELect 3")     
            elif "E36313A" in self.instrumentID:
                self.connection.write("INSTrument:NSELect 3")
            elif "E36234A" in self.instrumentID:
                self.connection.write("INSTrument:NSELect 3")
            elif "E3632A" in self.instrumentID:
                print(f"Device {self.instrumentID} does not use {inspect.currentframe().f_code.co_name}")
                return False 
            elif "E3649A" in self.instrumentID:
                print(f"Device {self.instrumentID} does not use {inspect.currentframe().f_code.co_name}")
                return False
            else:
                print(f"Device {self.instrumentID} not in library")
            return True
        except:
            return False      

    def set_voltage(self, voltage: float, current = "MAX") -> bool:
        '''
        Sets a voltage on the power supply
        '''
        try:
            if "E3631A" in self.instrumentID: 
                self.connection.write(f"VOLT {voltage}")
                self.connection.write(f"CURR {current}")
            elif "E3632A" in self.instrumentID:
                self.connection.write(f"APPLy {voltage},{current}")
            elif "E3649A" in self.instrumentID:
                self.connection.write(f"APPLy {voltage},{current}")
            elif "E36313A" in self.instrumentID:
                self.connection.write(f"VOLT {voltage}")
                self.connection.write(f"CURR {current}")            
            elif "E36234A" in self.instrumentID:
                self.connection.write(f"VOLT {voltage}")
                self.connection.write(f"CURR {current}")  
            else:
                print(f"Device {self.instrumentID} not in library")
        
            return True
        except:
            return False
    

    def set_range(self, voltage) -> bool:
        '''
        Sets the voltage range on the power supply
        '''
        try:
            if "E3631A" in self.instrumentID:
                print(f"Device {self.instrumentID} does not use {inspect.currentframe().f_code.co_name}")


            elif "E3632A" in self.instrumentID:

                if type(voltage) is str:
                    print(f"E3632A only accepts int/float in {inspect.currentframe().f_code.co_name}")
                    return False

                self.connection.write(f"VOLTage:RANGe P{voltage}V")

            elif "E3649A" in self.instrumentID:
                
                if type(voltage) is not str:
                    print(f"E3649A cant take int/float in {inspect.currentframe().f_code.co_name}")
                    return False                

                self.connection.write(f"VOLTage:RANGe {voltage}")
            
            else:
                print(f"Device {self.instrumentID} not in library")
        
            return True
        except:
            return False      

        
    def get_voltage_range(self):
        '''
        Gets the current voltage range
        '''

        retval = sys.maxsize

        try:
            if "E3631A" in self.instrumentID:
                print(f"Device {self.instrumentID} does not use {inspect.currentframe().f_code.co_name}")
            elif "E3632A" in self.instrumentID:
                retval = self.connection.query("VOLTage:RANGe?")
            elif "E3649A" in self.instrumentID:
                retval = self.connection.query("VOLTage:RANGe?")
            else:
                print(f"Device {self.instrumentID} not in library")
            
            return retval
        except:
            return retval

    def measure_voltage(self):
        '''
        Measures the voltage
        '''

        retval = sys.maxsize

        try:
            if "E3631A" in self.instrumentID:
                retval = self.connection.query("MEASure:VOLTage:DC?")
            elif "E3632A" in self.instrumentID:
                retval = self.connection.query("MEASure:VOLTage:DC?")
            elif "E3649A" in self.instrumentID:
                retval = self.connection.query("MEASure:VOLTage:DC?")
            else:
                print(f"Device {self.instrumentID} not in library")
            
            return float(retval)
        except:
            return retval

    def measure_current(self):
        '''
        Measures the current
        '''

        retval = sys.maxsize

        try:
            if "E3631A" in self.instrumentID:
                retval = self.connection.query("MEASure:CURRent:DC?")
            elif "E3632A" in self.instrumentID:
                retval = self.connection.query("MEASure:CURRent:DC?")
            elif "E3649A" in self.instrumentID:
                retval = self.connection.query("MEASure:CURRent:DC?")
            else:
                print(f"Device {self.instrumentID} not in library")
            
            return float(retval)
        except:
            return retval


    def check_for_errors(self) -> bool:
        '''
        Pull an error from the error buffer
        '''
        print(self.connection.query("SYSTem:ERROR?"))

    def reset(self):
        try:
            self.connection.write("*RST")
        except:
            print("Unit could not by be reset using *RST command")

    def clear(self):
        try:
            self.connection.write("*CLS")
        except:
            print("Unit could not by be cleared using *CLS command")

    def write(self, message):
        self.connection.write(message)

    def query(self, message):
        return self.connection.query(message)

# E3632A = Supply("GPIB0::2::INSTR")
# E3649A = Supply("GPIB0::5::INSTR")
# E3631A = Supply("GPIB::6::INSTR")
E36313A = Supply("USB0::0x2A8D::0x1202::MY61001838::INSTR")
E36234A = Supply("USB0::0x2A8D::0x3402::MY61001286::INSTR")



E36313A.select_output1()
E36313A.enable_output()
E36313A.set_voltage(6, 1)


E36313A.select_output2()
E36313A.enable_output()
E36313A.set_voltage(25)

E36313A.select_output3()
E36313A.enable_output()
E36313A.set_voltage(25)


E36234A.select_output1()
E36234A.enable_output()
E36234A.set_voltage(2, 1)

E36234A.select_output2()
E36234A.enable_output()
E36234A.set_voltage(2, 1)
