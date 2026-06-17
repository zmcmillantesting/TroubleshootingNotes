# tests/debug_ui.py
import sys
import os
import logging
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt5.QtWidgets import QApplication
from utils.logger import setup_logging
from frontend.main_window import LearningWindow

def debug_ui():
    """Debug function to test UI components"""
    # Setup logging
    setup_logging(log_level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting UI Debug")
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        # Create and show main window
        window = LearningWindow()
        window.show()
        
        logger.info("UI Debug - Window created successfully")
        
        # Test basic functionality
        logger.info("Testing company dropdown...")
        companies = window.db.get_companies()
        logger.info(f"Found {len(companies)} companies")
        
        if companies:
            # Try to select the first company
            for i in range(window.company_combo.count()):
                if window.company_combo.itemData(i) == companies[0][0]:
                    window.company_combo.setCurrentIndex(i)
                    logger.info(f"Selected company: {companies[0][1]}")
                    break
            
            # Test board loading
            logger.info("Testing board loading...")
            boards = window.db.get_boards(companies[0][0])
            logger.info(f"Found {len(boards)} boards for company")
            
            if boards:
                # Try to select the first board
                for i in range(window.board_combo.count()):
                    if window.board_combo.itemData(i) == boards[0][0]:
                        window.board_combo.setCurrentIndex(i)
                        logger.info(f"Selected board: {boards[0][1]}")
                        break
                
                # Test note loading
                logger.info("Testing note loading...")
                notes = window.db.get_notes(boards[0][0])
                logger.info(f"Found {len(notes)} notes for board")
        
        logger.info("UI Debug completed successfully")
        
        # Run application for manual testing
        return app.exec_()
        
    except Exception as e:
        logger.error(f"UI Debug failed with error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(debug_ui())