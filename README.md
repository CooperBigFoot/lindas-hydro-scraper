# lindas-hydro-scraper

A Python package for scraping hydrological data from the Swiss LINDAS platform.

## Features

- Fetches real-time hydrological measurements from Swiss monitoring stations
- Supports multiple data parameters (discharge, water level, temperature, etc.)
- Automatic duplicate detection and removal
- Configurable via environment variables
- Type-safe with Pydantic models
- Comprehensive error handling and retry logic

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/lindas-hydro-scraper.git
cd lindas-hydro-scraper

# Install with uv in editable mode
uv pip install -e .
```

## Usage

### Basic Usage

```bash
# Run with default settings
uv run lindas-hydro-scraper

# Or using the main module
uv run python -m lindas_hydro_scraper.main
```

### Configuration

Create a `.env` file based on `.env.example`:

```env
# SPARQL Configuration
SPARQL_ENDPOINT=https://ld.admin.ch/query
SPARQL_BASE_URL=https://environment.ld.admin.ch/foen/hydro

# Site Configuration
SITE_CODES=2044,2112,2491,2355

# Output Configuration
HYDRO_DATA_DIR=./data
OUTPUT_FILENAME=lindas_hydro_data.csv
```

### Docker Usage

```bash
docker build -t lindas-hydro-scraper .
docker run -v $(pwd)/data:/app/data lindas-hydro-scraper
```

## Development

```bash
# Install development dependencies
uv sync --dev

# Run linting
uv run ruff check src/

# Run type checking
uvx ty check src/

# Run tests
uv run pytest
```

## Project Structure

```
lindas-hydro-scraper/
   src/
      lindas_hydro_scraper/
          core/           # Core functionality
          models/         # Pydantic data models
          scrapers/       # Scraper implementations
          utils/          # Utility functions
   tests/                  # Test suite
   data/                   # Output directory
   old_code/              # Legacy implementation
```