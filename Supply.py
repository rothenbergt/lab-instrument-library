#     ____
#    / __ \___  ____  ___  _________ ______
#   / /_/ / _ \/ __ \/ _ \/ ___/ __ `/ ___/
#  / _, _/  __/ / / /  __(__  ) /_/ (__  )
# /_/ |_|\___/_/ /_/\___/____/\__,_/____/
# ----------------------------------------
#              Power Supply Library
#               Agilent 2000

import pyvisa
import sys
import time
import numpy as np

#TODO add multiple supplies like DC Supply

# Class which allows for easier access to the GPIB TEK Oscilloscope
class Supply(LibraryTemplate):

    def write(self, message):
        self.connection.write(message)

    def query(self, message):
        return self.connection.query(message)
    
    def enableOutput(self):
        self.connection.write("OUTPut ON")
    
    def disableOutput(self):
        self.connection.write("OUTPut OFF")
        
    def setVoltage(self, voltage):
        self.connection.write("VOLTage " + str(voltage))
    
    def setCurrent(self, current):
        self.connection.write("CURRent " + str(current))

    def setVoltageRange(self, range):
        self.connection.write("VOLTage:RANGe " + range)
        
    def getVoltageRange(self):
        return self.connection.query("VOLTage:RANGe?")

    def getCurrentVoltage(self):
        return float(self.connection.query("MEASure:VOLTage:DC?"))
    
    def reset(self):
        self.connection.write("*RST")
    
    def select_25(self):
        self.connection.write("INST:SEL P25V")
    
    def getCalibrationFactor(self, referenceVoltage):
        
        self.setVoltage(referenceVoltage)
        
        # Allow the output to settle for 500 msec
        time.sleep(0.5)        
        
        measuredVoltage = self.getCurrentVoltage()
        return measuredVoltage - referenceVoltage


#     ____
#    / __ \___  ____  ___  _________ ______
#   / /_/ / _ \/ __ \/ _ \/ ___/ __ `/ ___/
#  / _, _/  __/ / / /  __(__  ) /_/ (__  )
# /_/ |_|\___/_/ /_/\___/____/\__,_/____/
# ----------------------------------------


# from LibraryTemplate import LibraryTemplate
# from typing import List
# import inspect

# class E3649A(LibraryTemplate):
    
#     def getVoltage(self):
#         retval = self.connection.query(f"MEASure:VOLTage:DC?")
#         return float(retval)

#     def getCurrent(self):
#         retval = self.connection.query(f"MEASure:CURRent:DC?")
#         return float(retval)

#     def setVoltage(self, voltage):
#         self.connection.write(f"VOLT {voltage}")

