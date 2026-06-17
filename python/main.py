# main.py
import sys
import os
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PyQt5.QtWidgets import QApplication
from utils.logger import setup_logging
from frontend.main_window import LearningWindow

def main():
    """Main application entry point"""
    # Setup logging
    setup_logging(log_level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting Troubleshooting Notes Application")
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        # Create and show main window
        window = LearningWindow()
        window.show()
        
        logger.info("Application started successfully")
        
        # Run application
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())