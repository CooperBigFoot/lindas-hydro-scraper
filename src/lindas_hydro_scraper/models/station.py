"""Station data models."""

from pydantic import BaseModel, Field


class Station(BaseModel):
    """Represents a hydrological monitoring station."""

    code: str = Field(..., description="Station code (1-4 digit integer as string)")
    name: str | None = Field(None, description="Station name")

    @property
    def uri(self) -> str:
        """Generate LINDAS URI for this station."""
        from ..core.constants import LINDAS_BASE_URL
        return f"{LINDAS_BASE_URL}/river/observation/{self.code}"

    def __str__(self) -> str:
        """String representation."""
        return f"Station({self.code})"

    class Config:
        """Pydantic config."""
        frozen = True
