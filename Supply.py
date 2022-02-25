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

# Class which allows for easier access to the GPIB TEK Oscilloscope
class Supply:

    # When initializing the object, make the connection
    def __init__(self, givenInstrument = "GPIB0::23::INSTR"):
        self.instrument = givenInstrument
        self.rm = pyvisa.ResourceManager()
        self.connected = False
        self.connection = ""
        self.instrumentID = ""
        self.debug = False
        self.makeConnection(givenInstrument)
        self.disableOutput()

    # Make the GPIB connection & set up the instrument
    def makeConnection(self, givenInstrument):
        try:
            # Make the connection
            self.connection = self.rm.open_resource(givenInstrument)
            # print("Connection Made")
            self.connected = True
            self.connection.timeout = 2500                        # Increase Timeout
            self.instrumentID = self.connection.query("*IDN?")[:-1]
            print("Successfully established " + self.instrument + " connection with", self.instrumentID)
            
        except:
            print("Failed to make the connection with ", self.instrument)
            self.connected = False
            quit()

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
        print("The DMM is off by " + str(measuredVoltage - referenceVoltage))
        return measuredVoltage - referenceVoltage


