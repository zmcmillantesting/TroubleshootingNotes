# tests/test_database.py
import unittest
import tempfile
import os
import shutil
from backend.database_manager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test database
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_db")
        self.db = DatabaseManager(db_path=self.db_path, db_name="test_notes.db")
        
    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_init_database(self):
        """Test database initialization"""
        # Database should be created with all tables
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            self.assertIn('companies', tables)
            self.assertIn('boards', tables)
            self.assertIn('notes', tables)
    
    def test_company_operations(self):
        """Test company CRUD operations"""
        # Test add company
        company_id = self.db.add_company("Test Company")
        self.assertIsNotNone(company_id)
        
        # Test get companies
        companies = self.db.get_companies()
        self.assertEqual(len(companies), 1)
        self.assertEqual(companies[0][1], "Test Company")
        
        # Test duplicate company
        with self.assertRaises(ValueError):
            self.db.add_company("Test Company")
            
        # Test delete company
        result = self.db.delete_company(company_id)
        self.assertTrue(result)
        
        # Verify company was deleted
        companies = self.db.get_companies()
        self.assertEqual(len(companies), 0)
    
    def test_board_operations(self):
        """Test board CRUD operations"""
        # First add a company
        company_id = self.db.add_company("Test Company")
        
        # Test add board - FIXED: correct parameter order (name, description, company_id)
        board_id = self.db.add_board("Test Board", "Test Description", company_id)
        self.assertIsNotNone(board_id)
        
        # Test get boards
        boards = self.db.get_boards(company_id)
        self.assertEqual(len(boards), 1)
        self.assertEqual(boards[0][1], "Test Board")
        
        # Test duplicate board - FIXED: correct parameter order
        with self.assertRaises(ValueError):
            self.db.add_board("Test Board", "Another Description", company_id)
            
        # Test delete board
        result = self.db.delete_board(board_id)
        self.assertTrue(result)
        
        # Verify board was deleted
        boards = self.db.get_boards(company_id)
        self.assertEqual(len(boards), 0)
    
    def test_note_operations(self):
        """Test note CRUD operations"""
        # First add a company and board
        company_id = self.db.add_company("Test Company")
        board_id = self.db.add_board("Test Board", "Test Description", company_id)
        
        # Test add note
        note_id = self.db.add_note(
            board_id, "Test Topic", "Test Title", 
            "Test Content", "test_user", 2
        )
        self.assertIsNotNone(note_id)
        
        # Test get notes
        notes = self.db.get_notes(board_id)
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]['title'], "Test Title")
        
        # Test get topics
        topics = self.db.get_topics(board_id)
        self.assertEqual(len(topics), 1)
        self.assertEqual(topics[0], "Test Topic")
        
        # Test update note
        result = self.db.update_note(
            note_id, "Updated Title", "Updated Content", 
            "test_user", "Updated Topic", 3
        )
        self.assertTrue(result)
        
        # Verify update
        notes = self.db.get_notes(board_id)
        self.assertEqual(notes[0]['title'], "Updated Title")
        self.assertEqual(notes[0]['priority'], 3)
        
        # Test archive note
        result = self.db.archive_note(note_id, "test_user")
        self.assertTrue(result)
        
        # Verify archive (should not appear in normal get_notes)
        notes = self.db.get_notes(board_id)
        self.assertEqual(len(notes), 0)
        
        # But should appear when including archived
        notes = self.db.get_notes(board_id, include_archived=True)
        self.assertEqual(len(notes), 1)
    
    def test_search_notes(self):
        """Test note search functionality"""
        # First add a company and board
        company_id = self.db.add_company("Test Company")
        board_id = self.db.add_board("Test Board", "Test Description", company_id)
        
        # Add test notes
        self.db.add_note(
            board_id, "Network", "Router Issue", 
            "The main router is not responding", "user1", 2
        )
        self.db.add_note(
            board_id, "Software", "Application Crash", 
            "The application crashes when opening large files", "user2", 3
        )
        
        # Test search
        results = self.db.search_notes(board_id, "router")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "Router Issue")
        
        results = self.db.search_notes(board_id, "application")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "Application Crash")

if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)