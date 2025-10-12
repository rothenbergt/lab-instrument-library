"""
Tests for the Keithley SMU classes (Keithley228 and Keithley238).

Basic tests to verify functionality of Keithley 228 and 238 source measure units.
"""


def test_keithley_smu_classes_exist():
    """Test that Keithley SMU classes can be imported."""
    import pylabinstruments

    assert hasattr(pylabinstruments, "Keithley228")
    assert hasattr(pylabinstruments, "Keithley238")


def test_keithley228_init(mock_visa):
    """Test Keithley228 initialization."""
    from pylabinstruments import Keithley228
    from tests.mocks.mock_visa import MockResource

    # Create mock with appropriate responses
    responses = {
        "*IDN?": "KEITHLEY,228,12345,1.0",
        "*RST": "",
        "U0X": "",  # Keithley 228 command
        "G0X": "",  # Get reading
    }
    mock_resource = MockResource("GPIB0::12::INSTR", responses)
    mock_visa.resources["GPIB0::12::INSTR"] = mock_resource

    smu = Keithley228("GPIB0::12::INSTR")
    assert smu.instrument_address == "GPIB0::12::INSTR"


def test_keithley238_init(mock_visa):
    """Test Keithley238 initialization."""
    from pylabinstruments import Keithley238
    from tests.mocks.mock_visa import MockResource

    # Create mock with appropriate responses
    responses = {
        "*IDN?": "KEITHLEY,238,12345,1.0",
        "*RST": "",
        "F0X": "",  # Keithley 238 command
        "H0X": "",  # Execute function
    }
    mock_resource = MockResource("GPIB0::13::INSTR", responses)
    mock_visa.resources["GPIB0::13::INSTR"] = mock_resource

    smu = Keithley238("GPIB0::13::INSTR")
    assert smu.instrument_address == "GPIB0::13::INSTR"


def test_keithley228_basic_commands(mock_visa):
    """Test basic Keithley228 commands."""
    from pylabinstruments import Keithley228
    from tests.mocks.mock_visa import MockResource

    responses = {
        "*IDN?": "KEITHLEY,228,12345,1.0",
        "*RST": "",
        "U0X": "",
        "G0X": "",
    }
    mock_resource = MockResource("GPIB0::12::INSTR", responses)
    mock_visa.resources["GPIB0::12::INSTR"] = mock_resource

    smu = Keithley228("GPIB0::12::INSTR")

    # Test that we can call reset
    result = smu.reset()
    assert result is True

    # Test close
    smu.close()


def test_keithley238_basic_commands(mock_visa):
    """Test basic Keithley238 commands."""
    from pylabinstruments import Keithley238
    from tests.mocks.mock_visa import MockResource

    responses = {
        "*IDN?": "KEITHLEY,238,12345,1.0",
        "*RST": "",
        "F0X": "",
        "H0X": "",
    }
    mock_resource = MockResource("GPIB0::13::INSTR", responses)
    mock_visa.resources["GPIB0::13::INSTR"] = mock_resource

    smu = Keithley238("GPIB0::13::INSTR")

    # Test that we can call reset
    result = smu.reset()
    assert result is True

    # Test close
    smu.close()
