import sqlite3 as sql
import sys, os


def init_db():
    db_path = r"P:\EMS_TR_PATH\Shared_notes"
    os.makedirs(db_path, exist_ok=True)
    connection = sql.connect(os.path.join(db_path, "shard_notes.db"))
    cursor = connection.cursor()


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
        )""")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS boards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        name TEXT NOT NULL,
        UNIQUE(company_id, name),
        FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
        )""")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        board_id INTEGER, 
        topic TEXT DEFAULT 'General',
        content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_by TEXT,
        last_modified_by TEXT,
        FOREIGN KEY (board_id) REFERENCES boards(id) ON DELETE CASCADE
        )""")
    
    connection.commit()
    connection.close()


def add_company(name):
    db_path = r"P:\EMS_TR_PATH\Shared_notes"
    connection = sql.connect(os.path.join(db_path, "shard_notes.db"))
    cursor = connection.cursor()
    cursor.execute("INSERT INTO companies (name) VALUES (?)", (name,))
    connection.commit()
    company_id = cursor.lastrowid
    connection.close()
    return company_id

def add_board(company_id, name):
    db_path = r"P:\EMS_TR_PATH\Shared_notes"
    connection = sql.connect(os.path.join(db_path, "shard_notes.db"))
    cursor = connection.cursor()
    cursor.execute("INSERT INTO boards (company_id, name) VALUES (?, ?)", (company_id, name))
    connection.commit()
    board_id = cursor.lastrowid
    connection.close()
    return board_id

def add_note(board_id, topic, content, user_id):
    db_path = r"P:\EMS_TR_PATH\Shared_notes"
    connection = sql.connect(os.path.join(db_path, "shard_notes.db"))
    cursor = connection.cursor()
    cursor.execute("INSERT INTO notes (board_id, topic, content, created_by, last_modified_by) VALUES (?, ?, ?, ?, ?)", (board_id, topic, content, user_id, user_id))
    connection.commit()
    note_id = cursor.lastrowid
    connection.close()
    return note_id

def edit_note(note_id, new_content, user_id):
    db_path = r"P:\EMS_TR_PATH\Shared_notes"
    connection = sql.connect(os.path.join(db_path, "shard_notes.db"))
    cursor = connection.cursor()
    cursor.execute("UPDATE notes SET content = ?, last_modified_by = ?, timestamp = CURRENT_TIMESTAMP WHERE id = ?", (new_content, user_id, note_id))
    connection.commit()
    connection.close()

def get_topics(board_id):
    db_path = r"P:\EMS_TR_PATH\Shared_notes"
    con = sql.connect(os.path.join(db_path, "shard_notes.db"))
    query = con.cursor()
    query.execute("SELECT DISTINCT topic FROM notes WHERE board_id = ? ORDER BY topic", (board_id,))
    topics = [row[0] for row in query.fetchall()]
    con.close()
    return topics

def get_notes_by_topic(board_id, topic):
    db_path = r"P:\EMS_TR_PATH\Shared_notes"
    con = sql.connect(os.path.join(db_path, "shard_notes.db"))
    query = con.cursor()
    query.execute("SELECT content FROM notes WHERE board_id = ? AND topic = ?", (board_id, topic,))
    notes = [row[0] for row in query.fetchall()]
    con.close()
    return notes