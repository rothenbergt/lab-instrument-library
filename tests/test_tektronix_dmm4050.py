"""
Tests for the TektronixDMM4050 multimeter class.

This module tests the functionality of the Tektronix DMM4050 multimeter class,
including initialization, measurement functions, dual display mode, and
temperature reference junction settings.
"""

import pytest


def test_tektronix_dmm4050_exists():
    import lab_instrument_library

    assert hasattr(lab_instrument_library, "TektronixDMM4050")


def test_tektronix_dmm4050_init_and_basic_measurements(mock_visa):
    from lab_instrument_library import TektronixDMM4050
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("TEKTRONIXDMM4050", MULTIMETER_RESPONSES["GENERIC"])
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = TektronixDMM4050("GPIB0::22::INSTR")
    assert dmm.instrument_address == "GPIB0::22::INSTR"

    # Measure wrappers
    v = dmm.measure_voltage()
    i = dmm.measure_current()
    r = dmm.measure_resistance()
    assert isinstance(v, float)
    assert isinstance(i, float)
    assert isinstance(r, float)


def test_tektronix_dmm4050_dual_display(mock_visa):
    from lab_instrument_library import TektronixDMM4050
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("TEKTRONIXDMM4050", MULTIMETER_RESPONSES["GENERIC"])
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = TektronixDMM4050("GPIB0::22::INSTR")

    # Clear previous commands
    mock_resource.command_log.clear()

    # Test enabling dual display
    dmm.enable_dual_display("VOLT", "CURR")
    assert any("SENS:FUNC2" in cmd and "CURR" in cmd for cmd in mock_resource.command_log)
    assert any("DISP:WIND2:STAT ON" in cmd for cmd in mock_resource.command_log)

    # Clear log
    mock_resource.command_log.clear()

    # Test disabling dual display
    dmm.disable_dual_display()
    assert any("DISP:WIND2:STAT OFF" in cmd for cmd in mock_resource.command_log)


def test_tektronix_dmm4050_read_dual_display(mock_visa):
    from lab_instrument_library import TektronixDMM4050
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("TEKTRONIXDMM4050", MULTIMETER_RESPONSES["GENERIC"])
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = TektronixDMM4050("GPIB0::22::INSTR")

    # Enable dual display
    dmm.enable_dual_display("VOLT", "CURR")

    # Test reading both displays
    primary, secondary = dmm.read_dual_display()
    assert isinstance(primary, float)
    assert isinstance(secondary, float)
    assert primary > 0  # Should be voltage reading
    assert secondary > 0  # Should be current reading


def test_tektronix_dmm4050_temperature_reference_junction(mock_visa):
    from lab_instrument_library import TektronixDMM4050
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("TEKTRONIXDMM4050", MULTIMETER_RESPONSES["GENERIC"])
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = TektronixDMM4050("GPIB0::22::INSTR")

    # Test setting internal reference junction
    dmm.set_temperature_reference_junction("INT")
    assert any("TEMP:TRAN:TC:RJUN:TYPE INT" in cmd for cmd in mock_resource.command_log)

    # Clear log
    mock_resource.command_log.clear()

    # Test setting external reference junction
    dmm.set_temperature_reference_junction("EXT")
    assert any("TEMP:TRAN:TC:RJUN:TYPE EXT" in cmd for cmd in mock_resource.command_log)

    # Clear log
    mock_resource.command_log.clear()

    # Test setting simulated reference junction with value
    dmm.set_temperature_reference_junction("SIM", sim_value=25.0)
    assert any("TEMP:TRAN:TC:RJUN:TYPE SIM" in cmd for cmd in mock_resource.command_log)
    assert any("TEMP:TRAN:TC:RJUN:SIM 25.0" in cmd for cmd in mock_resource.command_log)


def test_tektronix_dmm4050_validation(mock_visa):
    from lab_instrument_library import TektronixDMM4050
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("TEKTRONIXDMM4050", MULTIMETER_RESPONSES["GENERIC"])
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = TektronixDMM4050("GPIB0::22::INSTR")

    # Test invalid reference junction type
    with pytest.raises(ValueError):
        dmm.set_temperature_reference_junction("INVALID")


def test_tektronix_dmm4050_range_and_autorange(mock_visa):
    from lab_instrument_library import TektronixDMM4050
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("TEKTRONIXDMM4050", MULTIMETER_RESPONSES["GENERIC"])
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = TektronixDMM4050("GPIB0::22::INSTR")

    # Test setting range
    dmm.set_range("VOLT", 10.0)
    range_val = dmm.get_range("VOLT")
    assert range_val == 10.0

    # Test auto-range
    dmm.set_auto_range("VOLT", False)
    auto_state = dmm.get_auto_range_state("VOLT")
    assert auto_state is False


def test_tektronix_dmm4050_fetch_and_trigger(mock_visa):
    from lab_instrument_library import TektronixDMM4050
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("TEKTRONIXDMM4050", MULTIMETER_RESPONSES["GENERIC"])
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = TektronixDMM4050("GPIB0::22::INSTR")

    # Ensure we can fetch after initiating
    dmm.set_function("VOLT")
    dmm.initiate()
    fetched = dmm.fetch_voltage()
    assert isinstance(fetched, float)
