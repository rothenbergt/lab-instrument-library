"""
Lab Instrument Library
======================

A Python library for interfacing with various laboratory instruments through GPIB/VISA connections.
This library provides a unified interface to control laboratory instruments from different
manufacturers while abstracting away device-specific command syntax.

Available instruments:
---------------------
Multimeters
    Interfaces for digital multimeters from various manufacturers (HP34401A, Keithley2000, etc.)
Supply
    Interface for DC power supplies
SMU
    Interface for Source Measure Units
Oscilloscope
    Interface for oscilloscopes
FunctionGenerator (AFG3000)
    Interface for function generators
NetworkAnalyzer
    Interface for network analyzers
TemperatureSensor
    Interface for temperature measurement devices (thermocouples, thermometers)
Thermonics
    Interface for temperature forcing systems
KeithlySMU
    Interface for Keithley SMU models 228 and 238
"""

__version__ = '0.1.0'

# Standard logging available to package module imports
import logging

# Re-export base class
from .base import LibraryTemplate as LibraryTemplate
from .function_generator import AFG3000 as AFG3000
from .keithly_smu import Keithly228 as Keithly228
from .keithly_smu import Keithly238 as Keithly238

# Re-export instrument classes
from .multimeter import (
    HP34401A as HP34401A,
)
from .multimeter import (
    Keithley2000 as Keithley2000,
)
from .multimeter import (
    Keithley2110 as Keithley2110,
)
from .multimeter import (
    Multimeter as Multimeter,
)
from .multimeter import (
    MultimeterBase as MultimeterBase,
)
from .multimeter import (
    TektronixDMM4050 as TektronixDMM4050,
)
from .network_analyzer import NetworkAnalyzer as NetworkAnalyzer
from .oscilloscope import Oscilloscope as Oscilloscope
from .smu import KeysightB2902A as KeysightB2902A
from .supply import Supply as Supply
from .temperature_sensor import (
    TemperatureSensor as TemperatureSensor,
)
from .temperature_sensor import (
    Thermocouple as Thermocouple,
)
from .temperature_sensor import (
    Thermometer as Thermometer,
)
from .thermonics import Thermonics as Thermonics

# Re-export utilities
from .utils import (
    Logger as Logger,
)
from .utils import (
    countdown as countdown,
)
from .utils import (
    create_run_folder as create_run_folder,
)
from .utils import (
    get_directory as get_directory,
)
from .utils import (
    getAllLiveUnits as getAllLiveUnits,
)
from .utils import (
    scan_gpib_devices as scan_gpib_devices,
)
from .utils import (
    stringToFloat as stringToFloat,
)
from .utils import (
    stringToInt as stringToInt,
)

# Convenience alias
SMU = KeysightB2902A

logging.getLogger(__name__).addHandler(logging.NullHandler())
