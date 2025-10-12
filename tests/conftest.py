"""
Common pytest fixtures for testing the lab instrument library.

This module provides fixtures for mocking PyVISA resources and
creating instrument instances for testing without physical hardware.
"""

import os
import sys
from unittest.mock import patch

import pytest

# Add parent directory to path to import the library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import our mock VISA implementation
from tests.mocks.mock_visa import MockResource, MockResourceManager
from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

# Import the library modules (adjust paths as needed)
# Note: we avoid importing the package eagerly here to keep tests isolated from import-time side effects.


@pytest.fixture
def mock_visa():
    """Fixture to provide a mock PyVISA implementation.

    Returns:
        A mock ResourceManager object with standard responses.
    """
    # Create a mock resource with standard responses
    standard_responses = {
        "*IDN?": "Mock Instrument,Model 123,SN123456,FW1.0",
        "*RST": "",
        "*CLS": "",
        "*OPC?": "1",
        "SYST:ERR?": "0,No error",
    }

    mock_resource = MockResource("GPIB0::22::INSTR", standard_responses)

    # Create a mock resource manager that returns our mock resource
    mock_manager = MockResourceManager({"GPIB0::22::INSTR": mock_resource})

    # Patch the pyvisa.ResourceManager to return our mock
    with patch('pyvisa.ResourceManager', return_value=mock_manager):
        yield mock_manager


@pytest.fixture
def mock_multimeter(mock_visa, model="HP34401A"):
    """Fixture to provide a mock multimeter.

    Args:
        mock_visa: The mock VISA resource manager
        model: The multimeter model to mock ('HP34401A', 'KEITHLEY2000', 'KEITHLEY2110', or 'TEKTRONIXDMM4050')

    Returns:
        A multimeter instance connected to a mock resource.
    """
    # Get responses for the specified model
    responses = MULTIMETER_RESPONSES.get(model, MULTIMETER_RESPONSES["GENERIC"])

    # Create a mock resource with multimeter responses
    mock_resource = MockResource("GPIB0::22::INSTR", responses)

    # Update the mock manager to use our multimeter resource
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    # Import specific multimeter classes
    try:
        if model == "HP34401A":
            from pylabinstruments import HP34401A

            multimeter = HP34401A("GPIB0::22::INSTR")
        elif model == "KEITHLEY2000":
            from pylabinstruments import Keithley2000

            multimeter = Keithley2000("GPIB0::22::INSTR")
        elif model == "KEITHLEY2110":
            from pylabinstruments import Keithley2110

            multimeter = Keithley2110("GPIB0::22::INSTR")
        elif model == "TEKTRONIXDMM4050":
            from pylabinstruments import TektronixDMM4050

            multimeter = TektronixDMM4050("GPIB0::22::INSTR")
        else:
            # Default to HP34401A if model not specified or recognized
            from pylabinstruments import HP34401A

            multimeter = HP34401A("GPIB0::22::INSTR")

        return multimeter
    except ImportError as e:
        pytest.skip(f"Multimeter class {model} not available: {str(e)}")


@pytest.fixture
def mock_oscilloscope(mock_visa):
    """Fixture to provide a mock oscilloscope.

    Args:
        mock_visa: The mock VISA resource manager

    Returns:
        An Oscilloscope instance connected to a mock resource.
    """
    # Add oscilloscope-specific responses
    oscilloscope_responses = {
        "*IDN?": "TEKTRONIX,TDS2024B,12345,1.0",
        "*RST": "",
        "*CLS": "",
        "*OPC?": "1",
        "SYST:ERR?": "0,No error",
        "DATA:SOURCE?": "CH1",
        "WFMPRE:YMULT?": "0.02",
        "WFMPRE:YZERO?": "0.0",
        "WFMPRE:PT_OFF?": "0",
        "WFMPRE:XINCR?": "1e-6",
        "WFMPRE:ENC?": "ASCII",
        "CURVE?": "#50100" + "".join([str(i % 256) for i in range(100)]),  # Simulated waveform data
        "CH1:SCA?": "1.0",
        "HORizontal:SCAle?": "1e-3",
        "TRIGger:A:EDGE:SOUrce?": "CH1",
        "TRIGger:A:LEVel?": "0.0",
        "ACQuire:MODe?": "SAMPLE",
    }

    # Create a mock resource with oscilloscope responses
    mock_resource = MockResource("GPIB0::23::INSTR", oscilloscope_responses)

    # Update the mock manager to use our oscilloscope resource
    mock_visa.resources["GPIB0::23::INSTR"] = mock_resource

    # Import the oscilloscope class
    try:
        from pylabinstruments import Oscilloscope

        # Create an oscilloscope instance that uses our mock
        oscilloscope = Oscilloscope("GPIB0::23::INSTR")
        return oscilloscope
    except ImportError:
        pytest.skip("pylabinstruments.Oscilloscope not available")


