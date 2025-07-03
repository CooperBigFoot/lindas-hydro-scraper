"""Shared pytest fixtures and configuration."""

import pytest


@pytest.fixture
def sample_station_id():
    """Provide a sample station ID for testing."""
    return "STATION001"


@pytest.fixture
def sample_sparql_endpoint():
    """Provide a sample SPARQL endpoint URL for testing."""
    return "http://example.com/sparql"