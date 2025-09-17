# frontend/styles.py
"""CSS styles for the application without unsupported properties"""

# Main window background
MAIN_WINDOW_STYLE = """
    QMainWindow {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #667eea, stop:1 #764ba2);
    }
"""

# Content area
CONTENT_AREA_STYLE = """
    QWidget {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        margin: 5px;
    }
"""

# Sidebar
SIDEBAR_STYLE = """
    QWidget {
        background: #f8f9fa;
        border-right: 1px solid #e9ecef;
    }
"""

# Section headers
SECTION_HEADER_STYLE = """
    QLabel {
        color: #6c757d;
        font-weight: bold;
        font-size: 11px;
        letter-spacing: 1px;
        padding: 5px 0;
    }
"""

# Input fields
INPUT_STYLE = """
    QLineEdit, QComboBox, QSpinBox, QTextEdit {
        padding: 8px;
        border: 2px solid #e9ecef;
        border-radius: 6px;
        font-size: 14px;
        background: white;
    }
    QLineEdit:focus, QComboBox:focus {
        border-color: #3498db;
    }
"""

# User input specific
USER_INPUT_STYLE = """
    QLineEdit {
        padding: 10px;
        border: 2px solid #e9ecef;
        border-radius: 8px;
        background: white;
        font-size: 14px;
    }
    QLineEdit:focus {
        border-color: #3498db;
    }
"""

# Combo boxes
COMBO_BOX_STYLE = """
    QComboBox {
        padding: 10px;
        border: 2px solid #e9ecef;
        border-radius: 8px;
        background: white;
        font-size: 14px;
        min-width: 180px;
        color: #2c3e50;
    }
    QComboBox:focus {
        border-color: #3498db;
    }
    QComboBox:hover {
        border-color: #3498db;
        background: #f8f9fa;
    }
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    QComboBox::down-arrow {
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid #6c757d;
        margin-right: 5px;
    }
"""

# Circular buttons
CIRCULAR_BUTTON_STYLE = """
    QPushButton {
        background: #3498db;
        color: white;
        border: none;
        width: 35px;
        height: 35px;
        border-radius: 17px;
        font-size: 12px;
        font-weight: bold;
    }
    QPushButton:hover {
        background: #2980b9;
    }
"""

DELETE_BUTTON_STYLE = CIRCULAR_BUTTON_STYLE.replace("#3498db", "#e74c3c").replace("#2980b9", "#c0392b")

# Action buttons
ACTION_BUTTON_STYLE = """
    QPushButton {
        padding: 10px 20px;
        border: none;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        color: white;
    }
"""

NEW_NOTE_BUTTON_STYLE = """
    QPushButton {
        padding: 10px 20px;
        border: none;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        color: white;
        background: #3498db;
    }
    QPushButton:hover {
        background: #2980b9;
    }
"""

EDIT_NOTE_BUTTON_STYLE = """
    QPushButton {
        padding: 10px 20px;
        border: none;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        color: white;
        background: #6c757d;
    }
    QPushButton:hover {
        background: #5a6268;
    }
"""

ARCHIVE_NOTE_BUTTON_STYLE = """
    QPushButton {
        padding: 10px 20px;
        border: none;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        color: white;
        background: #e74c3c;
    }
    QPushButton:hover {
        background: #c0392b;
    }
"""

# View toggle buttons
VIEW_BUTTON_STYLE = """
    QPushButton {
        background: #e9ecef;
        border: none;
        padding: 8px 12px;
        font-size: 12px;
        font-weight: 500;
        color: #6c757d;
    }
    QPushButton:checked {
        background: #3498db;
        color: white;
    }
    QPushButton:hover {
        background: #3498db;
        color: white;
    }
"""

# Search input
SEARCH_INPUT_STYLE = """
    QLineEdit {
        padding: 10px 15px;
        border: 2px solid #e9ecef;
        border-radius: 25px;
        background: white;
        font-size: 14px;
        min-width: 300px;
    }
    QLineEdit:focus {
        border-color: #3498db;
    }
"""

# Toolbar
TOOLBAR_STYLE = """
    QWidget {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
    }
"""
# table
TABLE_STYLE = """
QTableWidget {
    background: white;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    gridline-color: #f8f9fa;
    font-size: 14px;
}
QTableWidget::item {
    padding: 12px 8px;
    border-bottom: 1px solid #f8f9fa;
}
QTableWidget::item:selected {
    background: #e3f2fd;
    color: #1976d2;
}
QTableWidget::item:hover {
    background: #f8f9fa;
}
QHeaderView::section {
    background: #f8f9fa;
    color: #6c757d;
    padding: 12px 8px;
    border: none;
    border-bottom: 2px solid #e9ecef;
    font-weight: bold;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
"""

# Topic buttons
def topic_button_style(color):
    return f"""
    QPushButton {{
        background: {color};
        color: white;
        border: none;
        padding: 8px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        text-align: left;
    }}
    QPushButton:hover {{
        background: {color};
        opacity: 0.9;
    }}
    """