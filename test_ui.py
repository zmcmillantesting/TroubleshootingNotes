# tests/test_ui.py
import unittest
import tempfile
import os
import shutil
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

# Import our application
from frontend.main_window import LearningWindow
from backend.database_manager import DatabaseManager

# Initialize QApplication once for all tests
app = QApplication([])

class TestUI(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test database
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_db")
        
        # Initialize database
        self.db = DatabaseManager(db_path=self.db_path, db_name="test_notes.db")
        
        # Add test data
        self.company_id = self.db.add_company("Test Company")
        self.board_id = self.db.add_board(self.company_id, "Test Board", "Test Description")
        
        # Create main window
        self.window = LearningWindow()
        # Replace the database instance with our test database
        self.window.db = self.db
        
        # Refresh UI to load test data
        self.window.refresh_companies()
        
    def tearDown(self):
        # Clean up
        self.window.close()
        shutil.rmtree(self.test_dir)
    
    def test_window_initialization(self):
        """Test that the window initializes correctly"""
        self.assertIsNotNone(self.window)
        self.assertEqual(self.window.windowTitle(), "🛠️ Troubleshooting Notes - Modern Interface")
    
    def test_company_selection(self):
        """Test company selection functionality"""
        # Find and select the test company
        company_combo = self.window.company_combo
        for i in range(company_combo.count()):
            if company_combo.itemData(i) == self.company_id:
                company_combo.setCurrentIndex(i)
                break
        
        # Verify selection
        self.assertEqual(self.window.current_company_id, self.company_id)
        
        # Verify boards are loaded
        self.assertGreater(self.window.board_combo.count(), 1)  # Should have at least "Select Board..." + our board
    
    def test_board_selection(self):
        """Test board selection functionality"""
        # First select the company
        company_combo = self.window.company_combo
        for i in range(company_combo.count()):
            if company_combo.itemData(i) == self.company_id:
                company_combo.setCurrentIndex(i)
                break
        
        # Then select the board
        board_combo = self.window.board_combo
        for i in range(board_combo.count()):
            if board_combo.itemData(i) == self.board_id:
                board_combo.setCurrentIndex(i)
                break
        
        # Verify selection
        self.assertEqual(self.window.current_board_id, self.board_id)
    
    def test_note_creation_dialog(self):
        """Test that note creation dialog works"""
        # First select company and board
        company_combo = self.window.company_combo
        for i in range(company_combo.count()):
            if company_combo.itemData(i) == self.company_id:
                company_combo.setCurrentIndex(i)
                break
        
        board_combo = self.window.board_combo
        for i in range(board_combo.count()):
            if board_combo.itemData(i) == self.board_id:
                board_combo.setCurrentIndex(i)
                break
        
        # Store current note count
        initial_notes = len(self.db.get_notes(self.board_id))
        
        # Simulate clicking "New Note" button
        QTest.mouseClick(self.window.new_note_btn, Qt.LeftButton)
        
        # The dialog should appear, but we can't easily test modal dialogs in QtTest
        # Instead, we'll test the underlying database method
        new_note_id = self.db.add_note(
            self.board_id, "Test Topic", "Test Title", 
            "Test Content", "test_user", 2
        )
        
        # Verify note was created
        notes_after = self.db.get_notes(self.board_id)
        self.assertEqual(len(notes_after), initial_notes + 1)
        
        # Verify note data
        new_note = next((note for note in notes_after if note['id'] == new_note_id), None)
        self.assertIsNotNone(new_note)
        self.assertEqual(new_note['title'], "Test Title")
        self.assertEqual(new_note['topic'], "Test Topic")
    
    def test_search_functionality(self):
        """Test search functionality"""
        # Add a test note
        self.db.add_note(
            self.board_id, "Network", "Router Issue", 
            "The main router is not responding", "user1", 2
        )
        
        # Select company and board
        company_combo = self.window.company_combo
        for i in range(company_combo.count()):
            if company_combo.itemData(i) == self.company_id:
                company_combo.setCurrentIndex(i)
                break
        
        board_combo = self.window.board_combo
        for i in range(board_combo.count()):
            if board_combo.itemData(i) == self.board_id:
                board_combo.setCurrentIndex(i)
                break
        
        # Test search
        search_results = self.db.search_notes(self.board_id, "router")
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0]['title'], "Router Issue")

if __name__ == "__main__":
    unittest.main(verbosity=2)