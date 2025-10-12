"""
Tests for the Keithley2000 multimeter class.

This module tests the functionality of the Keithley 2000 multimeter class,
including initialization, measurement functions, filtering, and thermocouple operations.
"""

import pytest


def test_keithley2000_exists():
    import pylabinstruments

    assert hasattr(pylabinstruments, "Keithley2000")


def test_keithley2000_init_and_basic_measurements(mock_visa):
    from pylabinstruments import Keithley2000
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("KEITHLEY2000", MULTIMETER_RESPONSES["GENERIC"])
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = Keithley2000("GPIB0::22::INSTR")
    assert dmm.instrument_address == "GPIB0::22::INSTR"

    # Verify beeper was disabled during init
    assert any("SYST:BEEP:STAT OFF" in cmd for cmd in mock_resource.command_log)

    # Measure wrappers
    v = dmm.measure_voltage()
    i = dmm.measure_current()
    r = dmm.measure_resistance()
    assert isinstance(v, float)
    assert isinstance(i, float)
    assert isinstance(r, float)


def test_keithley2000_read_override(mock_visa):
    from pylabinstruments import Keithley2000
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("KEITHLEY2000", MULTIMETER_RESPONSES["GENERIC"])
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = Keithley2000("GPIB0::22::INSTR")

    # Clear previous commands
    mock_resource.command_log.clear()

    # Test that read() disables continuous initiation
    v = dmm.read_voltage()
    assert isinstance(v, float)
    assert any(":INIT:CONT OFF" in cmd for cmd in mock_resource.command_log)


def test_keithley2000_filter(mock_visa):
    from pylabinstruments import Keithley2000
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("KEITHLEY2000", MULTIMETER_RESPONSES["GENERIC"])
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = Keithley2000("GPIB0::22::INSTR")

    # Test setting filter with different parameters
    dmm.set_filter(state=True, type="MOV", count=20)
    assert any("SENS:AVER:TCON MOV" in cmd for cmd in mock_resource.command_log)
    assert any("SENS:AVER:COUN 20" in cmd for cmd in mock_resource.command_log)
    assert any("SENS:AVER ON" in cmd for cmd in mock_resource.command_log)

    # Clear log and test disable
    mock_resource.command_log.clear()
    dmm.set_filter(state=False, type="REP", count=5)
    assert any("SENS:AVER OFF" in cmd for cmd in mock_resource.command_log)


def test_keithley2000_thermocouple(mock_visa):
    from pylabinstruments import Keithley2000
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("KEITHLEY2000", MULTIMETER_RESPONSES["GENERIC"])
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = Keithley2000("GPIB0::22::INSTR")

    # Test setting thermocouple type
    dmm.set_thermocouple_type("J")
    assert any("TEMP:TC:TYPE J" in cmd for cmd in mock_resource.command_log)

    # Test getting thermocouple type
    tc_type = dmm.get_thermocouple_type()
    assert tc_type == "K"  # From mock response


def test_keithley2000_nplc(mock_visa):
    from pylabinstruments import Keithley2000
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("KEITHLEY2000", MULTIMETER_RESPONSES["GENERIC"])
    # Add NPLC responses
    responses["SENS:VOLT:DC:NPLC?"] = "1.0"
    responses["SENS:CURR:DC:NPLC?"] = "1.0"

    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = Keithley2000("GPIB0::22::INSTR")

    # Set function to VOLT
    dmm.set_function("VOLT")

    # Clear log
    mock_resource.command_log.clear()

    # Test setting NPLC
    dmm.set_nplc(5.0)
    assert any("SENS:VOLT:DC:NPLC 5.0" in cmd for cmd in mock_resource.command_log)

    # Test getting NPLC reflects the set value in our stateful mock
    nplc = dmm.get_nplc()
    assert nplc == 5.0


def test_keithley2000_validation(mock_visa):
    from pylabinstruments import Keithley2000
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("KEITHLEY2000", MULTIMETER_RESPONSES["GENERIC"])
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = Keithley2000("GPIB0::22::INSTR")

    # Test invalid filter type
    with pytest.raises(ValueError):
        dmm.set_filter(state=True, type="INVALID", count=10)

    # Test invalid filter count
    with pytest.raises(ValueError):
        dmm.set_filter(state=True, type="MOV", count=200)

    # Test invalid thermocouple type
    with pytest.raises(ValueError):
        dmm.set_thermocouple_type("X")
