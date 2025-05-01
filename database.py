import sqlite3
from datetime import datetime
import os
import time
import random

class Database:
    MAX_RETRIES = 5
    INITIAL_TIMEOUT = 20.0
    
    def __init__(self, db_file="notes.db"):
        self.db_file = db_file
        self.connection = None
        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        self._connect_with_retry()
        self._create_tables()

    def _connect_with_retry(self):
        """Attempt to connect to database with retries and exponential backoff"""
        retry_count = 0
        last_error = None
        
        while retry_count < self.MAX_RETRIES:
            try:
                self._connect()
                return  # Successfully connected
            except Exception as e:
                last_error = e
                retry_count += 1
                if retry_count < self.MAX_RETRIES:
                    # Add random jitter to prevent thundering herd
                    sleep_time = min(self.INITIAL_TIMEOUT * (2 ** retry_count) + random.random(), 60.0)
                    time.sleep(sleep_time)
        
        # If we get here, all retries failed
        raise Exception(f"Failed to connect to database after {self.MAX_RETRIES} attempts. Last error: {str(last_error)}")

    def _connect(self):
        """Create a new database connection with timeout and write-ahead logging"""
        try:
            if self.connection:
                try:
                    self.connection.close()
                except:
                    pass  # Ignore errors when closing existing connection
                
            # Set timeout to 20 seconds for network share access
            self.connection = sqlite3.connect(self.db_file, timeout=self.INITIAL_TIMEOUT)
            self.connection.row_factory = sqlite3.Row
            
            # Enable write-ahead logging for better concurrent access
            self.connection.execute('PRAGMA journal_mode=WAL')
            # Set busy timeout to 20 seconds
            self.connection.execute('PRAGMA busy_timeout=20000')
            # Enable foreign keys
            self.connection.execute('PRAGMA foreign_keys=ON')
            # Set synchronous mode to NORMAL for better performance while maintaining safety
            self.connection.execute('PRAGMA synchronous=NORMAL')
            # Set temp store to MEMORY to reduce disk I/O
            self.connection.execute('PRAGMA temp_store=MEMORY')
            
        except sqlite3.Error as e:
            if self.connection:
                try:
                    self.connection.close()
                except:
                    pass
            self.connection = None
            raise Exception(f"Failed to connect to database at {self.db_file}: {str(e)}")

    def execute_with_retry(self, operation, parameters=()):
        """Execute a database operation with retry logic"""
        retry_count = 0
        last_error = None
        
        while retry_count < self.MAX_RETRIES:
            try:
                if not self.connection:
                    self._connect_with_retry()
                    
                cursor = self.connection.cursor()
                result = cursor.execute(operation, parameters)
                self.connection.commit()
                return result
                
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    retry_count += 1
                    if retry_count < self.MAX_RETRIES:
                        sleep_time = min(self.INITIAL_TIMEOUT * (2 ** retry_count) + random.random(), 60.0)
                        time.sleep(sleep_time)
                        last_error = e
                        continue
                raise
            except Exception as e:
                last_error = e
                retry_count += 1
                if retry_count < self.MAX_RETRIES:
                    sleep_time = min(self.INITIAL_TIMEOUT * (2 ** retry_count) + random.random(), 60.0)
                    time.sleep(sleep_time)
                    # Try to reconnect on next iteration
                    try:
                        self._connect_with_retry()
                    except:
                        pass
                    continue
                raise
                
        raise Exception(f"Operation failed after {self.MAX_RETRIES} attempts. Last error: {str(last_error)}")

    # Update all database operations to use execute_with_retry
    def _create_tables(self):
        """Create database tables if they don't exist"""
        self.execute_with_retry('''
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        self.execute_with_retry('''
            CREATE TABLE IF NOT EXISTS boards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                board_identifier TEXT NOT NULL,
                FOREIGN KEY (company_id) REFERENCES companies (id),
                UNIQUE(company_id, board_identifier)
            )
        ''')
        
        self.execute_with_retry('''
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

    def clear_all_data(self):
        """Clear all data from the database"""
        self.execute_with_retry('DELETE FROM notes')
        self.execute_with_retry('DELETE FROM boards')
        self.execute_with_retry('DELETE FROM companies')
        self.execute_with_retry('UPDATE sqlite_sequence SET seq = 0')  # Reset autoincrement

    def add_company(self, company_name):
        self.execute_with_retry('INSERT OR IGNORE INTO companies (name) VALUES (?)', (company_name,))
        result = self.execute_with_retry('SELECT id FROM companies WHERE name = ?', (company_name,)).fetchone()
        return result[0]

    def add_board(self, company_id, board_identifier):
        self.execute_with_retry(
            'INSERT OR IGNORE INTO boards (company_id, board_identifier) VALUES (?, ?)',
            (company_id, board_identifier)
        )
        result = self.execute_with_retry(
            'SELECT id FROM boards WHERE company_id = ? AND board_identifier = ?',
            (company_id, board_identifier)
        ).fetchone()
        return result[0]

    def add_note(self, board_id, user_id, title, content):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        result = self.execute_with_retry('''
            INSERT INTO notes (board_id, user_id, title, content, created_at, updated_at, last_modified_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (board_id, user_id, title, content, current_time, current_time, user_id))
        return result.lastrowid

    def update_note(self, note_id, title, content, user_id):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.execute_with_retry('''
            UPDATE notes 
            SET title = ?, content = ?, updated_at = ?, last_modified_by = ?, currently_editing = NULL
            WHERE id = ?
        ''', (title, content, current_time, user_id, note_id))

    def delete_note(self, note_id):
        self.execute_with_retry('DELETE FROM notes WHERE id = ?', (note_id,))

    def delete_board(self, board_id):
        """Delete a board and all its associated notes"""
        self.execute_with_retry('DELETE FROM notes WHERE board_id = ?', (board_id,))
        self.execute_with_retry('DELETE FROM boards WHERE id = ?', (board_id,))

    def delete_company(self, company_id):
        """Delete a company and all its associated boards and notes"""
        boards = self.execute_with_retry('SELECT id FROM boards WHERE company_id = ?', (company_id,)).fetchall()
        for board_id in boards:
            self.execute_with_retry('DELETE FROM notes WHERE board_id = ?', (board_id[0],))
        self.execute_with_retry('DELETE FROM boards WHERE company_id = ?', (company_id,))
        self.execute_with_retry('DELETE FROM companies WHERE id = ?', (company_id,))

    def get_companies(self):
        return self.execute_with_retry('SELECT id, name FROM companies').fetchall()

    def get_boards(self, company_id):
        return self.execute_with_retry(
            'SELECT id, board_identifier FROM boards WHERE company_id = ?',
            (company_id,)
        ).fetchall()

    def get_notes(self, board_id):
        return self.execute_with_retry('''
            SELECT id, user_id, title, content, created_at, updated_at, last_modified_by 
            FROM notes 
            WHERE board_id = ?
            ORDER BY updated_at DESC
        ''', (board_id,)).fetchall()

    def get_note(self, note_id):
        return self.execute_with_retry('''
            SELECT id, board_id, user_id, title, content, created_at, updated_at, last_modified_by 
            FROM notes 
            WHERE id = ?
        ''', (note_id,)).fetchone()

    def set_note_editing_status(self, note_id, user_id):
        """Returns True if successfully set editing status, False if someone else is editing"""
        result = self.execute_with_retry('''
            SELECT currently_editing 
            FROM notes 
            WHERE id = ?
        ''', (note_id,)).fetchone()
        
        if result and result[0] and result[0] != user_id:
            return False, result[0]  # Return False and who is editing
            
        self.execute_with_retry('''
            UPDATE notes 
            SET currently_editing = ?
            WHERE id = ?
        ''', (user_id, note_id))
        return True, None

    def clear_note_editing_status(self, note_id, user_id):
        """Clear editing status only if this user was the editor"""
        self.execute_with_retry('''
            UPDATE notes 
            SET currently_editing = NULL
            WHERE id = ? AND currently_editing = ?
        ''', (note_id, user_id))

    def get_note_editing_status(self, note_id):
        """Returns who is currently editing the note, if anyone"""
        result = self.execute_with_retry('''
            SELECT currently_editing 
            FROM notes 
            WHERE id = ?
        ''', (note_id,)).fetchone()
        return result[0] if result else None

    def close(self):
        """Close the database connection"""
        if self.connection:
            try:
                self.connection.close()
            except:
                pass  # Ignore errors when closing
            self.connection = None

    def __del__(self):
        """Ensure all database connections are closed"""
        self.close()