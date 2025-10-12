"""
Tests for the Thermonics temperature controller classes.

Basic tests for Thermonics temperature forcing systems.
"""


def test_thermonics_class_exists():
    """Test that Thermonics class can be imported."""
    import pylabinstruments

    assert hasattr(pylabinstruments, "Thermonics")


def test_thermonics_init(mock_visa):
    """Test Thermonics initialization with explicit instrument selection."""
    from pylabinstruments import Thermonics
    from tests.mocks.mock_visa import MockResource

    # Create mock with Thermonics T-2500SE responses
    responses = {
        "*IDN?": "THERMONICS,T-2500SE,12345,1.0",
        "RA": "25.0",  # Read actual temperature
        "TH125": "",  # Set hot temperature
        "TC-40": "",  # Set cold temperature
        "AH": "",  # Select hot air
        "AC": "",  # Select cold air
        "AA": "",  # Select ambient air
        "AF": "",  # Select ambient forced air
        "CS": "",  # Compressor start
        "CP": "",  # Compressor stop
    }
    mock_resource = MockResource("GPIB0::21::INSTR", responses)
    mock_visa.resources["GPIB0::21::INSTR"] = mock_resource

    # Initialize with explicit instrument to avoid interactive prompt
    tc = Thermonics("GPIB0::21::INSTR", selected_instrument="Thermonics T-2500SE")
    assert tc.instrument_address == "GPIB0::21::INSTR"


def test_thermonics_get_temperature(mock_visa):
    """Test getting temperature from Thermonics."""
    from pylabinstruments import Thermonics
    from tests.mocks.mock_visa import MockResource

    responses = {
        "*IDN?": "THERMONICS,T-2500SE,12345,1.0",
        "RA": "25.0",
        "TH125": "",
        "TC-40": "",
        "AH": "",
        "AC": "",
        "AA": "",
    }
    mock_resource = MockResource("GPIB0::21::INSTR", responses)
    mock_visa.resources["GPIB0::21::INSTR"] = mock_resource

    tc = Thermonics("GPIB0::21::INSTR", selected_instrument="Thermonics T-2500SE")
    temp = tc.get_temperature()
    assert isinstance(temp, float)


def test_thermonics_set_temperature(mock_visa):
    """Test setting temperature."""
    from pylabinstruments import Thermonics
    from tests.mocks.mock_visa import MockResource

    responses = {
        "*IDN?": "THERMONICS,T-2500SE,12345,1.0",
        "RA": "25.0",
        "TH85": "",
        "TC-40": "",
        "AH": "",
        "AC": "",
        "AA": "",
    }
    mock_resource = MockResource("GPIB0::21::INSTR", responses)
    mock_visa.resources["GPIB0::21::INSTR"] = mock_resource

    tc = Thermonics("GPIB0::21::INSTR", selected_instrument="Thermonics T-2500SE")

    # Test hot temperature (> 25°C)
    result = tc.set_temperature(85.0)
    assert result is True
    assert any("TH85" in cmd for cmd in mock_resource.command_log)


def test_thermonics_select_ambient(mock_visa):
    """Test selecting ambient air."""
    from pylabinstruments import Thermonics
    from tests.mocks.mock_visa import MockResource

    responses = {
        "*IDN?": "THERMONICS,T-2500SE,12345,1.0",
        "RA": "25.0",
        "AA": "",
        "TH85": "",
        "TC-40": "",
        "AH": "",
        "AC": "",
    }
    mock_resource = MockResource("GPIB0::21::INSTR", responses)
    mock_visa.resources["GPIB0::21::INSTR"] = mock_resource

    tc = Thermonics("GPIB0::21::INSTR", selected_instrument="Thermonics T-2500SE")
    tc.select_ambient()
    assert any("AA" in cmd for cmd in mock_resource.command_log)


def test_thermonics_compressor_control(mock_visa):
    """Test compressor on/off control."""
    from pylabinstruments import Thermonics
    from tests.mocks.mock_visa import MockResource

    responses = {
        "*IDN?": "THERMONICS,T-2500SE,12345,1.0",
        "RA": "25.0",
        "CS": "",  # Compressor start
        "CP": "",  # Compressor stop
        "TH85": "",
        "TC-40": "",
        "AH": "",
        "AC": "",
        "AA": "",
    }
    mock_resource = MockResource("GPIB0::21::INSTR", responses)
    mock_visa.resources["GPIB0::21::INSTR"] = mock_resource

    tc = Thermonics("GPIB0::21::INSTR", selected_instrument="Thermonics T-2500SE")
    tc.turn_on_compressor()
    assert any("CS" in cmd for cmd in mock_resource.command_log)

    tc.turn_off_compressor()
    assert any("CP" in cmd for cmd in mock_resource.command_log)


def test_thermonics_close(mock_visa):
    """Test closing Thermonics controller (should return to ambient)."""
    from pylabinstruments import Thermonics
    from tests.mocks.mock_visa import MockResource

    responses = {
        "*IDN?": "THERMONICS,T-2500SE,12345,1.0",
        "RA": "25.0",
        "AA": "",
        "TH85": "",
        "TC-40": "",
        "AH": "",
        "AC": "",
    }
    mock_resource = MockResource("GPIB0::21::INSTR", responses)
    mock_visa.resources["GPIB0::21::INSTR"] = mock_resource

    tc = Thermonics("GPIB0::21::INSTR", selected_instrument="Thermonics T-2500SE")
    tc.close()
    # Should have called AA (ambient air) as part of safe shutdown
    assert any("AA" in cmd for cmd in mock_resource.command_log)
