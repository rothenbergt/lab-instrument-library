"""
Tests for the AFG3000 function generator class.

Basic tests to verify functionality of the Tektronix AFG3000 function generator.
"""


def test_afg3000_exists():
    """Test that AFG3000 class can be imported."""
    import pylabinstruments

    assert hasattr(pylabinstruments, "AFG3000")


def test_afg3000_init(mock_function_generator):
    """Test AFG3000 initialization."""
    from pylabinstruments import AFG3000

    fg = mock_function_generator
    assert isinstance(fg, AFG3000)
    assert fg.instrument_address == "GPIB0::24::INSTR"


def test_afg3000_basic_commands(mock_function_generator):
    """Test basic function generator commands."""
    fg = mock_function_generator

    # Test output control - should not raise exceptions
    fg.disable_output(1)
    fg.enable_output(1)

    # Test setting frequency
    fg.set_frequency(1, 1000.0)

    # Test setting amplitude
    fg.set_amplitude(1, 2.0)


def test_afg3000_close(mock_function_generator):
    """Test that function generator can be closed."""
    fg = mock_function_generator
    fg.close()
    # Should not raise an exception
