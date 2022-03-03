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

from LibraryTemplate import LibraryTemplate
import numpy as np
import time
import sys
import pyvisa


class Multimeter():

    supplyDictionary = {
        "1": "2000",
        "2": "2110",
        "3": "4050",
        "4": "34401A",
    }
    
    def __init__(self, instrument_address = "GPIB0::20::INSTR", nickname = None, identify = True):
        
        self.instrument_address = instrument_address
        self.rm = pyvisa.ResourceManager()
        self.connection = None
        self.instrumentID = None
        self.nickname = nickname
        if (not self.make_connection(instrument_address, identify)):
            sys.exit()

    # Make the GPIB connection & set up the instrument
    def make_connection(self, instrument_address, identify) -> bool:
        '''
        Identifies the instrument
        '''
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
                return True
            else:
                print(f"Successfully established {self.instrument_address} connection with {self.nickname}")
                return True
        
        except:
            print(f"Failed to establish {self.instrument_address} connection.")
            return False
            

    def identify(self):
        '''
        Identifies the instrument
        '''
        try:
            self.instrumentID = self.connection.query("*IDN?")[:-1]
        except:
            print("Unit could not by identified using *IDN? command")


    def initiate(self) -> bool:
        '''
        Change state of triggering system to wait for trigger state.
        '''
        retval = sys.maxsize 
        
        try:
            if "2000" in self.instrumentID:
                self.connection.write("INIT")
                return True

            elif "2110" in self.instrumentID:
                self.connection.write("INIT")
                return True

            elif "4050" in self.instrumentID:
                self.connection.write("INIT")
                return True

            elif "34401A":
                self.connection.write("INIT")
                return True
            else:
                print(f"Device {self.instrumentID} not in library")
        
        except ValueError as ex:
            # print(f"Could not convert returned value from meter: {self.instrumentID} at {self.instrument}")
            return retval
        except Exception as ex:
            # print(f"Could not fetch from meter: {self.instrumentID} at {self.instrument}")
            return retval

    def fetch_voltage(self) -> float:
        '''
        Sends the data in the instruments internal memory to the output buffer.
        '''
        retval = sys.maxsize 
        
        try:
            if "2000" in self.instrumentID:
                retval = float(self.connection.query("FETCh?"))
                return retval

            elif "2110" in self.instrumentID:
                retval = float(self.connection.query("FETCh?"))
                return retval

            elif "4050" in self.instrumentID:
                retval = float(self.connection.query("FETCh?"))
                return retval
            elif "34401A":
                retval = float(self.connection.query("FETCh?"))
                return retval
            else:
                print(f"Device {self.instrumentID} not in library")
                return retval
        
        except ValueError as ex:
            # print(f"Could not convert returned value from meter: {self.instrumentID} at {self.instrument}")
            return retval
        except Exception as ex:
            # print(f"Could not fetch from meter: {self.instrumentID} at {self.instrument}")
            return retval


        
        # Return either the error, or the value from the multimeter

    def read_voltage(self):
        retval = sys.maxsize
        try:
            retval = float(self.connection.query("READ?"))
        except ValueError as ex:
            print(f"Could not convert returned value from meter: {self.instrumentID} at {self.instrument}")
        except Exception as ex:
            print(f"Could not fetch from meter: {self.instrumentID} at {self.instrument}")
        return retval


    def measure_voltage(self, function = "VOLTage:DC"):
        
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

    def get_function(self):

        try:
            current_function = self.connection.query("FUNCtion?")
            return current_function
        except:
            print(f"General Exception from meter: {self.instrumentID} at {self.instrument}")

    def set_function(self, function: str):
        '''
        VOLTage:AC"
        "VOLTage[:DC]"
        "VOLTage[:DC]:RATio"
        "CURRent:AC"
        "CURRent[:DC]"
        "FREQuency[:VOLT]"
        "FREQuency:CURR"
        "FRESistance"
        "PERiod[:VOLT]"
        "PERiod:CURR"
        "RESistance"
        "DIODe"
        "TCOuple"
        "TEMPerature"
        "CONTinuity"
        Note: DIODe and
        '''
        self.connection.write(f":conf:{function}")

        return self.get_function()

    def get_voltage_range():
        get_range("VOLTage:DC")

    def get_range(self, function):
        '''
        Specify signal level in volts 
        '''
        retval = sys.maxsize 
        
        try:
            if "2000" in self.instrumentID:

                # Path to configure measurement range:
                # Select range (0 to 1010).
                retval = self.connection.query(f"{function}:RANGe?")
                return float(retval)

            elif "2110" in self.instrumentID:
                retval = self.connection.query(f"{function}:RANGe?")
                return float(retval)

            elif "4050" in self.instrumentID:
                retval = self.connection.query(f"{function}:RANGe?")
                return float(retval)
            elif "34401A":
                retval = self.connection.query(f"{function}:RANGe?")
                return float(retval)
            else:
                print(f"Device {self.instrumentID} not in library")
                return retval
        
        except ValueError as ex:
            # print(f"Could not convert returned value from meter: {self.instrumentID} at {self.instrument}")
            return retval
        except Exception as ex:
            # print(f"Could not fetch from meter: {self.instrumentID} at {self.instrument}")
            return retval      

    def set_voltage_range(self, voltage_range):
        self.set_range(voltage_range, "VOLTage:DC")


    def set_range(self, voltage_range: float, function):
        '''
        Specify signal level in volts 
        '''
        retval = sys.maxsize 
        
        try:
            if "2000" in self.instrumentID:

                # Path to configure measurement range:
                # Select range (0 to 1010).
                self.connection.write(f"{function}:RANGe {voltage_range}")

            elif "2110" in self.instrumentID:
                self.connection.write(f"{function}:RANGe {voltage_range}")

            elif "4050" in self.instrumentID:
                self.connection.write(f"{function}:RANGe {voltage_range}")

            elif "34401A":
                self.connection.write(f"{function}:RANGe {voltage_range}")

            else:
                print(f"Device {self.instrumentID} not in library")
                return retval
        
        except ValueError as ex:
            # print(f"Could not convert returned value from meter: {self.instrumentID} at {self.instrument}")
            return retval
        except Exception as ex:
            # print(f"Could not fetch from meter: {self.instrumentID} at {self.instrument}")
            return retval


    def get_error(self):
        try:
            # Get the error code from the multimeter
            error_string = self.connection.query("SYSTem:ERRor?").strip("\n")
            # If the error code is 0, we have no errors
            # If the error code is anything other than 0, we have errors
            
            # Attempt to lookup the errors from the dictionary
            return error_string
            
        except ValueError as ex:
            print(f"Could not convert returned value from meter: {self.instrumentID} at {self.instrument}")        
        except Exception as ex:
            print(f"General Exception from meter: {self.instrumentID} at {self.instrument}")


