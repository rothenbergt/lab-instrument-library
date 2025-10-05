# Lab Instrument Library

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/rothenbergt/lab-instrument-library/actions/workflows/ci.yml/badge.svg)](https://github.com/rothenbergt/lab-instrument-library/actions)

A Python library for interfacing with laboratory instruments through GPIB/VISA connections. Control multimeters, oscilloscopes, power supplies, SMUs, and more with a unified, Pythonic API.

**Born from real-world lab experience** - this library supports the common instruments you'll find in professional electronics and research labs, curated from years of hands-on testing and characterization work.

## Quick Start

```python
from lab_instrument_library import Multimeter

# Auto-detect and connect to any supported multimeter
dmm = Multimeter("GPIB0::15::INSTR")
voltage = dmm.measure_voltage()
print(f"Measured: {voltage} V")
dmm.close()
```

## Supported Instruments

<details>
<summary><b>Multimeters</b> (4 models)</summary>

- HP 34401A
- Keithley 2000
- Keithley 2110
- Tektronix DMM4050

</details>

<details>
<summary><b>Source Measure Units (SMUs)</b> (3 models)</summary>

- Keysight B2902A (2-channel, advanced features)
- Keithley 228
- Keithley 238

</details>

<details>
<summary><b>Power Supplies</b> (5 models)</summary>

- Agilent E3631A (Triple output)
- Agilent E3632A (Single output)
- Keysight E3649A (Dual output)
- Keysight E36313A (Triple output)
- Keysight E36234A (Quad output)

</details>

<details>
<summary><b>Oscilloscopes</b> (4 series)</summary>

- Tektronix TDS1000/2000 Series
- Tektronix DPO/MSO2000 Series
- Tektronix MDO3000 Series
- Tektronix TBS1000 Series

</details>

<details>
<summary><b>Other Instruments</b></summary>

- **Function Generators**: Tektronix AFG3000 series
- **Network Analyzers**: Agilent/Keysight E5061B
- **Temperature Controllers**: Thermonics T-2500SE, T-2420, X-Stream 4300
- **Temperature Sensors**: Thermocouples, Thermometers

</details>

## Installation

```bash
# Clone the repository
git clone https://github.com/rothenbergt/lab-instrument-library.git
cd lab-instrument-library

# Install in development mode
pip install -e .
```

**Requirements**: Python 3.10+, PyVISA, NumPy, and a VISA backend (NI-VISA or Keysight IO Libraries)

## Usage Examples

### Multimeter - Quick Measurements

```python
from lab_instrument_library import Multimeter

# Auto-detect instrument model
dmm = Multimeter("GPIB0::15::INSTR")

# Quick measurements
voltage = dmm.measure_voltage()
current = dmm.measure_current()
resistance = dmm.measure_resistance()

# Statistics from multiple readings
stats = dmm.measure_statistics("VOLT", samples=10)
print(f"Mean: {stats['mean']:.6f} V, StdDev: {stats['std_dev']:.6f} V")

dmm.close()
```

### Power Supply - Set and Measure

```python
from lab_instrument_library import Supply

ps = Supply("GPIB0::26::INSTR", selected_instrument="E36313A")

# Set 3.3V with 500mA current limit on channel 1
ps.set_voltage(3.3, 0.5, channel=1)
ps.enable_output(channel=1)

# Measure actual output
v = ps.measure_voltage(channel=1)
i = ps.measure_current(channel=1)
print(f"Output: {v:.3f}V @ {i*1000:.1f}mA")

ps.disable_output(channel=1)
ps.close()
```

### SMU - IV Characterization

```python
from lab_instrument_library.smu import KeysightB2902A

smu = KeysightB2902A("USB0::0x0957::0xCE18::MY51141974::INSTR")

# Perform voltage sweep and measure current
voltages, currents = smu.measure_iv_curve(
    channel=1,
    start_v=0,
    stop_v=5,
    points=50,
    current_limit=0.1
)

smu.close()
```

### Oscilloscope - Capture Waveform

```python
from lab_instrument_library.oscilloscope import TektronixTDS2000

scope = TektronixTDS2000("GPIB0::7::INSTR")

# Configure and capture
scope.auto_set()
scope.set_vertical_scale(1, 0.5)  # Channel 1: 500mV/div
scope.set_horizontal_scale(0.001)  # 1ms/div

# Acquire waveform data
time, voltage = scope.acquire(1)

# Save screenshot
scope.save_image("capture.png")

scope.close()
```

### Temperature Control

```python
from lab_instrument_library.thermonics import Thermonics

tc = Thermonics("GPIB0::21::INSTR", selected_instrument="Thermonics T-2500SE")

# Set and monitor temperature
tc.set_temperature(-40)
temp = tc.get_temperature()
print(f"Current: {temp}°C")

# Return to ambient
tc.select_ambient()
tc.close()
```

## Architecture

The library uses a base class pattern for consistency:

```
LibraryTemplate (base.py)
├── MultimeterBase → HP34401A, Keithley2000, Keithley2110, TektronixDMM4050
├── SMUBase → KeysightB2902A, Keithley228, Keithley238
├── OscilloscopeBase → TektronixTDS2000, TektronixDPO2000, ...
└── PowerSupplyBase → E3631A, E3632A, E36313A, ...
```

**Key Features:**

- 🎯 Common methods shared across instrument types
- 🔧 Model-specific capabilities when needed
- ✅ Parameter validation via decorators
- 🛡️ Consistent error handling

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=lab_instrument_library --cov-report=html

# Run specific test file
pytest tests/test_multimeter_factory.py -v
```

### Project Structure

```
lab-instrument-library/
├── lab_instrument_library/   # Main package
│   ├── multimeter.py         # Multimeter implementations
│   ├── smu.py                # SMU implementations
│   ├── oscilloscope.py       # Oscilloscope implementations
│   ├── supply.py             # Power supply implementations
│   ├── base.py               # Base classes
│   └── utils/                # Utilities and decorators
├── tests/                    # Test suite
├── examples/                 # Usage examples
└── docs/                     # Documentation
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run the test suite (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Documentation

- 📚 **Full API Documentation**: [Coming soon]
- 💡 **More Examples**: See the [`examples/`](examples/) directory
- 🐛 **Issues & Bugs**: [GitHub Issues](https://github.com/rothenbergt/lab-instrument-library/issues)

---

**Tip**: All instrument classes include links to official programming manuals in their docstrings. Check the source code for SCPI command references!
