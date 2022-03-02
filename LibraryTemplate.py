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

# definition of superclass "LibraryTemplate"
class LibraryTemplate(object):
      
    def __init__(self, instrument_address = "GPIB0::20::INSTR", nickname = None, identify = True):
        
        self.instrument_address = instrument_address
        self.rm = pyvisa.ResourceManager()
        self.connection = None
        self.instrumentID = None
        self.nickname = nickname
        self.make_connection(instrument_address, identify)     
  
    # Make the GPIB connection & set up the instrument
    def make_connection(self, instrument_address, identify):
        # Make the connection
        try:
            # Make the connection and store it
            self.connection = self.rm.open_resource(instrument_address)
            
            # Increase the timeout
            self.connection.timeout = 5000          
            
            # Display that the connection has been made
            if identify == True:              
                self.identify()
                print(f"Successfully established {self.instrument_address} connection with {self.instrumentID}")
            else:
                print(f"Successfully established {self.instrument_address} connection with {self.nickname}")
        
        except:
            print(f"Failed to establish {self.instrument_address} connection.")
            

    def close_connection(self):
        self.connection.close()

    def identify(self):
        try:
            self.instrumentID = self.connection.query("*IDN?")[:-1]
        except:
            print("Unit could not by identified using *IDN? command")
             
    def write(self, message):
        self.connection.write(message)
    
    def query(self, message):
        return self.connection.query(message)
    
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
        