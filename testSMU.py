from Supply import Supply
from Multimeter import Multimeter
import sys
from SMU import SMU
import time


smu = SMU("USB0::0x0957::0xCE18::MY51141974::INSTR")

smu.ch1_on()
smu.ch2_on()

time.sleep(2)

smu.ch1_off()
smu.ch2_off()

smu.set_mode("VOLT")

time.sleep(2)

smu.set_ch1_mode("CURR")
smu.set_ch2_mode("CURR")

time.sleep(2)

smu.set_ch1_mode("VOLT")
smu.set_ch2_mode("VOLT")

smu.set_mode_voltage_limit(channel = 1, mode = "VOLT", voltage = 5, limit = 0.05)
smu.set_mode_voltage_limit(channel = 2, mode = "VOLT", voltage = 5, limit = 0.05)

print(smu.get_function(1))
print(smu.get_function(2))

smu.ch1_on()
smu.ch2_on()

time.sleep(2)

smu.ch1_off()
smu.ch2_off()

smu.set_mode_current_limit(channel = 1, mode = "CURR", current = 0.05, limit = 5)
smu.set_mode_current_limit(channel = 2, mode = "CURR", current = 0.05, limit = 5)

print(smu.get_function(1))
print(smu.get_function(2))

smu.ch1_on()
smu.ch2_on()

time.sleep(2)


print(smu.get_voltage(1))
print(smu.get_voltage(2))

print(smu.get_ch1_voltage())
print(smu.get_ch2_voltage())

smu.ch1_off()
smu.ch2_off()
