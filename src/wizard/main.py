"""
Main entry point for CAPES Research Wizard application.
"""

import sys
import os
import argparse
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication, Qt

from . import __version__
from .ui.app import MainWindow
from .utils.logger import setup_logger, get_logger
from .utils.config import Config

# Initialize logger
logger = get_logger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="CAPES Research Wizard")
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--config', type=str, help='Path to custom config file')
    return parser.parse_args()

def main():
    """Main application entry point."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logging
    log_level = 'DEBUG' if args.debug else 'INFO'
    setup_logger(log_level)
    
    # Log application startup
    logger.info(f"Starting CAPES Research Wizard v{__version__}")
    
    # Initialize Qt application
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("CAPES Research Wizard")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("CAPES Research")
    
    # Load configuration
    config_path = args.config if args.config else None
    config = Config(config_path)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()