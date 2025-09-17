# frontend/dialogs.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class CompanyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Company")
        self.setModal(True)
        self.setFixedSize(400, 150)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Company name input
        layout.addWidget(QLabel("Company Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter company name...")
        layout.addWidget(self.name_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Add")
        self.cancel_button = QPushButton("Cancel")
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Focus on input
        self.name_input.setFocus()
        
    def get_company_name(self):
        return self.name_input.text().strip()

class BoardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Board")
        self.setModal(True)
        self.setFixedSize(450, 200)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Board name input
        layout.addWidget(QLabel("Board Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter board name...")
        layout.addWidget(self.name_input)
        
        # Description input
        layout.addWidget(QLabel("Description (optional):"))
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter board description...")
        self.description_input.setMaximumHeight(80)
        layout.addWidget(self.description_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Add")
        self.cancel_button = QPushButton("Cancel")
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Focus on input
        self.name_input.setFocus()
        
    def get_board_data(self):
        return (
            self.name_input.text().strip(),
            self.description_input.toPlainText().strip()
        )

class NoteDialog(QDialog):
    def __init__(self, parent=None, note_data=None, topics=None):
        super().__init__(parent)
        self.note_data = note_data
        self.topics = topics
        self.setWindowTitle("Edit Note" if note_data else "Add Note")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        self.setup_ui()
        # If editing, populate fields
        if note_data:
            self.populate_fields()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Topic input
        layout.addWidget(QLabel("Topic:"))
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("Enter topic (e.g., Network, Software, Hardware)...")
        # If topics are provided, show them as a dropdown
        if self.topics and isinstance(self.topics, (list, tuple)) and len(self.topics) > 0:
            self.topic_combo = QComboBox()
            self.topic_combo.setEditable(True)
            self.topic_combo.addItems(self.topics)
            self.topic_combo.setCurrentText("General")
            layout.addWidget(self.topic_combo)
            self.topic_input = self.topic_combo
        else:
            layout.addWidget(self.topic_input)
        
        # Title input
        layout.addWidget(QLabel("Title:"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter note title...")
        layout.addWidget(self.title_input)
        
        # Priority selection
        priority_layout = QHBoxLayout()
        priority_layout.addWidget(QLabel("Priority:"))
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["1 - Low", "2 - Medium", "3 - High", "4 - Critical"])
        self.priority_combo.setCurrentIndex(1)  # Default to Medium
        priority_layout.addWidget(self.priority_combo)
        priority_layout.addStretch()
        layout.addLayout(priority_layout)
        
        # Content input
        layout.addWidget(QLabel("Content:"))
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Enter detailed note content...")
        layout.addWidget(self.content_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        
        self.ok_button.clicked.connect(self.validate_and_accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Focus on title input
        self.title_input.setFocus()
        
    def populate_fields(self):
        """Populate fields when editing a note"""
        if self.note_data:
            self.topic_input.setText(self.note_data.get('topic', ''))
            self.title_input.setText(self.note_data.get('title', ''))
            self.content_input.setPlainText(self.note_data.get('content', ''))
            
            # Set priority
            priority = self.note_data.get('priority', 1)
            self.priority_combo.setCurrentIndex(priority - 1)
    
    def validate_and_accept(self):
        """Validate input before accepting"""
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "Warning", "Title cannot be empty")
            return
            
        if not self.content_input.toPlainText().strip():
            QMessageBox.warning(self, "Warning", "Content cannot be empty")
            return
            
        self.accept()
        
    def get_note_data(self):
        """Get note data as dictionary"""
        # Handle both QLineEdit and QComboBox for topic input
        if hasattr(self.topic_input, 'currentText'):  # QComboBox
            topic = self.topic_input.currentText().strip()
        else:  # QLineEdit
            topic = self.topic_input.text().strip()
            
        return {
            'topic': topic or 'General',
            'title': self.title_input.text().strip(),
<<<<<<< HEAD
            'content': self.content_input.toPlainText().strip(),
            'priority': self.priority_combo.currentIndex() + 1
        }
=======
            'topic': self.topic_input.currentText().strip(),
            'content': self.content_input.toPlainText(),
            'priority': self.priority_input.value()
        }
    
# Dialog for checking note history
class NoteHistoryDialog(QDialog):
    def __init__(self, history, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📜 Note History")
        self.setMinimumSize(600,400)

        layout = QVBoxLayout(self)

        if not history:
            layout.addWidget(QLabel("No history found for this note"))
            return
    
        table = QTableWidget(len(history), 7)
        table.setHorizontalHeaderLabels([
            "Action", "User", "Timestamp", "Old Title", "Old Content", "Old Topic", "Old Priority"
        ])
        table.horizontalHeader().setStretchLastSection(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        for row_idx, row in enumerate(history):
            table.setItem(row_idx, 0, QTableWidgetItem(row["action"]))
            table.setItem(row_idx, 1, QTableWidgetItem(row["user_id"]))
            table.setItem(row_idx, 2, QTableWidgetItem(row["timestamp"]))
            table.setItem(row_idx, 3, QTableWidgetItem(row["old_title"] or ""))
            table.setItem(row_idx, 4, QTableWidgetItem((row["old_content"][:50] + "...") if row["old_content"] else ""))
            table.setItem(row_idx, 5, QTableWidgetItem(row["old_topic"] or ""))
            table.setItem(row_idx, 6, QTableWidgetItem(str(row["old_priority"]) if row["old_priority"] else ""))

        layout.addWidget(table)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)
        
>>>>>>> V2
