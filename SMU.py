from LibraryTemplate import LibraryTemplate
import numpy as np
import time
import sys

class SMU(LibraryTemplate):
    
    OVERFLOW = 9.223372e+18
    
    def reset(self):
        self.connection.write("*RST")
        self.connection.write("*CLS")
    
    def ch_on(self, channel = 1):
        self.connection.write(f"OUTP{channel} ON")
    def ch1_on(self):
        self.connection.write(":OUTP ON")
    def ch2_on(self):
        self.connection.write(":OUTP2 ON")
    def ch_off(self, channel = 1):
        self.connection.write(f"OUTP{channel} OFF")
    def ch1_off(self):
        self.connection.write(":OUTP OFF")
    def ch2_off(self):
        self.connection.write(":OUTP2 OFF")
        
    def initiate_all(self):
        self.connection.write(f":INIT:ACQ (@1,2)")
    def initiate_ch1(self):
        self.connection.write(f":INIT:ACQ (@1)")
    def initiate_ch2(self):
        self.connection.write(f":INIT:ACQ (@2)")      
        
        
    def set_ch1_mode(self, ch = 1, mode = "VOLT"):
        self.connection.write(f":SOUR:FUNC:MODE {mode}")
    def set_ch2_mode(self, ch = 1, mode = "VOLT"):
        self.connection.write(f":SOUR2:FUNC:MODE {mode}")  
    def set_mode(self, channel = 1, mode = "VOLT"):
        self.connection.write(f":SOUR{channel}:FUNC:MODE {mode}")
        
    
    def set_ch1_current(self, current = 0.1):
        self.connection.write(f":SOUR:CURR {current}")
    def set_ch2_current(self, current = 0.1):
        self.connection.write(f":SOUR2:CURR {current}")
    def set_ch1_voltage(self, voltage = 1):
        self.connection.write(f":SOUR:VOLT {voltage}")
    def set_ch2_voltage(self, voltage = 1):
        self.connection.write(f":SOUR2:VOLT {voltage}")
    def set_voltage(self, channel = 1, voltage = 0):
        self.connection.write(f":SOUR{channel}:VOLT {voltage}")
    def set_current(self, channel = 1, current = 0):
        self.connection.write(f":SOUR{channel}:CURR {current}")
        
    def set_mode_voltage_limit(self, channel = 1, mode = "VOLT", voltage = 0, limit = 0):
        self.set_mode(channel, mode)
        self.set_voltage(channel, voltage)
        self.set_current_limit(channel, limit)
    def set_mode_current_limit(self, channel = 1, mode = "CURR", current = 0, limit = 0):
        self.set_mode(channel, mode)
        self.set_current(channel, current)
        self.set_voltage_limit(channel, limit)
        
    

    def set_ch1_voltage_limit(self, voltage = 0):
        if self.connection.query(":SOUR:FUNC:MODE?")[:-1] == "CURR":
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


    def get_ch1_voltage(self):
        return float(self.connection.query(":meas:volt?"))
    def get_ch2_voltage(self):
        return float(self.connection.query(":meas:volt? (@2)"))
    def get_voltage(self, channel = 1):
        return float(self.connection.query(f":meas:volt? (@{channel})"))
    
    def get_ch1_current(self):
        return float(self.connection.query(":meas:curr?"))
    def get_ch2_current(self):
        return float(self.connection.query(":meas:curr? (@2)"))
    def get_current(self, channel = 1):
        return float(self.connection.query(f":meas:curr? (@{channel})"))
    
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
        # self.connection.write(":TRIG:ACQ:SOUR AINT")
        # self.connection.write(":TRIG2:ACQ:SOUR AINT")
        self.connection.write(":TRIG:ACQ (@1,2)")

        # self.connection.write(":TRIG:ACQ:SOUR BUS")
        # self.connection.write(":TRIG2:ACQ:SOUR BUS")

        # time.sleep(0.2)

        # print("sending trigger")

        # self.connection.write("*TRG")



    def set_measure_count(self, amount, channel = 1):
        self.connection.write(f":TRIG{channel}:COUN {amount}")

    def turnOnPulse(self, channel = 1):
        self.connection.write(f"SOUR{channel}:FUNC PULS")

    def setPulsePeak(self, channel = 1, function = "CURR", peak = 0):
        self.connection.write(f"SOUR{channel}:{function}:TRIG {peak}")

    def setPulseWidth(self, width):
        self.connection.write(f"SOURce:PULSe:WIDTh {width}")

    def setMeasureDelay(self, channel = 1, value = 0):
        self.connection.write(f":TRIG{channel}:ACQ:DEL {value}")

    def setTriggerPeriod(self, period):
        self.connection.write(f":TRIG:TIM {period}")


# mALoads = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]

# s = SMU("GPIB0::28::INSTR")

# # Set channel 1 to be a current source
# s.set_mode_current_limit(channel = 1, mode = "CURR", current = 0, limit = 10)

# # Set channel 1 to pulse
# s.turnOnPulse()

# # Pulse width should be long enough that the part is fully regulating
# s.setPulseWidth(width = 10E-3)
# s.setPulsePeak(peak = 50E-3)

# # Set channel 2 to be the supply voltage 
# s.set_mode_voltage_limit(channel = 2, mode = "VOLT", voltage = 5, limit = 200E-3)

# # Measure Delay on both channels should be half the pulse width? Or at least where we are regulating
# s.setMeasureDelay(channel = 1, value = 5E-3)
# s.setMeasureDelay(channel = 2, value = 5E-3)

# s.ch1_on()
# s.ch2_on()

# # Set channel 2 measure speed to long, get quiescent current with no load.
# s.set_NPLC(channel = 2, NPLC = 100)

# quiescentCurrentnoLoad = s.get_voltage_current_both_channels()[-1]

# # Set channel 2 measure speed to short (0.01), get quiescent current with pulsed load
# s.set_NPLC(channel = 2, NPLC = 0.01)

# s.trigger()

# quiescentCurrentLoad = s.readBothChannel()[1]

# print(f"Quiescent Current no Load: {quiescentCurrentnoLoad * 1E6} uA")
# print(f"Quiescent Current Load: {quiescentCurrentLoad * 1E3} mA")


# for load in mALoads:
#     s.setPulsePeak(peak = load*1E-3)
#     time.sleep(5)

#     # Set channel 2 measure speed to short (0.01), get quiescent current with pulsed load
#     s.set_NPLC(channel = 2, NPLC = 0.01)

#     quiescentCurrentLoad = s.readBothChannel()[1]

#     print(f"Quiescent Current Load {load}mA: {quiescentCurrentLoad * 1E3} mA")



# s.setPulseWidth(11E-3)



# s.get_screen_image()
# s.get_voltage_array()
# s.write("SOURCE:CURRENT:TRANSIENT:SPEED FAST")
# s.turn_on_4_wire()
# s.check_for_errors(True)
# s.set_current_sens_range(1)
# s.set_voltage_source_range(200)

# s2 = SMU("GPIB0::6::INSTR")
# s2.turn_on_high_capacitance_mode(2)

# s2.check_for_errors()

# time.sleep(5)
# s2.turn_off_high_capacitance_mode(2)

# s2.check_for_errors()
