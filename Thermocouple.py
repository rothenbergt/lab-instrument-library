from LibraryTemplate import LibraryTemplate
import numpy as np
import time
import sys

class Thermocouple(LibraryTemplate):
    
    def get_temperature(self, channel = 1):
        retval = sys.maxsize
        try:
            retval = float(self.connection.query(f"MEAS?{channel}"))
        except Exception as ex:
            print(f"Could not read temperature")
            try:
                retval = float(self.connection.query(f"MEAS?{channel}"))
            except Exception as ex:
                print(f"Could not read temperature")
        return retval
    
    # def get_temperature(self):
    #     return self.get_temperature()
    
    def get_temperature_2(self):
        return self.get_temperature(channel = 2)

    
    def setType(self, ch, mnem = "T"):
        self.connection.write(f"TTYP {ch},{mnem}")
        
    