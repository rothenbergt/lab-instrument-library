'''
    File name: LibraryTemplate.py
    Author: Tyler Rothenberg
    Date created: 4/28/2021
    Date last modified: 6/11/2021
    Python Version: 3.9
    
    The purpose of this template is to organize all common instruments
    commands into one template which new libraries may inherit from.
'''

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
        