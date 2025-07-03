"""Unit tests for SparqlClient."""

import time
from unittest.mock import MagicMock, Mock, patch

import pytest
from SPARQLWrapper.SPARQLExceptions import SPARQLWrapperException

from lindas_hydro_scraper.core.sparql_client import SparqlClient


class TestSparqlClient:
    """Test cases for SparqlClient."""

    @pytest.fixture
    def client(self):
        """Create a SparqlClient instance."""
        return SparqlClient(
            endpoint_url="http://example.com/sparql",
            max_retries=3,
            initial_delay=0.1,
        )

    @pytest.fixture
    def mock_sparql_wrapper(self):
        """Create a mock SPARQLWrapper."""
        with patch("lindas_hydro_scraper.core.sparql_client.SPARQLWrapper") as mock:
            yield mock

    @pytest.fixture
    def valid_query_results(self):
        """Create valid query results."""
        return {
            "results": {
                "bindings": [
                    {"s": {"value": "http://example.com/subject1"}},
                    {"s": {"value": "http://example.com/subject2"}},
                ]
            }
        }

    def test_init(self, mock_sparql_wrapper):
        """Test client initialization."""
        endpoint_url = "http://example.com/sparql"
        client = SparqlClient(endpoint_url)

        assert client.endpoint_url == endpoint_url
        assert client.max_retries == 3  # Default from constants
        assert client.initial_delay == 2  # Default from constants

        mock_sparql_wrapper.assert_called_once_with(endpoint_url)
        mock_instance = mock_sparql_wrapper.return_value
        mock_instance.setReturnFormat.assert_called_once()
        mock_instance.setMethod.assert_called_once_with("POST")

    def test_execute_query_success(self, client, mock_sparql_wrapper, valid_query_results):
        """Test successful query execution."""
        mock_instance = Mock()
        mock_sparql_wrapper.return_value = mock_instance

        # Create new client to use mocked SPARQLWrapper
        client = SparqlClient("http://example.com/sparql")

        # Setup mock query result
        mock_query = Mock()
        mock_query.convert.return_value = valid_query_results
        mock_instance.query.return_value = mock_query

        query = "SELECT ?s WHERE { ?s ?p ?o } LIMIT 10"
        result = client.execute_query(query)

        assert result == valid_query_results
        mock_instance.setQuery.assert_called_once_with(query)
        mock_instance.query.assert_called_once()
        mock_query.convert.assert_called_once()

    def test_execute_query_empty_results(self, client, mock_sparql_wrapper):
        """Test query execution with empty results returns the results dict."""
        mock_instance = Mock()
        mock_sparql_wrapper.return_value = mock_instance

        # Create new client to use mocked SPARQLWrapper
        client = SparqlClient("http://example.com/sparql")

        # Setup mock query result with empty bindings
        empty_results = {"results": {"bindings": []}}
        mock_query = Mock()
        mock_query.convert.return_value = empty_results
        mock_instance.query.return_value = mock_query

        query = "SELECT ?s WHERE { ?s ?p ?o } LIMIT 10"
        result = client.execute_query(query)

        # Empty results are still valid results - they return the dict, not None
        assert result == empty_results

    def test_execute_query_retry_on_failure(self, client, mock_sparql_wrapper, valid_query_results):
        """Test retry logic on query failure."""
        mock_instance = Mock()
        mock_sparql_wrapper.return_value = mock_instance

        # Create new client with shorter retry delay for faster tests
        client = SparqlClient("http://example.com/sparql", initial_delay=0.01)

        # Setup mock to fail twice then succeed
        mock_query = Mock()
        mock_query.convert.side_effect = [
            SPARQLWrapperException("Connection error"),
            SPARQLWrapperException("Timeout"),
            valid_query_results,
        ]
        mock_instance.query.return_value = mock_query

        with patch("time.sleep") as mock_sleep:
            result = client.execute_query("SELECT ?s WHERE { ?s ?p ?o }")

        assert result == valid_query_results
        assert mock_instance.query.call_count == 3
        assert mock_sleep.call_count == 2
        # Check exponential backoff
        mock_sleep.assert_any_call(0.01)
        mock_sleep.assert_any_call(0.02)

    def test_execute_query_max_retries_exceeded(self, client, mock_sparql_wrapper):
        """Test query fails after max retries."""
        mock_instance = Mock()
        mock_sparql_wrapper.return_value = mock_instance

        # Create new client with shorter retry delay
        client = SparqlClient("http://example.com/sparql", max_retries=2, initial_delay=0.01)

        # Setup mock to always fail
        mock_instance.query.side_effect = SPARQLWrapperException("Connection error")

        with patch("time.sleep"):
            result = client.execute_query("SELECT ?s WHERE { ?s ?p ?o }")

        assert result is None
        assert mock_instance.query.call_count == 2

    def test_execute_query_unexpected_exception(self, client, mock_sparql_wrapper):
        """Test handling of unexpected exceptions."""
        mock_instance = Mock()
        mock_sparql_wrapper.return_value = mock_instance

        # Create new client
        client = SparqlClient("http://example.com/sparql")

        # Setup mock to raise unexpected exception
        mock_instance.query.side_effect = ValueError("Unexpected error")

        result = client.execute_query("SELECT ?s WHERE { ?s ?p ?o }")

        assert result is None
        assert mock_instance.query.call_count == 1

    def test_validate_results_valid(self, client, valid_query_results):
        """Test validation of valid results."""
        assert client._validate_results(valid_query_results) is True

    def test_validate_results_invalid_cases(self, client):
        """Test validation of various invalid results."""
        # Not a dictionary
        assert client._validate_results("invalid") is False
        assert client._validate_results(None) is False
        assert client._validate_results([]) is False

        # Missing 'results' key
        assert client._validate_results({}) is False

        # Missing 'bindings' key
        assert client._validate_results({"results": {}}) is False

        # Bindings not a list
        assert client._validate_results({"results": {"bindings": "not_a_list"}}) is False

    def test_test_connection_success(self, client, mock_sparql_wrapper):
        """Test successful connection test."""
        mock_instance = Mock()
        mock_sparql_wrapper.return_value = mock_instance

        # Create new client
        client = SparqlClient("http://example.com/sparql")

        # Setup mock for successful test query
        mock_query = Mock()
        mock_query.convert.return_value = {
            "results": {"bindings": [{"s": {"value": "http://example.com/test"}}]}
        }
        mock_instance.query.return_value = mock_query

        assert client.test_connection() is True

        # Verify test query was executed
        expected_query = "SELECT ?s WHERE { ?s ?p ?o } LIMIT 1"
        mock_instance.setQuery.assert_called_with(expected_query)

    def test_test_connection_failure(self, client, mock_sparql_wrapper):
        """Test failed connection test."""
        mock_instance = Mock()
        mock_sparql_wrapper.return_value = mock_instance

        # Create new client
        client = SparqlClient("http://example.com/sparql")

        # Setup mock to fail
        mock_instance.query.side_effect = SPARQLWrapperException("Connection refused")

        assert client.test_connection() is False

    @patch("lindas_hydro_scraper.core.sparql_client.logger")
    def test_execute_query_logging(self, mock_logger, client, mock_sparql_wrapper, valid_query_results):
        """Test logging during query execution."""
        mock_instance = Mock()
        mock_sparql_wrapper.return_value = mock_instance

        # Create new client
        client = SparqlClient("http://example.com/sparql")

        # Setup successful query
        mock_query = Mock()
        mock_query.convert.return_value = valid_query_results
        mock_instance.query.return_value = mock_query

        client.execute_query("SELECT ?s WHERE { ?s ?p ?o }")

        # Check debug log for execution
        mock_logger.debug.assert_called()
        debug_call = mock_logger.debug.call_args[0][0]
        assert "Executing query" in debug_call

        # Check info log for success
        mock_logger.info.assert_called()
        info_call = mock_logger.info.call_args[0][0]
        assert "Query successful" in info_call
        assert "2 bindings" in info_call

    @patch("lindas_hydro_scraper.core.sparql_client.logger")
    def test_execute_query_logging_on_failure(self, mock_logger, client, mock_sparql_wrapper):
        """Test logging during query failure."""
        mock_instance = Mock()
        mock_sparql_wrapper.return_value = mock_instance

        # Create new client with only 1 retry
        client = SparqlClient("http://example.com/sparql", max_retries=1)

        # Setup query to fail
        mock_instance.query.side_effect = SPARQLWrapperException("Connection error")

        client.execute_query("SELECT ?s WHERE { ?s ?p ?o }")

        # Check warning log
        mock_logger.warning.assert_called()
        warning_call = mock_logger.warning.call_args[0][0]
        assert "SPARQL query failed" in warning_call

        # Check error log for final failure
        mock_logger.error.assert_called()
        error_call = mock_logger.error.call_args[0][0]
        assert "Query failed after" in error_call

    @patch("lindas_hydro_scraper.core.sparql_client.logger")
    def test_execute_query_logging_empty_results(self, mock_logger, client, mock_sparql_wrapper):
        """Test logging when query returns empty results - logs info about 0 bindings."""
        mock_instance = Mock()
        mock_sparql_wrapper.return_value = mock_instance

        # Create new client
        client = SparqlClient("http://example.com/sparql")

        # Setup query with empty results
        mock_query = Mock()
        mock_query.convert.return_value = {"results": {"bindings": []}}
        mock_instance.query.return_value = mock_query

        client.execute_query("SELECT ?s WHERE { ?s ?p ?o }")

        # Check info log for successful query with 0 bindings
        mock_logger.info.assert_called()
        info_call = mock_logger.info.call_args[0][0]
        assert "Query successful" in info_call
        assert "0 bindings" in info_call

    def test_exponential_backoff(self, client, mock_sparql_wrapper):
        """Test exponential backoff behavior."""
        mock_instance = Mock()
        mock_sparql_wrapper.return_value = mock_instance

        # Create client with specific retry settings
        client = SparqlClient("http://example.com/sparql", max_retries=4, initial_delay=1.0)

        # Setup to fail all attempts
        mock_instance.query.side_effect = SPARQLWrapperException("Error")

        sleep_calls = []
        with patch("time.sleep", side_effect=lambda x: sleep_calls.append(x)):
            client.execute_query("SELECT ?s WHERE { ?s ?p ?o }")

        # Verify exponential backoff: 1, 2, 4 seconds
        assert len(sleep_calls) == 3
        assert sleep_calls == [1.0, 2.0, 4.0]