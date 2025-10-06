"""
Tests for SMU helpers (Keysight B2902A).
"""

import pytest


def test_smu_configure_output_and_compliance(mock_visa):
    from lab_instrument_library import SMU
    from tests.mocks.mock_visa import MockResource

    responses = {
        "*IDN?": "KEYSIGHT,B2902A,12345,1.0",
        "*OPC?": "1",
        "SOUR1:VOLT?": "0.0",
        "SOUR1:CURR:LIMIT?": "0.1",
        "SOUR1:VOLT:LIMIT?": "10.0",
    }
    mr = MockResource("GPIB0::25::INSTR", responses)
    mock_visa.resources["GPIB0::25::INSTR"] = mr

    smu = SMU("GPIB0::25::INSTR")

    # One-shot configure to voltage mode
    smu.configure_output("VOLT", 1.2, 0.05, channel=1)
    log = smu.connection.command_log  # type: ignore[attr-defined]
    assert any("SOUR1:VOLT 1.2" in cmd for cmd in log)
    assert any("SOUR1:CURR:LIMIT 0.05" in cmd for cmd in log)

    # Compliance setters/getters
    smu.set_voltage_compliance(0.2, channel=1)
    assert any("SOUR1:CURR:LIMIT 0.2" in cmd for cmd in log)
    _ = smu.get_voltage_compliance(channel=1)

    smu.set_current_compliance(12.0, channel=1)
    assert any("SOUR1:VOLT:LIMIT 12.0" in cmd for cmd in log)
    _ = smu.get_current_compliance(channel=1)


def test_smu_ramp_voltage(mock_visa):
    from lab_instrument_library import SMU
    from tests.mocks.mock_visa import MockResource

    responses = {
        "*IDN?": "KEYSIGHT,B2902A,12345,1.0",
        "SOUR1:VOLT?": "0.0",
        "SOUR1:CURR:LIMIT?": "0.1",
    }
    mr = MockResource("GPIB0::25::INSTR", responses)
    mock_visa.resources["GPIB0::25::INSTR"] = mr

    smu = SMU("GPIB0::25::INSTR")
    smu.ramp_voltage(1.0, step=0.5, delay=0.0, channel=1)

    # Ensure multiple set commands were issued ending at the target
    log = smu.connection.command_log  # type: ignore[attr-defined]
    assert any("SOUR1:VOLT 0.5" in cmd for cmd in log)
    assert any("SOUR1:VOLT 1.0" in cmd for cmd in log)
