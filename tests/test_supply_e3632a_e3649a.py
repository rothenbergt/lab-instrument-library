"""
Tests for Agilent E3632A and Keysight E3649A supplies.
"""

import pytest


def test_e3632a_set_voltage_and_output(mock_visa):
    from lab_instrument_library import Supply
    from tests.mocks.mock_visa import MockResource

    responses = {"*IDN?": "AGILENT,E3632A,12345,1.0"}
    mr = MockResource("GPIB0::26::INSTR", responses)
    mock_visa.resources["GPIB0::26::INSTR"] = mr

    ps = Supply("GPIB0::26::INSTR", selected_instrument="E3632A")

    # Set a low voltage (should select LOW range)
    ps.set_voltage(5.0, 1.0)
    log = ps.connection.command_log  # type: ignore[attr-defined]
    assert any("VOLT:RANG LOW" in cmd for cmd in log)
    assert any("VOLT 5.0000" in cmd for cmd in log)
    assert any("CURR 1.0000" in cmd for cmd in log)

    ps.enable_output()
    assert any("OUTP ON" in cmd for cmd in log)

    ps.disable_output()
    assert any("OUTP OFF" in cmd for cmd in log)


def test_e3649a_channel_selection_and_limits(mock_visa):
    from lab_instrument_library import Supply
    from tests.mocks.mock_visa import MockResource

    responses = {"*IDN?": "KEYSIGHT,E3649A,12345,1.0"}
    mr = MockResource("GPIB0::26::INSTR", responses)
    mock_visa.resources["GPIB0::26::INSTR"] = mr

    ps = Supply("GPIB0::26::INSTR", selected_instrument="E3649A")

    ps.set_voltage(12.0, 0.5, channel=2)
    log = ps.connection.command_log  # type: ignore[attr-defined]
    assert any("INST:SEL OUT2" in cmd for cmd in log)
    assert any("VOLT 12.0000" in cmd for cmd in log)
    assert any("CURR 0.5000" in cmd for cmd in log)

    # Current limit helper through Supply
    ps.set_current_limit(0.25, channel=2)
    assert any("CURR 0.2500" in cmd for cmd in log)