# TODO :init:cont off for 2000

mult_2000 = Multimeter("GPIB0::3::INSTR")
mult_2110 = Multimeter("USB0::0x05E6::0x2110::8015791::INSTR")
mult_4050 = Multimeter("GPIB0::2::INSTR")
mult_34401A = Multimeter("GPIB0::1::INSTR")

# mult_2000.initiate()
# mult_2110.initiate()
# mult_4050.initiate()
# mult_34401A.initiate()

# print(mult_2000.fetch_voltage())
# print(mult_2110.fetch_voltage())
# print(mult_4050.fetch_voltage())
# print(mult_34401A.fetch_voltage())

print(mult_2000.set_function('volt:dc'))
print(mult_2110.set_function('volt:dc'))
print(mult_4050.set_function('volt:dc'))
print(mult_34401A.set_function('volt:dc'))

print(mult_2000.set_voltage_range(2))
print(mult_2110.set_voltage_range(2))
print(mult_4050.set_voltage_range(2))
print(mult_34401A.set_voltage_range(2))

print(mult_2000.get_range("VOLTage:DC"))
print(mult_2110.get_range("VOLTage:DC"))
print(mult_4050.get_range("VOLTage:DC"))
print(mult_34401A.get_range("VOLTage:DC"))


print(mult_2000.measure_voltage())
print(mult_2110.measure_voltage())
print(mult_4050.measure_voltage())
print(mult_34401A.measure_voltage())


print(mult_2000.get_error())
print(mult_2110.get_error())
print(mult_4050.get_error())
print(mult_34401A.get_error())

# Turn on the average feature of the multimeter and set the variables
    # def set_average(self, function = "VOLTage:AC", control = "MOVing", count = 100):
    #     self.connection.write(function + ":AVERage:TCONtrol " + control)
    #     self.connection.write(function + ":AVERage:COUNt " + str(count))
    #     self.connection.write(function + ":AVERage:STATe ON")

    # def turn_off_averaging(self, function = "VOLTage:AC"):        
    #     self.connection.write(function + ":AVERage:STATe OFF")
                  

    # def get_average(self):
    #     try:
    #         print("There have been " + str(self.connection.query_ascii_values("CALCulate:AVERage:COUNt?")[0]) + " readings")
    #         retval = self.connection.query("CALC:AVER:AVER?")
    #     except ValueError as ex:
    #         print(f"Could not convert returned value from meter: {self.instrumentID} at {self.instrument}")
    #     except Exception as ex:
    #         print(f"Could not fetch from meter: {self.instrumentID} at {self.instrument}")
    #     return retval

    # # Clear all Event Registers
    # def clear_buffer(self):
    #     self.connection.write("*CLS")


    # # Set the line integration rate
    # def set_NPL_cycles(self, function, n):
    #     self.connection.write(f"{function}:NPLCycles {n}")

# #     ____
# #    / __ \___  ____  ___  _________ ______
# #   / /_/ / _ \/ __ \/ _ \/ ___/ __ `/ ___/
# #  / _, _/  __/ / / /  __(__  ) /_/ (__  )
# # /_/ |_|\___/_/ /_/\___/____/\__,_/____/
# # ----------------------------------------
# #              Multimeter Library
# #               Keithly 2000


        
    
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
