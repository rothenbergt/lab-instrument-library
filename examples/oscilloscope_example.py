"""
Example demonstrating how to use the Oscilloscope class.

This example shows how to connect to an oscilloscope, configure it,
capture waveforms, and save screenshots.
"""

from lab_instrument_library import Oscilloscope
import matplotlib.pyplot as plt
import numpy as np
import os

def main():
    """Run the oscilloscope example."""
    # Create an oscilloscope instance - replace with your oscilloscope's address
    print("Connecting to oscilloscope...")
    oscilloscope = Oscilloscope("GPIB0::7::INSTR")
    
    # Stop any ongoing acquisition
    print("Stopping acquisition...")
    oscilloscope.stop()
    
    # Configure the oscilloscope
    print("\nConfiguring oscilloscope...")
    oscilloscope.set_channel_label(1, "Signal")  # Updated to use snake_case
    oscilloscope.setVerticalScale(1, 0.5)  # 0.5V/division
    oscilloscope.changeGraticule("GRID")
    oscilloscope.changeWaveFormIntensity(80)
    
    # Start acquisition
    print("Starting acquisition...")
    oscilloscope.run()
    
    # Display a message on the oscilloscope
    oscilloscope.show_message("Controlled by Python")
    
    # Capture a waveform
    print("\nCapturing waveform data...")
    time_data, voltage_data = oscilloscope.acquire(1, show=False)
    
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
    oscilloscope.save_image(screenshot_filename)  # Updated to use snake_case
    print(f"Screenshot saved as {screenshot_filename}")
    
    # Remove the message
    oscilloscope.remove_message()  # Updated to use snake_case
    
    # Close the connection
    print("\nClosing connection...")
    oscilloscope.close()
    print("Connection closed.")

if __name__ == "__main__":
    main()
