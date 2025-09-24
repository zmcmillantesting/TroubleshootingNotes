

import sqlite3
import os
import sys
import logging
from contextlib import contextmanager
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class DatabaseManager:
    def __init__(self, db_path=resource_path(r"P:\EMS_TR_PATH\Shared_notes"), db_name="shard_notes.db"):
        if db_path is None:
            self.db_path = resource_path(r"P:\EMS_TR_PATH\Shared_notes")
        else:
            self.db_path = db_path
            
        self.db_name = db_name
        self.full_db_path = os.path.join(self.db_path, self.db_name)
        
        # Ensure directory exists
        os.makedirs(self.db_path, exist_ok=True)
        
        # Initialize database
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        connection = None
        try:
            connection = sqlite3.connect(self.full_db_path)
            connection.execute("PRAGMA foreign_keys = ON")
            yield connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()

    def init_database(self):
        """Initialize the database tables"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Companies table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS companies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Boards table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS boards (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        description TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(company_id, name),
                        FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
                    )
                """)

                # Enhanced notes table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS notes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        board_id INTEGER NOT NULL,
                        topic TEXT DEFAULT 'General',
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        created_by TEXT NOT NULL,
                        last_modified_by TEXT NOT NULL,
                        priority INTEGER DEFAULT 1,
                        is_archived BOOLEAN DEFAULT FALSE,
                        FOREIGN KEY (board_id) REFERENCES boards(id) ON DELETE CASCADE
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS note_history (
                    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER NOT NULL,
                    action TEXT NOT NULL,          -- 'created', 'updated', 'archived'
                    user_id TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    old_title TEXT,
                    old_content TEXT,
                    old_topic TEXT,
                    old_priority INTEGER,
                    FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
                    )           
                """)            

                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_board_id ON notes(board_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_topic ON notes(topic)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_boards_company_id ON boards(company_id)")
                
                conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    # Company operations
    def add_company(self, name):
        """Add a new company"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO companies (name) VALUES (?)", (name.strip(),))
                conn.commit()
                logger.info(f"Added company: {name}")
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Company already exists: {name}")
            raise ValueError(f"Company '{name}' already exists")
        except Exception as e:
            logger.error(f"Failed to add company {name}: {e}")
            raise

    def get_companies(self):
        """Get all companies as list of tuples (id, name)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name FROM companies ORDER BY name")
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to get companies: {e}")
            raise

    def delete_company(self, company_id):
        """Delete company and all related data"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM companies WHERE id = ?", (company_id,))
                company = cursor.fetchone()
                if company:
                    cursor.execute("DELETE FROM companies WHERE id = ?", (company_id,))
                    conn.commit()
                    logger.info(f"Deleted company ID {company_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to delete company ID {company_id}: {e}")
            raise

    def add_board(self, name, description, company_id):
        """Add a new board to a company"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # First check if the company exists
                cursor.execute("SELECT id FROM companies WHERE id = ?", (company_id,))
                if not cursor.fetchone():
                    raise ValueError(f"Company with ID {company_id} does not exist")

                # Check if board already exists for this company
                cursor.execute("SELECT id FROM boards WHERE company_id = ? AND name = ?", 
                              (company_id, name.strip()))
                if cursor.fetchone():
                    raise ValueError(f"Board '{name}' already exists for this company")

                # Add the board
                cursor.execute("INSERT INTO boards (company_id, name, description) VALUES (?, ?, ?)",
                              (company_id, name.strip(), description))
                conn.commit()
                logger.info(f"Added board: {name} for company ID {company_id}")
                return cursor.lastrowid

        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY" in str(e):
                raise ValueError(f"Company with ID {company_id} does not exist")
            else:
                logger.error(f"Database integrity error: {e}")
                raise
        except Exception as e:
            logger.error(f"Failed to add board '{name}': {e}")
            raise

    def get_boards(self, company_id):
        """Get all boards for a company"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name FROM boards WHERE company_id = ? ORDER BY name", 
                              (company_id,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to get boards for company ID {company_id}: {e}")
            raise

    def delete_board(self, board_id):
        """Delete board and all related notes"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM boards WHERE id = ?", (board_id,))
                board = cursor.fetchone()
                if board:
                    cursor.execute("DELETE FROM boards WHERE id = ?", (board_id,))
                    conn.commit()
                    logger.info(f"Deleted board ID {board_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to delete board ID {board_id}: {e}")
            raise

    # Note operations  
    def add_note(self, board_id, topic, title, content, user_id, priority=1):
        """Add a new note"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO notes (board_id, topic, title, content, created_by, last_modified_by, priority) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (board_id, topic.strip(), title.strip(), content, user_id, user_id, priority))
                
                note_id = cursor.lastrowid
                
                # Add to history
                cursor.execute("""
                    INSERT INTO note_history (note_id, action, user_id)
                    VALUES (?, 'created', ?)
                """, (note_id, user_id))
                
                conn.commit()
                logger.info(f"Added note '{title}' to board ID {board_id}")
                return note_id
        except Exception as e:
            logger.error(f"Failed to add note '{title}': {e}")
            raise

    def get_notes(self, board_id, topic=None, include_archived=False):
        """Get notes for a board, optionally filtered by topic"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT id, topic, title, content, created_at, updated_at, 
                           created_by, last_modified_by, priority, is_archived
                    FROM notes 
                    WHERE board_id = ?
                """
                params = [board_id]
                
                if not include_archived:
                    query += " AND is_archived = FALSE"
                
                if topic:
                    query += " AND topic = ?"
                    params.append(topic)
                
                query += " ORDER BY priority DESC, updated_at DESC"
                
                cursor.execute(query, params)
                
                # Convert to dictionaries for easier use
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get notes for board ID {board_id}: {e}")
            raise

    def get_note_history(self, note_id):
        """Get full history of a note"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT action, user_id, timestamp, old_title, old_content, old_topic, old_priority
                    FROM note_history
                    WHERE note_id = ?
                    ORDER BY timestamp DESC
                """, (note_id,))  # FIX: Added comma to make it a tuple

                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to fetch note history for note {note_id}: {e}")
            raise

    def get_topics(self, board_id):
        """Get all unique topics for a board"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT topic FROM notes 
                    WHERE board_id = ? AND is_archived = FALSE 
                    ORDER BY topic
                """, (board_id,))
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get topics for board ID {board_id}: {e}")
            raise

    def update_note(self, note_id, title, content, user_id, topic=None, priority=None):
        """Update an existing note"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Get old values first
                cursor.execute("SELECT title, content, topic, priority FROM notes WHERE id = ?", (note_id,))
                old = cursor.fetchone()
                
                if not old:
                    raise ValueError(f"Note with ID {note_id} not found")

                # Build dynamic update query
                updates = ["title = ?", "content = ?", "last_modified_by = ?", "updated_at = CURRENT_TIMESTAMP"]
                params = [title.strip(), content, user_id]

                if topic is not None:
                    updates.append("topic = ?")
                    params.append(topic.strip())

                if priority is not None:
                    updates.append("priority = ?")
                    params.append(priority)

                params.append(note_id)

                query = f"UPDATE notes SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
                
                # Add to history
                cursor.execute("""
                    INSERT INTO note_history 
                    (note_id, action, user_id, old_title, old_content, old_topic, old_priority) 
                    VALUES (?, 'updated', ?, ?, ?, ?, ?)
                """, (note_id, 
                    str(user_id),
                    str(old[0]) if old[0] is not None else None,
                    str(old[1]) if old[1] is not None else None,
                    str(old[2]) if old[2] is not None else None, 
                    str(old[3]) if old[3] is not None else None))

                conn.commit()
                
                logger.info(f"Updated note ID {note_id}")
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to update note ID {note_id}: {e}")
            raise

    def archive_note(self, note_id, user_id):
        """Archive a note instead of deleting it"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO note_history (note_id, action, user_id)
                    VALUES (?, 'archived', ?)
                """, (note_id, user_id))

                cursor.execute("""
                    UPDATE notes
                    SET is_archived = TRUE,
                        last_modified_by = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """, (user_id, note_id))
                
                conn.commit()
                logger.info(f"Archived note ID {note_id}")
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to archive note ID {note_id}: {e}")
            raise

    def search_notes(self, board_id, search_term):
        """Search notes by title or content"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, topic, title, content, created_at, updated_at, 
                           created_by, last_modified_by, priority
                    FROM notes 
                    WHERE board_id = ? AND is_archived = FALSE 
                    AND (title LIKE ? OR content LIKE ?)
                    ORDER BY priority DESC, updated_at DESC
                """, (board_id, f"%{search_term}%", f"%{search_term}%"))
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to search notes in board ID {board_id}: {e}")
            raise