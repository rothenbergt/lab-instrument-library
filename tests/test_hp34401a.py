"""
Tests for the HP34401A multimeter class.

This module tests the functionality of the HP34401A multimeter class,
including initialization, measurement functions, range settings, and configuration operations.
"""


def test_hp34401a_exists():
    import lab_instrument_library

    assert hasattr(lab_instrument_library, "HP34401A")


def test_hp34401a_init_and_basic_measurements(mock_visa):
    from lab_instrument_library import HP34401A
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("HP34401A", MULTIMETER_RESPONSES["GENERIC"])
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = HP34401A("GPIB0::22::INSTR")
    assert dmm.instrument_address == "GPIB0::22::INSTR"

    # Measure wrappers
    v = dmm.measure_voltage()
    i = dmm.measure_current()
    r = dmm.measure_resistance()
    assert isinstance(v, float)
    assert isinstance(i, float)
    assert isinstance(r, float)

    # Read wrappers (reuse config)
    v_read = dmm.read_voltage()
    assert isinstance(v_read, float)


def test_hp34401a_fetch_and_trigger(mock_visa):
    from lab_instrument_library import HP34401A
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("HP34401A", MULTIMETER_RESPONSES["GENERIC"])
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = HP34401A("GPIB0::22::INSTR")

    # Ensure we can fetch after initiating
    dmm.set_function("VOLT")
    dmm.initiate()
    fetched = dmm.fetch_voltage()
    assert isinstance(fetched, float)


def test_hp34401a_range_and_autorange(mock_visa):
    from lab_instrument_library import HP34401A
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("HP34401A", MULTIMETER_RESPONSES["GENERIC"])
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = HP34401A("GPIB0::22::INSTR")

    dmm.set_range("VOLT", 10.0)
    assert dmm.get_range("VOLT") == 10.0

    dmm.set_auto_range("VOLT", False)
    assert dmm.get_auto_range_state("VOLT") is False


def test_hp34401a_display_text_and_clear(mock_visa):
    from lab_instrument_library import HP34401A
    from tests.mocks.mock_visa import MockResource
    from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES

    responses = MULTIMETER_RESPONSES.get("HP34401A", MULTIMETER_RESPONSES["GENERIC"])
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = HP34401A("GPIB0::22::INSTR")

    msg = "TEST MESSAGE"
    dmm.display_text(msg)
    assert any("DISP:TEXT" in cmd for cmd in mock_resource.command_log)

    dmm.clear_display()
    assert any("DISP:TEXT:CLE" in cmd for cmd in mock_resource.command_log)
