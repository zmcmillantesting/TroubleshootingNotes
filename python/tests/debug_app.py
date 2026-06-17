# tests/debug_app.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logger import setup_logging  # Fixed import name
from backend.database_manager import DatabaseManager

def debug_database():
    """Debug function to test database operations"""
    logger = setup_logging()  # Fixed function name
    
    try:
        # Initialize database
        db = DatabaseManager()
        logger.info("Database initialized successfully")
        
        # Test basic operations
        companies = db.get_companies()
        logger.info(f"Found {len(companies)} companies")
        
        for company_id, name in companies:
            logger.info(f"Company: {name} (ID: {company_id})")
            boards = db.get_boards(company_id)
            logger.info(f"  - Has {len(boards)} boards")
            
            for board_id, board_name in boards:
                logger.info(f"    Board: {board_name} (ID: {board_id})")
                notes = db.get_notes(board_id)
                logger.info(f"      - Has {len(notes)} notes")
                
                for note in notes:
                    logger.info(f"        Note: {note['title']} (Priority: {note['priority']})")
        
        logger.info("Debug completed successfully")
        
    except Exception as e:
        logger.error(f"Debug failed with error: {e}", exc_info=True)

if __name__ == "__main__":
    debug_database()