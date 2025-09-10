import sqlite3 as sql
import sys, os

def main():
    db_path = r"P:\EMS_TR_PATH\Shared_notes"
    if os.path.exists(db_path):
        try:
            connection = sql.connect(os.path.join(db_path, "shard_notes.db"))
            query = connection.cursor()
            check1 = query.execute("SELECT name FROM sqlite_master")
            print(check1.fetchall())
            return check1.fetchall()
        except sql.Error as e:
            print(f"SQL error: {e}")

def contents(tables):
    db_path = r"P:\EMS_TR_PATH\Shared_notes"
    if os.path.exists(db_path):
        try:
            con = sql.connect(os.path.join(db_path, "shard_notes.db"))
            query = con.cursor()
            query.execute("SELECT name FROM companies")
            companies = query.fetchall()
            print("Companies:")
            for company in companies:
                print(company)
            query.execute("SELECT * FROM boards")
            boards = query.fetchall()
            print("\nBoards:")
            for board in boards:
                print(board)
            query.execute("SELECT * FROM notes")
            notes = query.fetchall()
            print("\nNotes:")
            for note in notes:
                print(note)
            con.close()
        except sql.Error as e:
            print(f"SQL error: {e}")
2
if __name__ == "__main__":
    user_input = input(f"enter 1 to run table check\n enter 2 to check contents of table\n enter 3 to exit\n")
    if user_input == '1':
        main()
    elif user_input == '2':
        tables = main()
        contents(tables)