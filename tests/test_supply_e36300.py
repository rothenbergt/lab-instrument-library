"""
Tests for Keysight E36300 series supply via Supply factory.
"""


def test_e36300_basic_channel_control(mock_visa):
    from pylabinstruments import Supply
    from tests.mocks.mock_visa import MockResource

    # Create resource with generic IDN (model is provided explicitly)
    responses = {"*IDN?": "KEYSIGHT,E36313A,12345,1.0"}
    mock_resource = MockResource("GPIB0::26::INSTR", responses)
    mock_visa.resources["GPIB0::26::INSTR"] = mock_resource

    ps = Supply("GPIB0::26::INSTR", selected_instrument="E36313A")

    # Set ch1 voltage/current
    ps.set_voltage(3.3, 0.5, channel=1)
    assert any("VOLT 3.3000, (@1)" in cmd for cmd in mock_resource.command_log)
    assert any("CURR 0.5000, (@1)" in cmd for cmd in mock_resource.command_log)

    # Enable ch1 and verify output state
    ps.enable_output(channel=1)
    assert any("OUTP ON, (@1)" in cmd for cmd in mock_resource.command_log)
    assert ps.get_output_state(1) is True

    # Read back set voltage and measurements
    vset = ps.get_voltage(1)
    vmeas = ps.measure_voltage(1)
    imeas = ps.measure_current(1)
    assert isinstance(vset, float)
    assert isinstance(vmeas, float)
    assert isinstance(imeas, float)

    # Disable ch1
    ps.disable_output(channel=1)
    assert any("OUTP OFF, (@1)" in cmd for cmd in mock_resource.command_log)
    assert ps.get_output_state(1) is False

    # Combined helper
    allm = ps.get_all_measurements(1)
    assert set(allm.keys()) == {"voltage", "current"}
