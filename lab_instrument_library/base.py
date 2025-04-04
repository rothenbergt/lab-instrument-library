"""
Base class for all lab instruments in the library.

This module defines a common base class that all instrument-specific classes
can inherit from. It provides shared functionality such as connection handling,
identification, and basic VISA commands.
"""

import pyvisa
import logging
import time
from typing import Optional, Union, List, Any, Tuple
from abc import ABC, abstractmethod

# Setup module logger
logger = logging.getLogger(__name__)

class LibraryTemplate(ABC):
    """Base class for lab instrument interfaces.
    
    This class implements common functionality for all instrument types, including
    connection establishment, identification, and basic VISA operations.
    
    Attributes:
        instrument_address (str): The VISA address of the instrument.
        rm (pyvisa.ResourceManager): PyVISA resource manager instance.
        connection (pyvisa.resources.Resource): Active connection to the instrument.
        instrumentID (str): Instrument identification string from *IDN? query.
        nickname (str): User-defined name for the instrument (optional).
    """
      
    def __init__(self, 
                instrument_address: str = "GPIB0::20::INSTR", 
                nickname: Optional[str] = None, 
                identify: bool = True,
                timeout: int = 5000):
        """Initialize a new instrument interface.
        
        Args:
            instrument_address: VISA address of the instrument.
            nickname: User-defined name for the instrument.
            identify: Whether to query the instrument ID on connection.
            timeout: Connection timeout in milliseconds.
        
        Raises:
            SystemExit: If connection fails and no exception handler is in place.
        """
        self.instrument_address = instrument_address
        self.rm = pyvisa.ResourceManager()
        self.connection = None
        self.instrumentID = None
        self.nickname = nickname
        self.timeout = timeout
        
        if not self.make_connection(instrument_address, identify):
            logger.error(f"Failed to establish connection with {instrument_address}")
            raise SystemExit(f"Could not connect to instrument at {instrument_address}")
  
    def make_connection(self, instrument_address: str, identify: bool) -> bool:
        """Establish a connection to the instrument.
        
        Args:
            instrument_address: VISA address of the instrument.
            identify: Whether to query the instrument ID.
        
        Returns:
            bool: True if connection succeeded, False otherwise.
        """
        try:
            # Make the connection and store it
            self.connection = self.rm.open_resource(instrument_address)
            
            # Set timeout for slower instruments
            self.connection.timeout = self.timeout
            
            # Configure termination characters if needed
            # self.connection.read_termination = '\n'
            # self.connection.write_termination = '\n'
            
            # Display that the connection has been made
            if identify:              
                self.identify()
                if self.instrumentID:
                    logger.info(f"Successfully established {self.instrument_address} connection with {self.instrumentID}")
                    print(f"Successfully established {self.instrument_address} connection with {self.instrumentID}")
                    return True
                else:
                    logger.warning(f"Connected to {self.instrument_address} but couldn't identify instrument")
                    return False
            else:
                display_name = self.nickname if self.nickname else instrument_address
                logger.info(f"Successfully established {self.instrument_address} connection with {display_name}")
                print(f"Successfully established {self.instrument_address} connection with {display_name}")
                return True
        
        except pyvisa.errors.VisaIOError as e:
            logger.error(f"VISA IO Error connecting to {self.instrument_address}: {str(e)}")
            print(f"VISA IO Error: {str(e)}")
            print(f"Failed to establish {self.instrument_address} connection.")
            return False
        except Exception as e:
            logger.error(f"Failed to establish {self.instrument_address} connection: {str(e)}")
            print(f"Failed to establish {self.instrument_address} connection.")
            return False
            
    def close_connection(self) -> None:
        """Close the connection to the instrument.
        
        This method should be called when finished with the instrument to release resources.
        """
        if self.connection:
            try:
                self.connection.close()
                logger.info(f"Connection to {self.instrument_address} closed")
            except Exception as e:
                logger.warning(f"Error closing connection to {self.instrument_address}: {str(e)}")
    
    # Alias for backward compatibility
    close = close_connection
    
    # Context manager support
    def __enter__(self):
        """Context manager entry method.
        
        Returns:
            self: The instrument instance for use in with statements.
        """
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit method.
        
        Ensures the connection is closed when exiting a with statement.
        
        Args:
            exc_type: Exception type if an exception was raised, else None.
            exc_val: Exception value if an exception was raised, else None.
            exc_tb: Exception traceback if an exception was raised, else None.
        """
        self.close_connection()

    def identify(self) -> Optional[str]:
        """Query the instrument's identification string.
        
        This method sends the standard IEEE-488.2 *IDN? query to identify the instrument.
        
        Returns:
            str: The instrument identification string, or None if identification failed.
        """
        try:
            response = self.connection.query("*IDN?").strip()
            self.instrumentID = response
            return self.instrumentID
        except Exception as e:
            logger.warning(f"Instrument at {self.instrument_address} could not be identified: {str(e)}")
            print("Unit could not be identified using *IDN? command")
            return None
             
    def write(self, command: str) -> None:
        """Send a command string to the instrument.
        
        Args:
            command: The command string to send.
            
        Raises:
            pyvisa.errors.VisaIOError: If the write operation fails.
        """
        try:
            self.connection.write(command)
            logger.debug(f"Wrote to {self.instrument_address}: {command}")
        except Exception as e:
            logger.error(f"Error writing '{command}' to {self.instrument_address}: {str(e)}")
            raise
    
    def query(self, command: str, delay: Optional[float] = None) -> str:
        """Send a query to the instrument and return the response.
        
        Args:
            command: The query string to send.
            delay: Optional delay in seconds between write and read operations.
            
        Returns:
            str: The response from the instrument.
            
        Raises:
            pyvisa.errors.VisaIOError: If the query operation fails.
        """
        try:
            if delay:
                self.connection.write(command)
                time.sleep(delay)
                response = self.connection.read()
            else:
                response = self.connection.query(command)
            
            logger.debug(f"Queried {self.instrument_address} with '{command}', got '{response}'")
            return response.strip()
        except Exception as e:
            logger.error(f"Error querying {self.instrument_address} with '{command}': {str(e)}")
            raise
    
    def query_binary_values(self, command: str, datatype: str = 'f', 
                          is_big_endian: bool = True, 
                          container: Any = list) -> List[Any]:
        """Query the instrument for binary values.
        
        Args:
            command: The query command to send.
            datatype: The format string for the binary values.
            is_big_endian: Whether the values are in big-endian format.
            container: The container type for the returned values.
            
        Returns:
            A list (or specified container) of the retrieved values.
        """
        try:
            values = self.connection.query_binary_values(
                command, datatype, is_big_endian, container)
            return values
        except Exception as e:
            logger.error(f"Error querying binary values from {self.instrument_address}: {str(e)}")
            raise
    
    def query_ascii_values(self, command: str, separator: str = ',', 
                         container: Any = list) -> List[Any]:
        """Query the instrument for ASCII values.
        
        Args:
            command: The query command to send.
            separator: The separator character between values.
            container: The container type for the returned values.
            
        Returns:
            A list (or specified container) of the retrieved values.
        """
        try:
            values = self.connection.query_ascii_values(
                command, separator, container)
            return values
        except Exception as e:
            logger.error(f"Error querying ASCII values from {self.instrument_address}: {str(e)}")
            raise
    
    def reset(self) -> bool:
        """Send reset command (*RST) to the instrument.
        
        This performs a device reset which places the instrument in a known state.
        
        Returns:
            bool: True if reset succeeded, False otherwise.
        """
        try:
            self.connection.write("*RST")
            # Some instruments need time after reset
            time.sleep(0.5)
            logger.info(f"Reset {self.instrument_address}")
            return True
        except Exception as e:
            logger.warning(f"Could not reset {self.instrument_address}: {str(e)}")
            print("Unit could not be reset using *RST command")
            return False

    def clear(self) -> bool:
        """Send clear command (*CLS) to the instrument.
        
        This clears the instrument's error queue and status registers.
        
        Returns:
            bool: True if clear succeeded, False otherwise.
        """
        try:
            self.connection.write("*CLS")
            logger.info(f"Cleared {self.instrument_address}")
            return True
        except Exception as e:
            logger.warning(f"Could not clear {self.instrument_address}: {str(e)}")
            print("Unit could not be cleared using *CLS command")
            return False
            
    def wait_for_operation_complete(self, timeout: float = 10.0) -> bool:
        """Wait for pending operations to complete.
        
        Uses the *OPC? query to wait until all pending commands are completed.
        
        Args:
            timeout: Maximum time to wait in seconds.
            
        Returns:
            bool: True if completed within timeout, False otherwise.
        """
        try:
            start_time = time.time()
            response = self.connection.query("*OPC?", delay=timeout)
            elapsed = time.time() - start_time
            logger.debug(f"Operation completed in {elapsed:.2f} seconds")
            return bool(int(response.strip()))
        except Exception as e:
            logger.warning(f"Error waiting for operation complete: {str(e)}")
            return False
    
    # Abstract methods that should be implemented by all instrument classes
    @abstractmethod
    def get_error(self) -> str:
        """Get the first error from the instrument's error queue.
        
        Returns:
            str: Error message or indication of no error.
        """
        pass