"""Helper utilities for extracting site lists from CSV files."""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def get_river_station_codes(csv_file: Path | str) -> list[str]:
    """Extract station codes for rivers from CSV file.

    Filters for rows where lhg_code == 'lhg_fluss' and extracts
    station codes from lhg_url column.

    Args:
        csv_file: Path to CSV file containing station information.

    Returns:
        List of station codes.

    Raises:
        FileNotFoundError: If CSV file doesn't exist.
        ValueError: If CSV file is invalid or missing required columns.
    """
    csv_path = Path(csv_file)

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    try:
        # Read CSV with various encodings
        for encoding in ["utf-8", "latin1", "cp1252"]:
            try:
                df = pd.read_csv(csv_path, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError(f"Unable to read CSV file with any encoding: {csv_path}")

        # Check required columns
        required_columns = {"lhg_code", "lhg_url"}
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            raise ValueError(f"CSV missing required columns: {missing}")

        # Filter for river stations
        river_stations = df[df["lhg_code"] == "lhg_fluss"]["lhg_url"]

        # Extract station codes (remove .htm extension)
        station_codes = [
            str(url).replace(".htm", "").strip()
            for url in river_stations
            if pd.notna(url)
        ]

        # Validate station codes are numeric
        valid_codes = []
        for code in station_codes:
            try:
                int(code)
                valid_codes.append(code)
            except ValueError:
                logger.warning(f"Skipping invalid station code: {code}")

        logger.info(f"Extracted {len(valid_codes)} river station codes from {csv_path}")
        return valid_codes

    except Exception as e:
        raise ValueError(f"Error processing CSV file: {e}") from e
