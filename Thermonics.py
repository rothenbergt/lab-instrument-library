"""  ____
    / __ \___  ____  ___  _________ ______
   / /_/ / _ \/ __ \/ _ \/ ___/ __ `/ ___/
  / _, _/  __/ / / /  __(__  ) /_/ (__  )
 /_/ |_|\___/_/ /_/\___/____/\__,_/____/
 ----------------------------------------
A one line summary of the module or program, terminated by a period.

Leave one blank line.  The rest of this docstring should contain an
overall description of the module or program.  Optionally, it may also
contain a brief description of exported classes and functions and/or usage
examples.

  Typical usage example:

  foo = ClassFoo()
  bar = foo.FunctionBar()
"""

import pyvisa
import sys

class Thermonics:
    """Summary of class here.

    Longer class information....
    Longer class information....

    Attributes:
        likes_spam: A boolean indicating if we like SPAM or not.
        eggs: An integer count of the eggs we have laid.
    """

    instrumentDictionary = {
        "1": "Oven",
        "2": "Thermonics T-2500SE",
        "3": "Thermonics T-2420",
        "4": "X-Stream 4300"
    }

    fullIndustrialTemperatureRange = [25, 0, -40, 125, 85]
    industrialTemperatureRange = [25, 0, -40, 105, 55]


    def __init__(self, instrumentAddress = "GPIB0::21::INSTR"):
        '''
        Constructs all the necessary attributes for the Thermonics object.
        '''
        
        self.instrument = instrumentAddress
        self.rm = pyvisa.ResourceManager()
        self.connection = None
        self.instrument_name = None
        self.instrumentID = None
        self.make_connection(instrumentAddress)

    # TODO, add ability to choose temperature system from __init__
    def make_connection(self, instrumentAddress : str) -> None:
        '''
        Attempts to establish a connection with a given instrument
        '''
                  
        try:
            self.connection = self.rm.open_resource(instrumentAddress)
            self.connection.timeout = 2500                  

            # Determine which instrument we are attempting to connect to. This method is used instead of
            # first identifying the instrument, then using its name to pick an instruction set
            # as not all instruments have the ability to use IEEE-488.2 commands such as *IDN?. 
            # The Thermonics T-2420 and T-2500 use IEEE-488.1 commands which are more simple. 
            while True:
                print("Please select your temperature forcing system:")
                
                for key,value in self.instrumentDictionary.items():
                    print(key, value)
                
                user_choice = input("Chocie: ")
                                    
                if user_choice in self.instrumentDictionary:
                    self.instrument_name = str(self.instrumentDictionary[user_choice])
                    break
                else:
                    print("Not a valid choice! Try again...")
        
            # Finish setup for specific instruments. Instrument names are used throughout
            # the class instead of the dictionary key, value as it is easier to read.
            if ("Oven" in self.instrument_name or "Thermonics" in self.instrument_name):
                # The Thermonics T-2420 only worked with the below settings. 
                # It is applied to the oven and T-2500 as well.
                self.connection.write_termination = '\r\n'
                self.connection.read_termination = '\r\n'
                self.connection.baud_rate = 9600
                print("Successfully established " + self.instrument + " connection")    
            else:
                # The only instrument which uses IEEE-488.2 is the X-Stream 4300.
                # IEEE-488.2 allows the use of the newer commands such as *IDN?
                self.instrumentID = self.connection.query("*IDN?")[:-1]           
                print("Successfully established " + self.instrument + " connection with", self.instrumentID)
            
        except:
            print("Failed to make the connection with ", self.instrument)
            self.connected = False


    def set_temperature(self, temp : float) -> None: 
        '''
        Sets the temperature of a given temperature forcing system
        '''
        
        if "Oven" in self.instrument_name:
            self.connection.write(f"{temp}C") 
            
        elif "Thermonics" in self.instrument_name:
            print(f"Setting Thermonics Temperature to: {temp}")
            
            if (float(temp) <= 25):
                self.set_cold_temp(temp)
                self.select_cold()
            else:
                self.set_hot_temp(temp)
                self.select_hot()
        elif "X-Stream" in self.instrument_name:
            print("A set_temperature method has not been written for the X-Stream 4300")


    def select_cold(self) -> None:
        '''
        Selects cold air on the temperature forcing system
        '''
        
        if "Thermonics" in self.instrument_name:
            self.connection.write("AC")
        elif "X-Stream" in self.instrument_name:
            print("A selectCold method has not been written for the X-Stream 4300")
        elif "Oven" in self.instrument_name:
            print("Whoops! You cannot select cold on the Oven through code.")

        
    def select_hot(self) -> None:
        '''
        Selects hot air on the temperature forcing system
        '''
        
        if "Thermonics" in self.instrument_name:
            self.connection.write("AH")
        elif "X-Stream" in self.instrument_name:
            print("A selectHot method has not been written for the X-Stream 4300")
        elif "Oven" in self.instrument_name:
            print("Whoops! You cannot select hot on the Oven through code.")
        
    
    def select_ambient(self) -> None:
        '''
        Selects ambient air on the temperature forcing system
        '''
        
        if "Thermonics" in self.instrument_name:
            self.connection.write("AA")
        elif "X-Stream" in self.instrument_name:
            print("A selectAmbient method has not been written for the X-Stream 4300")
        elif "Oven" in self.instrument_name:
            print("Whoops! You cannot select ambient on the Oven through code.")   
        
    def select_ambient_forced(self) -> None:
        '''
        Selects ambient forced air on the temperature forcing system
        '''

        if "Thermonics" in self.instrument_name:
            self.connection.write("AF")
        elif "X-Stream" in self.instrument_name:
            print("A selectAmbientForced method has not been written for the X-Stream 4300")
        elif "Oven" in self.instrument_name:
            print("Whoops! You cannot select ambient forced on the Oven through code.")   
            
            
    def set_hot_temp(self, temp : float) -> None:
        '''
        Set the temperature of the hot air
        '''
        if "Thermonics" in self.instrument_name:
            self.connection.write(f"TH{temp}")
        elif "X-Stream" in self.instrument_name:
            print("A selectHotTemp method has not been written for the X-Stream 4300")
        elif "Oven" in self.instrument_name:
            self.connection.write(f"{temp}C") 


    def set_cold_temp(self, temp : float) -> None:
        '''
        Set the temperature of the cold air
        '''   
        if "Thermonics" in self.instrument_name:
            self.connection.write(f"TC{temp}")
        elif "X-Stream" in self.instrument_name:
            print("A selectColdTemp method has not been written for the X-Stream 4300")
        elif "Oven" in self.instrument_name:
            self.connection.write(f"{temp}C")  
        

    def turn_off_compressor(self) -> None:
        '''
        Turn off the compressor 
        '''   
        
        if "Thermonics" in self.instrument_name:
            self.connection.write(f"CP")
        elif "X-Stream" in self.instrument_name:
            print("A selectColdTemp method has not been written for the X-Stream 4300")
        elif "Oven" in self.instrument_name:
            print("The Oven has no compressor to turn off.")
        
    def turn_on_compressor(self) -> None:
        '''
        Turn on the compressor 
        '''   
        
        if "Thermonics" in self.instrument_name:
            self.connection.write(f"CS")
        elif "X-Stream" in self.instrument_name:
            print("A selectColdTemp method has not been written for the X-Stream 4300")
        elif "Oven" in self.instrument_name:
            print("The Oven has no compressor to turn off.")

    def get_temperature(self) -> float:
        '''
        Get the current temperature of the temperature forcing system
        '''    
        
        retval = sys.maxsize
        
        if "Oven" in self.instrument_name:
            retval = self.connection.query("T")
        elif "Thermonics" in self.instrument_name:
            retval = self.connection.query("RA")
        elif "X-Stream" in self.instrument_name:
            print("A getTemperature method has not been written for the X-Stream 4300")
            
        return float(retval)          

    def turn_off_air(self):
        '''
        Turn the forced air off
        '''    
        
        if "Thermonics" in self.instrument_name:
            self.connection.write(f"AA")
        elif "X-Stream" in self.instrument_name:
            print("A turnAirOff method has not been written for the X-Stream 4300")
        elif "Oven" in self.instrument_name:
            print("The Oven has no air to turn off.")   
        

    def write(self, message):
        '''
        General write method for unwritten functionality
        '''    
        self.connection.write(message)

    def query(self, message):
        '''
        General query method for unwritten functionality
        '''    
        return self.connection.query(message)
    
