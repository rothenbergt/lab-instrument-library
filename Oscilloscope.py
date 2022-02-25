#     ____                                 
#    / __ \___  ____  ___  _________ ______
#   / /_/ / _ \/ __ \/ _ \/ ___/ __ `/ ___/
#  / _, _/  __/ / / /  __(__  ) /_/ (__  ) 
# /_/ |_|\___/_/ /_/\___/____/\__,_/____/  
# ----------------------------------------
#        Oscilloscope Library                                         
#               MDO4104C

from struct import unpack

import PySimpleGUI as sg
import io
import numpy as np
import os
import pandas as pd
import pylab
import pyvisa
import shutil
import tempfile
import time
from PIL import Image, ImageColor, ImageDraw

# Class which allows for easier access to the GPIB TEK Oscilloscope
class Oscilloscope:

    # When initializing the object, make the connection
    def __init__(self, givenInstrument="USB0::0x0699::0x0456::C013314::INSTR", use=""):
        self.instrument = givenInstrument
        self.rm = pyvisa.ResourceManager()
        self.connected = False
        self.connection = ""
        self.instrumentID = ""
        self.scopeUse = use
        self.makeConnection(givenInstrument)

    # Make the GPIB connection & set up the instrument
    def makeConnection(self, givenInstrument):
        try:
            # Make the connection
            self.connection = self.rm.open_resource(givenInstrument)
            # print("Connection Made")
            self.connected = True
            self.connection.timeout = 250000                       # TODO might need to increase for *OPC
            self.instrumentID = self.connection.query("*IDN?")[:-1]
            print("Successfully established " + self.instrument + " connection with", self.instrumentID)
        except Exception as ex:
            print("Failed to make the connection with " + self.instrument + " EXITING...")
            self.connected = False
            quit()

    def setScopeUse(self, use):
        self.scopeUse = use

    # Set the state of the Oscilloscope to STOP or RUN
    def setState(self, command="STOP"):
        self.connection.write("ACQuire:STATE " + command)

    def run(self):
        self.connection.write("ACQuire:STATE RUN")

    def stop(self):
        self.connection.write("ACQuire:STATE STOP")

    def saveSetup(self, filename="TempSetup"):
        self.connection.write('SAVe:SETUp \"F:/' + filename + '.set\"')

    def recallSetup(self):
        self.connection.write('RECAll:SETUp \"F:/TempSetup.set\"')

    # Save a single image to a given location
    def saveImage(self, location):
        try:
            self.connection.write(
                'SAVE:IMAGe \"F:/Temp.png\"')  # Save screen capture to a temporary folder on F: Drive (Flash Drive)
            self.connection.query('*OPC?')  # Wait for the oscilloscope to finish saving the image.
            self.connection.write('FILESystem:READFile \"F:/Temp.png\"')  # Read the picture into the buffer
            imgData = self.connection.read_raw(1024 * 1024)  # get the raw picture from the buffer

        except Exception as ex:
            print("Timeout error from scope: " + self.instrumentID + " at " + self.instrument)
            print("USB DRIVE PROBABLY NOT PLUGGED IN....")
            os._exit(1)

        try:
            file = open(location, "wb")
            file.write(imgData)
            file.close()
        except IOError as ex:
            print("Could not write picture to .png file.... EXITING....")
            os._exit(1)
        except Exception as ex:
            print("Unkown error caused the picture saving to fail...")
            os._exit(1)

    def setChannelLabel(self, channel, label):
        self.connection.write("CH" + str(channel) + ":LABel \" " + label + " \"")

    def setLogicLabel(self, channel, label):
        self.connection.write("D" + str(channel) + ":LABel \" " + label + " \"")


    def getLabel(self, channel):
        return self.connection.query("CH" + str(channel) + ":LAB?")

    def setVerticalScale(self, channel, unitsPerDivision):
        self.connection.write("CH" + str(channel) + ":SCAle " + str(unitsPerDivision))

    def getCurrentMessage(self):
        return self.connection.query("MESSage:SHOW?")

    # TODO Why do we have this? I need to rewrite the current sensor script to remove this
    def setMessageBoxLocation(self):
        self.connection.write("MESSage:BOX 610, 600, 950, 645")

    def showMessage(self, message, x1="610", y1="600", x2="950", y2="645"):
        # print("MESSage:BOX " + x1 + ", " + y1 + ", "+ x2 + ", "+ y2)
        self.connection.write("MESSage:STATE ON")
        self.connection.write("MESSage:BOX " + x1 + ", " + y1 + ", " + x2 + ", " + y2)
        self.connection.write("MESSage:SHOW \"" + str(message) + " \"")

    def show_message(self, message):
        self.connection.write("MESSage:STATE ON")
        self.connection.write(f"MESSage:SHOW \"{message}\"")

    def removeMessage(self):
        self.connection.write("MESSage:STATE OFF")

    # TODO Can I remove this
    def write(self, message):
        self.connection.write(message)

    def query(self, message):
        return self.connection.query(message)

    # TODO change name to get waveform as numpy array
    def acquire(self, channel, show=False):
        try:
            # Setup the Oscilloscope 
            self.connection.write("DATA INIT")  # initializes the waveform data parameters to their factory defaults.
            self.connection.write('DATA:ENC RPB')  # encoding format for outgoing waveform data
            self.connection.write('DATA:WIDTH 1')  # Sets 1 byte per point
            self.connection.write("DATA:SOURCE CH" + str(channel))  # Select a channel to source

                
            # Get information which will help to decode the waveform
            ymult = float(self.connection.query('WFMPRE:YMULT?'))
            
            yzero = float(self.connection.query('WFMPRE:YZERO?'))
            
            yoff = float(self.connection.query('WFMPRE:YOFF?'))
            
            xincr = float(self.connection.query('WFMPRE:XINCR?'))
            # xdelay = float(self.connection.query('HORizontal:POSition?')) Not sure why here

            self.connection.write('CURVE?')
            data = self.connection.read_raw()

            headerlen = 2 + int(data[1])
            header = data[:headerlen]
            ADC_wave = data[headerlen:-1]

            ADC_wave = np.array(unpack('%sB' % len(ADC_wave), ADC_wave))

            Volts = (ADC_wave - yoff) * ymult + yzero

            # Time = np.arange(0, (xincr * len(Volts)), xincr)-((xincr * len(Volts))/2-xdelay) Not sure why here
            Time = np.arange(0, (xincr * len(Volts)), xincr)

            np.savetxt("time.csv", Time, delimiter=",")
            np.savetxt("Volts.csv", Volts, delimiter=",")

            if (show):
                pylab.plot(Time, Volts)
                pylab.title("Channel " + str(channel) + " Oscilloscope Result")
                pylab.xlabel("Time")
                pylab.ylabel("Volts")
                pylab.show()

            return Time, Volts
        except IndexError:
            return 0, 0

    def waveformToCSV(self, directory):
        retval = self.acquire(3)
        list_of_tuples = list(zip(retval[0], retval[1]))
        df = pd.DataFrame(list_of_tuples, columns=['Time', 'Volts'])
        df.to_csv(directory)

    def autoSet(self):
        self.connection.write("AUTOSet EXECute")

    # CROSSHair|FRAme|FULl|GRId|SOLid
    def changeGraticule(self, graticule):
        self.connection.write("DISplay:GRAticule " + str(graticule))

    # Change the Graticule intensity from 0 to 100
    def changeGraticuleIntensity(self, intensity):
        self.connection.write("DISplay:INTENSITy:GRAticule " + str(intensity))

    # Change the waveform intensity from 0 to 100
    def changeWaveFormIntensity(self, intensity):
        self.connection.write("DISplay:INTENSITy:WAVEform " + str(intensity))

    # Set the measurement type 
    # {AMPlitude|AREa|BURst|CARea|CMEan|CRMs|DELay|FALL|FREQuency
    # |HIGH|HITS|LOW|MAXimum|MEAN|MEDian|MINImum|NDUty|NEDGECount
    # |NOVershoot|NPULSECount|NWIdth|PEAKHits|PEDGECount|PDUty
    # |PERIod|PHAse|PK2Pk|POVershoot|PPULSECount|PWIdth|RISe|RMS
    # |SIGMA1|SIGMA2|SIGMA3|STDdev|TOVershoot|WAVEFORMS}
    def setMeasurementType(self, measurement):
        self.connection.write('MEASUREMENT:IMMED:TYPE ' + str(measurement))
        # print("\nThe measurement type is now: " + self.connection.query('MEASUrement:IMMed:TYPe?')[:-1])
        # print("The units is: " + self.connection.query("MEASUrement:IMMed:UNIts?"))

    # Set the measurement source CH1|CH2|CH3|CH4|MATH
    def setMeasurementSource(self, source):
        self.connection.write('MEASUrement:IMMed:SOUrce ' + str(source))
        # print("\nThe measurement source is now " + self.connection.query("MEASUrement:IMMed:SOUrce?")[:-1])

    # Returns a tuple of both the measurement result along with its units
    def getMeasurement(self):
        return (
        self.connection.query('MEASUrement:IMMed:VALue?')[:-1], self.connection.query("MEASUrement:IMMed:UNIts?")[1:-2])

    # Get the current aquire average sample count
    def getAquire(self):
        # print("The current numavg is " + self.connection.query("ACQuire:NUMAVg?")[:-1])
        return self.connection.query('ACQuire?')[:-1]

    # The range of values is
    # from 2 to 512 in powers of two.
    def setAquireAcquisitions(self, acquistions):

        if (acquistions % 2 != 0):
            print("The input must be powers of 2")
            return

        self.connection.write("ACQuire:NUMAVg " + str(acquistions))

        # print("The number of aquire averages is now " + self.connection.query('ACQuire:NUMAVg?')[:-1])

    # SAMple|PEAKdetect|HIRes|AVErage|ENVelope
    def setAquireMode(self, acquireMode):
        self.connection.write("ACQuire:MODe " + str(acquireMode))
        # print("\nThe aquire mode is now: " + self.connection.query('ACQuire:MODe?')[:-1])

    def setTriggerLevel(self, value):
        self.connection.write(f"TRIGger:A:LEVel {value}")

    def getAquireNumber(self):
        return self.connection.query('ACQuire:NUMAVg?')[:-1]

    # 1,000, 10,000, 100,000, 1M, 5M, 10M and 20M
    def setSampleRecordLength(self, length):
        self.connection.write("HORizontal:RECOrdlength " + str(length))

    def getSampleRecordLength(self):
        return self.connection.query("HORizontal:RECOrdlength?")[:-1]

    def setActionState(self):
        self.connection.write("ACTONEVent:EVENTTYPe ACQCOMPLete")
        self.connection.write('ACTONEVent:ACTION:SRQ:STATE ON')
        self.connection.write("ACTONEVent:ACTION:STOPACQ:STATE ON")

    def turnOffActionState(self):
        self.connection.write("ACTONEVent:ACTION:STOPACQ:STATE OFF")
        self.connection.write('ACTONEVent:ACTION:SRQ:STATE OFF')

    def OPC(self):
        print("Waiting for Oscilloscope to finish task.")
        self.connection.query("*OPC?")
        print("Oscilloscope is finished with task.")

    # Press a button on the front panel of the oscilloscope
    def pressButton(self, button):
        self.connection.write('FPAnel:PRESS ' + str(button))

    def messageBoxTool(self):

        def getCurrentCoordinates():
            return self.query("MESSage:BOX?").split(",")

        def get_value(key, values):
            value = values[key]
            if value.isdigit():
                return int(value)
            return 0

        def apply_drawing(values, window):
            image_file = "temp.png"
            shape = "Rectangle"
            begin_x = get_value("-BEGIN_X-", values)
            begin_y = get_value("-BEGIN_Y-", values)
            end_x = get_value("-END_X-", values) + 20
            end_y = get_value("-END_Y-", values) + 55
            width = 1
            fill_color = "aliceblue"
            outline_color = "black"
            if os.path.exists(image_file):
                shutil.copy(image_file, tmp_file)
                image = Image.open(tmp_file)
                image.thumbnail((1024, 1024))
                draw = ImageDraw.Draw(image)
                if shape == "Rectangle":
                    draw.rectangle(
                        (begin_x, begin_y, end_x, end_y),
                        fill=fill_color,
                        width=width,
                        outline=outline_color,
                    )
                image.save(tmp_file)
                bio = io.BytesIO()
                image.save(bio, format="PNG")
                window["-IMAGE-"].update(data=bio.getvalue())

        def create_coords_elements(label, begin_x, begin_y, key1, key2):
            return [
                sg.Text(label),
                sg.Input(begin_x, size=(5, 1), key=key1, enable_events=True),
                sg.Input(begin_y, size=(5, 1), key=key2, enable_events=True),
            ]

        file_types = [("PNG (*.png)", "*.png"), ("All files (*.*)", "*.*")]
        tmp_file = tempfile.NamedTemporaryFile(suffix=".png").name
        currentCoordinates = getCurrentCoordinates()
        currentCoordinates[3] = int(currentCoordinates[3]) - 35
        colors = list(ImageColor.colormap.keys())
        layout = [
            [sg.Image(key="-IMAGE-")],
            [
                sg.Text("Image File"),
                sg.Input(
                    size=(25, 1), key="-FILENAME-"
                ),
                sg.FileBrowse(file_types=file_types),
                sg.Button("Load Image"),
                sg.Button("Take Image"),
                sg.Button("Apply Coordinates")
            ],
            [sg.Text("Input Text"),
             sg.Input(
                 size=(25, 1), key="-INPUTTEXT-", default_text=self.getCurrentMessage()
             ), ],
            [
                *create_coords_elements(
                    "Begin Coords", str(currentCoordinates[0]), str(currentCoordinates[1]), "-BEGIN_X-", "-BEGIN_Y-"
                ),
                *create_coords_elements(
                    "End Coords", str(currentCoordinates[2]), str(currentCoordinates[3]), "-END_X-", "-END_Y-"
                ),
            ],
            [sg.Button("Save")],
        ]

        window = sg.Window("OSCOPE Box Tool", layout, size=(1200, 1024))
        events = [
            "Load Image",
            "-BEGIN_X-",
            "-BEGIN_Y-",
            "-END_X-",
            "-END_Y-",
            "-FILL_COLOR-",
            "-OUTLINE_COLOR-",
            "-WIDTH-",
        ]
        while True:
            event, values = window.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                break
            if event in events:
                apply_drawing(values, window)
            if event == "Take Image":
                self.saveImage("temp.png")
                values["-FILENAME-"] = "temp.png"
                apply_drawing(values, window)

            if event == "Apply Coordinates":
                # Get the coordinates
                x1 = str(values["-BEGIN_X-"])
                x2 = str(values["-END_X-"])
                y1 = str(values["-BEGIN_Y-"])
                y2 = str(int(values["-END_Y-"]) + 35)

                # Apply them
                self.showMessage(values["-INPUTTEXT-"], x1, y1, x2, y2)

            if event == "Save" and values["-FILENAME-"]:
                save_image(values)

        window.close()

    # Clean up the connection when we are finished with it
    def closeConnection(self):
        self.connection.close()

    def close(self):
        self.connection.close()
        
