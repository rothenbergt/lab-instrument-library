"""
Unit tests for utility functions in pylabinstruments.utils.utilities
"""

import os
import re

import pytest

from pylabinstruments.utils.utilities import (
    create_run_folder,
    format_bytes,
    is_valid_ip,
    parse_numeric,
    scan_gpib_devices,
    stringToFloat,
    stringToInt,
)


def test_parse_numeric_basic():
    assert parse_numeric("12.34V") == 12.34
    assert parse_numeric("100Ω") == 100

    with pytest.raises(ValueError):
        parse_numeric("abc")


def test_stringToInt_and_stringToFloat():
    assert stringToInt("123abc") == 123
    assert stringToFloat("3.14V") == 3.14

    # On failure, return 0/0.0 for backward compatibility
    assert stringToInt("bad") == 0
    assert stringToFloat("bad") == 0.0


def test_is_valid_ip():
    assert is_valid_ip("192.168.1.1") is True
    assert is_valid_ip("255.255.255.255") is True
    assert is_valid_ip("256.1.1.1") is False
    assert is_valid_ip("not.an.ip") is False


def test_format_bytes():
    assert format_bytes(512) == "512 B"
    assert format_bytes(2048) == "2.00 KB"
    assert format_bytes(1048576) == "1.00 MB"


def test_create_run_folder(tmp_path):
    base = tmp_path / "runs"
    base.mkdir()

    run1 = create_run_folder(str(base))
    assert os.path.isdir(run1)
    assert os.path.basename(os.path.normpath(run1)) == "run1"

    run2 = create_run_folder(str(base))
    assert os.path.isdir(run2)
    assert os.path.basename(os.path.normpath(run2)) == "run2"


def test_scan_gpib_devices(mock_visa):
    # Limit to a single address so the test is fast and deterministic
    devices = scan_gpib_devices(start=22, end=22, verbose=False)
    # Our mock creates a default resource with HP34401A IDN
    assert 22 in devices
    assert re.search(r"34401A|Mock Instrument|KEITHLEY|TEKTRONIX", devices[22])
