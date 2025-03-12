"""
Main entry point for Wizard application.
"""

import argparse
import sys

from PySide6.QtWidgets import QApplication

from . import __version__
from .ui.app import MainWindow
from .utils.logger import get_logger, setup_logger

# Initialize logger
logger = get_logger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Wizard")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--debug", action="store_true", help="Ativar registro de depuração")
    parser.add_argument(
        "--config", type=str, help="Caminho para arquivo de configuração personalizado"
    )
    return parser.parse_args()


def main():
    """Main application entry point."""
    # Parse command line arguments
    args = parse_arguments()

    # Setup logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logger(log_level)

    # Log application startup
    logger.info(f"Iniciando Wizard v{__version__}")

    app = QApplication(sys.argv)
    app.setApplicationName("Wizard")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("CAPES Research")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
