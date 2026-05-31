"""
Main entry point for MOOSE LOON AI Mentor Platform.

This file provides a convenient starting point for the application.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    logger.info("🫎 MOOSE LOON AI Mentor Platform")
    logger.info("=" * 50)
    logger.info("")
    logger.info("To start the application:")
    logger.info("")
    logger.info("Backend:  uvicorn backend.main:app --reload")
    logger.info("Frontend: streamlit run frontend/app.py")
    logger.info("")
    logger.info("Backend:  http://localhost:8000")
    logger.info("Frontend: http://localhost:8501")
    logger.info("")
    logger.info("See docs/SETUP.md for detailed instructions")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
