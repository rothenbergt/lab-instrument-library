# Lab Instrument Library

A Python library for interfacing with various laboratory instruments through GPIB/VISA connections.

## Overview

The Lab Instrument Library provides a unified interface to control common laboratory instruments from different manufacturers while abstracting away device-specific command syntax. It aims to simplify lab automation by providing consistent methods for common operations.

## Instruments Supported

### Multimeters

- HP 34401A (via HP34401A class)
- Keithley 2000 (via Keithley2000 class)
- Keithley 2110 (via Keithley2110 class)
- Tektronix DMM4050 (via TektronixDMM4050 class)

### Power Supplies

- Agilent E3631A
- Agilent E3632A
- Keysight E3649A
- Keysight E36313A
- Keysight E36234A

### Source Measure Units (SMUs)

- Keysight B2902A (via KeysightB2902A class)
- Keithley 228
- Keithley 238

### Oscilloscopes

- Tektronix TDS1000/2000 Series (via TektronixTDS2000 class)
- Tektronix DPO/MSO2000 Series (via TektronixDPO2000 class)
- Tektronix MDO3000 Series (via TektronixMDO3000 class)
- Tektronix TBS1000 Series (via TektronixTBS1000 class)

### Function Generators

- Tektronix AFG3000 series

### Network Analyzers

- Agilent/Keysight E5061B

### Temperature Instruments

- Thermocouples
- Thermometers
- Thermonics temperature forcing systems (T-2500SE, T-2420, X-Stream 4300)

## Architecture

The library follows a consistent pattern with base classes and device-specific implementations:

```
Instrument Base Classes
└── Model-Specific Classes
```

For example:
```
MultimeterBase
├── HP34401A  
├── Keithley2000
├── Keithley2110
└── TektronixDMM4050

OscilloscopeBase
├── TektronixTDS2000
├── TektronixDPO2000
├── TektronixMDO3000
└── TektronixTBS1000
```

This architecture allows for:
- Common methods shared across all instruments of a type
- Specialized methods and capabilities for specific instrument models
- Parameter validation tailored to each instrument's limitations
- Consistent error handling through decorators

## Installation

### Requirements

- Python 3.6+
- PyVISA
- PyVISA-py (for non-NI VISA implementations)
- NumPy
- SciPy
- Pandas
- Matplotlib
- PIL (Pillow)
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

# Connect using the generic Multimeter factory (auto-detects the model using *IDN?)
multimeter = Multimeter("GPIB0::15::INSTR")

# Read voltage measurement (triggers and returns using current configuration)
voltage = multimeter.read_voltage()
print(f"Measured voltage: {voltage} V")

# Measure voltage (configure VOLT, trigger, return in one step)
voltage = multimeter.measure_voltage()
print(f"Measured voltage: {voltage} V")

# Change measurement function to current
multimeter.set_function("CURR")

# Read current measurement
current = multimeter.read_current()
print(f"Measured current: {current} A")

# Get statistics from multiple measurements
stats = multimeter.measure_statistics("VOLT", samples=10, delay=0.1)
print(f"Mean voltage: {stats['mean']} V")
print(f"Standard deviation: {stats['std_dev']} V")

# Clean up resources when finished
multimeter.close()
```

### Power Supply

```python
from lab_instrument_library.supply import KeysightE36xx

# Connect to a power supply
supply = KeysightE36xx("GPIB0::5::INSTR")

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
from lab_instrument_library.oscilloscope import TektronixTDS2000

# Connect to a specific oscilloscope model
scope = TektronixTDS2000("GPIB0::7::INSTR")

# Configure the scope
scope.auto_set()  # Auto-configure for the current signal
scope.set_channel_label(1, "Signal")
scope.set_vertical_scale(1, 0.5)  # 0.5V/division
scope.set_horizontal_scale(0.001)  # 1ms/division

# Capture waveform data
time, voltage = scope.acquire(1)

# Export data to CSV
scope.export_waveform_to_csv(1, "waveform_data.csv")

# Save a screenshot
scope.save_image("capture.png")

# Close the connection
scope.close()
```

### Function Generator

```python
from lab_instrument_library.function_generator import AFG3000

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
from lab_instrument_library.smu import KeysightB2902A

# Connect to a specific SMU model
smu = KeysightB2902A("USB0::0x0957::0xCE18::MY51141974::INSTR")

# Configure and enable channel 1 as a voltage source
smu.set_voltage(3.3, 0.1)  # 3.3V with 100mA current limit
smu.enable_output(1)

# Measure the results
measurements = smu.get_all_measurements(1)
print(f"Voltage: {measurements['voltage']}V")
print(f"Current: {measurements['current']}A")
print(f"Power: {measurements['power']}W")
print(f"Resistance: {measurements['resistance']}Ω")

# Turn off output and close connection
smu.disable_output(1)
smu.close()
```

### Temperature Control

```python
from lab_instrument_library.thermonics import Thermonics

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

## Error Handling

All instrument classes use the `@visa_exception_handler` decorator to provide consistent error handling:

- Graceful recovery from communication failures
- Detailed logging of errors
- Sensible default values when operations fail
- Parameter validation with the `@parameter_validator` decorator

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
- `parameter_validator`: Decorator for validating method parameters
- Various logging utilities in the `utils` module
