"""
Canned responses for mocking multimeter instruments.

This module contains predefined responses for different multimeter
models that can be used for testing without physical instruments.
"""

from typing import Dict

# Generic multimeter responses
GENERIC_MULTIMETER_RESPONSES: Dict[str, str] = {
    # Basic identification and status
    "*IDN?": "MOCK,MULTIMETER500,1234,1.0",
    "*RST": "",
    "*CLS": "",
    "*OPC?": "1",
    "SYST:ERR?": "0,No error",
    
    # Function setting
    ":CONF:VOLT?": "VOLT",
    ":CONF:CURR?": "CURR",
    ":CONF:RES?": "RES",
    "FUNC?": "\"VOLT:DC\"",
    
    # Measurements
    "MEAS:VOLT?": "1.234",
    "MEAS:VOLT:DC?": "1.234",
    "MEAS:VOLT:AC?": "0.707",
    "MEAS:CURR?": "0.0567",
    "MEAS:CURR:DC?": "0.0567",
    "MEAS:CURR:AC?": "0.0354",
    "MEAS:RES?": "1000.56",
    "MEAS:FRES?": "1000.57",
    "READ?": "1.234",
    "FETC?": "1.234",
    
    # Range settings
    "VOLT:RANG?": "10.0",
    "CURR:RANG?": "1.0",
    "RES:RANG?": "10000.0",
    "VOLT:RANG:AUTO?": "1",
    "CURR:RANG:AUTO?": "1",
    "RES:RANG:AUTO?": "1",
}

# HP 34401A specific responses
HP34401A_RESPONSES: Dict[str, str] = {
    # Update the generic responses with HP-specific ones
    **GENERIC_MULTIMETER_RESPONSES,
    "*IDN?": "HEWLETT-PACKARD,34401A,0,1.0-5.0",
    
    # HP-specific commands
    "DISP:TEXT?": "\"TEST MESSAGE\"",
    "SYST:BEEP:STAT?": "0",
    "SAMP:COUN?": "1",
    "TRIG:COUN?": "1",
    "TRIG:SOUR?": "IMM",
}

# Keithley 2000 specific responses
KEITHLEY2000_RESPONSES: Dict[str, str] = {
    # Update the generic responses with Keithley-specific ones
    **GENERIC_MULTIMETER_RESPONSES,
    "*IDN?": "KEITHLEY INSTRUMENTS,2000,1234567,1.0",

    # Keithley-specific commands
    ":INIT:CONT?": "0",
    ":SENS:AVER:TCON?": "MOV",
    ":SENS:AVER:COUN?": "10",
    ":SENS:AVER?": "1",
    "TEMP:TC:TYPE?": "K",
}

# Keithley 2110 specific responses
KEITHLEY2110_RESPONSES: Dict[str, str] = {
    # Update the generic responses with Keithley-specific ones
    **GENERIC_MULTIMETER_RESPONSES,
    "*IDN?": "KEITHLEY INSTRUMENTS,2110,1234567,1.0",

    # Keithley 2110-specific commands
    ":SENS:AVER:TCON?": "MOV",
    ":SENS:AVER:COUN?": "10",
    ":SENS:AVER?": "1",
    "TC:TYPE?": "K",
    "UNIT:TEMP?": "CEL",
}

# Tektronix DMM4050 specific responses
TEKTRONIXDMM4050_RESPONSES: Dict[str, str] = {
    # Update the generic responses with Tektronix-specific ones
    **GENERIC_MULTIMETER_RESPONSES,
    "*IDN?": "TEKTRONIX,DMM4050,12345,1.0",

    # Tektronix-specific commands
    "DISP:WIND2:STAT?": "0",
    "SENS:FUNC2?": "\"CURR\"",
    "SENS:DATA2?": "0.0567",
    "TEMP:TRAN:TC:RJUN:TYPE?": "INT",
}

# Dictionary mapping model identifiers to response sets
MULTIMETER_RESPONSES = {
    "HP34401A": HP34401A_RESPONSES,
    "KEITHLEY2000": KEITHLEY2000_RESPONSES,
    "KEITHLEY2110": KEITHLEY2110_RESPONSES,
    "TEKTRONIXDMM4050": TEKTRONIXDMM4050_RESPONSES,
    "GENERIC": GENERIC_MULTIMETER_RESPONSES,
}