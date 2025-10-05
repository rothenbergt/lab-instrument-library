"""
Base class for all lab instruments in the library.

This module defines a common base class that all instrument-specific classes
can inherit from. It provides shared functionality such as connection handling,
identification, and basic VISA commands.
"""

import pyvisa
import logging
import time
from typing import Optional, Union, List, Any, Tuple, Generator
from abc import ABC, abstractmethod
from contextlib import contextmanager

from .utils.decorators import visa_exception_handler

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
  
    def make_connection(self, instrument_address: str, identify: bool = True) -> bool:
        """Establish a connection to the instrument.
        
        Simplified connection logic with clearer error messages and better logging.
        
        Args:
            instrument_address: VISA address of the instrument.
            identify: Whether to query the instrument ID.
        
        Returns:
            bool: True if connection succeeded, False otherwise.
        """
        try:
            # Make the connection
            self.connection = self.rm.open_resource(instrument_address)
            self.connection.timeout = self.timeout
            
            # Handle identification if requested
            if identify and not self._identify_instrument():
                return False
                
            # Connection successful
            display_name = self.instrumentID if identify and self.instrumentID else \
                          (self.nickname if self.nickname else instrument_address)
            logger.info(f"Connected to {instrument_address}: {display_name}")
            return True
                
        except pyvisa.errors.VisaIOError as e:
            error_message = self._get_visa_error_message(e, instrument_address)
            logger.error(error_message)
            return False
        except Exception as e:
            logger.error(f"Failed to connect to {instrument_address}: {str(e)}")
            return False
    
    def _identify_instrument(self) -> bool:
        """Helper method to identify the instrument.
        
        Returns:
            bool: True if identification succeeded, False otherwise.
        """
        try:
            self.identify()
            if not self.instrumentID:
                logger.warning(f"Connected to {self.instrument_address} but couldn't identify instrument")
                return False
            return True
        except Exception as e:
            logger.warning(f"Connected to {self.instrument_address} but identification failed: {str(e)}")
            return False
    
    def _get_visa_error_message(self, error: pyvisa.errors.VisaIOError, address: str) -> str:
        """Generate a helpful error message for VISA errors.
        
        Args:
            error: The VISA error that occurred
            address: The instrument address
            
        Returns:
            str: A user-friendly error message
        """
        messages = {
            "VI_ERROR_NLISTENERS": f"No listeners at {address}. Check the GPIB address and ensure device is powered on.",
            "VI_ERROR_TMO": f"Connection timeout at {address}. Device not responding.",
            "VI_ERROR_RSRC_NFOUND": f"Resource not found at {address}. Check connections and VISA configuration.",
            "VI_ERROR_CONN_LOST": f"Connection lost to {address}. Check physical connections."
        }
        
        for key, message in messages.items():
            if key in str(error):
                return f"{message} ({error})"
                
        return f"VISA error connecting to {address}: {error}"
            
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def close_connection(self) -> None:
        """Close the connection to the instrument.
        
        This method should be called when finished with the instrument to release resources.
        """
        if self.connection:
            self.connection.close()
            logger.info(f"Connection to {self.instrument_address} closed")
    
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

    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def identify(self) -> Optional[str]:
        """Query the instrument's identification string.
        
        This method sends the standard IEEE-488.2 *IDN? query to identify the instrument.
        
        Returns:
            str: The instrument identification string, or None if identification failed.
        """
        response = self.connection.query("*IDN?").strip()
        self.instrumentID = response
        return self.instrumentID
             
    @visa_exception_handler(default_return_value=None, module_logger=logger)
    def write(self, command: str) -> None:
        """Send a command string to the instrument.
        
        Args:
            command: The command string to send.
            
        Returns:
            None: Returns None if successful, None if operation fails.
        """
        self.connection.write(command)
        logger.debug(f"Wrote to {self.instrument_address}: {command}")
    
    @visa_exception_handler(default_return_value="", module_logger=logger)
    def query(self, command: str, delay: Optional[float] = None) -> str:
        """Send a query to the instrument and return the response.
        
        Args:
            command: The query string to send.
            delay: Optional delay in seconds between write and read operations.
            
        Returns:
            str: The response from the instrument or empty string on failure.
        """
        if delay:
            self.connection.write(command)
            time.sleep(delay)
            response = self.connection.read()
        else:
            response = self.connection.query(command)
        
        logger.debug(f"Queried {self.instrument_address} with '{command}', got '{response}'")
        return response.strip()
    
    @visa_exception_handler(default_return_value=[], module_logger=logger)
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
            A list (or specified container) of the retrieved values, or empty list on failure.
        """
        values = self.connection.query_binary_values(
            command, datatype, is_big_endian, container)
        return values
    
    @visa_exception_handler(default_return_value=[], module_logger=logger)
    def query_ascii_values(self, command: str, separator: str = ',', 
                         container: Any = list) -> List[Any]:
        """Query the instrument for ASCII values.
        
        Args:
            command: The query command to send.
            separator: The separator character between values.
            container: The container type for the returned values.
            
        Returns:
            A list (or specified container) of the retrieved values, or empty list on failure.
        """
        values = self.connection.query_ascii_values(
            command, separator, container)
        return values
    
    @visa_exception_handler(default_return_value=False, module_logger=logger)
    def reset(self) -> bool:
        """Send reset command (*RST) to the instrument.
        
        This performs a device reset which places the instrument in a known state.
        
        Returns:
            bool: True if reset succeeded, False otherwise.
        """
        self.write("*RST")
        # Some instruments need time after reset
        time.sleep(0.5)
        logger.info(f"Reset {self.instrument_address}")
        return True

    @visa_exception_handler(default_return_value=False, module_logger=logger)
    def clear(self) -> bool:
        """Send clear command (*CLS) to the instrument.
        
        This clears the instrument's error queue and status registers.
        
        Returns:
            bool: True if clear succeeded, False otherwise.
        """
        self.connection.write("*CLS")
        logger.info(f"Cleared {self.instrument_address}")
        return True
            
    @visa_exception_handler(default_return_value=False, module_logger=logger)
    def wait_for_operation_complete(self, timeout: float = 10.0) -> bool:
        """Wait for pending operations to complete.
        
        Uses the *OPC? query to wait until all pending commands are completed.
        
        Args:
            timeout: Maximum time to wait in seconds.
            
        Returns:
            bool: True if completed within timeout, False otherwise.
        """
        start_time = time.time()
        response = self.connection.query("*OPC?", delay=timeout)
        elapsed = time.time() - start_time
        logger.debug(f"Operation completed in {elapsed:.2f} seconds")
        return bool(int(response.strip()))
    
    @visa_exception_handler(default_return_value="Error: Unable to retrieve error status", module_logger=logger)
    def get_error(self) -> str:
        """Get the first error from the instrument's error queue.
        
        Most instruments use the SYST:ERR? command to retrieve errors
        from the error queue. Subclasses can override this method if
        their instruments use a different command.
        
        Returns:
            str: Error message or indication of no error.
        """
        response = self.query("SYST:ERR?")
        logger.debug(f"Error query response: {response}")
        return response
    
    @visa_exception_handler(default_return_value="", module_logger=logger)
    def safe_query(self, command: str, default: str = "") -> str:
        """Send a query to the instrument with exception handling.
        
        Args:
            command: Command string to send
            default: Default value to return if query fails
            
        Returns:
            Response from instrument or default value if operation fails
        """
        try:
            return self.query(command)
        except Exception:
            return default

    def is_connected(self) -> bool:
        """Check if the instrument is currently connected.
        
        Returns:
            bool: True if there's an active connection, False otherwise.
        """
        return self.connection is not None and hasattr(self.connection, 'session')
        
    @contextmanager
    def temporary_timeout(self, timeout_ms: int) -> None:
        """Temporarily change the connection timeout.
        
        Args:
            timeout_ms: Timeout value in milliseconds
            
        Yields:
            None
        
        Example:
            with instrument.temporary_timeout(10000):
                # Operation that needs longer timeout
                result = instrument.query("LONG_OPERATION?")
        """
        original_timeout = self.connection.timeout
        try:
            self.connection.timeout = timeout_ms
            yield
        finally:
            self.connection.timeout = original_timeout
            
    @visa_exception_handler(default_return_value=False, module_logger=logger)
    def check_error_status(self) -> Union[bool, str]:
        """Check if the instrument has any errors.
        
        Returns:
            Union[bool, str]: False if no error, error message string if error was found.
        """
        error = self.get_error()
        if not error or "+0," in error or "No error" in error:
            return False
        return error
            
    def set_remote_mode(self) -> bool:
        """Set the instrument to remote operation mode.
        
        This is a generic implementation; specific instruments may need to override this.
        
        Returns:
            bool: True if successfully set to remote mode, False otherwise.
        """
        try:
            # Generic implementation that works with many instruments
            self.write("SYST:REM")
            logger.info(f"Set {self.instrument_address} to remote mode")
            return True
        except Exception as e:
            logger.warning(f"Could not set {self.instrument_address} to remote mode: {str(e)}")
            return False
            
    def set_local_mode(self) -> bool:
        """Set the instrument to local operation mode.
        
        This is a generic implementation; specific instruments may need to override this.
        
        Returns:
            bool: True if successfully set to local mode, False otherwise.
        """
        try:
            # Generic implementation that works with many instruments
            self.write("SYST:LOC")
            logger.info(f"Set {self.instrument_address} to local mode")
            return True
        except Exception as e:
            logger.warning(f"Could not set {self.instrument_address} to local mode: {str(e)}")
            return False