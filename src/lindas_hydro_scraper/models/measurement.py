"""Measurement data models."""

from datetime import datetime
from decimal import Decimal, InvalidOperation

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Measurement(BaseModel):
    """Represents a hydrological measurement at a specific time."""

    model_config = ConfigDict(str_strip_whitespace=True)

    station_id: str = Field(..., description="Station identifier")
    timestamp: datetime = Field(..., description="Measurement timestamp")
    discharge: Decimal | None = Field(None, description="Water discharge (m³/s)")
    water_level: Decimal | None = Field(None, description="Water level (m)")
    water_temperature: Decimal | None = Field(None, description="Water temperature (°C)")
    danger_level: int | None = Field(None, ge=0, le=5, description="Danger level (0-5)")
    is_liter: bool | None = Field(None, description="Is measurement in liters")

    @field_validator("discharge", "water_level", "water_temperature", mode="before")
    @classmethod
    def parse_decimal(cls, v: float | str | None) -> Decimal | None:
        """Parse decimal values from various inputs."""
        if v is None:
            return None
        if isinstance(v, str) and v.strip() == "":
            return None
        try:
            return Decimal(str(v))
        except (ValueError, TypeError, InvalidOperation):
            return None

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: str | datetime) -> datetime:
        """Parse timestamp from string or datetime."""
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            # Handle ISO format with timezone
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        raise ValueError(f"Invalid timestamp format: {v}")

    @field_validator("is_liter", mode="before")
    @classmethod
    def parse_bool(cls, v: bool | str | None) -> bool | None:
        """Parse boolean values from various inputs."""
        if v is None:
            return None
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            v_lower = v.lower().strip()
            if v_lower in ("true", "1", "yes"):
                return True
            elif v_lower in ("false", "0", "no"):
                return False
        return None

    def has_measurements(self) -> bool:
        """Check if this record has any actual measurement values."""
        return any(
            getattr(self, field) is not None
            for field in ["discharge", "water_level", "water_temperature"]
        )

    def to_csv_dict(self) -> dict[str, str | None]:
        """Convert to dictionary for CSV export."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "station_id": self.station_id,
            "discharge": str(self.discharge) if self.discharge is not None else None,
            "water_level": str(self.water_level) if self.water_level is not None else None,
            "danger_level": str(self.danger_level) if self.danger_level is not None else None,
            "water_temperature": str(self.water_temperature) if self.water_temperature is not None else None,
            "is_liter": str(self.is_liter).lower() if self.is_liter is not None else None,
        }

    @property
    def unique_key(self) -> str:
        """Generate unique key for duplicate detection."""
        return f"{self.timestamp.isoformat()}_{self.station_id}"
