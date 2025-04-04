"""
Lab Instrument Library
======================

A Python library for interfacing with various laboratory instruments through GPIB/VISA connections.
This library provides a unified interface to control laboratory instruments from different 
manufacturers while abstracting away device-specific command syntax.

Available instruments:
---------------------
Multimeter
    Interface for digital multimeters from various manufacturers
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

# Import base class
from .base import LibraryTemplate

# Import instrument classes
from .multimeter import Multimeter
from .supply import Supply
from .smu import SMU
from .oscilloscope import Oscilloscope
from .function_generator import AFG3000
from .network_analyzer import NetworkAnalyzer
from .temperature_sensor import TemperatureSensor, Thermocouple, Thermometer
from .thermonics import Thermonics
from .keithly_smu import Keithly228, Keithly238

# Import utilities
from .utils import Logger, create_run_folder, get_directory, countdown, scan_gpib_devices, getAllLiveUnits, stringToInt, stringToFloat

# Optional: Set up a logger
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
