"""Constants used throughout the application."""

# LINDAS SPARQL endpoints and URLs
DEFAULT_SPARQL_ENDPOINT = "https://ld.admin.ch/query"
LINDAS_BASE_URL = "https://environment.ld.admin.ch/foen/hydro"
DIMENSION_URL = f"{LINDAS_BASE_URL}/dimension"
LINDAS_GRAPH = "https://lindas.admin.ch/foen/hydro"

# Default configuration
DEFAULT_SITE_CODES = ["2044", "2112", "2491", "2355"]
DEFAULT_OUTPUT_FILENAME = "lindas_hydro_data.csv"

# CSV column names
CSV_COLUMNS = [
    "timestamp",
    "station_id",
    "discharge",
    "water_level",
    "danger_level",
    "water_temperature",
    "is_liter",
]

# Retry configuration
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 2  # seconds

# Logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
