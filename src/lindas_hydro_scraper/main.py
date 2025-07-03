"""Main entry point for LINDAS hydro scraper."""

import logging
import sys
import time

from dotenv import load_dotenv

from .core import Settings
from .scrapers import LindasHydroScraper
from .utils import setup_logging

logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point for the scraper."""
    # Load environment variables
    load_dotenv()

    # Setup logging
    setup_logging(level="INFO")

    logger.info("Starting LINDAS Hydro Scraper")

    try:
        # Load configuration
        settings = Settings()
        logger.info(f"Configuration loaded: {len(settings.site_codes)} sites to scrape")
        logger.debug(f"Output directory: {settings.hydro_data_dir}")

        # Initialize and run scraper
        scraper = LindasHydroScraper(settings)
        scraper.run()

        # Small delay before cleaning duplicates
        time.sleep(1)

        # Clean duplicates
        scraper.clean_duplicates()

        logger.info("Scraping completed successfully")

    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
