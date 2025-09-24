import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.database_manager import DatabaseManager

def main():
    db = DatabaseManager()
    print('DB path:', db.full_db_path)
    companies = db.get_companies()
    print('Companies:', companies)
    for cid, name in companies:
        boards = db.get_boards(cid)
        print(f'Boards for {name} ({cid}):', boards)
        for b in boards:
            bid = b[0]
            notes = db.get_notes(bid, include_archived=True)
            print(f'Notes for board id {bid}:')
            for n in notes:
                print(' -', n['id'], n['topic'], n['title'], '(archived)' if n.get('is_archived') else '')

if __name__ == '__main__':
    main()
