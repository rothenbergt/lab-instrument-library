from Supply import Supply
from Multimeter import Multimeter

# supply = Supply('GPIB0::5::INSTR')

# supply.select_output1()
# supply.set_voltage(9)

# supply.select_output2()
# supply.set_voltage(9)

# supply.enable_output()

mult = Multimeter("GPIB0::3::INSTR")

print(mult.measure_voltage_AC())

print(mult.measure_voltage())

print(mult.get_error())