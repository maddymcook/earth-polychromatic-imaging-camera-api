"""Shared pytest configuration and fixtures."""

import sys
from pathlib import Path

import pytest

# Add the src directory to the Python path for imports
src_dir = Path(__file__).parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment for all tests."""
    # Any global setup can go here
    yield
    # Any cleanup can go here
