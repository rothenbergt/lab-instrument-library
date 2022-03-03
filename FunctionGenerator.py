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

  --------------------------------------------------------------------------------------------------------------------- |
  | COMPANY     MODEL     DOCUMENT      LINK                                                                            |
  --------------------------------------------------------------------------------------------------------------------- |
  | Tektronix   AFG3052C  Users Guide   https://mmrc.caltech.edu/Tektronics/AFG3021B/AFG3021B%20Programmer%20Manual.pdf |
  --------------------------------------------------------------------------------------------------------------------- |
"""

import time
import sys
import inspect
import numpy as np
from typing import Union
from LibraryTemplate import LibraryTemplate

# AFG3052C

class AFG3000(LibraryTemplate):
    """Summary of class here.

    Longer class information....
    Longer class information....

    Attributes:
        likes_spam: A boolean indicating if we like SPAM or not.
        eggs: An integer count of the eggs we have laid.
    """
       
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


    def set_burst_mode(self, channel = 1, cycles = 1) -> None:
        
        self.connection.write(f"SOURce1:BURSt:STATe ON")
        self.connection.write(f"SOURce1:BURSt:MODE TRIGgered")
        self.connection.write(f"SOURce1:BURSt:NCYCles {cycles}")
    
    def set_low_voltage(self, voltage = 0, channel = 1) -> None:
        self.connection.write(f"SOURce{channel}:VOLTage:LEVel:IMMediate:LOW {voltage}V")
    
    
    def set_high_voltage(self, voltage = 5, channel = 1) -> None:
        self.connection.write(f"SOURce{channel}:VOLTage:LEVel:IMMediate:HIGH {voltage}V")
    
    def trigger(self):
        self.connection.write("*TRG")
        
    def check_for_errors(self) -> bool:
        '''
        Pull an error from the error buffer
        '''
        print(self.connection.query("SYSTem:ERROR?"))

# arb = AFG3000("GPIB0::11::INSTR")
