# frontend/dialogs.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Dialog for adding/editing companies
class CompanyDialog(QDialog):
    def __init__(self, parent=None, company_name=""):
        super().__init__(parent)
        self.setWindowTitle("Add Company" if not company_name else "Edit Company")
        self.setModal(True)
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout(self)
        
        # Company name input
        layout.addWidget(QLabel("Company Name:"))
        self.name_input = QLineEdit(company_name)
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.name_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.name_input.setFocus()

    def get_company_name(self):
        return self.name_input.text().strip()

# Dialog for adding/editing boards
class BoardDialog(QDialog):
    def __init__(self, parent=None, board_name="", description=""):
        super().__init__(parent)
        self.setWindowTitle("Add Board" if not board_name else "Edit Board")
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout(self)
        
        # Board name input
        layout.addWidget(QLabel("Board Name:"))
        self.name_input = QLineEdit(board_name)
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.name_input)
        
        # Description input
        layout.addWidget(QLabel("Description (optional):"))
        self.description_input = QTextEdit(description)
        self.description_input.setMaximumHeight(80)
        self.description_input.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.description_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.name_input.setFocus()

    def get_board_data(self):
        return self.name_input.text().strip(), self.description_input.toPlainText().strip()

# Dialog for adding/editing notes
class NoteDialog(QDialog):
    def __init__(self, parent=None, note_data=None, topics=None):
        super().__init__(parent)
        self.note_data = note_data
        self.setWindowTitle("Add Note" if not note_data else "Edit Note")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Title input
        layout.addWidget(QLabel("Title:"))
        self.title_input = QLineEdit()
        if note_data:
            self.title_input.setText(note_data.get('title', ''))
        layout.addWidget(self.title_input)
        
        # Topic input
        layout.addWidget(QLabel("Topic:"))
        self.topic_input = QComboBox()
        self.topic_input.setEditable(True)
        if topics:
            self.topic_input.addItems(topics)
        if note_data:
            self.topic_input.setCurrentText(note_data.get('topic', 'General'))
        else:
            self.topic_input.setCurrentText('General')
        layout.addWidget(self.topic_input)
        
        # Priority input
        layout.addWidget(QLabel("Priority:"))
        self.priority_input = QSpinBox()
        self.priority_input.setRange(1, 5)
        if note_data:
            self.priority_input.setValue(note_data.get('priority', 1))
        else:
            self.priority_input.setValue(1)
        layout.addWidget(self.priority_input)
        
        # Content input
        layout.addWidget(QLabel("Content:"))
        self.content_input = QTextEdit()
        if note_data:
            self.content_input.setText(note_data.get('content', ''))
        layout.addWidget(self.content_input)
        
        # Style the inputs
        input_style = """
            QLineEdit, QComboBox, QSpinBox, QTextEdit {
                padding: 8px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                font-size: 14px;
            }
        """
        self.setStyleSheet(input_style)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.title_input.setFocus()

    def get_note_data(self):
        return {
            'title': self.title_input.text().strip(),
            'topic': self.topic_input.currentText().strip(),
            'content': self.content_input.toPlainText(),
            'priority': self.priority_input.value()
        }