"""Process SPARQL query results into structured data."""

import logging
from typing import Any

from ..models import Measurement

logger = logging.getLogger(__name__)


class DataProcessor:
    """Process raw SPARQL results into structured measurements."""

    def process_results(
        self, results: dict[str, Any], station_id: str
    ) -> Measurement | None:
        """Process SPARQL results for a single station.

        Args:
            results: Raw SPARQL query results.
            station_id: Station identifier.

        Returns:
            Measurement object if valid data found, None otherwise.
        """
        if not self._validate_results(results):
            logger.warning(f"Invalid results structure for station {station_id}")
            return None

        # Extract data from results
        data = self._extract_data(results, station_id)

        # Check if we have a timestamp and at least one measurement
        if not data.get("timestamp"):
            logger.warning(f"No timestamp found for station {station_id}")
            return None

        try:
            measurement = Measurement(**data)

            # Only return if we have actual measurements
            if measurement.has_measurements():
                return measurement
            else:
                logger.warning(f"No valid measurements found for station {station_id}")
                return None

        except Exception as e:
            logger.error(f"Error creating measurement for station {station_id}: {e}")
            return None

    def _validate_results(self, results: dict[str, Any]) -> bool:
        """Validate SPARQL results structure.

        Args:
            results: Results to validate.

        Returns:
            True if valid, False otherwise.
        """
        return bool(
            results
            and isinstance(results, dict)
            and "results" in results
            and "bindings" in results["results"]
            and results["results"]["bindings"]
        )

    def _extract_data(self, results: dict[str, Any], station_id: str) -> dict[str, Any]:
        """Extract measurement data from SPARQL results.

        Args:
            results: SPARQL query results.
            station_id: Station identifier.

        Returns:
            Dictionary of extracted data.
        """
        data = {"station_id": station_id}

        for binding in results["results"]["bindings"]:
            predicate = binding.get("predicate", {}).get("value", "")
            value = binding.get("object", {}).get("value")

            if not predicate or value is None:
                continue

            # Map predicate to field name
            field_name = self._map_predicate_to_field(predicate)
            if field_name:
                data[field_name] = value

        return data

    def _map_predicate_to_field(self, predicate_uri: str) -> str | None:
        """Map SPARQL predicate URI to measurement field name.

        Args:
            predicate_uri: Full predicate URI.

        Returns:
            Field name or None if not recognized.
        """
        # Extract parameter name from URI
        if "/dimension/" in predicate_uri:
            param_name = predicate_uri.split("/dimension/")[-1]
        elif "example.com/" in predicate_uri:
            param_name = predicate_uri.split("example.com/")[-1]
        else:
            return None

        # Map to field names
        field_mapping = {
            "measurementTime": "timestamp",
            "discharge": "discharge",
            "waterLevel": "water_level",
            "waterTemperature": "water_temperature",
            "dangerLevel": "danger_level",
            "isLiter": "is_liter",
        }

        return field_mapping.get(param_name)
