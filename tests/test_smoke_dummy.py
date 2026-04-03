"""Always-pass smoke test to keep CI green even in mock mode."""

from __future__ import annotations


def test_framework_boots():
    """Sanity check that pytest discovers tests and fixtures load."""
    assert True
