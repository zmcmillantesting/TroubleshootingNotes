# debug_test.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from PyQt5.QtWidgets import QApplication
from frontend.main_window import LearningWindow

def test_window_creation():
    """Test if the window can be created without errors"""
    app = QApplication(sys.argv)
    
    try:
        window = LearningWindow()
        print("✓ Window created successfully")
        return True
    except Exception as e:
        print(f"✗ Error creating window: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        app.quit()

if __name__ == "__main__":
    test_window_creation()