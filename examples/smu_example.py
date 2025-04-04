"""
Simple example demonstrating how to use the Source Measure Unit (SMU) classes.

This example shows how to connect to a Keysight B2902A SMU,
configure it as a voltage source, and perform basic measurements.
"""

from lab_instrument_library.smu import KeysightB2902A
import matplotlib.pyplot as plt
import numpy as np
import time

def main():
    """Run the SMU example."""
    # Create an SMU instance - replace with your SMU's address
    print("Connecting to Keysight B2902A SMU...")
    smu = KeysightB2902A("GPIB0::23::INSTR")
    
    # Reset the instrument to a known state
    print("Resetting instrument...")
    smu.reset()
    time.sleep(1)  # Give the instrument time to reset
    
    # Configure as voltage source
    print("\nConfiguring as voltage source...")
    channel = 1
    voltage = 3.3  # 3.3 Volts
    current_limit = 0.1  # 100 mA compliance
    smu.set_voltage(voltage, current_limit, channel)
    
    # Enable the output
    print(f"Enabling output on channel {channel}...")
    smu.enable_output(channel)
    
    # Take measurements
    print("\nTaking measurements...")
    time.sleep(0.5)  # Allow time to settle
    
    measurements = smu.get_all_measurements(channel)
    
    print(f"Voltage: {measurements['voltage']:.6f} V")
    print(f"Current: {measurements['current']*1000:.6f} mA")
    print(f"Power: {measurements['power']*1000:.6f} mW")
    print(f"Resistance: {measurements['resistance']:.2f} Ω")
    
    # Perform a simple voltage sweep
    print("\nPerforming voltage sweep (0V to 5V)...")
    start_voltage = 0
    stop_voltage = 5
    steps = 11
    
    voltages = np.linspace(start_voltage, stop_voltage, steps)
    currents = []
    
    for v in voltages:
        smu.set_voltage(v, current_limit, channel)
        time.sleep(0.1)  # Wait for settling
        curr = smu.measure_current(channel)
        currents.append(curr)
        print(f"  {v:.1f}V: {curr*1000:.3f} mA")
    
    # Disable the output
    print("\nDisabling output...")
    smu.disable_output(channel)
    
    # Plot the IV curve
    plt.figure(figsize=(8, 6))
    plt.plot(voltages, np.array(currents)*1000, 'bo-')  # Convert to mA
    plt.title("IV Curve")
    plt.xlabel("Voltage (V)")
    plt.ylabel("Current (mA)")
    plt.grid(True)
    
    # Save the plot
    plot_filename = "smu_iv_curve.png"
    plt.savefig(plot_filename)
    print(f"IV curve plot saved as {plot_filename}")
    
    # Optionally show the plot
    # plt.show()
    
    # Close the connection
    print("\nClosing connection...")
    smu.close()
    print("Connection closed.")

if __name__ == "__main__":
    main()
