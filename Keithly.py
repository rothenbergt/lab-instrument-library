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

####

# #     ____
# #    / __ \___  ____  ___  _________ ______
# #   / /_/ / _ \/ __ \/ _ \/ ___/ __ `/ ___/
# #  / _, _/  __/ / / /  __(__  ) /_/ (__  )
# # /_/ |_|\___/_/ /_/\___/____/\__,_/____/
# # ----------------------------------------
# #              Multimeter Library
# #               Keithly 2000

# import pyvisa
# import sys
# import time
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt

# # One of the quirks of the Agilent (HP) 34401A is that when you are remotly connected
# # the device doesn't gather more data unless you send an INITIATE command. This takes
# # much longer than if the device were operating without this constraint.

# # Class which allows for easier access to the GPIB TEK Oscilloscope
# class Keithly:

#     # When initializing the object, make the connection
#     def __init__(self, givenInstrument = ""):
#         self.instrument = givenInstrument
#         self.rm = pyvisa.ResourceManager()
#         self.connected = False
#         self.connection = ""
#         self.instrumentID = ""
#         self.Agilent = False
#         self.Keithly = False
#         self.Tektronix = False
#         self.debug = False
#         self.makeConnection(givenInstrument)

#     def close_connection(self):
#         self.connection.close()

#     # Make the GPIB connection & set up the instrument
#     def makeConnection(self, givenInstrument):
#         try:
#             # Make the connection
#             self.connection = self.rm.open_resource(givenInstrument)
#             # print("Connection Made")
#             self.connected = True
#             self.connection.timeout = 250000                     # Increase Timeout
#             self.instrumentID = self.connection.query("*IDN?")[:-1]
#             print("Successfully established " + self.instrument + " connection with", self.instrumentID)
            
#             if ("34401A" in self.instrumentID):
#                 print("We will be using Agilent 33401A instruction set")
#                 self.Agilent = True
#             elif ("2000" in self.instrumentID):
#                 print("We will be using Keithly 2000 instruction set")
#                 self.Keithly = True
            
#         except:
#             print("Failed to make the connection with ", self.instrument)
#             self.connected = False
#             quit()

#     def write(self, message):
#         self.connection.write(message)

#     def query(self, message):
#         return self.connection.query(message)

#     def setRange(self, function = "VOLTage:AC", upper = "1"):
#         self.connection.write(f"{function}:RANGE:UPPER {upper}")
        
#     def autoOff(self, function = "VOLTage:AC"):
#         self.connection.write(f"VOLTAGE:AC:RANGE:AUTO 0")
    
#     def autoOn(self, function = "VOLTage:AC"):
#         self.connection.write(f"VOLTAGE:AC:RANGE:AUTO 1")
    
#     # Turn on the average feature of the multimeter and set the variables
#     def setAverage(self, function = "VOLTage:AC", control = "MOVing", count = 100):
        
#         if (self.debug): print("Turning on averaging for " + self.instrumentID + " at " + self.instrument)
        
#         if self.Agilent:
#             self.connection.write("CALC:FUNC AVER")          # Turn on Averaging
#             self.connection.write("CALC:STATe ON")           # Turn on Math State

#             # The beeper is turned off as for each new MIN / MAX value found, the device will beep. 
#             self.connection.write("SYSTem:BEEPer:STATe OFF") 

#         elif self.Keithly:
#             self.connection.write(function + ":AVERage:TCONtrol " + control)
#             self.connection.write(function + ":AVERage:COUNt " + str(count))
#             self.connection.write(function + ":AVERage:STATe ON")

#     def turnOffAveraging(self, function = "VOLTage:AC"):
        
#         if (self.debug): print("Turning off averaging for " + self.instrumentID + " at " + self.instrument)
        
#         if self.Keithly:
#             self.connection.write(function + ":AVERage:STATe OFF")
            
#         elif self.Agilent:
#             self.connection.write("CALC:STATe OFF")          
            

#     def getAverage(self):
        
#         if self.Agilent:
#             retval = sys.maxsize
#             # Try to get the value from the multimeter
#             try:
#                 print("There have been " + str(self.connection.query_ascii_values("CALCulate:AVERage:COUNt?")[0]) + " readings")
                
#                 retval = self.connection.query("CALC:AVER:AVER?")
#             except ValueError as ex:
#                 print("Could not convert returned value from meter: " + self.instrumentID + " at " + self.instrument)
#             except Exception as ex:
#                 print("Could not fetch from meter: " + self.instrumentID + " at " + self.instrument)
        
#         return retval

#     # Clear all Event Registers
#     def clearBuffer(self):
#         self.connection.write("*CLS")

#     # Power up to the default conditions
#     def reset(self):
#         self.connection.write("*RST")

#     # Set the line integration rate
#     def setNPLCycles(self, function, n):
#         self.connection.write(function + ":NPLCycles " + n)

#     def getAverageCount(self, readings, interval = 0):
#         self.connection.write(":status:measurement:enable 512; *sre 1")
#         self.connection.write("INITiate:CONTinuous OFF")
#         self.connection.write(f":SAMPle:COUNt {readings}")
#         self.connection.write("trigger:source bus")
#         # self.connection.write(f"trigger:delay {interval / 1000}")
#         self.connection.write(f"trace:points {readings}")
#         self.connection.write("trace:feed sense1; feed:control next")
        
#         self.connection.write("initiate")
#         self.connection.assert_trigger()
#         self.connection.query("*OPC?")

#         voltages = self.connection.query_ascii_values("trace:data?")
#         print(voltages)
#         print("Average voltage: ", sum(voltages) / len(voltages))
#         return voltages

#     def fetchVoltage(self):
        
#         # if (self.debug): print("Fetching voltage from " + self.instrumentID + " at " + self.instrument)
        
#         # If there is an error, return max int
#         retval = sys.maxsize 
        
#         # If we are using the Agilent 34401A instruction set, we will want to
#         # first send the initiate command to transfer the readings to the internal memory
#         if (self.Agilent):
#             self.connection.write("INITiate")

#         # Try to get the value from the multimeter
#         try:
#             retval = float(self.connection.query("FETCh?"))
#         except ValueError as ex:
#             print("Could not convert returned value from meter: " + self.instrumentID + " at " + self.instrument)
#         except Exception as ex:
#             print("Could not fetch from meter: " + self.instrumentID + " at " + self.instrument)
        
#         # Return either the error, or the value from the multimeter
#         return retval

#     def readVoltage(self):
#         retval = sys.maxsize
#         try:
#             retval = float(self.connection.query("READ?"))
#         except ValueError as ex:
#             print("Could not convert returned value from meter: " + self.instrumentID + " at " + self.instrument)
#         except Exception as ex:
#             print("Could not fetch from meter: " + self.instrumentID + " at " + self.instrument)
#         return retval

#     def measure(self, function = "VOLTage:DC"):
#         retval = sys.maxsize
#         try:
#             retval = float(self.connection.query(":MEASure:" + function + "?"))
#         except ValueError as ex:
#             print("Could not convert returned value from meter: " + self.instrumentID + " at " + self.instrument)
#         except TimeoutError as ex:
#             print("Timeout error from meter: " + self.instrumentID + " at " + self.instrument)
#         except Exception as ex:
#             print("Could not fetch from meter: " + self.instrumentID + " at " + self.instrument)
#         return retval

#     def getErrors(self):
        
#         if self.Agilent:
#             print(multi.query("SYSTem:ERRor?"))

