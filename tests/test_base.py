"""
Tests for the LibraryTemplate base class.

This module tests the base functionality shared by all instrument classes,
such as connection handling, identification, and basic VISA operations.
"""

import pytest


def test_library_template_init(mock_visa):
    """Test that LibraryTemplate can be initialized."""
    try:
        from pylabinstruments.base import LibraryTemplate

        # Initialize a LibraryTemplate instance
        template = LibraryTemplate("GPIB0::22::INSTR")

        # Check that it's initialized correctly
        assert template.instrument_address == "GPIB0::22::INSTR"
        assert template.instrumentID == "Mock Instrument,Model 123,SN123456,FW1.0"
        assert template.connection is not None
    except ImportError:
        pytest.skip("pylabinstruments.base.LibraryTemplate not available")


def test_library_template_write(mock_visa):
    """Test that LibraryTemplate.write works."""
    try:
        from pylabinstruments.base import LibraryTemplate

        # Initialize a LibraryTemplate instance
        template = LibraryTemplate("GPIB0::22::INSTR")

        # Write a command
        template.write("TEST:COMMAND")

        # Check that the command was sent
        assert mock_visa.resources["GPIB0::22::INSTR"].last_command == "TEST:COMMAND"
        assert "TEST:COMMAND" in mock_visa.resources["GPIB0::22::INSTR"].command_log
    except ImportError:
        pytest.skip("pylabinstruments.base.LibraryTemplate not available")


def test_library_template_query(mock_visa):
    """Test that LibraryTemplate.query works."""
    try:
        from pylabinstruments.base import LibraryTemplate

        # Add a specific response for our test command
        mock_visa.resources["GPIB0::22::INSTR"].responses["TEST:QUERY?"] = "TEST_RESPONSE"

        # Initialize a LibraryTemplate instance
        template = LibraryTemplate("GPIB0::22::INSTR")

        # Query a command
        response = template.query("TEST:QUERY?")

        # Check that the response is correct
        assert response == "TEST_RESPONSE"
    except ImportError:
        pytest.skip("pylabinstruments.base.LibraryTemplate not available")


def test_library_template_identify(mock_visa):
    """Test that LibraryTemplate.identify works."""
    try:
        from pylabinstruments.base import LibraryTemplate

        # Initialize a LibraryTemplate instance
        template = LibraryTemplate("GPIB0::22::INSTR", identify=False)

        # Manually identify the instrument
        identifier = template.identify()

        # Check that the identification is correct
        assert identifier == "Mock Instrument,Model 123,SN123456,FW1.0"
        assert template.instrumentID == "Mock Instrument,Model 123,SN123456,FW1.0"
    except ImportError:
        pytest.skip("pylabinstruments.base.LibraryTemplate not available")


def test_library_template_reset(mock_visa):
    """Test that LibraryTemplate.reset works."""
    try:
        from pylabinstruments.base import LibraryTemplate

        # Initialize a LibraryTemplate instance
        template = LibraryTemplate("GPIB0::22::INSTR")

        # Reset the instrument
        result = template.reset()

        # Check that reset was successful
        assert result is True
        assert "*RST" in mock_visa.resources["GPIB0::22::INSTR"].command_log
    except ImportError:
        pytest.skip("pylabinstruments.base.LibraryTemplate not available")


def test_library_template_clear(mock_visa):
    """Test that LibraryTemplate.clear works."""
    try:
        from pylabinstruments.base import LibraryTemplate

        # Initialize a LibraryTemplate instance
        template = LibraryTemplate("GPIB0::22::INSTR")

        # Clear the instrument
        result = template.clear()

        # Check that clear was successful
        assert result is True
        assert "*CLS" in mock_visa.resources["GPIB0::22::INSTR"].command_log
    except ImportError:
        pytest.skip("pylabinstruments.base.LibraryTemplate not available")


def test_library_template_error_handling(mock_visa):
    """Test that LibraryTemplate handles errors properly."""
    try:
        from pylabinstruments.base import LibraryTemplate

        # First initialize the library template normally
        template = LibraryTemplate("GPIB0::22::INSTR")

        # Then make the mock resource raise an exception on write
        def mock_write_error(cmd):
            raise ValueError("Mock write error")

        mock_visa.resources["GPIB0::22::INSTR"].write = mock_write_error

        # Write should not raise an exception but return None
        result = template.write("TEST:COMMAND")
        assert result is None
    except ImportError:
        pytest.skip("pylabinstruments.base.LibraryTemplate not available")


def test_library_template_close(mock_visa):
    """Test that LibraryTemplate.close works."""
    try:
        from pylabinstruments.base import LibraryTemplate

        # Initialize a LibraryTemplate instance
        template = LibraryTemplate("GPIB0::22::INSTR")

        # Close the connection
        template.close()

        # Check that the connection was closed
        assert mock_visa.resources["GPIB0::22::INSTR"].closed is True
    except ImportError:
        pytest.skip("pylabinstruments.base.LibraryTemplate not available")


def test_library_template_context_manager(mock_visa):
    """Test that LibraryTemplate works as a context manager."""
    try:
        from pylabinstruments.base import LibraryTemplate

        # Use LibraryTemplate as a context manager
        with LibraryTemplate("GPIB0::22::INSTR") as template:
            # Check that it's initialized correctly
            assert template.instrument_address == "GPIB0::22::INSTR"
            assert template.instrumentID == "Mock Instrument,Model 123,SN123456,FW1.0"

            # Use the connection
            template.write("TEST:COMMAND")

        # Check that the connection was closed
        assert mock_visa.resources["GPIB0::22::INSTR"].closed is True
    except ImportError:
        pytest.skip("pylabinstruments.base.LibraryTemplate not available")
