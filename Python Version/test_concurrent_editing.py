import tkinter as tk
from app import NotesApp
import threading
import time
import unittest
from database import Database
import os
import json
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed

class TestNotesApp(unittest.TestCase):
    def setUp(self):
        # Clean up any existing test database and settings
        if os.path.exists("test_notes.db"):
            try:
                os.remove("test_notes.db")
            except PermissionError:
                pass
        
        if os.path.exists("test_settings.json"):
            try:
                os.remove("test_settings.json")
            except PermissionError:
                pass
        
        # Use a test database file
        self.db = Database("test_notes.db")
        # Clear any existing data
        self.db.clear_all_data()

    def tearDown(self):
        # Clear test data
        if self.db:
            self.db.close()
            
        time.sleep(0.1)  # Give SQLite time to release the file
        try:
            if os.path.exists("test_notes.db"):
                os.remove("test_notes.db")
            if os.path.exists("test_settings.json"):
                os.remove("test_settings.json")
        except PermissionError:
            pass

    def test_individual_company_operations(self):
        """Test individual company operations"""
        # Add company
        company_id = self.db.add_company("Test Company")
        self.assertIsNotNone(company_id)
        
        # Verify company exists
        companies = self.db.get_companies()
        self.assertEqual(len(companies), 1)
        self.assertEqual(companies[0][1], "Test Company")
        
        # Delete company
        self.db.delete_company(company_id)
        companies = self.db.get_companies()
        self.assertEqual(len(companies), 0)

    def test_individual_board_operations(self):
        """Test individual board operations"""
        company_id = self.db.add_company("Test Company")
        
        # Add board
        board_id = self.db.add_board(company_id, "Test Board")
        self.assertIsNotNone(board_id)
        
        # Verify board exists
        boards = self.db.get_boards(company_id)
        self.assertEqual(len(boards), 1)
        self.assertEqual(boards[0][1], "Test Board")
        
        # Delete board
        self.db.delete_board(board_id)
        boards = self.db.get_boards(company_id)
        self.assertEqual(len(boards), 0)

    def test_individual_note_operations(self):
        """Test individual note operations"""
        company_id = self.db.add_company("Test Company")
        board_id = self.db.add_board(company_id, "Test Board")
        
        # Add note
        note_id = self.db.add_note(board_id, "user1", "Test Note", "Test Content")
        self.assertIsNotNone(note_id)
        
        # Verify note exists
        note = self.db.get_note(note_id)
        self.assertEqual(note[3], "Test Note")
        self.assertEqual(note[4], "Test Content")
        
        # Update note
        self.db.update_note(note_id, "Updated Note", "Updated Content", "user1")
        updated_note = self.db.get_note(note_id)
        self.assertEqual(updated_note[3], "Updated Note")
        self.assertEqual(updated_note[4], "Updated Content")
        
        # Delete note
        self.db.delete_note(note_id)
        notes = self.db.get_notes(board_id)
        self.assertEqual(len(notes), 0)

    def test_concurrent_note_editing(self):
        """Test concurrent note editing between multiple users"""
        # Setup test data
        company_id = self.db.add_company("Test Company")
        board_id = self.db.add_board(company_id, "Test Board")
        note_id = self.db.add_note(board_id, "user1", "Test Note", "Initial content")

        # First user tries to edit
        success1, editor = self.db.set_note_editing_status(note_id, "user1")
        self.assertTrue(success1)
        self.assertIsNone(editor)
        
        # Second user tries to edit while first user is editing
        success2, editor = self.db.set_note_editing_status(note_id, "user2")
        self.assertFalse(success2)
        self.assertEqual(editor, "user1")

        # First user finishes editing
        self.db.clear_note_editing_status(note_id, "user1")

        # Second user tries again after first user is done
        success3, editor = self.db.set_note_editing_status(note_id, "user2")
        self.assertTrue(success3)
        self.assertIsNone(editor)

    def test_concurrent_company_board_creation(self):
        """Test concurrent creation of companies and boards"""
        def add_companies(user_id, companies):
            db = Database("test_notes.db")  # Create new connection for thread
            company_ids = []
            for company in companies:
                company_id = db.add_company(company)
                company_ids.append((company, company_id))
            return company_ids

        # Create companies concurrently
        companies1 = ['Company A', 'Company B']
        companies2 = ['Company C', 'Company D']
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(add_companies, "user1", companies1)
            future2 = executor.submit(add_companies, "user2", companies2)
            
            # Wait for results
            results1 = future1.result()
            results2 = future2.result()
        
        # Verify results
        companies = self.db.get_companies()
        self.assertEqual(len(companies), 4)
        company_names = {company[1] for company in companies}
        self.assertEqual(company_names, {'Company A', 'Company B', 'Company C', 'Company D'})

    def test_concurrent_note_creation(self):
        """Test concurrent creation of notes"""
        company_id = self.db.add_company("Test Company")
        board_id = self.db.add_board(company_id, "Test Board")
        
        def create_notes(user_id, num_notes):
            db = Database("test_notes.db")  # Create new connection for thread
            for i in range(num_notes):
                db.add_note(board_id, user_id, f"Note {i} by {user_id}", f"Content {i}")
        
        # Create notes concurrently from multiple users
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(create_notes, "user1", 5),
                executor.submit(create_notes, "user2", 5),
                executor.submit(create_notes, "user3", 5)
            ]
            # Wait for all tasks to complete
            for future in as_completed(futures):
                future.result()
        
        # Verify results
        notes = self.db.get_notes(board_id)
        self.assertEqual(len(notes), 15)  # Should have 15 notes total
        
        # Verify notes from each user
        user_notes = {"user1": 0, "user2": 0, "user3": 0}
        for note in notes:
            user_notes[note[1]] += 1
        
        self.assertEqual(user_notes["user1"], 5)
        self.assertEqual(user_notes["user2"], 5)
        self.assertEqual(user_notes["user3"], 5)

    def test_editing_status_cleared_on_save(self):
        """Test that editing status is properly cleared when saving a note"""
        company_id = self.db.add_company("Test Company")
        board_id = self.db.add_board(company_id, "Test Board")
        note_id = self.db.add_note(board_id, "user1", "Test Note", "Initial content")
        
        # Set editing status
        success, _ = self.db.set_note_editing_status(note_id, "user1")
        self.assertTrue(success)

        # Update note (which should clear editing status)
        self.db.update_note(note_id, "Updated Title", "Updated content", "user1")
        
        # Another user should now be able to edit
        success, editor = self.db.set_note_editing_status(note_id, "user2")
        self.assertTrue(success)
        self.assertIsNone(editor)

    @classmethod
    def setUpClass(cls):
        """Set up any test-wide resources"""
        # Create a root window that will exist throughout the tests
        cls.root = tk.Tk()
        
    @classmethod
    def tearDownClass(cls):
        """Clean up test-wide resources"""
        cls.root.destroy()

    def test_user_settings_persistence(self):
        """Test that user settings are properly persisted"""
        # Create a temporary settings file
        settings = {"last_user": "test_user"}
        with open("test_settings.json", "w") as f:
            json.dump(settings, f)
        
        # Create app instance which should load the settings
        app = NotesApp(self.root, settings_file="test_settings.json")
        
        # Verify settings were loaded
        self.assertEqual(app.settings.get("last_user"), "test_user")
        
        # Update settings
        app.user_id.delete(0, tk.END)
        app.user_id.insert(0, "new_user")
        app.save_user_id()
        
        # Verify settings were saved
        with open("test_settings.json", "r") as f:
            updated_settings = json.load(f)
        self.assertEqual(updated_settings.get("last_user"), "new_user")

def main():
    unittest.main()

if __name__ == "__main__":
    main()