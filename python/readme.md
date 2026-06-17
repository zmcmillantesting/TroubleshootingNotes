@zmcmillantesting
# Project Structure:
- project/
    - ├── backend/
        - │   ├── __init__.py
        - │   ├── database_manager.py  # Refactored MyDatabaseManager
        - │   └── models.py           # Data models if needed
    - ├── frontend/
        - │   ├── __init__.py
        - │   ├── main_window.py      # LearningWindow class
        - │   ├── dialogs.py          # All dialog classes
        - │   └── widgets.py          # Custom widgets like ModernCard
    - ├── tests/
        - │   ├── __init__.py
        - │   ├── test_database.py    # Database tests
        - │   └── test_ui.py         # UI tests (if needed)
    - ├── utils/
        - │   ├── __init__.py
        - │   └── logger.py          # Logging configuration
    - └── main.py                # Application entry point

# TODOS
- perform testing on compiled version to ensure all features work on V2.1.0
- topic label shows white on white which makes the topic difficult to read. Change topic button background or lettering for ease of reading 
- disable all features until user enters in user id 