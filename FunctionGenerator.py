from LibraryTemplate import LibraryTemplate
import numpy as np
import time
import sys

class AFG3000(LibraryTemplate):
    
    def helloWolrd(self) -> None:
        
        print("Hello, World")
        
    
    def setFunction(self, function = "SINusoid", channel = 1) -> None:
        """
        param function: SINusoid|SQUare|PULSe|RAMP|PRNoise|DC
        """
        self.connection.write(f"SOURCE{channel}:FUNCTION:SHAPE {function}")
    
    
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
        
        
