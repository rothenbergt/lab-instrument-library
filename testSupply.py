from Supply import Supply

supply = Supply('GPIB0::5::INSTR')

supply.select_output1()
supply.set_voltage(9)

supply.select_output2()
supply.set_voltage(9)

supply.enable_output()