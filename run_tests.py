#!/usr/bin/env python3
"""
Test runner script for the lab instruments library.

This script provides a convenient way to run the unit tests and/or
integration tests for the lab instruments library.
"""

import argparse
import os
import subprocess
import sys
import time


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run tests for lab instruments library")
    parser.add_argument("-u", "--unit-tests", action="store_true", help="Run unit tests with mocks")
    parser.add_argument(
        "-i", "--integration-tests", action="store_true", help="Run integration tests with real hardware"
    )
    parser.add_argument("-a", "--all-tests", action="store_true", help="Run all tests")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-k", "--keyword", type=str, help="Only run tests matching the given keyword expression")
    parser.add_argument("-x", "--stop-on-first-failure", action="store_true", help="Stop on first test failure")
    parser.add_argument("-s", "--show-output", action="store_true", help="Show test output")
    parser.add_argument("-d", "--discover", action="store_true", help="Just discover and list available instruments")

    args = parser.parse_args()

    # Default to unit tests if nothing specified
    if not (args.unit_tests or args.integration_tests or args.all_tests or args.discover):
        args.unit_tests = True

    return args


def discover_instruments():
    """Discover available instruments and print information."""
    try:
        import pyvisa

        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()

        if not resources:
            print("No VISA resources found.")
            return

        print("Found VISA resources:")
        for i, resource in enumerate(resources):
            print(f"  {i+1}. {resource}")

            try:
                # Open the resource with a short timeout
                instrument = rm.open_resource(resource)
                instrument.timeout = 1000

                # Try to identify it
                idn = instrument.query("*IDN?").strip()
                print(f"     Identified as: {idn}")

                # Close the connection
                instrument.close()
            except Exception as e:
                print(f"     Error identifying: {str(e)}")
    except ImportError:
        print("PyVISA not installed. Cannot discover instruments.")
    except Exception as e:
        print(f"Error discovering instruments: {str(e)}")


def run_tests(args):
    """Run the specified tests.

    Args:
        args: Parsed command line arguments

    Returns:
        int: Return code (0 for success, non-zero for failure)
    """
    if args.discover:
        discover_instruments()
        return 0

    # Determine which tests to run
    test_dirs = []

    if args.unit_tests or args.all_tests:
        test_dirs.append("tests")

    if args.integration_tests or args.all_tests:
        test_dirs.append("tests/integration")
        # Set environment variable to enable live instrument tests
        os.environ["USE_LIVE_INSTRUMENTS"] = "1"

    # Build pytest command
    cmd = ["pytest"]

    if args.verbose:
        cmd.append("-v")

    if args.keyword:
        cmd.extend(["-k", args.keyword])

    if args.stop_on_first_failure:
        cmd.append("-x")

    if args.show_output:
        cmd.append("-s")

    cmd.extend(test_dirs)

    # Run tests
    print("\nRunning tests with command:", " ".join(cmd))
    print("-" * 80)

    start_time = time.time()
    result = subprocess.run(cmd)
    elapsed_time = time.time() - start_time

    print("-" * 80)
    print(f"Tests completed in {elapsed_time:.2f} seconds")
    if result.returncode == 0:
        print("All tests passed!")
    else:
        print(f"Tests failed with return code {result.returncode}")

    return result.returncode


if __name__ == "__main__":
    args = parse_args()
    sys.exit(run_tests(args))
