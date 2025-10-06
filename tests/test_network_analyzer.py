"""
Tests for network analyzer helpers and data retrieval.
"""

import pytest


def test_network_analyzer_helpers_and_trace(mock_network_analyzer):
    vna = mock_network_analyzer

    # Basic sweep and settings
    vna.set_sweep_parameters(1e6, 10e6, points=3)
    vna.set_if_bandwidth(1000)
    vna.set_averaging(count=8, enabled=True)
    vna.set_sweep_type("LIN")
    vna.set_format("MLOG")
    vna.enable_source(True)
    vna.set_trigger_source("IMM")

    # Perform sweep and fetch data
    ok = vna.perform_sweep(wait=True)
    assert ok is True

    freqs, values = vna.get_trace_data()
    assert len(freqs) == 3
    assert len(values) == 3

    # Touchstone saving is a write-only operation; ensure no error
    assert vna.save_touchstone("test_data", ports=2) is True