scope = Oscilloscope("USB0::0x0699::0x0456::C013314::INSTR")


# def setLogicLabel(self, channel, label):

scope.setLogicLabel(0, "MOSI")
scope.setLogicLabel(1, "SPI_CS")
scope.setLogicLabel(2, "MISO")
scope.setLogicLabel(3, "CLK")

scope.setLogicLabel(4, "BUSY")
scope.setLogicLabel(5, "SDO")
scope.setLogicLabel(6, "CS")



# scope = Oscilloscope("USB0::0x0699::0x0456::C013314::INSTR")

# scope = Oscilloscope("TCPIP0::132.158.220.45::INSTR")

##### scope = Oscilloscope("USB0::0x0699::0x0456::C013315::INSTR")

# scope = Oscilloscope("TCPIP0::132.158.220.35::INSTR")
# scope.messageBoxTool()

scope.setChannelLabel(1, "V_IN")
scope.setChannelLabel(2, "HI")
scope.setChannelLabel(4, "LO")
scope.setChannelLabel(3, "V_OUT (ac coupled)")

# scope.setChannelLabel(4, "Current")
# scope.changeGraticule("SOLID")

# scope.setChannelLabel(4, "Single-Ended RAA788000")
# scope.setChannelLabel(2, "OPA2376")
# scope.setChannelLabel(3, "RAA788000")
# scope.setChannelLabel(1, "Trigger Signal")


