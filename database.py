import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_file="notes.db"):
        self.db_file = db_file
        self.connection = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """Create a new database connection"""
        if self.connection:
            self.connection.close()
        self.connection = sqlite3.connect(self.db_file)
        self.connection.row_factory = sqlite3.Row

    def _create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.connection.cursor()
        
        # Create companies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        # Create boards table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS boards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                board_identifier TEXT NOT NULL,
                FOREIGN KEY (company_id) REFERENCES companies (id),
                UNIQUE(company_id, board_identifier)
            )
        ''')
        
        # Create notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                board_id INTEGER,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                last_modified_by TEXT,
                currently_editing TEXT,
                FOREIGN KEY (board_id) REFERENCES boards (id)
            )
        ''')
        
        self.connection.commit()

    def clear_all_data(self):
        """Clear all data from the database"""
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM notes')
        cursor.execute('DELETE FROM boards')
        cursor.execute('DELETE FROM companies')
        cursor.execute('UPDATE sqlite_sequence SET seq = 0')  # Reset autoincrement
        self.connection.commit()

    def add_company(self, company_name):
        cursor = self.connection.cursor()
        cursor.execute('INSERT OR IGNORE INTO companies (name) VALUES (?)', (company_name,))
        self.connection.commit()
        return cursor.lastrowid if cursor.lastrowid else cursor.execute('SELECT id FROM companies WHERE name = ?', (company_name,)).fetchone()[0]

    def add_board(self, company_id, board_identifier):
        cursor = self.connection.cursor()
        cursor.execute('INSERT OR IGNORE INTO boards (company_id, board_identifier) VALUES (?, ?)',
                     (company_id, board_identifier))
        self.connection.commit()
        return cursor.lastrowid if cursor.lastrowid else cursor.execute(
            'SELECT id FROM boards WHERE company_id = ? AND board_identifier = ?',
            (company_id, board_identifier)).fetchone()[0]

    def add_note(self, board_id, user_id, title, content):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO notes (board_id, user_id, title, content, created_at, updated_at, last_modified_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (board_id, user_id, title, content, current_time, current_time, user_id))
        self.connection.commit()
        return cursor.lastrowid

    def update_note(self, note_id, title, content, user_id):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = self.connection.cursor()
        cursor.execute('''
            UPDATE notes 
            SET title = ?, content = ?, updated_at = ?, last_modified_by = ?, currently_editing = NULL
            WHERE id = ?
        ''', (title, content, current_time, user_id, note_id))
        self.connection.commit()

    def delete_note(self, note_id):
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        self.connection.commit()

    def delete_board(self, board_id):
        """Delete a board and all its associated notes"""
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM notes WHERE board_id = ?', (board_id,))
        cursor.execute('DELETE FROM boards WHERE id = ?', (board_id,))
        self.connection.commit()

    def delete_company(self, company_id):
        """Delete a company and all its associated boards and notes"""
        cursor = self.connection.cursor()
        boards = cursor.execute('SELECT id FROM boards WHERE company_id = ?', (company_id,)).fetchall()
        for board_id in boards:
            cursor.execute('DELETE FROM notes WHERE board_id = ?', (board_id[0],))
        cursor.execute('DELETE FROM boards WHERE company_id = ?', (company_id,))
        cursor.execute('DELETE FROM companies WHERE id = ?', (company_id,))
        self.connection.commit()

    def get_companies(self):
        cursor = self.connection.cursor()
        return cursor.execute('SELECT id, name FROM companies').fetchall()

    def get_boards(self, company_id):
        cursor = self.connection.cursor()
        return cursor.execute(
            'SELECT id, board_identifier FROM boards WHERE company_id = ?',
            (company_id,)).fetchall()

    def get_notes(self, board_id):
        cursor = self.connection.cursor()
        return cursor.execute('''
            SELECT id, user_id, title, content, created_at, updated_at, last_modified_by 
            FROM notes 
            WHERE board_id = ?
            ORDER BY updated_at DESC
        ''', (board_id,)).fetchall()

    def get_note(self, note_id):
        cursor = self.connection.cursor()
        return cursor.execute('''
            SELECT id, board_id, user_id, title, content, created_at, updated_at, last_modified_by 
            FROM notes 
            WHERE id = ?
        ''', (note_id,)).fetchone()

    def set_note_editing_status(self, note_id, user_id):
        """Returns True if successfully set editing status, False if someone else is editing"""
        cursor = self.connection.cursor()
        # First check if someone else is editing
        result = cursor.execute('''
            SELECT currently_editing 
            FROM notes 
            WHERE id = ?
        ''', (note_id,)).fetchone()
        
        if result and result[0] and result[0] != user_id:
            return False, result[0]  # Return False and who is editing
            
        # Set editing status
        cursor.execute('''
            UPDATE notes 
            SET currently_editing = ?
            WHERE id = ?
        ''', (user_id, note_id))
        self.connection.commit()
        return True, None

    def clear_note_editing_status(self, note_id, user_id):
        """Clear editing status only if this user was the editor"""
        cursor = self.connection.cursor()
        cursor.execute('''
            UPDATE notes 
            SET currently_editing = NULL
            WHERE id = ? AND currently_editing = ?
        ''', (note_id, user_id))
        self.connection.commit()

    def get_note_editing_status(self, note_id):
        """Returns who is currently editing the note, if anyone"""
        cursor = self.connection.cursor()
        result = cursor.execute('''
            SELECT currently_editing 
            FROM notes 
            WHERE id = ?
        ''', (note_id,)).fetchone()
        return result[0] if result else None

    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def __del__(self):
        """Ensure all database connections are closed"""
        self.close()