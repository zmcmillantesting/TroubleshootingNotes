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
        content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
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

def add_note(board_id, content):
    db_path = r"P:\EMS_TR_PATH\Shared_notes"
    connection = sql.connect(os.path.join(db_path, "shard_notes.db"))
    cursor = connection.cursor()
    cursor.execute("INSERT INTO notes (board_id, content) VALUES (?, ?)", (board_id, content))
    connection.commit()
    note_id = cursor.lastrowid
    connection.close()
    return note_id