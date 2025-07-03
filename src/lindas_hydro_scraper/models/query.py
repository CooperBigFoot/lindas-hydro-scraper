"""Query parameter models."""

from enum import Enum

from pydantic import BaseModel, Field


class Parameter(str, Enum):
    """Available SPARQL query parameters."""

    STATION = "station"
    DISCHARGE = "discharge"
    MEASUREMENT_TIME = "measurementTime"
    WATER_LEVEL = "waterLevel"
    DANGER_LEVEL = "dangerLevel"
    WATER_TEMPERATURE = "waterTemperature"
    IS_LITER = "isLiter"

    @property
    def uri(self) -> str:
        """Get full URI for this parameter."""
        from ..core.constants import DIMENSION_URL

        if self == self.IS_LITER:
            return "http://example.com/isLiter"
        return f"{DIMENSION_URL}/{self.value}"


class QueryParameters(BaseModel):
    """Parameters for SPARQL query construction."""

    site_code: str = Field(..., description="Station code to query")
    parameters: list[Parameter] = Field(
        default_factory=lambda: list(Parameter),
        description="Parameters to retrieve",
    )

    class Config:
        """Pydantic config."""
        use_enum_values = True
