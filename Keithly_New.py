#     ____
#    / __ \___  ____  ___  _________ ______
#   / /_/ / _ \/ __ \/ _ \/ ___/ __ `/ ___/
#  / _, _/  __/ / / /  __(__  ) /_/ (__  )
# /_/ |_|\___/_/ /_/\___/____/\__,_/____/
# ----------------------------------------
#              Multimeter Library
#               Keithly 2000

from LibraryTemplate import LibraryTemplate
import numpy as np
import time
import sys

# Note to self. I was playing around with error handling within the library.

class Keithly(LibraryTemplate):

    # Turn on the average feature of the multimeter and set the variables
    def set_average(self, function = "VOLTage:AC", control = "MOVing", count = 100):
        self.connection.write(function + ":AVERage:TCONtrol " + control)
        self.connection.write(function + ":AVERage:COUNt " + str(count))
        self.connection.write(function + ":AVERage:STATe ON")

    def turn_off_averaging(self, function = "VOLTage:AC"):        
        self.connection.write(function + ":AVERage:STATe OFF")
                  

    def get_average(self):
        try:
            print("There have been " + str(self.connection.query_ascii_values("CALCulate:AVERage:COUNt?")[0]) + " readings")
            retval = self.connection.query("CALC:AVER:AVER?")
        except ValueError as ex:
            print(f"Could not convert returned value from meter: {self.instrumentID} at {self.instrument}")
        except Exception as ex:
            print(f"Could not fetch from meter: {self.instrumentID} at {self.instrument}")
        return retval

    # Clear all Event Registers
    def clear_buffer(self):
        self.connection.write("*CLS")


    # Set the line integration rate
    def set_NPL_cycles(self, function, n):
        self.connection.write(f"{function}:NPLCycles {n}")

    def fetch_voltage(self):
        # If there is an error, return max int
        retval = sys.maxsize 
        
        # Try to get the value from the multimeter
        try:
            retval = float(self.connection.query("FETCh?"))
        except ValueError as ex:
            print(f"Could not convert returned value from meter: {self.instrumentID} at {self.instrument}")
        except Exception as ex:
            print(f"Could not fetch from meter: {self.instrumentID} at {self.instrument}")
        
        # Return either the error, or the value from the multimeter
        return retval

    def read_voltage(self):
        retval = sys.maxsize
        try:
            retval = float(self.connection.query("READ?"))
        except ValueError as ex:
            print(f"Could not convert returned value from meter: {self.instrumentID} at {self.instrument}")
        except Exception as ex:
            print(f"Could not fetch from meter: {self.instrumentID} at {self.instrument}")
        return retval

    def measure(self, function = "VOLTage:DC"):
        
        retval = sys.maxsize
        
        try:
            retval = float(self.connection.query(f"MEASure:{function}?"))
        except ValueError as ex:
            print(f"Could not convert returned value from meter: {self.instrumentID} at {self.instrument}")
        except TimeoutError as ex:
            print(f"Timeout error from meter: {self.instrumentID} at {self.instrument}")
        except Exception as ex:
            print(f"Could not fetch from meter: {self.instrumentID} at {self.instrument}")
        return retval


    # def load_errors(self):
    #     # Load errors into memory

    def get_error(self):
        try:
            # Get the error code from the multimeter
            error_code = int(multi.query("SYSTem:ERRor?")[:-1])
            # If the error code is 0, we have no errors
            
            # If the error code is anything other than 0, we have errors
            
            # Attempt to lookup the errors from the dictionary
            
        except ValueError as ex:
            print(f"Could not convert returned value from meter: {self.instrumentID} at {self.instrument}")        
        except Exception as ex:
            print(f"General Exception from meter: {self.instrumentID} at {self.instrument}")

