"""
Tests for the HP34401A multimeter class.

This module tests the functionality of the HP34401A multimeter class,
including initialization, measurement functions, range settings, and configuration operations.
"""

import pytest
from unittest.mock import patch, MagicMock

def test_hp34401a_exists():
    """Test that HP34401A is defined in the package."""
    import sys
    import lab_instrument_library
    
    # Just check that the module has HP34401A defined
    assert hasattr(lab_instrument_library, "HP34401A")
    print("HP34401A class exists in the package")

def test_hp34401a_init(mock_visa):
    """Test that HP34401A can be initialized with a VISA address."""
    try:
        # Import the HP34401A class
        from lab_instrument_library import HP34401A
        
        # Create a mock resource
        from tests.mocks.mock_visa import MockResource
        from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES
        
        # Get responses for the HP34401A model
        responses = MULTIMETER_RESPONSES.get("HP34401A", MULTIMETER_RESPONSES["GENERIC"])
        
        # Create a mock resource with multimeter responses
        mock_resource = MockResource("GPIB0::22::INSTR", responses)
        
        # Update the mock manager to use our multimeter resource
        mock_visa.resources["GPIB0::22::INSTR"] = mock_resource
        
        # Create a multimeter instance
        multimeter = HP34401A("GPIB0::22::INSTR")
        
        # Check that it's initialized correctly
        assert multimeter.instrument_address == "GPIB0::22::INSTR"
        
        # Check that it attempted to get the instrument ID
        assert any("*IDN?" in cmd for cmd in mock_resource.command_log)
        
        print("HP34401A initialization test passed")
    except Exception as e:
        pytest.fail(f"Failed to initialize HP34401A: {e}")

def test_hp34401a_measure_voltage(mock_visa):
    """Test that HP34401A.measure_voltage works correctly."""
    try:
        # Import the HP34401A class
        from lab_instrument_library import HP34401A
        
        # Create a mock resource
        from tests.mocks.mock_visa import MockResource
        from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES
        
        # Get responses for the HP34401A model
        responses = MULTIMETER_RESPONSES.get("HP34401A", MULTIMETER_RESPONSES["GENERIC"])
        
        # Create a mock resource with multimeter responses
        mock_resource = MockResource("GPIB0::22::INSTR", responses)
        
        # Update the mock manager to use our multimeter resource
        mock_visa.resources["GPIB0::22::INSTR"] = mock_resource
        
        # Create a multimeter instance
        multimeter = HP34401A("GPIB0::22::INSTR")
        
        # Measure voltage
        voltage = multimeter.measure_voltage()
        
        # Check that the response is as expected based on our mock
        assert isinstance(voltage, float)
        
        # Check that the correct command was sent
        assert any("MEAS:VOLT" in cmd for cmd in mock_resource.command_log)
        
        print("HP34401A measure_voltage test passed")
    except Exception as e:
        pytest.fail(f"Failed to measure voltage with HP34401A: {e}")

def test_hp34401a_measure_current(mock_visa):
    """Test that HP34401A.measure_current works correctly."""
    try:
        # Import the HP34401A class
        from lab_instrument_library import HP34401A
        
        # Create a mock resource
        from tests.mocks.mock_visa import MockResource
        from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES
        
        # Get responses for the HP34401A model
        responses = MULTIMETER_RESPONSES.get("HP34401A", MULTIMETER_RESPONSES["GENERIC"])
        
        # Create a mock resource with multimeter responses
        mock_resource = MockResource("GPIB0::22::INSTR", responses)
        
        # Update the mock manager to use our multimeter resource
        mock_visa.resources["GPIB0::22::INSTR"] = mock_resource
        
        # Create a multimeter instance
        multimeter = HP34401A("GPIB0::22::INSTR")
        
        # Measure current
        current = multimeter.measure_current()
        
        # Check that the response is as expected based on our mock
        assert isinstance(current, float)
        
        # Check that the correct command was sent
        assert any("MEAS:CURR" in cmd for cmd in mock_resource.command_log)
        
        print("HP34401A measure_current test passed")
    except Exception as e:
        pytest.fail(f"Failed to measure current with HP34401A: {e}")