# scope.setChannelLabel(4, "I_LOAD")
# scope.setChannelLabel(2, "Threshold Voltage")

# scope.setChannelLabel(1, "Pulse Generator")
# scope.setChannelLabel(2, "V_IN (ac coupled)")
# scope.setChannelLabel(3, "V_OUT (ac coupled)")
# scope.setChannelLabel(4, "I_LOAD")



# # Get the Rise Time
# scope.setMeasurementType("RISe")
# scope.setMeasurementSource("CH3")
# riseTime = scope.getMeasurement()

# scope.setMeasurementType("FALL")
# scope.setMeasurementSource("CH3")
# fallTime = scope.getMeasurement()

# scope.setMeasurementType("MINImum")
# scope.setMeasurementSource("CH3")
# minimum = scope.getMeasurement()

# scope.setMeasurementType("MAXimum")
# scope.setMeasurementSource("CH3")
# maximum  = float(scope.getMeasurement()[0])

# v0 = (0.9 * maximum) - (0.1 * maximum) 
# slewRate = v0 / float(riseTime[0])

# fallingSlewRate = v0 / float(fallTime[0])

# print(f"The minimum is {minimum}")
# print(f"The maximum is {maximum}")
# print(f"The 90% is {v0}")


# print(f"The rising slew rate is {round(slewRate/1000/1000, 2)} mA/ns")
# print(f"The falling slew rate is {round(fallingSlewRate/1000/1000, 2)} mA/ns")

