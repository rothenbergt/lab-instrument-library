"""
Tests for the Keithley2110 multimeter class.

This module tests the functionality of the Keithley 2110 multimeter class,
including initialization, measurement functions, filtering, thermocouple operations,
and temperature unit settings.
"""

import pytest


def test_keithley2110_exists():
    import lab_instrument_library

    assert hasattr(lab_instrument_library, "Keithley2110")


def test_keithley2110_init_and_basic_measurements(mock_visa):
    from lab_instrument_library import Keithley2110
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("KEITHLEY2110", MULTIMETER_RESPONSES["GENERIC"])
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = Keithley2110("GPIB0::22::INSTR")
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


def test_keithley2110_filter(mock_visa):
    from lab_instrument_library import Keithley2110
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("KEITHLEY2110", MULTIMETER_RESPONSES["GENERIC"])
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = Keithley2110("GPIB0::22::INSTR")

    # Test setting filter with different parameters
    dmm.set_filter(state=True, type="MOV", count=20)
    assert any("SENS:AVER:TCON MOV" in cmd for cmd in mock_resource.command_log)
    assert any("SENS:AVER:COUN 20" in cmd for cmd in mock_resource.command_log)
    assert any("SENS:AVER ON" in cmd for cmd in mock_resource.command_log)

    # Clear log and test disable
    mock_resource.command_log.clear()
    dmm.set_filter(state=False, type="REP", count=5)
    assert any("SENS:AVER OFF" in cmd for cmd in mock_resource.command_log)


def test_keithley2110_thermocouple(mock_visa):
    from lab_instrument_library import Keithley2110
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("KEITHLEY2110", MULTIMETER_RESPONSES["GENERIC"])
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = Keithley2110("GPIB0::22::INSTR")

    # Test setting thermocouple type (note: different command than 2000)
    dmm.set_thermocouple_type("J")
    assert any("TC:TYPE J" in cmd for cmd in mock_resource.command_log)

    # Test getting thermocouple type
    tc_type = dmm.get_thermocouple_type()
    assert tc_type == "K"  # From mock response


def test_keithley2110_temperature_unit(mock_visa):
    from lab_instrument_library import Keithley2110
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("KEITHLEY2110", MULTIMETER_RESPONSES["GENERIC"])
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = Keithley2110("GPIB0::22::INSTR")

    # Test setting temperature unit with different formats
    dmm.set_temperature_unit("C")
    assert any("UNIT:TEMP CEL" in cmd for cmd in mock_resource.command_log)

    mock_resource.command_log.clear()
    dmm.set_temperature_unit("CEL")
    assert any("UNIT:TEMP CEL" in cmd for cmd in mock_resource.command_log)

    mock_resource.command_log.clear()
    dmm.set_temperature_unit("F")
    assert any("UNIT:TEMP FAR" in cmd for cmd in mock_resource.command_log)

    mock_resource.command_log.clear()
    dmm.set_temperature_unit("K")
    assert any("UNIT:TEMP K" in cmd for cmd in mock_resource.command_log)


def test_keithley2110_nplc(mock_visa):
    from lab_instrument_library import Keithley2110
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("KEITHLEY2110", MULTIMETER_RESPONSES["GENERIC"])
    # Add NPLC responses
    responses["SENS:VOLT:DC:NPLC?"] = "1.0"
    responses["SENS:CURR:DC:NPLC?"] = "1.0"

    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = Keithley2110("GPIB0::22::INSTR")

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


def test_keithley2110_validation(mock_visa):
    from lab_instrument_library import Keithley2110
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("KEITHLEY2110", MULTIMETER_RESPONSES["GENERIC"])
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = Keithley2110("GPIB0::22::INSTR")

    # Test invalid filter type
    with pytest.raises(ValueError):
        dmm.set_filter(state=True, type="INVALID", count=10)

    # Test invalid filter count
    with pytest.raises(ValueError):
        dmm.set_filter(state=True, type="MOV", count=200)

    # Test invalid thermocouple type
    with pytest.raises(ValueError):
        dmm.set_thermocouple_type("X")

    # Test invalid temperature unit
    with pytest.raises(ValueError):
        dmm.set_temperature_unit("INVALID")
