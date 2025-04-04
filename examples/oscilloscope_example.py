"""
Simple example demonstrating how to use the Tektronix oscilloscope classes.

This example shows how to connect to a TDS2000 series oscilloscope,
configure it, capture a waveform, and save a screenshot.
"""

from lab_instrument_library.oscilloscope import TektronixTDS2000
import matplotlib.pyplot as plt
import numpy as np
import os

def main():
    """Run the oscilloscope example."""
    # Create an oscilloscope instance - replace with your oscilloscope's address
    print("Connecting to oscilloscope...")
    scope = TektronixTDS2000("GPIB0::7::INSTR")
    
    # Stop any ongoing acquisition
    print("Stopping acquisition...")
    scope.stop()
    
    # Configure the oscilloscope
    print("\nConfiguring oscilloscope...")
    scope.set_channel_label(1, "Signal")
    scope.set_vertical_scale(1, 0.5)  # 0.5V/division
    scope.change_graticule("GRID")
    scope.change_waveform_intensity(80)
    
    # Start acquisition
    print("Starting acquisition...")
    scope.run()
    
    # Display a message on the oscilloscope
    scope.show_message("Controlled by Python")
    
    # Capture a waveform
    print("\nCapturing waveform data...")
    time_data, voltage_data = scope.acquire(1, show=False)
    
    if len(time_data) > 0 and len(voltage_data) > 0:
        # Plot the captured data
        print(f"Captured {len(time_data)} points")
        plt.figure(figsize=(10, 6))
        plt.plot(time_data, voltage_data)
        plt.title("Captured Waveform")
        plt.xlabel("Time (s)")
        plt.ylabel("Voltage (V)")
        plt.grid(True)
        
        # Save the plot
        plot_filename = "captured_waveform.png"
        plt.savefig(plot_filename)
        print(f"Plot saved as {plot_filename}")
        
        # Optionally show the plot
        # plt.show()
    else:
        print("Failed to capture waveform data")
    
    # Save a screenshot of the oscilloscope display
    print("\nSaving oscilloscope screenshot...")
    screenshot_filename = "oscilloscope_screenshot.png"
    scope.save_image(screenshot_filename)
    print(f"Screenshot saved as {screenshot_filename}")
    
    # Remove the message
    scope.remove_message()
    
    # Close the connection
    print("\nClosing connection...")
    scope.close()
    print("Connection closed.")

if __name__ == "__main__":
    main()
