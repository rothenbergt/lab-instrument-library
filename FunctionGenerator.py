from LibraryTemplate import LibraryTemplate
import numpy as np
import time
import sys
from typing import Union
import inspect

# AFG3052C

class AFG3000(LibraryTemplate):
    
    def set_function(self, function: float = "SINusoid", source: int = 1) -> None:
        """
        param function: SINusoid|SQUare|PULSe|RAMP|PRNoise|DC
        """

        self.connection.write(f"SOURCE{source}:FUNCTION:SHAPE {function}")
    
    def get_function(self, source):
        """Gets the selected function.

        Args:
        minimum: The selected channel

        Returns:
        The current selected function.

        Raises:
        Except: If the query fails.
        """
        print(self.connection.query(f"SOURCE{source}:FUNCTION:SHAPE?"))

    def get_amplitude(self, source: int) -> float:
        retval = sys.maxsize

        try:
            retval = self.connection.query(f"SOURce{source}:VOLTage:LEVel:IMMediate:AMPLitude?")
            return float(retval)
        except:
            print(f"Device {self.instrumentID} failed in {inspect.currentframe().f_code.co_name}")
            return retval

    
    def set_amplitude(self, source: int, amplitude: float) -> float:
        retval = sys.maxsize

        try:
            self.connection.write(f"SOURce{source}:VOLTage:LEVel:IMMediate:AMPLitude {amplitude}")
            retval = self.get_amplitude(source)
            return float(retval)
        except:
            print(f"Device {self.instrumentID} failed in {inspect.currentframe().f_code.co_name}")
            return retval


    def get_frequency(self, source: int) -> float:

        retval = sys.maxsize

        try:
            retval = self.connection.query(f"SOURce{source}:FREQUENCY?")
            return float(retval)
        except:
            print(f"Device {self.instrumentID} failed in {inspect.currentframe().f_code.co_name}")
            return retval


    def set_frequency(self, source: int, frequency: int) -> float:

        retval = sys.maxsize

        try:
            self.connection.write(f"SOURce{source}:FREQUENCY {frequency}")
            retval = self.get_frequency(source)
            return float(retval)
        except:
            print(f"Device {self.instrumentID} failed in {inspect.currentframe().f_code.co_name}")
            return retval
  
    def set_period(self, source: int, period: int) -> bool:
        
        self.set_frequency(source, 1 / period)


    def get_leading_edge(self, source:int) -> float:

        retval = sys.maxsize

        try:
            retval =  self.connection.query(f"SOURce{source}:PULSe:TRANsition:LEADing?")
            return retval
        except:
            print(f"Device {self.instrumentID} failed in {inspect.currentframe().f_code.co_name}")
            return retval

    def get_trailing_edge(self, source:int) -> float:

        retval = sys.maxsize

        try:
            retval =  self.connection.query(f"SOURce{source}:PULSe:TRANsition:TRAiling?")
            return retval
        except:
            print(f"Device {self.instrumentID} failed in {inspect.currentframe().f_code.co_name}")
            return retval


    def set_leading_edge(self, source: int, value: str) -> float:
        """
        param value: <units>::=[ns | μs | ms | s]
        """
        retval = sys.maxsize

        try:
            self.connection.write(f"SOURce{source}:PULSe:TRANsition:LEADing {value}")
            retval =  self.get_leading_edge(source)
            return retval
        except:
            print(f"Device {self.instrumentID} failed in {inspect.currentframe().f_code.co_name}")
            return retval

    def set_trailing_edge(self, source: int, value: str) -> float:
        """
        param value: <units>::=[ns | μs | ms | s]
        """
        retval = sys.maxsize

        try:
            self.connection.write(f"SOURce{source}:PULSe:TRANsition:TRAiling {value}")
            retval =  self.get_trailing_edge(source)
            return retval
        except:
            print(f"Device {self.instrumentID} failed in {inspect.currentframe().f_code.co_name}")
            return retval


    def set_duty_cycle(self, source: int, duty: float) -> float:

        self.connection.write(f"SOURce{source}:PULSE:DCYCle {duty}")


    def setBurstMode(self, channel = 1, cycles = 1) -> None:
        
        self.connection.write(f"SOURce1:BURSt:STATe ON")
        self.connection.write(f"SOURce1:BURSt:MODE TRIGgered")
        self.connection.write(f"SOURce1:BURSt:NCYCles {cycles}")
    
    def setLowVoltage(self, voltage = 0, channel = 1) -> None:
        self.connection.write(f"SOURce{channel}:VOLTage:LEVel:IMMediate:LOW {voltage}V")
    
    
    def setHighVoltage(self, voltage = 5, channel = 1) -> None:
        self.connection.write(f"SOURce{channel}:VOLTage:LEVel:IMMediate:HIGH {voltage}V")
    
    def trigger(self):
        self.connection.write("*TRG")
        
    def check_for_errors(self) -> bool:
        '''
        Pull an error from the error buffer
        '''
        print(self.connection.query("SYSTem:ERROR?"))

arb = AFG3000("GPIB0::11::INSTR")

arb.set_function("SIN")

# frequency_measured = arb.set_frequency(1, 6E3)

# print(frequency_measured)

# arb.set_period(1, 1E-3)
# arb.set_duty_cycle(1, 5)
# arb.set_leading_edge(1, "15ns")
# arb.set_trailing_edge(1, "15ns")

# print(arb.set_amplitude(1, 0.25))

# print(arb.get_function(1))

arb.check_for_errors()

print()