"""Configuration management using Pydantic Settings."""

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from ..models import Parameter
from .constants import (
    DEFAULT_OUTPUT_FILENAME,
    DEFAULT_SITE_CODES,
    DEFAULT_SPARQL_ENDPOINT,
)


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # SPARQL configuration
    sparql_endpoint: str = Field(
        default=DEFAULT_SPARQL_ENDPOINT,
        description="SPARQL endpoint URL",
    )
    sparql_base_url: str = Field(
        default="https://environment.ld.admin.ch/foen/hydro",
        description="Base URL for LINDAS hydro data",
    )

    # Data collection configuration
    site_codes: list[str] = Field(
        default_factory=lambda: DEFAULT_SITE_CODES.copy(),
        description="List of station codes to scrape",
    )
    parameters: list[Parameter] = Field(
        default_factory=lambda: list(Parameter),
        description="Parameters to collect from LINDAS",
    )

    # Output configuration
    hydro_data_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "data",
        description="Directory for output files",
    )
    output_filename: str = Field(
        default=DEFAULT_OUTPUT_FILENAME,
        description="Output CSV filename",
    )

    # Runtime configuration
    retry_max_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum retry attempts for failed requests",
    )
    retry_delay: float = Field(
        default=2.0,
        ge=0.1,
        le=60.0,
        description="Initial retry delay in seconds",
    )

    model_config = SettingsConfigDict(
        env_prefix="",
        env_nested_delimiter="__",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("site_codes", mode="before")
    @classmethod
    def parse_site_codes(cls, v: str | list[str]) -> list[str]:
        """Parse site codes from comma-separated string or list."""
        if isinstance(v, str):
            return [code.strip() for code in v.split(",") if code.strip()]
        return v

    @field_validator("parameters", mode="before")
    @classmethod
    def parse_parameters(cls, v: str | list[str | Parameter]) -> list[Parameter]:
        """Parse parameters from comma-separated string or list."""
        if isinstance(v, str):
            param_names = [p.strip() for p in v.split(",") if p.strip()]
            return [Parameter(name) for name in param_names]
        elif isinstance(v, list):
            return [Parameter(p) if isinstance(p, str) else p for p in v]
        return []  # Return empty list instead of v

    @field_validator("hydro_data_dir", mode="before")
    @classmethod
    def parse_path(cls, v: str | Path) -> Path:
        """Parse path from string."""
        if isinstance(v, str):
            return Path(v)
        return v

    @property
    def output_path(self) -> Path:
        """Full path to output CSV file."""
        return self.hydro_data_dir / self.output_filename

    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        self.hydro_data_dir.mkdir(parents=True, exist_ok=True)
