"""
Example demonstrating how to use the SMU class.

This example shows how to connect to an SMU, configure channels,
set operating modes, and perform measurements.
"""

from lab_instrument_library import SMU
import time

def main():
    """Run the SMU example."""
    print("Connecting to SMU...")
    smu = SMU("USB0::0x0957::0xCE18::MY51141974::INSTR")

    print("\nSetting output to high impedance mode...")
    smu.set_output_hiz(1)
    smu.set_output_hiz(2)

    print("\nEnabling channels...")
    smu.ch1_on()
    smu.ch2_on()
    
    time.sleep(2)
    
    print("\nSetting output to normal mode...")
    smu.set_output_normal(1)
    smu.set_output_normal(2)
    
    print("\nDisabling channels...")
    smu.ch1_off()
    smu.ch2_off()
    
    print("\nTesting different operating modes...")
    # Switch to voltage mode, channel 1
    smu.set_mode(1, "VOLT")
    time.sleep(1)
    
    # Switch to current mode, both channels
    smu.set_ch1_mode("CURR")
    smu.set_ch2_mode("CURR")
    time.sleep(1)
    
    # Switch back to voltage mode, both channels
    smu.set_ch1_mode("VOLT")
    smu.set_ch2_mode("VOLT")
    
    # Configure voltage source with current limit
    print("\nConfiguring voltage source with current limit...")
    smu.set_mode_voltage_limit(channel=1, mode="VOLT", voltage=5, limit=0.05)
    smu.set_mode_voltage_limit(channel=2, mode="VOLT", voltage=5, limit=0.05)
    
    # Check the function settings
    print(f"Channel 1 function: {smu.get_function(1)}")
    print(f"Channel 2 function: {smu.get_function(2)}")
    
    # Enable outputs
    print("\nEnabling outputs...")
    smu.ch1_on()
    smu.ch2_on()
    time.sleep(2)
    
    # Measure output
    ch1_v = smu.get_voltage(1)
    ch2_v = smu.get_voltage(2)
    print(f"Channel 1 voltage: {ch1_v}V")
    print(f"Channel 2 voltage: {ch2_v}V")
    
    # Get all measurements
    print("\nGetting all measurements:")
    print(f"Channel 1: {smu.get_all_measurements(1)}")
    print(f"Channel 2: {smu.get_all_measurements(2)}")
    
    # Disable outputs when done
    print("\nDisabling outputs...")
    smu.ch1_off()
    smu.ch2_off()
    
    print("\nClosing connection...")
    smu.close()
    print("Connection closed.")

if __name__ == "__main__":
    main()