# startAmp = 0
# endAmp = 50


# message = f"Part = Richtek RT9069, Details = 36V 2uA IQ Peak 200mA LDO, Package = SOT-23-5, , \
# Test: Load Transient, \
# I_LOAD = {startAmp}mA -> {endAmp}mA, \
# V_IN = 14V V_OUT = 12V, \
# C_IN = 1uF C_OUT = 1uF, , \
# Rising Slew = {round(slewRate/1000, 2)} mA/us, \
# Falling Slew = {round(fallingSlewRate/1000, 2)} mA/us"

# # message = message.replace('\n', ',')
# # message = message.replace('|', '')
# message = message.replace(', ', '\n')

# scope.show_message(message)

# scope.saveImage(f"10A_POT.png")

# scope.removeMessage()

message = f"Part = Richtek RT9069, Details = 36V 2uA IQ 200mA LDO, Package = SOT-23-5, , \
Test: Line Transient, \
V_IN = 6V -> 30V, V_OUT = 5V, \
I_LOAD = 100mA (RL = 50Ohm), \
C_IN = 1uF C_OUT = 1uF"

message = message.replace('\n', ',')
message = message.replace('|', '')
message = message.replace(', ', '\n')

scope.show_message(message)
scope.removeMessage()


message = f"RAA214250 (10V) Start-Up Time, \
(VIN=12.00V VEN=5.00V VOUT=10.00V IOUT=0.500A T=25C, \
CIN=4.7uF Wire 1uF COUT=4x22uF CFF=0uF RL=0 ohms, \
From VEN to 90% VOUT"

message = message.replace('\n', ',')
message = message.replace('|', '')
message = message.replace(', ', '\n')

# scope.show_message(message)

scope.setChannelLabel(1, "V_IN")
scope.setChannelLabel(2, "V_OUT")
scope.setChannelLabel(4, "I_IN")
scope.setChannelLabel(3, "PWM")

scope.changeGraticule("FULL")

# scope.saveImage(f"Juan3.png")
