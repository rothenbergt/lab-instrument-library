"""
Example demonstrating how to use the Multimeter class.

This example shows how to connect to a multimeter, make various measurements,
and how to handle different measurement commands.
"""

import time

from pylabinstruments import Multimeter


def main():
    """Run the multimeter example."""
    # Create a multimeter instance - replace with your multimeter's address
    print("Connecting to multimeter...")
    multimeter = Multimeter("GPIB0::15::INSTR")

    # Make various measurements
    print("\nMaking various measurements:")

    # Read the DC voltage
    voltage = multimeter.read_voltage()
    print(f"DC Voltage: {voltage:.6f} V")

    # Read the AC voltage
    voltage_ac = multimeter.read_voltage_ac()
    print(f"AC Voltage: {voltage_ac:.6f} V")

    # Measure the resistance
    resistance = multimeter.measure_resistance()
    print(f"Resistance: {resistance:.6f} Ω")

    # Set a specific function and make a measurement
    multimeter.set_function("VOLT")
    print("\nManually setting function to VOLT...")
    time.sleep(1)
    voltage = multimeter.measure_voltage()
    print(f"Measured voltage: {voltage:.6f} V")

    # Demonstrate the difference between read, measure, and fetch
    print("\nDemonstrating different measurement commands:")
    print("1. measure_voltage(): Configures, triggers, and returns (all-in-one)")
    voltage = multimeter.measure_voltage()
    print(f"   Result: {voltage:.6f} V")

    print("2. read_voltage(): Triggers and returns without reconfiguration")
    voltage = multimeter.read_voltage()
    print(f"   Result: {voltage:.6f} V")

    print("3. fetch_voltage(): Returns the last reading without triggering")
    voltage = multimeter.fetch_voltage()
    print(f"   Result: {voltage:.6f} V")

    # Close the connection
    print("\nClosing connection...")
    multimeter.close()
    print("Connection closed.")


if __name__ == "__main__":
    main()
