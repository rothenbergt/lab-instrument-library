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

import pyvisa, sys, pandas, math
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from LibraryTemplate import LibraryTemplate

class NetworkAnalyzer(LibraryTemplate):
    """Summary of class here.

    Longer class information....
    Longer class information....

    Attributes:
        likes_spam: A boolean indicating if we like SPAM or not.
        eggs: An integer count of the eggs we have laid.
    """
    # Set the power level of channel 1
    def set_power(self, newPowerLevel):
        self.connection.write(f":SOUR1:POW " + str(newPowerLevel))

    def get_power(self):
        return round(float(self.connection.query(":SOUR1:POW?")),2)

    def turn_on_backlight(self):
        self.connection.write(":SYST:BACK ON")

    def clear_all_markers(self):
        self.connection.write(":CALC1:MARK:AOFF")

    def display_marker_table(self, display = "ON"):
        self.connection.write(":DISP:TABL " + str(display))

    def set_log_sweep(self):
        self.connection.write(":SENS1:SWE:TYPE LOG")

    # TODO Save in a specific location
    def save_image(self, pictureName = "temp", scale = "NO"):
        # Turn the back Light On
        self.turnBackLightOn()
        
        # Invert the display for better picture quality
        # self.invertDisplay()

        # Scale the image on the screen of the network analyzer
        if ("YES" in scale):
            self.connection.write(":DISP:WIND1:TRAC1:Y:SCAL:AUTO")
            self.connection.write(":DISP:WIND1:TRAC2:Y:SCAL:AUTO")

        # TODO Remove the user menu before taking the picture
        # I Dont think this is possible after looking into it

        # Store the image on the network analzer, then transfer the image data over to the computer. 
        self.connection.write(":MMEM:STOR:IMAG \"D:\\temp.png\"")   # Save temp image on device
        self.connection.write("MMEM:TRAN? \"D:\\temp.png\"")        # Move image into buffer
        data = self.connection.read_raw()                           # Read raw data from buffer
        
        self.setNormalDisplay()

        f = open(pictureName + ".png", "wb")                           # Save raw data in local file

        # We remove the first 8 characters here because bad data appears before the 
        # PNG header and corrupt the file. 
        # The header given to us looks like: #6034162\x89PNG\r\n
        # The header we want looks like:     \x89PNG\r\n
        f.write(data[8:])                                   # Write Data
        f.close()                                           # Close the file

    # Change the current active trace
    def change_active_trace(self, trace):
        self.connection.write(":CALC:PAR" + str(trace) + ":SEL")

    # Add a title to the current window
    def set_title(self, title):
        self.connection.write(":DISP:WIND1:TITL:DATA \"""{}\"".format(title))
        self.connection.write(":DISP:WIND1:TITL ON")

    def get_start_frequency(self):
        return float(self.connection.query(":SENS1:FREQ:STAR?"))

    def get_stop_frequency(self):
        return float(self.connection.query(":SENS1:FREQ:STOP?"))

    def turn_off_R_attenuator(self):
        self.connection.write("INP:ATT:GPP:R 0")

    def turn_on_R_attenuator(self):
        self.connection.write("INP:ATT:GPP:R 20")

    def turn_off_T_attenuator(self):
        self.connection.write("INP:ATT:GPP:T 0")

    def turn_on_T_attenuator(self):
        self.connection.write("INP:ATT:GPP:T 20")

    # Get current frequency data
    def get_frequency_data(self):
        return self.connection.query_ascii_values("SENS1:FREQ:DATA?")

    # Get current active trace data
    def get_data(self):
        return self.connection.query_ascii_values("CALC:DATA:FDAT?")[::2]

    def get_data_as_dataframe(self):
        # Grab all of the dB data from the first trace on the network analyzer
        # We skip every other entry we are given bunk data
        data = self.get_data()

        # Get the frequency at which we have tested the data points at
        frequency_data = self.get_frequency_data()

        # Zip the data together so each frequency has a dB
        zipped_data = zip(frequency_data, data)

        # Get the type of data PHAS DB
        data_tile = self.connection.query(":CALC:FORM?")[:-1]

        # Turn the zipped data into a dataframe with columns
        df = pandas.DataFrame(zipped_data, columns = ['Frequency', data_tile])

        return df

    # Save the current trace data as a CSV file
    def save_trace_CSV(self, fileName = "temp"):
        # Get the data as a DataFrame
        df = self.getDataAsDataFrame()
        # Save the data as a csv
        df.to_csv(fileName + ".csv", index = False)

    # Wait for the Standard Event Status Register to show operation Completed
    def wait_for_OPC(self):
        self.connection.write("*OPC?")          # Ensure the instrument has completed all opreations
        self.connection.read()                  # Wait for a response from the network analyzer

    # Automatically find the -3dB point given a graph
    def find_3dB(self, marker = 1, searchStart = 20, activeTrace = 1):
        
        # Set the active trace to the one with MLOG
        self.changeActiveTrace(activeTrace)

        # Turn on search range. We don't want to search at our first datapoint
        self.connection.write("CALC:MARK:FUNC:DOM ON")
        self.connection.write("CALC:MARK:FUNC:DOM:STAR " + str(searchStart))

        # Turn on reference marker and set it to find max
        self.connection.write("CALC:SEL:MARK10 ON")
        self.connection.write("CALC:SEL:MARK10:FUNC:TYPE MAX")

        # Turn on second marker and set it to -3dB of the reference marker
        self.connection.write("CALC:SEL:MARK" + str(marker) + " ON")
        self.connection.write("CALC:SEL:MARK" + str(marker) + ":FUNC:TYPE TARG")
        self.connection.write("CALC:SEL:MARK" + str(marker) + ":FUNC:TARG -3")
        self.connection.write("CALC:MARK" + str(marker) + ":FUNC:EXEC")

    def find_phase_target(self, degree = -45, marker = 2, activeTrace = 2):

        # Set the active trace to the one with Phase
        self.changeActiveTrace(activeTrace)

        dataTile = self.connection.query(":CALC:FORM?")[:-1]

        if ("PHAS" not in dataTile):
            print("Whoa! The channel you selected isn't for Phase")
            # TODO add graceful exit

        # Turn on second marker and set it to -3dB of the reference marker
        self.connection.write("CALC:SEL:MARK" + str(marker) + " ON")
        self.connection.write("CALC:SEL:MARK" + str(marker) + ":FUNC:TYPE TARG")
        self.connection.write("CALC:SEL:MARK" + str(marker) + ":FUNC:TARG " + str(degree))
        self.connection.write("CALC:MARK" + str(marker) + ":FUNC:EXEC")      

    def find_dB_target(self, db = 57, marker = 2, activeTrace = 2):

        # Set the active trace to the one with Phase
        self.changeActiveTrace(activeTrace)

        dataTile = self.connection.query(":CALC:FORM?")[:-1]

        if ("MLOG" not in dataTile):
            print("Whoa! The channel you selected isn't for dB")
            # TODO add graceful exit

        # Turn on second marker and set it to -3dB of the reference marker
        self.connection.write("CALC:SEL:MARK" + str(marker) + " ON")
        self.connection.write("CALC:SEL:MARK" + str(marker) + ":FUNC:TYPE TARG")
        self.connection.write("CALC:SEL:MARK" + str(marker) + ":FUNC:TARG " + str(db))
        self.connection.write("CALC:MARK" + str(marker) + ":FUNC:EXEC")   

    # Trigger a single run of the network analyzer
    def trigger_single_run(self):
        self.connection.write(":INIT1:CONT ON") # Turn on continous mode
        self.connection.write(":TRIG:SOUR BUS") # Set the trigger source to be the bus
        self.connection.write(":TRIG:SING")     # Trigger a single run

        # Wait until the single frequency scan to complete
        self.waitForOPC()

    # Save the current state to the state folder
    def save_current_state(self, stateName = "tempSavedState"):
        self.connection.write(":MMEM:STOR \"D:\\State\\" + stateName + ".sta\"")

    # Set the starting frequency
    def set_start_frequency(self, start):
        # self.connection.write(":SENS1:BWID " + str(start))         # Change the bandwidth resolution
        self.connection.write(":SENS1:FREQ:STAR " + str(start))    # to be the same as the starting frequency  

    # Set the starting frequency
    def set_stop_frequency(self, stop):
        self.connection.write(":SENS1:FREQ:STOP " + str(start))    # to be the same as the starting frequency 

    def change_IF_bandwidth(self, onOrOff = 1):
        self.connection.write(":SENS1:BWA " + str(onOrOff))

    # Set the stopping frequency
    def set_stop_frequency(self, stop):
        self.connection.write(":SENS1:FREQ:STOP " + str(stop))

    # Invert the display depending on its current state
    def invert_display(self):
        self.connection.write(":DISP:IMAG INV")

    # Return the display to have a black background
    def set_normal_display(self):
        self.connection.write(":DISP:IMAG NORM")

    # Set the current active trace to measure trace
    def set_active_trace_to_phase(self):
        self.connection.write(":CALC:FORM PHAS")

    # Set the current active trace to measure Magnitude Log
    def set_active_trace_to_logdB(self):
        self.connection.write(":CALC:FORM MLOG")

    def get_marker_X_and_Y(self, marker):
        x = float(self.connection.query(":CALC:SEL:MARK" + str(marker) + ":X?"))
        return str(x)

    # Allow the user to select a state file saved on the machine
    def select_state_file(self):
        # Get all files in the state folder
        allStates = self.connection.query(":MMEM:CAT? \"D:\\State\"").split(",")
        # Remove anything that isn't a state file
        allStates = [state for state in allStates if ".sta" in state]

        # Create the PYSimpleGUI layout
        layout = [[sg.Listbox(values=allStates, size=(30, 35), key="-LIST-", enable_events=True), 
                   sg.Button('Ok'),
                   sg.Button("Cancel"),
                   sg.Button("Preset") 
                 ]]
        # Create the PYSimpleGUI window
        window = sg.Window('Available States', layout)

        # Create the GUI Loop
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Cancel':       # if user closes window or clicks cancel
                break
            if event == 'Preset':                                 # if user presses the reset button
                self.connection.write(":SYST:PRES")
                self.waitForOPC()
                break
            if event == 'Ok':                                     # if user presses the OK button
                break
            if values['-LIST-']:                                  # If user makes a selection from the list
                print("You selected " + values['-LIST-'][0])
                self.connection.write(":MMEM:LOAD \"D:\\State\\" + str(values['-LIST-'][0]) + "\"")
    
        # Clean up
        window.close()
    

