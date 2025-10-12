"""
Decorators for the lab instrument library.

This module provides utility decorators that can be used across
the library for common cross-cutting concerns like exception handling.
"""

import functools
import logging
import sys
import time
import traceback
from typing import Any, Callable, List, Optional, Type, TypeVar, Union

import pyvisa

# Setup module logger
logger = logging.getLogger(__name__)

# Type variable for the decorated function's return type
T = TypeVar('T')


def visa_exception_handler(
    default_return_value: Any = sys.maxsize,
    module_logger: Optional[logging.Logger] = None,
    retry_count: int = 0,
    retry_delay: float = 1.0,
    log_success: bool = False,
    suppress_traceback: bool = False,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Create a decorator to handle common VISA/instrument exceptions.

    This decorator wraps instrument communication functions to provide consistent
    exception handling for VISA operations, value conversions, and other common errors.

    Args:
        default_return_value: Value to return if all exception handling fails.
        module_logger: Logger to use for error messages. If None, uses the calling module's logger.
        retry_count: Number of times to retry the operation before giving up (0 = no retry).
        retry_delay: Delay in seconds between retry attempts.
        log_success: Whether to log successful operations (useful for debugging).
        suppress_traceback: Whether to omit the traceback from logged errors.

    Returns:
        Decorator function that wraps the target function with exception handling.

    Example:
        @visa_exception_handler(default_return_value=None, retry_count=3)
        def query_sensitive_instrument(self, command):
            # This function will be retried up to 3 times if it fails
            return self.connection.query(command)
    """
    # Use provided logger or default to module's logger
    log = module_logger or logger

    # Mapping of common VISA error codes to human-friendly explanations
    visa_error_messages = {
        "VI_ERROR_NLISTENERS": "No listeners found. Device may be off or address may be incorrect.",
        "VI_ERROR_TMO": "Operation timed out. Device may be busy or unresponsive.",
        "VI_ERROR_RSRC_NFOUND": "Resource not found. Check cables and VISA configuration.",
        "VI_ERROR_CONN_LOST": "Connection lost. Check cables and device power.",
        "VI_ERROR_INV_OBJECT": "Invalid object. VISA session may have been closed.",
        "VI_ERROR_NSUP_OPER": "Operation not supported by device.",
        "VI_ERROR_RAW_WR_PROT_VIOL": "Write to protected address. Check instrument settings.",
        "VI_ERROR_RAW_RD_PROT_VIOL": "Read from protected address. Check instrument settings.",
        "VI_ERROR_BERR": "Bus error occurred. Check interface configuration.",
        "VI_ERROR_NCIC": "Not controller-in-charge. Another controller may be active.",
        "VI_ERROR_INV_SETUP": "Invalid setup. Check instrument configuration.",
        "VI_ERROR_QUEUE_OVERFLOW": "Queue overflow. Too many operations queued.",
        "VI_ERROR_ALLOC": "Insufficient memory. Check system resources.",
        "VI_ERROR_INSTR_NFOUND": "Instrument not found. Check address and connections.",
    }

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(self, *args: Any, **kwargs: Any) -> Union[T, Any]:
            instrument_id = getattr(self, 'instrumentID', getattr(self, 'instrument_ID', 'unknown instrument'))
            address = getattr(self, 'instrument_address', 'unknown address')

            # Add retry logic
            attempt = 0
            max_attempts = retry_count + 1  # +1 for the initial attempt

            while attempt < max_attempts:
                try:
                    start_time = time.time()
                    result = func(self, *args, **kwargs)
                    elapsed = time.time() - start_time

                    # Log success if requested (useful for performance monitoring)
                    if log_success:
                        log.debug(
                            f"Successfully executed {func.__name__} on {instrument_id} "
                            f"at {address} in {elapsed:.3f}s"
                        )

                    return result

                except ValueError as ex:
                    # Value conversion errors (e.g., float parsing)
                    error_msg = (
                        f"Could not convert returned value from {instrument_id} "
                        f"at {address} in method {func.__name__}: {str(ex)}"
                    )
                    log.error(error_msg)

                    # For value errors, don't retry as they're likely to persist
                    return default_return_value

                except TypeError as ex:
                    # Type errors (wrong parameter types)
                    error_msg = f"Type error in {func.__name__}: {str(ex)}"
                    log.error(error_msg)

                    # For type errors, don't retry as they're likely to persist
                    return default_return_value

                except pyvisa.errors.VisaIOError as ex:
                    # Get a user-friendly error message if available
                    friendly_msg = ""
                    for error_code, message in visa_error_messages.items():
                        if error_code in ex.abbreviation:
                            friendly_msg = f" - {message}"
                            break

                    error_msg = f"VISA error in {func.__name__} on {instrument_id} at {address}: {ex.abbreviation}{friendly_msg}"

                    # Log the error with appropriate level based on retry strategy
                    if attempt < max_attempts - 1:
                        log.warning(f"{error_msg} (attempt {attempt + 1}/{max_attempts}, retrying in {retry_delay}s)")
                    else:
                        log.error(error_msg)

                    # Only retry certain VISA errors that might be transient
                    retriable_errors = ["VI_ERROR_TMO", "VI_ERROR_CONN_LOST", "VI_ERROR_RSRC_BUSY"]
                    can_retry = any(code in ex.abbreviation for code in retriable_errors)

                    if can_retry and attempt < max_attempts - 1:
                        attempt += 1
                        time.sleep(retry_delay)
                        continue
                    return default_return_value

                except Exception as ex:
                    # Catch-all for unexpected exceptions
                    tb = "" if suppress_traceback else f"\nTraceback: {traceback.format_exc()}"
                    error_msg = (
                        f"Unexpected error in {func.__name__} on {instrument_id} at {address}: "
                        f"{type(ex).__name__}: {str(ex)}{tb}"
                    )

                    log.error(error_msg)

                    # For unexpected errors, attempt retry if configured
                    if attempt < max_attempts - 1:
                        attempt += 1
                        time.sleep(retry_delay)
                        continue
                    return default_return_value

        return wrapper

    return decorator


def parameter_validator(**validators: Callable[[Any], bool]):
    """Decorator to validate parameters before executing a function.

    This decorator checks that each specified parameter meets its validation
    criteria before allowing the function to execute.

    Args:
        **validators: Dictionary of parameter names to validation functions.
            Each function should take a single argument and return True if valid.

    Returns:
        The decorator function.

    Example:
        @parameter_validator(
            frequency=lambda f: 0 < f < 1e9,
            amplitude=lambda a: 0 <= a <= 10
        )
        def set_output(self, frequency, amplitude):
            # This will only execute if frequency and amplitude are valid
            self.write(f"FREQ {frequency}")
            self.write(f"VOLT {amplitude}")
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Get function signature
            import inspect

            sig = inspect.signature(func)
            bound_args = sig.bind(self, *args, **kwargs)
            bound_args.apply_defaults()

            # Extract actual parameter values (excluding 'self')
            actual_args = dict(bound_args.arguments)
            actual_args.pop('self', None)

            # Validate parameters
            for param_name, validator in validators.items():
                if param_name in actual_args:
                    value = actual_args[param_name]
                    if not validator(value):
                        error_msg = f"Invalid value for parameter '{param_name}': {value}"
                        logger.error(error_msg)
                        raise ValueError(error_msg)

            # All validations passed, call the function
            return func(self, *args, **kwargs)

        return wrapper

    return decorator


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    retriable_exceptions: List[Type[Exception]] = None,
    logger: Optional[logging.Logger] = None,
):
    """Decorator to retry a function multiple times before giving up.

    Args:
        max_attempts: Maximum number of attempts (including first try).
        delay: Time to wait between retries in seconds.
        retriable_exceptions: List of exception types that should trigger a retry.
            If None, all exceptions will trigger retries.
        logger: Logger to use. If None, uses this module's logger.

    Returns:
        The decorator function.
    """
    log = logger or logging.getLogger(__name__)

    # Default to retrying on any exception if none specified
    if retriable_exceptions is None:
        retriable_exceptions = [Exception]

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts_left = max_attempts

            while attempts_left > 0:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts_left -= 1

                    # Check if this exception should trigger a retry
                    should_retry = any(isinstance(e, exc_type) for exc_type in retriable_exceptions)

                    if not should_retry or attempts_left == 0:
                        # If not a retriable exception or no attempts left, re-raise
                        log.error(f"Function {func.__name__} failed after {max_attempts} attempts: {str(e)}")
                        raise

                    # Log the retry attempt
                    log.warning(f"Retry {max_attempts - attempts_left}/{max_attempts-1} for {func.__name__}: {str(e)}")
                    time.sleep(delay)

        return wrapper

    return decorator
