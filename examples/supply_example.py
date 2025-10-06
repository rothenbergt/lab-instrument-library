"""
Example demonstrating how to use the Supply class.

This example shows how to connect to a power supply, set voltage and current,
and make measurements.
"""

import time

from lab_instrument_library import Supply


def main():
    """Run the power supply example."""
    # Create a supply instance - replace with your supply's address
    print("Connecting to power supply...")
    supply = Supply("GPIB0::5::INSTR")

    # Get initial state
    print("\nChecking initial state...")
    output_state = supply.get_output_state()
    print(f"Output state: {output_state}")

    # Set voltage and current
    print("\nSetting voltage to 3.3V with 0.1A current limit...")
    supply.set_voltage(3.3, 0.1)

    # Enable output
    print("Enabling output...")
    supply.enable_output()
    time.sleep(1)  # Wait for output to stabilize

    # Make measurements
    print("\nMaking measurements:")
    voltage = supply.measure_voltage()
    current = supply.measure_current()
    print(f"Measured voltage: {voltage:.6f} V")
    print(f"Measured current: {current:.6f} A")

    # Try different voltages
    print("\nSweeping through different voltages:")
    for volt in [1.0, 1.5, 2.0, 2.5, 3.0]:
        supply.set_voltage(volt, 0.1)
        time.sleep(0.5)  # Wait for output to stabilize
        voltage = supply.measure_voltage()
        current = supply.measure_current()
        print(f"Set: {volt:.1f}V, Measured: {voltage:.3f}V, {current*1000:.2f}mA")

    # Disable output
    print("\nDisabling output...")
    supply.disable_output()

    # Close the connection
    print("Closing connection...")
    supply.close()
    print("Connection closed.")


if __name__ == "__main__":
    main()
