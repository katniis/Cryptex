"""
Cryptex - Cryptocurrency Portfolio Tracker
Main Entry Point
"""

import sys
import logging
from ui.app import CryptexApp

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """
    Main entry point for the application
    """
    try:
        logger.info("="*50)
        logger.info("Starting Cryptex Portfolio Tracker")
        logger.info("="*50)
        
        # Create and start app
        app = CryptexApp()
        app.start()
        
        logger.info("Application closed")
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()