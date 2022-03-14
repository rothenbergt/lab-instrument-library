"""  ____
    / __ \___  ____  ___  _________ ______
   / /_/ / _ \/ __ \/ _ \/ ___/ __ `/ ___/
  / _, _/  __/ / / /  __(__  ) /_/ (__  )
 /_/ |_|\___/_/ /_/\___/____/\__,_/____/
 ----------------------------------------
Python library containing general functions to control Keysight B2902A SMU.

    The current methods available within the module are:

    Class Methods:
        __init__()
        ch1_off()
        ch1_on()
        ch2_off()
        ch2_on()
        ch_off()
        ch_on()
        change_display()
        check_for_errors()
        clear()
        close_connection()
        fetchBothChannel()
        find_best_current()
        get_all_measurements()
        get_all_measurements_both_channels()
        get_both_channel_current()
        get_both_channel_voltage()
        get_ch1_current()
        get_ch1_power()
        get_ch1_voltage()
        get_ch1_voltage_and_current()
        get_ch2_current()
        get_ch2_power()
        get_ch2_voltage()
        get_ch2_voltage_and_current()
        get_current()
        get_current_array()
        get_screen_image()
        get_voltage()
        get_voltage_array()
        get_voltage_current_both_channels()
        identify()
        initiate_all()
        initiate_ch1()
        initiate_ch2()
        make_connection()
        query()
        readBothChannel()
        reset()
        set_NPLC()
        set_ch1_2_wire()
        set_ch1_4_wire()
        set_ch1_current()
        set_ch1_current_limit()
        set_ch1_floating()
        set_ch1_mode()
        set_ch1_voltage()
        set_ch1_voltage_limit()
        set_ch2_2_wire()
        set_ch2_4_wire()
        set_ch2_current()
        set_ch2_current_limit()
        set_ch2_floating()
        set_ch2_mode()
        set_ch2_voltage()
        set_ch2_voltage_limit()
        set_current()
        set_current_limit()
        set_current_sens_range()
        set_floating()
        set_measure_count()
        set_measure_delay()
        set_mode()
        set_mode_current_limit()
        set_mode_voltage_limit()
        set_pulse_peak()
        set_pulse_width()
        set_trigger_period()
        set_voltage()
        set_voltage_limit()
        set_voltage_source_range()
        trigger()
        turn_off_high_capacitance_mode()
        turn_on_4_wire()
        turn_on_high_capacitance_mode()
        turn_on_high_z()
        turn_on_pulse()
        write()

    Typical usage example:

        smu = SMU()
        voltage, current = smu.get_ch1_voltage_and_current()

  --------------------------------------------------------------------------------------------------------------------- |
  | COMPANY     MODEL     DOCUMENT      LINK                                                                            |
  --------------------------------------------------------------------------------------------------------------------- |
  | Keysight    B2902A    Users Guide   https://assets.testequity.com/te1/Documents/pdf/B2900A-prog.pdf                 |
  --------------------------------------------------------------------------------------------------------------------- |
"""

from LibraryTemplate import LibraryTemplate
import numpy as np
import time
import sys
import pyvisa

# TODO, change to query_as_ascii

