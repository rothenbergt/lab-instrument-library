# Import time to allow for delays
import time

# from Supply.py import the Supply class
from Supply import Supply

# from Multimeter.py import the Multimeter clas
from Multimeter import Multimeter

# Imported numpy for use of arange
import numpy as np

# Imported pandas for use of DataFrame
import pandas as pd

# Instantiate the objects with a given GPIB address
supply = Supply("GPIB0::5::INSTR")
multimeter = Multimeter("GPIB0::3::INSTR")

# The maximum supply voltage for Richtek is 36V, for TI/Renesas 40V
maximum_supply_voltage = 36

# The minimum supply voltage for 5V is 6V, etc
minimum_supply_voltage = 6

# Step size between each voltage is given at 0.250V
step_size = 0.5

# Create a supply voltage list using the given variables
supply_voltage_list = np.arange(minimum_supply_voltage, (maximum_supply_voltage + step_size), step_size)

# Create an empty DataFrame which will hold all data
df = pd.DataFrame()

# For each supply voltage in the list
for supply_voltage in supply_voltage_list:

    # Set the supply
    supply.set_voltage(supply_voltage)
    supply.enable_output()

    # Wait a bit
    time.sleep(0.2)
    
    # Record from multimeter
    output_voltage = multimeter.measure_voltage()

    # Build the row of data
    temp_row = {'Output Voltage (V)': output_voltage,
                'Supply Voltage (V)': supply_voltage}   

    # Append it
    df = df.append(temp_row, ignore_index=True)
    
    # Print it
    print(df)

    # Save it
    df.to_csv("G:\Analog Solutions PL\Applications Loading\Tyler Rothenberg\donTest\don_test.csv")

# Turn Off Supply
supply.disable_output()

# Close Instruments
supply.close()
multimeter.close()


