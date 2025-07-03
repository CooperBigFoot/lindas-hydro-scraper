"""SPARQL query builder for LINDAS hydro data."""

from ..models import Parameter, QueryParameters
from .constants import LINDAS_BASE_URL, LINDAS_GRAPH


class SparqlQueryBuilder:
    """Builder for constructing SPARQL queries for hydrological data."""

    def __init__(self, base_url: str = LINDAS_BASE_URL) -> None:
        """Initialize query builder.

        Args:
            base_url: Base URL for LINDAS hydro data.
        """
        self.base_url = base_url

    def build_query(self, params: QueryParameters) -> str:
        """Build SPARQL query for given parameters.

        Args:
            params: Query parameters including site code and data parameters.

        Returns:
            Complete SPARQL query string.

        Raises:
            ValueError: If parameters are invalid.
        """
        self._validate_parameters(params)

        # Build the FILTER clause for parameters
        params_filter = self._build_parameters_filter(params.parameters)

        # Construct the query
        query = f"""PREFIX schema: <http://schema.org/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?predicate ?object
FROM <{LINDAS_GRAPH}>
WHERE {{
  BIND(<{self.base_url}/river/observation/{params.site_code}> AS ?subject)
  ?subject ?predicate ?object .
  FILTER (?predicate IN (
    {params_filter}
  ))
}}"""

        return query

    def _validate_parameters(self, params: QueryParameters) -> None:
        """Validate query parameters.

        Args:
            params: Parameters to validate.

        Raises:
            ValueError: If parameters are invalid.
        """
        if not params.site_code:
            raise ValueError("Site code is required")

        # Validate site code format (1-4 digit integer)
        try:
            code_int = int(params.site_code)
            if not 1 <= code_int <= 9999:
                raise ValueError(f"Site code must be 1-4 digit integer: {params.site_code}")
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(f"Site code must be numeric: {params.site_code}") from e
            raise

        if not params.parameters:
            raise ValueError("At least one parameter is required")

    def _build_parameters_filter(self, parameters: list[Parameter]) -> str:
        """Build FILTER clause for parameters.

        Args:
            parameters: List of parameters to filter.

        Returns:
            Formatted filter string for SPARQL query.
        """
        param_uris = [f"<{param.uri}>" for param in parameters]
        return ",\n    ".join(param_uris)

    def build_batch_query(self, site_codes: list[str], parameters: list[Parameter]) -> str:
        """Build query for multiple sites (for future optimization).

        Args:
            site_codes: List of station codes.
            parameters: Parameters to retrieve.

        Returns:
            SPARQL query for multiple sites.
        """
        # For now, we'll continue processing sites individually
        # This method is a placeholder for future batch optimization
        raise NotImplementedError("Batch queries not yet implemented")
