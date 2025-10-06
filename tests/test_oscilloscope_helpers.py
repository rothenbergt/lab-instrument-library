"""
Tests for oscilloscope helpers and configuration.
"""


def test_oscilloscope_configure_channel_and_acquisition(mock_oscilloscope):
    scope = mock_oscilloscope
    # Access the underlying mock to inspect commands

    # Configure CH1 in one call
    scope.configure_channel(
        channel=1,
        scale=0.5,
        position=1.0,
        coupling="AC",
        enabled=True,
        label="Signal",
    )

    # Basic assertions that commands were issued
    log = scope.connection.command_log  # type: ignore[attr-defined]
    assert any("CH1:SCA 0.5" in cmd for cmd in log)
    assert any("CH1:POSition 1.0" in cmd for cmd in log)
    assert any("CH1:COUPling AC" in cmd for cmd in log)
    assert any("SELECT:CH1 1" in cmd for cmd in log)
    assert any("CH1:LAB \"Signal\"" in cmd for cmd in log)

    # Configure acquisition (AVERAGE + averages + timebase)
    scope.configure_acquisition(acquisition_mode="AVERAGE", averages=16, timebase=1e-3)
    assert any("ACQuire:MODe AVERAGE" in cmd for cmd in log)
    assert any("ACQuire:NUMAVg 16" in cmd for cmd in log)
    assert any("HORizontal:SCAle 0.001" in cmd for cmd in log)


def test_oscilloscope_measurements(mock_oscilloscope):
    scope = mock_oscilloscope
    # Provide a canned measurement response
    scope.connection.responses["MEASUrement:IMMed:VALue?"] = "123.45"  # type: ignore[attr-defined]

    f = scope.measure_frequency(1)
    vpp = scope.measure_vpp(1)
    assert isinstance(f, float)
    assert isinstance(vpp, float)