@pytest.fixture
def mock_function_generator(mock_visa):
    """Fixture to provide a mock function generator.

    Args:
        mock_visa: The mock VISA resource manager

    Returns:
        An AFG3000 instance connected to a mock resource.
    """
    # Add function generator-specific responses
    fg_responses = {
        "*IDN?": "TEKTRONIX,AFG3052C,12345,1.0",
        "*RST": "",
        "*CLS": "",
        "*OPC?": "1",
        "SYSTem:ERRor?": "0,No Error",
        "OUTPut1:STATe?": "OFF",
        "OUTPut2:STATe?": "OFF",
    }

    # Create a mock resource with function generator responses
    mock_resource = MockResource("GPIB0::24::INSTR", fg_responses)

    # Update the mock manager to use our function generator resource
    mock_visa.resources["GPIB0::24::INSTR"] = mock_resource

    # Import the function generator class
    try:
        from pylabinstruments import AFG3000

        # Create a function generator instance that uses our mock
        fg = AFG3000("GPIB0::24::INSTR")
        return fg
    except ImportError:
        pytest.skip("pylabinstruments.AFG3000 not available")


@pytest.fixture
def mock_smu(mock_visa):
    """Fixture to provide a mock source measure unit.

    Args:
        mock_visa: The mock VISA resource manager

    Returns:
        An SMU instance connected to a mock resource.
    """
    # Add SMU-specific responses
    smu_responses = {
        "*IDN?": "KEYSIGHT,B2902A,12345,1.0",
        "*RST": "",
        "*CLS": "",
        "*OPC?": "1",
        "SYST:ERR?": "0,No error",
        "SOUR1:VOLT?": "1.0",
        "SOUR1:CURR?": "0.1",
        "MEAS:VOLT? (@1)": "0.9998",
        "MEAS:CURR? (@1)": "0.0997",
    }

    # Create a mock resource with SMU responses
    mock_resource = MockResource("GPIB0::25::INSTR", smu_responses)

    # Update the mock manager to use our SMU resource
    mock_visa.resources["GPIB0::25::INSTR"] = mock_resource

    # Import the SMU class
    try:
        from pylabinstruments import SMU

        # Create an SMU instance that uses our mock
        smu = SMU("GPIB0::25::INSTR")
        return smu
    except ImportError:
        pytest.skip("pylabinstruments.SMU not available")


@pytest.fixture
def mock_power_supply(mock_visa):
    """Fixture to provide a mock power supply.

    Args:
        mock_visa: The mock VISA resource manager

    Returns:
        A Supply instance connected to a mock resource.
    """
    # Add power supply-specific responses
    ps_responses = {
        "*IDN?": "KEYSIGHT,E36313A,12345,1.0",
        "*RST": "",
        "*CLS": "",
        "*OPC?": "1",
        "SYST:ERR?": "0,No error",
        "VOLT? (@1)": "5.0",
        "CURR? (@1)": "0.5",
        "MEAS:VOLT? (@1)": "4.998",
        "MEAS:CURR? (@1)": "0.251",
        "OUTP? (@1)": "1",
    }

    # Create a mock resource with power supply responses
    mock_resource = MockResource("GPIB0::26::INSTR", ps_responses)

    # Update the mock manager to use our power supply resource
    mock_visa.resources["GPIB0::26::INSTR"] = mock_resource

    # Import the Supply class
    try:
        from pylabinstruments import Supply

        # Create a Supply instance that uses our mock
        supply = Supply("GPIB0::26::INSTR")
        return supply
    except ImportError:
        pytest.skip("pylabinstruments.Supply not available")


@pytest.fixture
def mock_network_analyzer(mock_visa):
    """Fixture to provide a mock network analyzer.

    Returns a NetworkAnalyzer instance connected to a mock resource with canned responses.
    """
    # Basic frequency and trace data
    vna_responses = {
        "*IDN?": "KEYSIGHT,E5061B,12345,1.0",
        "*RST": "",
        "*CLS": "",
        "*OPC?": "1",
        # Frequency axis (3 points)
        "SENS:X:VAL?": "1.0,2.0,3.0",
        # FDAT: interleaved real, imag
        "CALC:DATA:FDAT?": "0.0,0.0, -10.0,0.0, -20.0,0.0",
    }

    mock_resource = MockResource("GPIB0::27::INSTR", vna_responses)
    mock_visa.resources["GPIB0::27::INSTR"] = mock_resource

    try:
        from pylabinstruments import NetworkAnalyzer

        vna = NetworkAnalyzer("GPIB0::27::INSTR")
        return vna
    except ImportError:
        pytest.skip("pylabinstruments.NetworkAnalyzer not available")