class SMU(LibraryTemplate):
    """General SMU class.

    Attributes:
        lab_supplies: A dictionary of the current lab multimeters.
        instrument_address:
        connection:
        instrument_ID:
        nickname:
    """        

    def exception_handler(func):
        """Handles the exceptions which might occur during a visa transaction.

        Args:
        func: the function which is being called

        Returns:
        The return value from the function

        Raises:
        ValueError: If the result couldn't be convereted to float.
        pyvisa.errors.VisaIOError: 
        pyvisa.errors.VisaIOErrorVI_ERROR_NLISTENERS:
        pyvisa.errors.VI_ERROR_TMO:
        """
        def inner_function(self, *args, **kw):
            try:
                return func(self, *args, **kw)
            except ValueError as ex:
                print(f"Could not convert returned value to float from meter: {self.instrument_ID} at {self.instrument} \n \
                        in class {self.__class__.__name__}, method {func.__name__}")
                return retval
            except TypeError as ex:
                print("Wrong param Type")
            except pyvisa.errors.VisaIOError as ex:
                print(f"Exception {type(ex)} {ex.abbreviation}")

                if "VI_ERROR_NLISTENERS" in ex.abbreviation:
                    print(f"Looks like the instrument at {self.instrument_address} isn't responding.. Are you sure this is the right GPIB address?.")

                if "VI_ERROR_TMO" in ex.abbreviation:
                    print(f"Looks like the instrument at {self.instrument_address} is timing out.. Are you sure this is the right GPIB address?.")

                return sys.maxsize
            except Exception as ex:
                print(f"This was an exception we were not prepared for {type(ex)}, {ex}")

        return inner_function

    @exception_handler   
    def ch_on(self, channel = 1):
        self.connection.write(f"OUTP{channel} ON")

    @exception_handler
    def ch1_on(self):
        self.ch_on(1)

    @exception_handler
    def ch2_on(self):
        self.ch_on(2)

    @exception_handler
    def ch_off(self, channel = 1):
        self.connection.write(f"OUTP{channel} OFF")

    @exception_handler
    def ch1_off(self):
        self.ch_off(1)

    @exception_handler
    def ch2_off(self):
        self.ch_off(2)

    @exception_handler
    def initiate_all(self):
        self.connection.write(f":INIT:ACQ (@1,2)")

    @exception_handler
    def initiate_ch1(self):
        self.connection.write(f":INIT:ACQ (@1)")

    @exception_handler
    def initiate_ch2(self):
        self.connection.write(f":INIT:ACQ (@2)")      
        
    @exception_handler
    def set_mode(self, channel = 1, mode = "VOLT"):
        self.connection.write(f":SOUR{channel}:FUNC:MODE {mode}")

    @exception_handler      
    def set_ch1_mode(self, mode = "VOLT"):
        self.set_mode(1, mode)

    @exception_handler
    def set_ch2_mode(self, mode = "VOLT"):
        self.set_mode(2, mode)

    @exception_handler  
    def set_current(self, channel = 1, current = 0):
        self.connection.write(f":SOUR{channel}:CURR {current}")
    
    @exception_handler
    def set_ch1_current(self, current = 0.1):
        self.set_current(1, current)

    @exception_handler
    def set_ch2_current(self, current = 0.1):
        self.set_current(2, current)

    @exception_handler
    def set_voltage(self, channel = 1, voltage = 0):
        self.connection.write(f":SOUR{channel}:VOLT {voltage}")

    @exception_handler
    def set_ch1_voltage(self, voltage = 1):
        self.set_voltage(1, voltage)

    @exception_handler
    def set_ch2_voltage(self, voltage = 1):
        self.set_voltage(2, voltage)
        

    @exception_handler
    def set_mode_voltage_limit(self, channel = 1, mode = "VOLT", voltage = 0, limit = 0):
        self.set_mode(channel, mode)
        self.set_voltage(channel, voltage)
        self.set_current_limit(channel, limit)


    @exception_handler
    def set_mode_current_limit(self, channel = 1, mode = "CURR", current = 0, limit = 0):
        self.set_mode(channel, mode)
        self.set_current(channel, current)
        self.set_voltage_limit(channel, limit)
        
    
    @exception_handler
    def get_function(self, channel = 1):
        return self.connection.query(":SOUR:FUNC:MODE?").strip("\n")


    @exception_handler
    def set_ch1_voltage_limit(self, voltage = 0):
        if self.get_function(channel = 1) == "CURR":
            self.connection.write(f":SENS:VOLT:PROT {voltage}")    
        else:
            print("ERROR Cannot set voltage limit we are not on current mode")


    def set_ch1_current_limit(self, current = 0):
        if self.connection.query(":SOUR:FUNC:MODE?")[:-1] == "VOLT":
            self.connection.write(f":SENS:CURR:PROT {current}")       
        else:
            print("ERROR Cannot set current limit we are not on voltage mode")
    def set_ch2_voltage_limit(self, voltage = 1):
        if self.connection.query(":SOUR2:FUNC:MODE?")[:-1] == "CURR":
            self.connection.write(f":SENS2:VOLT:PROT {voltage}")    
        else:
            print("ERROR Cannot set voltage limit we are not on current mode")
    def set_ch2_current_limit(self, current = 1):
        if self.connection.query(":SOUR2:FUNC:MODE?")[:-1] == "VOLT":
            self.connection.write(f":SENS2:CURR:PROT {current}")       
        else:
            print("ERROR Cannot set current limit we are not on voltage mode")
    def set_current_limit(self, channel = 1, current = 0):
        if self.connection.query(f":SOUR{channel}:FUNC:MODE?")[:-1] == "VOLT":
            self.connection.write(f":SENS{channel}:CURR:PROT {current}")       
        else:
            print("ERROR Cannot set current limit we are not on voltage mode")
    def set_voltage_limit(self, channel = 1, voltage = 0):
        if self.connection.query(f":SOUR{channel}:FUNC:MODE?")[:-1] == "CURR":
            self.connection.write(f":SENS{channel}:VOLT:PROT {voltage}")    
        else:
            print("ERROR Cannot set voltage limit we are not on current mode")


    @exception_handler
    def get_voltage(self, channel = 1):
        return float(self.connection.query(f":meas:volt? (@{channel})"))

    @exception_handler
    def get_ch1_voltage(self):
        return self.get_voltage(channel = 1)

    @exception_handler
    def get_ch2_voltage(self):
        return self.get_voltage(channel = 2)

    def get_current(self, channel = 1):
        return float(self.connection.query(f":meas:curr? (@{channel})"))
    
    def get_ch1_current(self):
        return self.get_current(channel = 1)

    def get_ch2_current(self):
        return self.get_current(channel = 2)
    
    def get_all_measurements(self, channel = 1):
        measure_result = self.connection.query(f":MEAS? (@{channel})")
        measure_result = measure_result.split(",")
        measure_result = [float(x) for x in measure_result]
        return measure_result

    
    def get_all_measurements_both_channels(self):
            measure_result = self.connection.query(f":MEAS? (@1,2)")            
            measure_result = measure_result.split(",")
            measure_result = [float(x) for x in measure_result]
            return measure_result

    def get_voltage_current_both_channels(self):
        measure_results = self.get_all_measurements_both_channels()
        return measure_results[0], measure_results[1], measure_results[6], measure_results[7]


    
    def get_ch1_voltage_and_current(self):
        
        # Attempt to get all measurements
        measure_result = self.get_all_measurements(channel = 1)
        
        # If measuring caused an error, return sys.maxsize as a bad value
        if measure_result is None:
            return sys.maxsize, sys.maxsize
        else:
            return measure_result[0], measure_result[1]
    
    
    def get_ch2_voltage_and_current(self):
        measure_result = self.get_all_measurements(channel = 2)
        return measure_result[0], measure_result[1]
    
    def get_both_channel_voltage(self):
        results = self.connection.query(":meas:volt? (@1,2)")[:-1]
        split_results = results.split(",")
        return float(split_results[0]), float(split_results[1])


    def fetchBothChannel(self):
        results = self.connection.query(":fetch? (@1,2)")[:-1]
        split_results = results.split(",")
        split_results = [float(x) for x in split_results]
        return split_results[0], split_results[1], split_results[6], split_results[7]

    def readBothChannel(self):
        results = self.connection.query(":read? (@1,2)")[:-1]
        split_results = results.split(",")
        split_results = [float(x) for x in split_results]
        return split_results[0], split_results[1], split_results[6], split_results[7]


    def get_both_channel_current(self):
        results = self.connection.query(":meas:curr? (@1,2)")[:-1]
        split_results = results.split(",")
        return float(split_results[0]), float(split_results[1])    
    
    def get_ch1_power(self):
        voltage, current = self.get_ch1_voltage_and_current()
        return voltage*current
    def get_ch2_power(self):
        voltage, current = self.get_ch2_voltage_and_current()
        return voltage*current
    
    def get_voltage_array(self, channel = 1):
        voltage_array = self.connection.query(f":FETC:ARR:VOLT? (@{channel})")
        voltage_array_split = voltage_array.split(",")
        voltage_array = [float(x) for x in voltage_array_split]
        return voltage_array
    def get_current_array(self, channel = 1):
        current_array = self.connection.query(f":FETC:ARR:CURR? (@{channel})")
        current_array_split = current_array.split(",")
        current_array = [float(x) for x in current_array_split]
        return current_array
    
    
    def set_ch1_4_wire(self):
        self.connection.write(":SENS:REM ON")
        
    def set_ch2_4_wire(self):
        self.connection.write(":SENS2:REM ON")
    
    def set_ch1_2_wire(self):
        self.connection.write(":SENS:REM OFF")

    def set_ch2_2_wire(self):
        self.connection.write(":SENS2:REM OFF")
        
    def set_ch1_floating(self):
        self.connection.write(":OUTP:LOW FLO")
    
    def set_ch2_floating(self):
        self.connection.write(":OUTP2:LOW FLO")
        
    def set_floating(self, channel = 1):
        self.connection.write(f"OUTP{channel}:LOW FLO")
    
    def find_best_current(self, goal):      
        # The best current will start out as the minimum value (it can only get larger)
        best_current = -sys.maxsize
        
        # The best power will start out as the maximum value (it can only get smaller)
        best_power = sys.maxsize
        
        # Set the curr_current to near the goal
        curr_current = goal / 2
        
        for i in range(0, 10000):
            
            # Increase the current
            curr_current += 0.01 
            self.set_ch1_current(curr_current)
            time.sleep(0.01)
            
            # Calculate the power
            power = self.get_ch1_power()

            # If we are closer to our goal, update our best values 
            if abs(goal - power) < best_power:
                best_power = goal-power
                best_current = curr_current
            
            # If we've moved too far, exit
            if (power > goal * 1.05):
                # Reduce the current to allow for fine grain tuning
                curr_current =  best_current - 0.1
                break
            
            if curr_current > goal + 0.5:
                # Reduce the current to allow for fine grain tuning
                curr_current = best_current - 0.1
                break
                
        # self.set_ch1_current(best_current)

        for i in range(0, 10000):
           
            # Increase the current
            curr_current += 0.001
            self.set_ch1_current(curr_current)
            time.sleep(0.01)
            
            # Calculate the power
            power = self.get_ch1_power()
            
            # If we are closer to our goal, update our best values 
            if abs(goal - power) < best_power:
                best_power = goal-power
                best_current = curr_current
           
            # If we've moved too far, exit    
            if (power > goal * 1.05) or (curr_current > goal + 0.5):
                break
            
        print(f"Best Current {round(best_current, 4)}A")
        self.set_ch1_current(best_current)

    def check_for_errors(self, show = False):
        try:
            
            query_response = self.connection.query(":SYST:ERR:ALL?")
            query_response_split = query_response.split(",")
            error_code = float(query_response_split[0])
            
            if (error_code == 0):
                if show: print("No Errors")
                return True
            else:
                if show: 
                    for i, error in enumerate(query_response_split):
                        if i % 2:
                            print(error)
                        else:
                            print(f"Error Code: {error}", end = ', ')
        except:
            print("Error checking for errors...")
            return False

        return True
    
    
    # GRAPH, DUAL, SING1, SING2
    def change_display(self, mode = "DUAL"):
        self.connection.write(":DISP:ENAB ON")
        self.connection.write(":DISP:VIEW " + mode)

    # TODO have user enter the save directory
    def get_screen_image(self, directory = "good_5"):
        self.connection.write(":DISP:ENAB ON")
        self.connection.write(":HCOP:SDUM:FORM JPG")
        self.connection.write("*OPC?")
        self.connection.write(":HCOP:SDUM:DATA?")
        
        imgData = self.connection.read_raw(1024 * 1024)  # get the raw picture from the buffer
    
        # TODO maybe change to with open?
        try:
            file = open(f"{directory}.JPG", "wb")
            file.write(imgData[8:])
            file.close()
        except IOError as ex:
            print(f"Could not write picture to {directory}.JPG file.")
        except Exception as ex:
            print("Unkown error caused the picture saving to fail...")
       
    def set_current_sens_range(self, current, channel = 1):
        # If we are setting a current range, then we dont want an auto range
        self.connection.write(f":SENS{channel}:CURR:RANG:AUTO OFF")
        self.connection.write(f":SENS{channel}:CURR:RANG {current}")
    
    def set_voltage_source_range(self, voltage, channel = 1):
        self.connection.write(f":SOUR{channel}:VOLT:RANG:AUTO OFF")
        self.connection.write(f":SOUR{channel}:VOLT:RANG {voltage}")

    def turn_on_high_capacitance_mode(self, channel = 1):
        self.connection.write(f"OUTP{channel}:HCAP ON")
    def turn_off_high_capacitance_mode(self, channel = 1):
        self.connection.write(f"OUTP{channel}:HCAP OFF")   
    def turn_on_high_z(self, channel = 1):
        self.connection.write(f"OUTP{channel}:OFF:MODE HIZ")   
    def turn_on_4_wire(self, channel = 1):
        self.connection.write(f":SENS{channel}:REM ON")  
    def set_NPLC(self, NPLC, channel = 1):
        self.connection.write(f":SENS{channel}:CURR:NPLC {NPLC}")
        
        
    def trigger(self):
        self.connection.write(":TRIG:ACQ (@1,2)")

    def set_measure_count(self, amount, channel = 1):
        self.connection.write(f":TRIG{channel}:COUN {amount}")

    def turn_on_pulse(self, channel = 1):
        self.connection.write(f"SOUR{channel}:FUNC PULS")

    def set_pulse_peak(self, channel = 1, function = "CURR", peak = 0):
        self.connection.write(f"SOUR{channel}:{function}:TRIG {peak}")

    def set_pulse_width(self, width):
        self.connection.write(f"SOURce:PULSe:WIDTh {width}")

    def set_measure_delay(self, channel = 1, value = 0):
        self.connection.write(f":TRIG{channel}:ACQ:DEL {value}")

    def set_trigger_period(self, period):
        self.connection.write(f":TRIG:TIM {period}")

