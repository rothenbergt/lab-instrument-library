from Supply import Supply
from Multimeter import Multimeter

voltage_to_set = 9.05


# supply = Supply('GPIB0::4::INSTR')

# supply.select_output1()
# supply.set_voltage(voltage_to_set)
# supply.enable_output()

mult = Multimeter("GPIB0::5::INSTR")
mult = Multimeter("USB0::0x05E6::0x2110::8015791::INSTR")


print(mult.read_function(function = 'VOLTage:AC'))

# mult.turn_off_auto_range()
# voltage_range = mult.set_voltage_range(4)

# print(f"The range is {voltage_range}")

# # print(mult.measure_voltage_AC())

# voltage = mult.read_voltage()

# new_voltage = voltage_to_set

# while (round(voltage, 2) != 9):
#     new_voltage = new_voltage - 0.001
#     supply.set_voltage(new_voltage)
#     voltage = mult.read_voltage()

#     print(f"The voltage is now {round(voltage, 2)}")


print(mult.read_voltage())
print(mult.read_current())
print(mult.read_current_AC())
print(mult.read_resistance())
print(mult.get_error())

