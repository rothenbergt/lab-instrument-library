"""
Mock implementation of PyVISA for testing without real hardware.

This module provides mock classes that mimic the behavior of PyVISA's
ResourceManager and Resource classes, allowing tests to run without
physical instruments connected.
"""

import time
from typing import Dict, Any, List, Optional, Union

class MockResource:
    """Mock implementation of a PyVISA Resource."""
    
    def __init__(self, resource_name: str, responses: Dict[str, str] = None):
        """Initialize a mock VISA resource.
        
        Args:
            resource_name: The VISA address of the simulated instrument
            responses: Dictionary mapping commands to responses
        """
        self.resource_name = resource_name
        self.responses = responses or {}
        self.default_response = "0"
        self.timeout = 5000
        self.write_termination = '\n'
        self.read_termination = '\n'
        self.baud_rate = 9600
        self.last_command = None
        self.closed = False
        self.command_log = []  # Track all commands sent
        
    def write(self, command: str) -> None:
        """Simulate writing a command to an instrument.
        
        Args:
            command: The command to write
        """
        if self.closed:
            raise ValueError("Resource is closed")
            
        self.last_command = command
        self.command_log.append(command)
        
    def read(self) -> str:
        """Simulate reading a response from an instrument.
        
        Returns:
            A simulated response string
        """
        if self.closed:
            raise ValueError("Resource is closed")
            
        if not self.last_command:
            return "ERROR: No command sent"
            
        # Get response for the last command if available
        if self.last_command in self.responses:
            response = self.responses[self.last_command]
        else:
            response = self.default_response
            
        return response + self.read_termination
        
    def query(self, command: str) -> str:
        """Simulate querying an instrument.
        
        Args:
            command: The command to send
            
        Returns:
            A simulated response string
        """
        self.write(command)
        return self.read()
        
    def read_raw(self) -> bytes:
        """Simulate reading raw binary data.
        
        Returns:
            Raw bytes response
        """
        if self.closed:
            raise ValueError("Resource is closed")
            
        response = self.read()
        return response.encode('utf-8')
        
    def query_binary_values(self, command: str, datatype: str = 'f', 
                          is_big_endian: bool = True, 
                          container: Any = list) -> List[Any]:
        """Simulate querying for binary values.
        
        Args:
            command: The command to send
            datatype: The format string for the binary values
            is_big_endian: Whether the values are in big-endian format
            container: The container type for the returned values
            
        Returns:
            A list of simulated values
        """
        self.write(command)
        # Just return a list of 10 simulated values
        return container([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        
    def query_ascii_values(self, command: str, separator: str = ',', 
                         container: Any = list) -> List[Any]:
        """Simulate querying for ASCII values.
        
        Args:
            command: The command to send
            separator: The separator character between values
            container: The container type for the returned values
            
        Returns:
            A list of simulated values
        """
        self.write(command)
        # Return simulated values
        return container([1.1, 2.2, 3.3, 4.4, 5.5])
        
    def close(self) -> None:
        """Simulate closing the connection."""
        self.closed = True


class MockResourceManager:
    """Mock implementation of PyVISA ResourceManager."""
    
    def __init__(self, resources: Dict[str, MockResource] = None):
        """Initialize a mock resource manager.
        
        Args:
            resources: Dictionary mapping resource names to mock resources
        """
        self.resources = resources or {}
        
    def open_resource(self, resource_name: str, **kwargs) -> MockResource:
        """Simulate opening a connection to an instrument.
        
        Args:
            resource_name: The VISA address to connect to
            **kwargs: Additional arguments (ignored)
            
        Returns:
            A mock resource object
            
        Raises:
            ValueError: If the resource is not found
        """
        if resource_name in self.resources:
            return self.resources[resource_name]
            
        # If resource doesn't exist, create a new one with default responses
        standard_responses = {
            "*IDN?": "Mock Instrument,Model 123,SN123456,FW1.0",
            "*RST": "",
            "*CLS": "",
            "*OPC?": "1",
            "SYST:ERR?": "0,No error"
        }
        
        # Create a new resource
        resource = MockResource(resource_name, standard_responses)
        self.resources[resource_name] = resource
        return resource
        
    def list_resources(self, query: str = "?*::INSTR") -> List[str]:
        """Simulate listing available resources.
        
        Args:
            query: Resource query string (ignored)
            
        Returns:
            List of resource names
        """
        return list(self.resources.keys())
        
    def close(self) -> None:
        """Simulate closing the resource manager."""
        for resource in self.resources.values():
            resource.close()