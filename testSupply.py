from Supply import Supply
from Multimeter import Multimeter
import sys
voltage_to_set = 9.05


# supply = Supply('GPIB0::4::INSTR')

# supply.select_output1()
# supply.set_voltage(voltage_to_set)
# supply.enable_output()

mult = Multimeter("USB0::0x05E6::0x2110::8015791::INSTR")
mult = Multimeter("GPIB0::5::INSTR")


print(mult.read_function(function = 'VOLTage:DC'))
mult.turn_off_auto_range()
voltage_range = mult.set_voltage_range(4)

while True:
    print(mult.get_auto_range_state())
    res = mult.read_voltage_AC()
    print(res)
    


# print(f"The range is {voltage_range}")

# # print(mult.measure_voltage_AC())

# voltage = mult.read_voltage()

# new_voltage = voltage_to_set

# while (round(voltage, 2) != 9):
#     new_voltage = new_voltage - 0.001
#     supply.set_voltage(new_voltage)
#     voltage = mult.read_voltage()

#     print(f"The voltage is now {round(voltage, 2)}")


# print(mult.read_voltage())
# print(mult.read_current())
# print(mult.read_current_AC())
# print(mult.read_resistance())

# mult.set_function("VOLTage:DC")

# mult.initiate()

# mult.set_function("VOLTage:AC")
# mult.initiate()

# print(mult.fetch_voltage())
# print(mult.fetch_voltage_AC())

# print(mult.fetch_current())
# print(mult.fetch_current_AC())

# print(mult.fetch_resistance())
print(mult.get_error())

# print(sys.maxsize)