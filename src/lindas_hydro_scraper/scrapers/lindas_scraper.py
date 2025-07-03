"""Main LINDAS hydro data scraper implementation."""

import logging

from ..core import DataProcessor, Settings, SparqlQueryBuilder
from ..core.sparql_client import SparqlClient
from ..models import Measurement, QueryParameters
from ..utils.csv_handler import CsvHandler

logger = logging.getLogger(__name__)


class LindasHydroScraper:
    """Scraper for LINDAS hydrological data."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize scraper with configuration.

        Args:
            settings: Application settings. If None, loads from environment.
        """
        self.settings = settings or Settings()
        self.settings.ensure_directories()

        # Initialize components
        self.sparql_client = SparqlClient(
            endpoint_url=self.settings.sparql_endpoint,
            max_retries=self.settings.retry_max_attempts,
            initial_delay=self.settings.retry_delay,
        )
        self.query_builder = SparqlQueryBuilder(base_url=self.settings.sparql_base_url)
        self.data_processor = DataProcessor()
        self.csv_handler = CsvHandler(self.settings.output_path)

    def run(self) -> None:
        """Run the scraper for all configured sites."""
        logger.info(
            f"Starting data collection for {len(self.settings.site_codes)} sites"
        )

        # Test connection first
        if not self.sparql_client.test_connection():
            logger.error("Failed to connect to SPARQL endpoint")
            return

        measurements: list[Measurement] = []
        errors = 0

        # Process each site
        for site_code in self.settings.site_codes:
            try:
                measurement = self._scrape_site(site_code)
                if measurement:
                    measurements.append(measurement)
                else:
                    logger.warning(f"No data retrieved for site {site_code}")

            except Exception as e:
                logger.error(f"Error processing site {site_code}: {e}")
                errors += 1
                continue

        # Save results
        if measurements:
            new_count = self.csv_handler.save_measurements(measurements)
            logger.info(
                f"Completed: {len(measurements)} sites processed, "
                f"{new_count} new records saved, {errors} errors"
            )
        else:
            logger.warning("No measurements collected from any site")

    def _scrape_site(self, site_code: str) -> Measurement | None:
        """Scrape data for a single site.

        Args:
            site_code: Station code to scrape.

        Returns:
            Measurement object or None if no data.
        """
        logger.debug(f"Processing site {site_code}")

        # Build query
        query_params = QueryParameters(
            site_code=site_code,
            parameters=self.settings.parameters,
        )

        try:
            query = self.query_builder.build_query(query_params)
        except ValueError as e:
            logger.error(f"Invalid parameters for site {site_code}: {e}")
            return None

        # Execute query
        results = self.sparql_client.execute_query(query)
        if not results:
            return None

        # Process results
        measurement = self.data_processor.process_results(results, site_code)

        if measurement:
            logger.debug(f"Retrieved measurement for site {site_code}: {measurement.timestamp}")

        return measurement

    def clean_duplicates(self) -> int:
        """Clean duplicate records from CSV file.

        Returns:
            Number of duplicates removed.
        """
        try:
            removed = self.csv_handler.remove_duplicates()
            if removed > 0:
                logger.info(f"Removed {removed} duplicate records")
            else:
                logger.info("No duplicates found")
            return removed
        except Exception as e:
            logger.error(f"Error cleaning duplicates: {e}")
            return 0
