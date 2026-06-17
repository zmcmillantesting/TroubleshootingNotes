# database_debug_test.py
import tempfile
import os
import shutil
from backend.database_manager import DatabaseManager

def test_cascade_deletion():
    """Test if cascade deletion is working properly"""
    
    # Create temp database
    test_dir = tempfile.mkdtemp()
    db_path = os.path.join(test_dir, "test_db")
    db = DatabaseManager(db_path=db_path, db_name="test_cascade.db")
    
    try:
        print("=== Testing Cascade Deletion ===")
        
        # 1. Add company
        company_id = db.add_company("Test Company")
        print(f"✓ Added company ID: {company_id}")
        
        # 2. Add board
        board_id = db.add_board("Test Board", "Test Description", company_id)
        print(f"✓ Added board ID: {board_id}")
        
        # 3. Add some notes
        note1_id = db.add_note(board_id, "Topic1", "Note 1", "Content 1", "user1", 1)
        note2_id = db.add_note(board_id, "Topic2", "Note 2", "Content 2", "user1", 2)
        print(f"✓ Added notes: {note1_id}, {note2_id}")
        
        # 4. Check current state
        companies = db.get_companies()
        boards = db.get_boards(company_id)
        notes = db.get_notes(board_id)
        
        print(f"Current state:")
        print(f"  Companies: {len(companies)}")
        print(f"  Boards: {len(boards)}")
        print(f"  Notes: {len(notes)}")
        
        # 5. Delete company (should cascade delete boards and notes)
        print("\n--- Deleting company (should cascade) ---")
        result = db.delete_company(company_id)
        print(f"Delete company result: {result}")
        
        # 6. Check state after deletion
        companies_after = db.get_companies()
        boards_after = db.get_boards(company_id) if company_id else []
        notes_after = db.get_notes(board_id) if board_id else []
        
        print(f"After company deletion:")
        print(f"  Companies: {len(companies_after)}")
        print(f"  Boards: {len(boards_after)}")
        print(f"  Notes: {len(notes_after)}")
        
        # 7. Test foreign key constraints are working
        print("\n--- Testing Foreign Key Constraints ---")
        try:
            # This should fail because company doesn't exist
            db.add_board("Orphan Board", "Should fail", 999)
            print("✗ Foreign key constraint NOT working - orphan board created")
        except ValueError as e:
            print(f"✓ Foreign key constraint working: {e}")
        except Exception as e:
            print(f"✓ Foreign key constraint working (different error): {e}")
            
        return len(companies_after) == 0 and len(boards_after) == 0 and len(notes_after) == 0
        
    except Exception as e:
        print(f"✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        shutil.rmtree(test_dir)

def test_database_isolation():
    """Test if creating fresh databases gives clean state"""
    print("\n=== Testing Database Isolation ===")
    
    results = []
    
    for i in range(3):
        print(f"\n--- Test iteration {i+1} ---")
        
        # Create fresh temp database
        test_dir = tempfile.mkdtemp()
        db_path = os.path.join(test_dir, "test_db")
        db = DatabaseManager(db_path=db_path, db_name=f"test_isolation_{i}.db")
        
        try:
            # Check initial state
            companies = db.get_companies()
            print(f"Initial companies in fresh DB: {len(companies)}")
            
            # Add test data
            company_id = db.add_company(f"Company {i}")
            board_id = db.add_board(f"Board {i}", f"Description {i}", company_id)
            
            # Check state
            companies_after = db.get_companies()
            boards_after = db.get_boards(company_id)
            
            print(f"After adding data - Companies: {len(companies_after)}, Boards: {len(boards_after)}")
            
            results.append({
                'iteration': i,
                'initial_companies': len(companies),
                'final_companies': len(companies_after),
                'final_boards': len(boards_after)
            })
            
        finally:
            shutil.rmtree(test_dir)
    
    print(f"\nIsolation test results: {results}")
    
    # All fresh databases should start with 0 companies
    all_clean = all(r['initial_companies'] == 0 for r in results)
    print(f"All databases started clean: {all_clean}")
    
    return all_clean

if __name__ == "__main__":
    print("Running database diagnostics...")
    
    cascade_works = test_cascade_deletion()
    isolation_works = test_database_isolation()
    
    print(f"\n=== SUMMARY ===")
    print(f"Cascade deletion works: {cascade_works}")
    print(f"Database isolation works: {isolation_works}")
    
    if not cascade_works:
        print("⚠️  CASCADE DELETION ISSUE - Foreign keys might not be properly configured")
    if not isolation_works:
        print("⚠️  DATABASE ISOLATION ISSUE - Test databases are not starting clean")
    
    if cascade_works and isolation_works:
        print("✅ Database operations appear to be working correctly")