"""
Tests for the temperature sensor classes.

Basic tests for TemperatureSensor, Thermometer, and Thermocouple classes.
"""


def test_temperature_sensor_classes_exist():
    """Test that temperature sensor classes can be imported."""
    import pylabinstruments

    assert hasattr(pylabinstruments, "TemperatureSensor")
    assert hasattr(pylabinstruments, "Thermometer")
    assert hasattr(pylabinstruments, "Thermocouple")


def test_temperature_sensor_init(mock_visa):
    """Test TemperatureSensor initialization with explicit type."""
    from pylabinstruments import TemperatureSensor
    from tests.mocks.mock_visa import MockResource

    # Create mock with temperature sensor responses
    responses = {
        "*IDN?": "ACME,THERMOMETER,12345,1.0",
        "*RST": "",
        "FETCH?": "25.5",  # Temperature reading
        "UNIT:TEMP C": "",
    }
    mock_resource = MockResource("GPIB0::28::INSTR", responses)
    mock_visa.resources["GPIB0::28::INSTR"] = mock_resource

    # Create sensor with explicit type to avoid interactive prompt
    sensor = TemperatureSensor("GPIB0::28::INSTR", sensor_type="ThermometerFetch")
    assert sensor.instrument_address == "GPIB0::28::INSTR"


def test_thermometer_init(mock_visa):
    """Test Thermometer (legacy) initialization."""
    from pylabinstruments import Thermometer
    from tests.mocks.mock_visa import MockResource

    responses = {
        "*IDN?": "ACME,THERMOMETER,12345,1.0",
        "*RST": "",
        "FETCH?": "25.5",
    }
    mock_resource = MockResource("GPIB0::28::INSTR", responses)
    mock_visa.resources["GPIB0::28::INSTR"] = mock_resource

    therm = Thermometer("GPIB0::28::INSTR")
    assert therm.instrument_address == "GPIB0::28::INSTR"


def test_thermocouple_init(mock_visa):
    """Test Thermocouple initialization."""
    from pylabinstruments import Thermocouple
    from tests.mocks.mock_visa import MockResource

    responses = {
        "*IDN?": "ACME,THERMOCOUPLE,12345,1.0",
        "*RST": "",
        "MEAS?1": "22.3",  # Temperature reading for channel 1
        "TTYP 1,T": "",  # Set thermocouple type
    }
    mock_resource = MockResource("GPIB0::29::INSTR", responses)
    mock_visa.resources["GPIB0::29::INSTR"] = mock_resource

    tc = Thermocouple("GPIB0::29::INSTR")
    assert tc.instrument_address == "GPIB0::29::INSTR"


def test_temperature_sensor_get_temperature(mock_visa):
    """Test getting temperature reading."""
    from pylabinstruments import TemperatureSensor
    from tests.mocks.mock_visa import MockResource

    responses = {
        "*IDN?": "ACME,THERMOMETER,12345,1.0",
        "FETCH?": "25.5",
    }
    mock_resource = MockResource("GPIB0::28::INSTR", responses)
    mock_visa.resources["GPIB0::28::INSTR"] = mock_resource

    sensor = TemperatureSensor("GPIB0::28::INSTR", sensor_type="ThermometerFetch")
    temp = sensor.get_temperature()
    assert isinstance(temp, float)


def test_thermocouple_set_type(mock_visa):
    """Test setting thermocouple type."""
    from pylabinstruments import Thermocouple
    from tests.mocks.mock_visa import MockResource

    responses = {
        "*IDN?": "ACME,THERMOCOUPLE,12345,1.0",
        "MEAS?1": "22.3",
        "TTYP 1,K": "",  # K-type thermocouple
    }
    mock_resource = MockResource("GPIB0::29::INSTR", responses)
    mock_visa.resources["GPIB0::29::INSTR"] = mock_resource

    tc = Thermocouple("GPIB0::29::INSTR")
    tc.setType(1, "K")  # Legacy method name
    assert any("TTYP" in cmd for cmd in mock_resource.command_log)


def test_temperature_sensor_close(mock_visa):
    """Test closing temperature sensor."""
    from pylabinstruments import TemperatureSensor
    from tests.mocks.mock_visa import MockResource

    responses = {
        "*IDN?": "ACME,THERMOMETER,12345,1.0",
        "FETCH?": "25.5",
    }
    mock_resource = MockResource("GPIB0::28::INSTR", responses)
    mock_visa.resources["GPIB0::28::INSTR"] = mock_resource

    sensor = TemperatureSensor("GPIB0::28::INSTR", sensor_type="ThermometerFetch")
    sensor.close()
    # Should not raise an exception