def test_hp34401a_measure_resistance(mock_visa):
    """Test that HP34401A.measure_resistance works correctly."""
    try:
        # Import the HP34401A class
        from lab_instrument_library import HP34401A
        
        # Create a mock resource
        from tests.mocks.mock_visa import MockResource
        from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES
        
        # Get responses for the HP34401A model
        responses = MULTIMETER_RESPONSES.get("HP34401A", MULTIMETER_RESPONSES["GENERIC"])
        
        # Create a mock resource with multimeter responses
        mock_resource = MockResource("GPIB0::22::INSTR", responses)
        
        # Update the mock manager to use our multimeter resource
        mock_visa.resources["GPIB0::22::INSTR"] = mock_resource
        
        # Create a multimeter instance
        multimeter = HP34401A("GPIB0::22::INSTR")
        
        # Measure resistance
        resistance = multimeter.measure_resistance()
        
        # Check that the response is as expected based on our mock
        assert isinstance(resistance, float)
        
        # Check that the correct command was sent
        assert any("MEAS:RES" in cmd for cmd in mock_resource.command_log)
        
        print("HP34401A measure_resistance test passed")
    except Exception as e:
        pytest.fail(f"Failed to measure resistance with HP34401A: {e}")

def test_hp34401a_display_text(mock_visa):
    """Test that HP34401A.display_text works correctly."""
    try:
        # Import the HP34401A class
        from lab_instrument_library import HP34401A
        
        # Create a mock resource
        from tests.mocks.mock_visa import MockResource
        from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES
        
        # Get responses for the HP34401A model
        responses = MULTIMETER_RESPONSES.get("HP34401A", MULTIMETER_RESPONSES["GENERIC"])
        
        # Create a mock resource with multimeter responses
        mock_resource = MockResource("GPIB0::22::INSTR", responses)
        
        # Update the mock manager to use our multimeter resource
        mock_visa.resources["GPIB0::22::INSTR"] = mock_resource
        
        # Create a multimeter instance
        multimeter = HP34401A("GPIB0::22::INSTR")
        
        # Display text on the multimeter
        test_message = "TEST MESSAGE"
        multimeter.display_text(test_message)
        
        # Check that the correct command was sent
        display_commands = [cmd for cmd in mock_resource.command_log if "DISP:TEXT" in cmd]
        assert len(display_commands) > 0
        assert any(test_message in cmd for cmd in display_commands)
        
        print("HP34401A display_text test passed")
    except Exception as e:
        pytest.fail(f"Failed to display text with HP34401A: {e}")

def test_hp34401a_clear_display(mock_visa):
    """Test that HP34401A.clear_display works correctly."""
    try:
        # Import the HP34401A class
        from lab_instrument_library import HP34401A
        
        # Create a mock resource
        from tests.mocks.mock_visa import MockResource
        from tests.mocks.responses.multimeter_responses import MULTIMETER_RESPONSES
        
        # Get responses for the HP34401A model
        responses = MULTIMETER_RESPONSES.get("HP34401A", MULTIMETER_RESPONSES["GENERIC"])
        
        # Create a mock resource with multimeter responses
        mock_resource = MockResource("GPIB0::22::INSTR", responses)
        
        # Update the mock manager to use our multimeter resource
        mock_visa.resources["GPIB0::22::INSTR"] = mock_resource
        
        # Create a multimeter instance
        multimeter = HP34401A("GPIB0::22::INSTR")
        
        # First display some text
        multimeter.display_text("TEST MESSAGE")
        
        # Then clear the display
        multimeter.clear_display()
        
        # Check that the correct command was sent
        clear_commands = [cmd for cmd in mock_resource.command_log if "DISP:TEXT:CLE" in cmd]
        assert len(clear_commands) > 0
        
        print("HP34401A clear_display test passed")
    except Exception as e:
        pytest.fail(f"Failed to clear display with HP34401A: {e}")