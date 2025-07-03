"""Unit tests for DataProcessor."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from lindas_hydro_scraper.core.data_processor import DataProcessor
from lindas_hydro_scraper.models import Measurement


class TestDataProcessor:
    """Test cases for DataProcessor."""

    @pytest.fixture
    def processor(self):
        """Create a DataProcessor instance."""
        return DataProcessor()

    @pytest.fixture
    def valid_sparql_results(self):
        """Create valid SPARQL results for testing."""
        return {
            "results": {
                "bindings": [
                    {
                        "predicate": {"value": "http://example.com/dimension/measurementTime"},
                        "object": {"value": "2024-01-15T10:30:00Z"},
                    },
                    {
                        "predicate": {"value": "http://example.com/dimension/discharge"},
                        "object": {"value": "123.45"},
                    },
                    {
                        "predicate": {"value": "http://example.com/dimension/waterLevel"},
                        "object": {"value": "456.78"},
                    },
                    {
                        "predicate": {"value": "http://example.com/dimension/waterTemperature"},
                        "object": {"value": "15.5"},
                    },
                    {
                        "predicate": {"value": "http://example.com/dimension/dangerLevel"},
                        "object": {"value": "3"},
                    },
                    {
                        "predicate": {"value": "http://example.com/dimension/isLiter"},
                        "object": {"value": "false"},
                    },
                ]
            }
        }

    def test_process_results_success(self, processor, valid_sparql_results):
        """Test successful processing of valid SPARQL results."""
        station_id = "STATION001"
        result = processor.process_results(valid_sparql_results, station_id)

        assert isinstance(result, Measurement)
        assert result.station_id == station_id
        assert result.discharge == Decimal("123.45")
        assert result.water_level == Decimal("456.78")
        assert result.water_temperature == Decimal("15.5")
        assert result.danger_level == 3
        assert result.is_liter is False

    def test_process_results_empty_results(self, processor):
        """Test processing empty results returns None."""
        empty_results = {}
        result = processor.process_results(empty_results, "STATION001")

        assert result is None

    def test_process_results_no_bindings(self, processor):
        """Test processing results with no bindings returns None."""
        results = {"results": {"bindings": []}}
        result = processor.process_results(results, "STATION001")

        assert result is None

    def test_process_results_missing_timestamp(self, processor):
        """Test processing results without timestamp returns None."""
        results = {
            "results": {
                "bindings": [
                    {
                        "predicate": {"value": "http://example.com/dimension/discharge"},
                        "object": {"value": "123.45"},
                    }
                ]
            }
        }
        result = processor.process_results(results, "STATION001")

        assert result is None

    def test_process_results_no_measurements(self, processor):
        """Test processing results with only timestamp returns None."""
        results = {
            "results": {
                "bindings": [
                    {
                        "predicate": {"value": "http://example.com/dimension/measurementTime"},
                        "object": {"value": "2024-01-15T10:30:00Z"},
                    }
                ]
            }
        }
        result = processor.process_results(results, "STATION001")

        assert result is None

    def test_process_results_invalid_measurement_data(self, processor):
        """Test processing results with invalid measurement data."""
        results = {
            "results": {
                "bindings": [
                    {
                        "predicate": {"value": "http://example.com/dimension/measurementTime"},
                        "object": {"value": "invalid_timestamp"},
                    },
                    {
                        "predicate": {"value": "http://example.com/dimension/discharge"},
                        "object": {"value": "123.45"},
                    },
                ]
            }
        }
        result = processor.process_results(results, "STATION001")

        assert result is None

    def test_validate_results_valid(self, processor, valid_sparql_results):
        """Test validation of valid results structure."""
        assert processor._validate_results(valid_sparql_results) is True

    def test_validate_results_invalid_cases(self, processor):
        """Test validation of various invalid results structures."""
        # None results
        assert processor._validate_results(None) is False

        # Not a dictionary
        assert processor._validate_results("invalid") is False

        # Missing 'results' key
        assert processor._validate_results({}) is False

        # Missing 'bindings' key
        assert processor._validate_results({"results": {}}) is False

        # Empty bindings
        assert processor._validate_results({"results": {"bindings": []}}) is False

    def test_extract_data_all_fields(self, processor, valid_sparql_results):
        """Test extraction of all data fields from SPARQL results."""
        station_id = "STATION001"
        data = processor._extract_data(valid_sparql_results, station_id)

        assert data["station_id"] == station_id
        assert data["timestamp"] == "2024-01-15T10:30:00Z"
        assert data["discharge"] == "123.45"
        assert data["water_level"] == "456.78"
        assert data["water_temperature"] == "15.5"
        assert data["danger_level"] == "3"
        assert data["is_liter"] == "false"

    def test_extract_data_missing_predicate(self, processor):
        """Test extraction with missing predicate in binding."""
        results = {
            "results": {
                "bindings": [
                    {
                        "object": {"value": "123.45"},
                    }
                ]
            }
        }
        data = processor._extract_data(results, "STATION001")

        assert data == {"station_id": "STATION001"}

    def test_extract_data_missing_object(self, processor):
        """Test extraction with missing object value in binding."""
        results = {
            "results": {
                "bindings": [
                    {
                        "predicate": {"value": "http://example.com/dimension/discharge"},
                    }
                ]
            }
        }
        data = processor._extract_data(results, "STATION001")

        assert data == {"station_id": "STATION001"}

    def test_map_predicate_to_field_dimension_uri(self, processor):
        """Test mapping of dimension URIs to field names."""
        mappings = {
            "http://example.com/dimension/measurementTime": "timestamp",
            "http://example.com/dimension/discharge": "discharge",
            "http://example.com/dimension/waterLevel": "water_level",
            "http://example.com/dimension/waterTemperature": "water_temperature",
            "http://example.com/dimension/dangerLevel": "danger_level",
            "http://example.com/dimension/isLiter": "is_liter",
        }

        for uri, expected_field in mappings.items():
            assert processor._map_predicate_to_field(uri) == expected_field

    def test_map_predicate_to_field_example_com_uri(self, processor):
        """Test mapping of example.com URIs to field names."""
        mappings = {
            "http://example.com/measurementTime": "timestamp",
            "http://example.com/discharge": "discharge",
            "http://example.com/waterLevel": "water_level",
            "http://example.com/waterTemperature": "water_temperature",
            "http://example.com/dangerLevel": "danger_level",
            "http://example.com/isLiter": "is_liter",
        }

        for uri, expected_field in mappings.items():
            assert processor._map_predicate_to_field(uri) == expected_field

    def test_map_predicate_to_field_unknown_uri(self, processor):
        """Test mapping of unknown URIs returns None."""
        unknown_uris = [
            "http://unknown.com/property",
            "http://example.com/unknown/property",
            "invalid_uri",
        ]

        for uri in unknown_uris:
            assert processor._map_predicate_to_field(uri) is None

    def test_map_predicate_to_field_unmapped_parameter(self, processor):
        """Test mapping of known URI format but unmapped parameter returns None."""
        assert processor._map_predicate_to_field("http://example.com/dimension/unknownParam") is None

    @patch("lindas_hydro_scraper.core.data_processor.logger")
    def test_process_results_logs_warning_invalid_structure(self, mock_logger, processor):
        """Test that warning is logged for invalid results structure."""
        processor.process_results({}, "STATION001")

        mock_logger.warning.assert_called_with("Invalid results structure for station STATION001")

    @patch("lindas_hydro_scraper.core.data_processor.logger")
    def test_process_results_logs_warning_no_timestamp(self, mock_logger, processor):
        """Test that warning is logged when no timestamp found."""
        results = {
            "results": {
                "bindings": [
                    {
                        "predicate": {"value": "http://example.com/dimension/discharge"},
                        "object": {"value": "123.45"},
                    }
                ]
            }
        }
        processor.process_results(results, "STATION001")

        mock_logger.warning.assert_called_with("No timestamp found for station STATION001")

    @patch("lindas_hydro_scraper.core.data_processor.logger")
    def test_process_results_logs_warning_no_measurements(self, mock_logger, processor):
        """Test that warning is logged when no valid measurements found."""
        results = {
            "results": {
                "bindings": [
                    {
                        "predicate": {"value": "http://example.com/dimension/measurementTime"},
                        "object": {"value": "2024-01-15T10:30:00Z"},
                    }
                ]
            }
        }
        processor.process_results(results, "STATION001")

        mock_logger.warning.assert_called_with("No valid measurements found for station STATION001")

    @patch("lindas_hydro_scraper.core.data_processor.logger")
    def test_process_results_logs_error_on_exception(self, mock_logger, processor):
        """Test that error is logged when exception occurs during measurement creation."""
        results = {
            "results": {
                "bindings": [
                    {
                        "predicate": {"value": "http://example.com/dimension/measurementTime"},
                        "object": {"value": "invalid_timestamp"},
                    },
                    {
                        "predicate": {"value": "http://example.com/dimension/discharge"},
                        "object": {"value": "123.45"},
                    },
                ]
            }
        }
        processor.process_results(results, "STATION001")

        assert mock_logger.error.called
        error_call = mock_logger.error.call_args[0][0]
        assert "Error creating measurement for station STATION001" in error_call