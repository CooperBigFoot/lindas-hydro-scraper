"""SPARQL client for querying LINDAS endpoint."""

import logging
import time
from typing import Any

from SPARQLWrapper import JSON, SPARQLWrapper
from SPARQLWrapper.SPARQLExceptions import SPARQLWrapperException

from .constants import INITIAL_RETRY_DELAY, MAX_RETRIES

logger = logging.getLogger(__name__)


class SparqlClient:
    """Client for executing SPARQL queries with retry logic."""

    def __init__(
        self,
        endpoint_url: str,
        max_retries: int = MAX_RETRIES,
        initial_delay: float = INITIAL_RETRY_DELAY,
    ) -> None:
        """Initialize SPARQL client.

        Args:
            endpoint_url: SPARQL endpoint URL.
            max_retries: Maximum number of retry attempts.
            initial_delay: Initial retry delay in seconds.
        """
        self.endpoint_url = endpoint_url
        self.max_retries = max_retries
        self.initial_delay = initial_delay

        self._client = SPARQLWrapper(endpoint_url)
        self._client.setReturnFormat(JSON)
        self._client.setMethod("POST")

    def execute_query(self, query: str) -> dict[str, Any] | None:
        """Execute SPARQL query with retry logic.

        Args:
            query: SPARQL query string.

        Returns:
            Query results as dictionary or None if failed.
        """
        self._client.setQuery(query)

        retry_delay = self.initial_delay
        last_error = None

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Executing query (attempt {attempt + 1}/{self.max_retries})")
                results = self._client.query().convert()

                # Validate results
                if self._validate_results(results):
                    bindings_count = len(results.get("results", {}).get("bindings", []))
                    logger.info(f"Query successful, retrieved {bindings_count} bindings")
                    return results
                else:
                    logger.warning("Query returned empty or invalid results")
                    return None

            except SPARQLWrapperException as e:
                last_error = e
                logger.warning(
                    f"SPARQL query failed (attempt {attempt + 1}/{self.max_retries}): {e}"
                )

                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff

            except Exception as e:
                logger.error(f"Unexpected error executing query: {e}")
                return None

        logger.error(f"Query failed after {self.max_retries} attempts. Last error: {last_error}")
        return None

    def _validate_results(self, results: Any) -> bool:
        """Validate query results structure.

        Args:
            results: Results to validate.

        Returns:
            True if valid, False otherwise.
        """
        return (
            isinstance(results, dict)
            and "results" in results
            and "bindings" in results["results"]
            and isinstance(results["results"]["bindings"], list)
        )

    def test_connection(self) -> bool:
        """Test connection to SPARQL endpoint.

        Returns:
            True if connection successful, False otherwise.
        """
        test_query = "SELECT ?s WHERE { ?s ?p ?o } LIMIT 1"

        try:
            result = self.execute_query(test_query)
            return result is not None
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
