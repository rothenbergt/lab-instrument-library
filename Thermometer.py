from LibraryTemplate import LibraryTemplate
import numpy as np
import time
import sys

class Thermometer(LibraryTemplate):
    
    def get_temperature(self):
        retval = sys.maxsize
        try:
            return float(self.connection.query("FETCH?")[:-1])
        except Exception as ex:
            print(f"Could not read temperature from {self.instrumentID} at {self.instrument}")
        return retval



