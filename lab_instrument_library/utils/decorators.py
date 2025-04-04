"""
Decorators for the lab instrument library.

This module provides utility decorators that can be used across
the library for common cross-cutting concerns like exception handling.
"""

import sys
import logging
import functools
import pyvisa
import traceback
from typing import Callable, Any, TypeVar, Optional, Dict, Union

# Setup module logger
logger = logging.getLogger(__name__)

# Type variable for the decorated function's return type
T = TypeVar('T')

def visa_exception_handler(
    default_return_value: Any = sys.maxsize,
    module_logger: Optional[logging.Logger] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Create a decorator to handle common VISA/instrument exceptions.
    
    This decorator wraps instrument communication functions to provide consistent
    exception handling for VISA operations, value conversions, and other common errors.
    
    Args:
        default_return_value: Value to return if an exception occurs.
        module_logger: Logger to use for error messages. If None, uses the calling module's logger.
    
    Returns:
        Decorator function that wraps the target function with exception handling.
    """
    # Use provided logger or default to module's logger
    log = module_logger or logger
        
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(self, *args: Any, **kwargs: Any) -> Union[T, Any]:
            try:
                return func(self, *args, **kwargs)
            except ValueError as ex:
                # Value conversion errors (e.g., float parsing)
                instrument_id = getattr(self, 'instrument_ID', 'unknown instrument')
                address = getattr(self, 'instrument_address', 'unknown address')
                error_msg = (f"Could not convert returned value from {instrument_id} "
                           f"at {address} in method {func.__name__}: {str(ex)}")
                log.error(error_msg)
                print(error_msg)
                return default_return_value
            except TypeError as ex:
                # Type errors (wrong parameter types)
                log.error(f"Type error in {func.__name__}: {str(ex)}")
                print(f"Wrong parameter type: {str(ex)}")
                return default_return_value
            except pyvisa.errors.VisaIOError as ex:
                # VISA communication errors
                log.error(f"VISA error in {func.__name__}: {ex.abbreviation}")
                print(f"VISA exception: {ex.abbreviation}")
                
                address = getattr(self, 'instrument_address', 'unknown')
                
                # Handle specific VISA errors with helpful messages
                if "VI_ERROR_NLISTENERS" in ex.abbreviation:
                    print(f"No listeners at {address}. Check the GPIB address.")
                elif "VI_ERROR_TMO" in ex.abbreviation:
                    print(f"Timeout at {address}. Check the instrument.")
                elif "VI_ERROR_RSRC_NFOUND" in ex.abbreviation:
                    print("Resource not found. Check connections and VISA configuration.")
                
                return default_return_value
            except Exception as ex:
                # Catch-all for unexpected exceptions
                log.error(f"Unexpected error in {func.__name__}: {type(ex).__name__}: {str(ex)}")
                log.debug(f"Exception traceback: {traceback.format_exc()}")
                print(f"Unexpected error: {type(ex).__name__}: {str(ex)}")
                return default_return_value
        
        return wrapper
    
    return decorator
