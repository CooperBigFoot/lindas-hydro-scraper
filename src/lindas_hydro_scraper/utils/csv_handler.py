"""CSV file handling for measurement data."""

import csv
import logging
from pathlib import Path

import pandas as pd

from ..core.constants import CSV_COLUMNS
from ..models import Measurement

logger = logging.getLogger(__name__)


class CsvHandler:
    """Handle CSV operations for measurement data."""

    def __init__(self, csv_path: Path) -> None:
        """Initialize CSV handler.

        Args:
            csv_path: Path to CSV file.
        """
        self.csv_path = csv_path
        self._processed_keys: set[str] = set()
        self._ensure_csv_exists()
        self._load_processed_keys()

    def _ensure_csv_exists(self) -> None:
        """Ensure CSV file exists with headers."""
        if not self.csv_path.exists():
            self.csv_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
                writer.writeheader()
            logger.info(f"Created new CSV file: {self.csv_path}")

    def _load_processed_keys(self) -> None:
        """Load existing record keys for duplicate detection."""
        if self.csv_path.exists() and self.csv_path.stat().st_size > 0:
            try:
                df = pd.read_csv(self.csv_path, dtype=str)
                self._processed_keys = {
                    f"{row['timestamp']}_{row['station_id']}"
                    for _, row in df.iterrows()
                    if pd.notna(row.get("timestamp")) and pd.notna(row.get("station_id"))
                }
                logger.debug(f"Loaded {len(self._processed_keys)} existing records")
            except Exception as e:
                logger.error(f"Error loading existing records: {e}")
                self._processed_keys = set()

    def save_measurements(self, measurements: list[Measurement]) -> int:
        """Save measurements to CSV, skipping duplicates.

        Args:
            measurements: List of measurements to save.

        Returns:
            Number of new records saved.
        """
        if not measurements:
            return 0

        new_records = []

        for measurement in measurements:
            # Check for duplicates
            if measurement.unique_key not in self._processed_keys:
                new_records.append(measurement.to_csv_dict())
                self._processed_keys.add(measurement.unique_key)

        if new_records:
            try:
                with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
                    writer.writerows(new_records)
                logger.info(f"Saved {len(new_records)} new records to {self.csv_path}")
            except Exception as e:
                logger.error(f"Error writing to CSV: {e}")
                return 0

        return len(new_records)

    def remove_duplicates(self) -> int:
        """Remove duplicate records from CSV file.

        Returns:
            Number of duplicates removed.
        """
        if not self.csv_path.exists():
            logger.warning("CSV file does not exist")
            return 0

        try:
            # Read CSV
            df = pd.read_csv(self.csv_path, dtype=str)
            initial_count = len(df)

            # Remove duplicates
            df_cleaned = df.drop_duplicates(subset=["timestamp", "station_id"], keep="first")
            removed_count = initial_count - len(df_cleaned)

            if removed_count > 0:
                # Save cleaned data
                df_cleaned.to_csv(self.csv_path, index=False)

                # Update processed keys
                self._processed_keys = {
                    f"{row['timestamp']}_{row['station_id']}"
                    for _, row in df_cleaned.iterrows()
                    if pd.notna(row.get("timestamp")) and pd.notna(row.get("station_id"))
                }

                logger.info(f"Removed {removed_count} duplicate records")

            return removed_count

        except Exception as e:
            logger.error(f"Error removing duplicates: {e}")
            return 0

    def get_record_count(self) -> int:
        """Get total number of records in CSV.

        Returns:
            Number of records.
        """
        if not self.csv_path.exists():
            return 0

        try:
            df = pd.read_csv(self.csv_path)
            return len(df)
        except Exception:
            return 0
