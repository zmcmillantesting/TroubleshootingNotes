# tests/test_no_warnings.py
import unittest
import sys
from io import StringIO
from contextlib import redirect_stderr

# Import Qt modules
from PyQt5.QtWidgets import QApplication

# Import the simplified window
from frontend.main_window import LearningWindow

class TestNoWarnings(unittest.TestCase):
    def setUp(self):
        # Create QApplication instance if it doesn't exist
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.captured_stderr = StringIO()
        
    def test_no_transform_warnings(self):
        """Test that no transform warnings are generated"""
        with redirect_stderr(self.captured_stderr):
            # This should not generate transform warnings
            window = LearningWindow()
            window.show()  # Show the window briefly
            window.close()  # Close it immediately
        
        stderr_output = self.captured_stderr.getvalue()
        print("Captured stderr output:")
        print(stderr_output)
        
        # Check for the specific warnings we want to eliminate
        self.assertNotIn("Unknown property transform", stderr_output)
        self.assertNotIn("Unknown property box-shadow", stderr_output)

if __name__ == "__main__":
    unittest.main()