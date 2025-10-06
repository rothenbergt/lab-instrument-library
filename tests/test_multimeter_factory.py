"""
Factory tests for the generic Multimeter entry point.
"""

import pytest


@pytest.mark.parametrize(
    "idn, expected_class_name",
    [
        ("HEWLETT-PACKARD,34401A,0,1.0-5.0", "HP34401A"),
        ("KEITHLEY INSTRUMENTS,2000,1234567,1.0", "Keithley2000"),
        ("KEITHLEY INSTRUMENTS,2110,1234567,1.0", "Keithley2110"),
        ("TEKTRONIX,DMM4050,12345,1.0", "TektronixDMM4050"),
    ],
)
def test_multimeter_factory_detects_models(mock_visa, idn, expected_class_name):
    from lab_instrument_library import Multimeter
    from tests.mocks.mock_visa import MockResource

    # Create resource with specific IDN
    responses = {"*IDN?": idn}
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = Multimeter("GPIB0::22::INSTR")
    assert dmm.__class__.__name__ == expected_class_name


def test_multimeter_factory_model_override(mock_visa):
    from lab_instrument_library import Multimeter
    from tests.mocks.mock_visa import MockResource

    # Unknown IDN but override should select class
    responses = {"*IDN?": "UNKNOWN,MODEL,0,0"}
    mock_resource = MockResource("GPIB0::22::INSTR", responses)
    mock_visa.resources["GPIB0::22::INSTR"] = mock_resource

    dmm = Multimeter("GPIB0::22::INSTR", model_override="HP34401A")
    assert dmm.__class__.__name__ == "HP34401A"
