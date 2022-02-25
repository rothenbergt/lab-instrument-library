#     ____
#    / __ \___  ____  ___  _________ ______
#   / /_/ / _ \/ __ \/ _ \/ ___/ __ `/ ___/
#  / _, _/  __/ / / /  __(__  ) /_/ (__  )
# /_/ |_|\___/_/ /_/\___/____/\__,_/____/
# ----------------------------------------
#               SMU Library
#               Keithly 238
#               Keithly 228

from LibraryTemplate import LibraryTemplate
from typing import List
import inspect

class Keithly228(LibraryTemplate):
    
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
        
        
# smu2 = Keithly238("GPIB0::1::INSTR", identify = False)
# smu = Keithly228("GPIB0::11::INSTR", identify = False)

# smu2.operate()
# smu.operate()

# # time.sleep(2)
# # print(smu2.getData())
# # print(smu.getData())
# # smu2.standby()
# # smu.standby()
        
# smu.setCurrent(5)

# v = 0.6

# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import time

# df = pd.DataFrame()

# watt = 0

# while watt <= 3:
#     smu.setVoltage(v)
#     time.sleep(3)
#     voltage, current = smu.getData()
#     watt = voltage * current
#     v += 0.05
#     print(f"The voltage is {voltage}V The current is {current}A Power is {voltage * current}W")
    
#     # Add to dataframe
#     new_row = { 'Voltage (V)': voltage,
#                 'Current (A)': current,
#                 'Watt (W)': voltage * current
#     }
    
#     df = df.append(new_row, ignore_index=True)
# smu.standby()
# df.to_csv("currentWattTest.csv")


# x = df['Voltage (V)']
# y = df['Watt (W)']
# a, b, c, d, e = np.polyfit(x, y, deg=4)

# voltageSeries = (np.arange(0.6, max(x), 0.0001))

# watt_est = a * voltageSeries **4 + b * voltageSeries **3 + c * voltageSeries**2 + d * voltageSeries + e
# print(watt_est)  


# plt.xlabel('Voltage')
# plt.ylabel('Watt')
# plt.plot(voltageSeries, watt_est)
# plt.plot(x, y)


# print(zip(voltageSeries, watt_est))

# watt_est = list(watt_est)
# myNumber = 0.5

# cloesetWatt = min(watt_est, key=lambda x:abs(x-myNumber))
# index = watt_est.index(cloesetWatt)

# # print(f"The closest watt is {cloesetWatt} at index {index}. The voltage is {voltageSeries[index]}")

# smu.setVoltage(voltageSeries[index])
# smu.operate()

# plt.show()

# watts = [0.5, 1, 1.5, 2, 2.5, 3]

# for watt in watts:
#     cloesetWatt = min(watt_est, key=lambda x:abs(x-watt))
#     index = watt_est.index(cloesetWatt)
#     smu.setVoltage(voltageSeries[index])

#     print(f"The closest watt is {cloesetWatt} at index {index}. The voltage is {voltageSeries[index]}")

#     errorTotal = 0
#     for i in range(0, 20):
#         voltage, current = smu.getData()
#         calc_watt = voltage * current
#         # print(f"The voltage is {voltage}V The current is {current}A Power is {watt}W ... Error {((0.5-watt) / 0.5) * 100 }%")
#         errorTotal += ((watt-calc_watt) / watt) * 100

#     print(f"Average error for {watt} is {errorTotal / 100}%")

# time.sleep(1)
# smu.standby()

