# test_imports.py
try:
    from backend.database_manager import DatabaseManager
    print("✓ DatabaseManager imported successfully")
    
    db = DatabaseManager()
    print("✓ Database connection established")
    
    companies = db.get_companies()
    print(f"✓ Found {len(companies)} companies")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()