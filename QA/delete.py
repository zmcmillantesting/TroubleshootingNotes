import sqlite3 as sql
import sys, os

def main():
    db_path = r"P:\EMS_TR_PATH\Shared_notes"
    if os.path.exists(db_path):
        try:
            con = sql.connect(os.path.join(db_path, "shard_notes.db"))
            query = con.cursor()
            query.execute("DELETE FROM sql_master 'sqlite_autoindex_companies_1' AND 'sqlite_sequence' AND 'sqlite_autoindex_boards_1'")
            con.commit()
            con.close()
        except sql.Error as e:
            print(f"SQL error: {e}")

if __name__ == "__main__":
    main()