# Lab Instrument Library

A Python library for interfacing with various laboratory instruments through GPIB/VISA connections.

## Overview

The Lab Instrument Library provides a unified interface to control common laboratory instruments from different manufacturers while abstracting away device-specific command syntax. It aims to simplify lab automation by providing consistent methods for common operations.

## Instruments Supported

### Multimeters

- HP 34401A
- Keithley 2000
- Keithley 2110
- Tektronix DMM4050

### Power Supplies

- Agilent E3631A
- Agilent E3632A
- Keysight E3649A
- Keysight E36313A
- Keysight E36234A

### Source Measure Units (SMUs)

- Keysight B2902A
- Keithley 228
- Keithley 238

### Oscilloscopes

- Tektronix series with GPIB support

### Function Generators

- Tektronix AFG3000 series

### Network Analyzers

- Agilent/Keysight E5061B

### Temperature Instruments

- Thermocouples
- Thermometers
- Thermonics temperature forcing systems (T-2500SE, T-2420, X-Stream 4300)

## Installation

### Requirements

- Python 3.6+
- PyVISA
- PyVISA-py (for non-NI VISA implementations)
- An appropriate VISA backend (e.g., National Instruments VISA, Keysight VISA)

### Local Installation

```bash
# Clone the repository
git clone https://github.com/rothenbergt/lab-instrument-library.git

# Navigate to the project directory
cd lab-instrument-library

# Install in development mode
pip install -e .
```

## Usage Examples

### Multimeter

```python
from lab_instrument_library import Multimeter

# Connect to a multimeter using its VISA address
multimeter = Multimeter("GPIB0::15::INSTR")

# Read voltage measurement
voltage = multimeter.read_voltage()
print(f"Measured voltage: {voltage} V")

# Change measurement function to current
multimeter.set_function("CURR")

# Read current measurement
current = multimeter.read_current()
print(f"Measured current: {current} A")

# Clean up resources when finished
multimeter.close()
```

### Power Supply

```python
from lab_instrument_library import Supply

# Connect to a power supply
supply = Supply("GPIB0::5::INSTR")

# Set voltage and current limit
supply.set_voltage(3.3, 0.5)  # 3.3V with 0.5A current limit

# Enable the output
supply.enable_output()

# Measure the actual output
voltage = supply.measure_voltage()
current = supply.measure_current()
print(f"Output: {voltage:.3f}V, {current:.3f}A")

# Disable the output before disconnecting
supply.disable_output()
supply.close()
```

### Oscilloscope

```python
from lab_instrument_library import Oscilloscope

# Connect to an oscilloscope
scope = Oscilloscope("GPIB0::7::INSTR")

# Configure the scope
scope.autoSet()  # Auto-configure for the current signal
scope.set_channel_label(1, "Signal")
scope.setVerticalScale(1, 0.5)  # 0.5V/division

# Capture waveform data
time, voltage = scope.acquire(1)

# Save a screenshot
scope.save_image("capture.png")

# Close the connection
scope.close()
```

### Function Generator

```python
from lab_instrument_library import AFG3000

# Connect to a function generator
fg = AFG3000("GPIB0::11::INSTR")

# Configure a sine wave output
fg.set_function("SIN", 1)
fg.set_frequency(1, 1000)  # 1 kHz
fg.set_amplitude(1, 2.0)   # 2.0 Vpp

# Enable output
fg.enable_output(1)

# Close connection when done
fg.close()
```

### SMU (Source Measure Unit)

```python
from lab_instrument_library import SMU

# Connect to an SMU
smu = SMU("USB0::0x0957::0xCE18::MY51141974::INSTR")

# Configure and enable channel 1 as a voltage source
smu.set_function("VOLT")
smu.set_voltage(3.3)
smu.set_voltage_range(10)  # Set appropriate voltage range
smu.enable_output(1)

# Measure the results
voltage = smu.measure_voltage()
current = smu.measure_current()
print(f"Applied {voltage}V, measured {current}A")

# Turn off output and close connection
smu.disable_output(1)
smu.close()
```

### Temperature Control

```python
from lab_instrument_library import Thermonics

# Connect to a temperature controller
tc = Thermonics("GPIB0::21::INSTR", selected_instrument="Thermonics T-2500SE")

# Set temperature to -40°C
tc.set_temperature(-40)

# Read current temperature
temp = tc.get_temperature()
print(f"Current temperature: {temp}°C")

# Return to ambient when done
tc.select_ambient()
tc.close()
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a new Pull Request

## Development

For developers working on this library, there are several utility classes and helpers:

- `LibraryTemplate`: Base class for all instrument classes
- `visa_exception_handler`: Decorator for consistent error handling
- Various logging utilities in the `utils` module
