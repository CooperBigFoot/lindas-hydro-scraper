"""Unit tests for Measurement model."""

from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from lindas_hydro_scraper.models.measurement import Measurement


class TestMeasurement:
    """Test cases for Measurement model."""

    def test_create_measurement_with_all_fields(self):
        """Test creating a measurement with all fields populated."""
        measurement = Measurement(
            station_id="STATION001",
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            discharge=Decimal("123.45"),
            water_level=Decimal("456.78"),
            water_temperature=Decimal("15.5"),
            danger_level=3,
            is_liter=False,
        )

        assert measurement.station_id == "STATION001"
        assert measurement.timestamp == datetime(2024, 1, 15, 10, 30, 0)
        assert measurement.discharge == Decimal("123.45")
        assert measurement.water_level == Decimal("456.78")
        assert measurement.water_temperature == Decimal("15.5")
        assert measurement.danger_level == 3
        assert measurement.is_liter is False

    def test_create_measurement_minimal(self):
        """Test creating a measurement with only required fields."""
        measurement = Measurement(
            station_id="STATION001",
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
        )

        assert measurement.station_id == "STATION001"
        assert measurement.timestamp == datetime(2024, 1, 15, 10, 30, 0)
        assert measurement.discharge is None
        assert measurement.water_level is None
        assert measurement.water_temperature is None
        assert measurement.danger_level is None
        assert measurement.is_liter is None

    def test_parse_decimal_from_string(self):
        """Test decimal parsing from string values."""
        measurement = Measurement(
            station_id="STATION001",
            timestamp=datetime.now(),
            discharge="123.45",
            water_level="456.78",
            water_temperature="15.5",
        )

        assert measurement.discharge == Decimal("123.45")
        assert measurement.water_level == Decimal("456.78")
        assert measurement.water_temperature == Decimal("15.5")

    def test_parse_decimal_from_float(self):
        """Test decimal parsing from float values."""
        measurement = Measurement(
            station_id="STATION001",
            timestamp=datetime.now(),
            discharge=123.45,
            water_level=456.78,
            water_temperature=15.5,
        )

        assert measurement.discharge == Decimal("123.45")
        assert measurement.water_level == Decimal("456.78")
        assert measurement.water_temperature == Decimal("15.5")

    def test_parse_decimal_invalid_values(self):
        """Test decimal parsing with invalid values returns None."""
        measurement = Measurement(
            station_id="STATION001",
            timestamp=datetime.now(),
            discharge="invalid",
            water_level="not_a_number",
            water_temperature="",
        )

        assert measurement.discharge is None
        assert measurement.water_level is None
        assert measurement.water_temperature is None

    def test_parse_timestamp_from_iso_string(self):
        """Test timestamp parsing from ISO format string."""
        iso_timestamp = "2024-01-15T10:30:00+00:00"
        measurement = Measurement(
            station_id="STATION001",
            timestamp=iso_timestamp,
        )

        expected = datetime.fromisoformat("2024-01-15T10:30:00+00:00")
        assert measurement.timestamp == expected

    def test_parse_timestamp_from_iso_string_with_z(self):
        """Test timestamp parsing from ISO format with Z suffix."""
        iso_timestamp = "2024-01-15T10:30:00Z"
        measurement = Measurement(
            station_id="STATION001",
            timestamp=iso_timestamp,
        )

        expected = datetime.fromisoformat("2024-01-15T10:30:00+00:00")
        assert measurement.timestamp == expected

    def test_parse_timestamp_invalid_format(self):
        """Test timestamp parsing with invalid format raises error."""
        with pytest.raises(ValidationError) as exc_info:
            Measurement(
                station_id="STATION001",
                timestamp="invalid_timestamp",
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "timestamp" in str(errors[0])

    def test_danger_level_validation(self):
        """Test danger level range validation."""
        # Valid danger levels
        for level in range(0, 6):
            measurement = Measurement(
                station_id="STATION001",
                timestamp=datetime.now(),
                danger_level=level,
            )
            assert measurement.danger_level == level

        # Invalid danger levels
        for invalid_level in [-1, 6, 10]:
            with pytest.raises(ValidationError) as exc_info:
                Measurement(
                    station_id="STATION001",
                    timestamp=datetime.now(),
                    danger_level=invalid_level,
                )

            errors = exc_info.value.errors()
            assert len(errors) == 1
            assert "danger_level" in str(errors[0])

    def test_has_measurements_with_values(self):
        """Test has_measurements returns True when measurements exist."""
        # With discharge only
        measurement = Measurement(
            station_id="STATION001",
            timestamp=datetime.now(),
            discharge=Decimal("100"),
        )
        assert measurement.has_measurements() is True

        # With water level only
        measurement = Measurement(
            station_id="STATION001",
            timestamp=datetime.now(),
            water_level=Decimal("200"),
        )
        assert measurement.has_measurements() is True

        # With water temperature only
        measurement = Measurement(
            station_id="STATION001",
            timestamp=datetime.now(),
            water_temperature=Decimal("15"),
        )
        assert measurement.has_measurements() is True

        # With all measurements
        measurement = Measurement(
            station_id="STATION001",
            timestamp=datetime.now(),
            discharge=Decimal("100"),
            water_level=Decimal("200"),
            water_temperature=Decimal("15"),
        )
        assert measurement.has_measurements() is True

    def test_has_measurements_without_values(self):
        """Test has_measurements returns False when no measurements exist."""
        measurement = Measurement(
            station_id="STATION001",
            timestamp=datetime.now(),
            danger_level=3,
            is_liter=True,
        )
        assert measurement.has_measurements() is False

    def test_to_csv_dict(self):
        """Test conversion to CSV dictionary."""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        measurement = Measurement(
            station_id="STATION001",
            timestamp=timestamp,
            discharge=Decimal("123.45"),
            water_level=Decimal("456.78"),
            water_temperature=Decimal("15.5"),
            danger_level=3,
            is_liter=False,
        )

        csv_dict = measurement.to_csv_dict()

        assert csv_dict == {
            "timestamp": timestamp.isoformat(),
            "station_id": "STATION001",
            "discharge": "123.45",
            "water_level": "456.78",
            "water_temperature": "15.5",
            "danger_level": "3",
            "is_liter": "false",
        }

    def test_to_csv_dict_with_none_values(self):
        """Test conversion to CSV dictionary with None values."""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        measurement = Measurement(
            station_id="STATION001",
            timestamp=timestamp,
        )

        csv_dict = measurement.to_csv_dict()

        assert csv_dict == {
            "timestamp": timestamp.isoformat(),
            "station_id": "STATION001",
            "discharge": None,
            "water_level": None,
            "water_temperature": None,
            "danger_level": None,
            "is_liter": None,
        }

    def test_unique_key_generation(self):
        """Test unique key generation for deduplication."""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        measurement = Measurement(
            station_id="STATION001",
            timestamp=timestamp,
        )

        expected_key = f"{timestamp.isoformat()}_STATION001"
        assert measurement.unique_key == expected_key

    def test_str_strip_whitespace(self):
        """Test that string fields have whitespace stripped."""
        measurement = Measurement(
            station_id="  STATION001  ",
            timestamp=datetime.now(),
        )

        assert measurement.station_id == "STATION001"

    def test_timestamp_required(self):
        """Test that timestamp is required."""
        with pytest.raises(ValidationError) as exc_info:
            Measurement(station_id="STATION001")

        errors = exc_info.value.errors()
        assert any("timestamp" in str(error) for error in errors)

    def test_station_id_required(self):
        """Test that station_id is required."""
        with pytest.raises(ValidationError) as exc_info:
            Measurement(timestamp=datetime.now())

        errors = exc_info.value.errors()
        assert any("station_id" in str(error) for error in errors)