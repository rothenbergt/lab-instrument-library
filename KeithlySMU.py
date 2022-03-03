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
from typing import List
import inspect

class Keithly228(LibraryTemplate):
    """Summary of class here.

    Longer class information....
    Longer class information....

    Attributes:
        likes_spam: A boolean indicating if we like SPAM or not.
        eggs: An integer count of the eggs we have laid.
    """   
    def operate(self) -> bool:
        try:
            self.connection.write("F1X")
            return True
        except:
            print(f"Method {inspect.currentframe().f_code.co_name} failed on {self.instrument_address}")
            return False
    
    def standby(self) -> bool:
        try:
            self.connection.write("F0X")
            return True
        except:
            print(f"Method {inspect.currentframe().f_code.co_name} failed on {self.instrument_address}")
            return False
        
    def getData(self) -> List[float]:
        try:
            retString = self.connection.query("G5X").split(",")
            retString = [float(x) for x in retString]
            # Voltage, Current, Dwell Time, Memory Step
            
            # I only return voltage and current
            return retString[:2]
        except:
            print(f"Method {inspect.currentframe().f_code.co_name} failed on {self.instrument_address}")
            return None # Should I return None? Is this the best way to go about error handling
    
    def setVoltage(self, v: int) -> bool:
        try:
            self.connection.write(f"V{v}X")
            return True
        except:
            print(f"Method {inspect.currentframe().f_code.co_name} failed on {self.instrument_address}")
            return False
        
    def setCurrent(self, i: int) -> bool:
        try:
            self.connection.write(f"I{i}X")
            return True
        except:
            print(f"Method {inspect.currentframe().f_code.co_name} failed on {self.instrument_address}")
            return False        
        
        
class Keithly238(LibraryTemplate):
    
    def operate(self) -> bool:
        try:
            self.connection.write("N1X")
            return True
        except:
            print(f"Method {inspect.currentframe().f_code.co_name} failed on {self.instrument_address}")
            return False
    
    def standby(self) -> bool:
        try:
            self.connection.write("N0X")
            return True
        except:
            print(f"Method {inspect.currentframe().f_code.co_name} failed on {self.instrument_address}")
            return False
        
    def getData(self) -> List[float]:
        try:
            # Ask the instrument for current reading
            retString = self.connection.query("G15,0,0X").split(",")
            
            # At this point, retString looks like:
            # ['OSDCI-100.00E-06', 'D+00.000E+00', 'OMDCV-10.0019E+00', 'T+000.000E+00', 'B0000\r\n']
            
            # Return only (Voltage, Current) with prefix chopped off
            return float(retString[2][5:]), float(retString[0][5:])
            
        except:
            print(f"Method {inspect.currentframe().f_code.co_name} failed on {self.instrument_address}")
            # Should I return None? Is this the best way to go about error handling
            return None 
        
        
