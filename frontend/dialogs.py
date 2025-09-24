# frontend/dialogs.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime

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

# Dialog for viewing notes in read-only format
class NoteViewerDialog(QDialog):
    def __init__(self, note_data, parent=None):
        super().__init__(parent)
        self.note_data = note_data
        self.setWindowTitle(f"📖 View Note: {note_data.get('title', 'Untitled')}")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with metadata
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        # Title
        title_label = QLabel(self.note_data.get('title', 'Untitled'))
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        title_label.setWordWrap(True)
        header_layout.addWidget(title_label)
        
        # Metadata row
        metadata_layout = QHBoxLayout()
        
        # Topic
        topic_label = QLabel(f"📋 Topic: {self.note_data.get('topic', 'General')}")
        topic_label.setStyleSheet("color: #1976d2; font-weight: 500;")
        metadata_layout.addWidget(topic_label)
        
        # Priority
        priority = self.note_data.get('priority', 1)
        priority_colors = {1: "#27ae60", 2: "#f39c12", 3: "#e67e22", 4: "#e74c3c", 5: "#8e44ad"}
        priority_color = priority_colors.get(priority, "#6c757d")
        
        priority_label = QLabel(f"🔥 Priority: {priority}")
        priority_label.setStyleSheet(f"color: {priority_color}; font-weight: 500;")
        metadata_layout.addWidget(priority_label)
        
        metadata_layout.addStretch()
        header_layout.addLayout(metadata_layout)
        
        # Creation info
        creation_layout = QHBoxLayout()
        created_by = self.note_data.get('created_by', 'Unknown')
        created_at = self.note_data.get('created_at', '')
        
        # Format date
        try:
            if isinstance(created_at, str) and created_at:
                from datetime import datetime
                date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime('%B %d, %Y at %I:%M %p')
            else:
                formatted_date = "Unknown date"
        except:
            formatted_date = "Unknown date"
        
        created_label = QLabel(f"👤 Created by: {created_by}")
        created_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        creation_layout.addWidget(created_label)
        
        date_label = QLabel(f"📅 {formatted_date}")
        date_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        creation_layout.addWidget(date_label)
        
        creation_layout.addStretch()
        header_layout.addLayout(creation_layout)
        
        # Last modified info
        updated_at = self.note_data.get('updated_at', '')
        last_modified_by = self.note_data.get('last_modified_by', '')
        
        if updated_at and updated_at != created_at:
            try:
                if isinstance(updated_at, str):
                    date_obj = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    formatted_update = date_obj.strftime('%B %d, %Y at %I:%M %p')
                else:
                    formatted_update = "Unknown date"
            except:
                formatted_update = "Unknown date"
            
            modified_label = QLabel(f"✏️ Last modified by {last_modified_by} on {formatted_update}")
            modified_label.setStyleSheet("color: #6c757d; font-size: 11px; font-style: italic;")
            header_layout.addWidget(modified_label)
        
        layout.addWidget(header_frame)
        
        # Content section
        content_label = QLabel("Content:")
        content_label.setStyleSheet("font-weight: bold; color: #2c3e50; margin-top: 10px;")
        layout.addWidget(content_label)
        
        # Content display
        content_display = QTextEdit()
        content_display.setReadOnly(True)
        content_display.setText(self.note_data.get('content', 'No content available'))
        content_display.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 15px;
                background: white;
                font-size: 14px;
                line-height: 1.6;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        layout.addWidget(content_display)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Edit button
        edit_btn = QPushButton("📝 Edit Note")
        edit_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        edit_btn.clicked.connect(self.edit_note)
        button_layout.addWidget(edit_btn)
        
        # Close button
        close_btn = QPushButton("❌ Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #5a6268;
            }
        """)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
    def edit_note(self):
        """Signal that the user wants to edit this note"""
        self.done(2)  # Return code 2 indicates edit was requested

# Dialog for checking note history
class NoteHistoryDialog(QDialog):
    def __init__(self, history, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📜 Note History")
        self.setMinimumSize(800, 400)
        self.setModal(True)

        layout = QVBoxLayout(self)

        if not history:
            no_history_label = QLabel("No history found for this note")
            no_history_label.setAlignment(Qt.AlignCenter)
            no_history_label.setStyleSheet("""
                QLabel {
                    color: #6c757d;
                    font-size: 16px;
                    padding: 40px;
                }
            """)
            layout.addWidget(no_history_label)
        else:
            # Create table
            table = QTableWidget(len(history), 7)
            table.setHorizontalHeaderLabels([
                "Action", "User", "Timestamp", "Old Title", "Old Content", "Old Topic", "Old Priority"
            ])
            
            # Set column widths
            header = table.horizontalHeader()
            header.setStretchLastSection(False)
            header.resizeSection(0, 80)   # Action
            header.resizeSection(1, 100)  # User
            header.resizeSection(2, 150)  # Timestamp
            header.resizeSection(3, 120)  # Old Title
            header.resizeSection(4, 200)  # Old Content
            header.resizeSection(5, 100)  # Old Topic
            header.resizeSection(6, 80)   # Old Priority
            
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setAlternatingRowColors(True)
            table.setStyleSheet("""
                QTableWidget {
                    gridline-color: #e9ecef;
                    background-color: white;
                }
                QTableWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #e9ecef;
                }
                QTableWidget::item:selected {
                    background-color: #e3f2fd;
                }
                QHeaderView::section {
                    background-color: #f8f9fa;
                    padding: 8px;
                    border: none;
                    border-bottom: 2px solid #dee2e6;
                    font-weight: bold;
                }
            """)

            # Populate table
            for row_idx, row in enumerate(history):
                # Action
                action_item = QTableWidgetItem(row.get("action", ""))
                if row.get("action") == "created":
                    action_item.setBackground(QColor(212, 237, 218))
                elif row.get("action") == "updated":
                    action_item.setBackground(QColor(255, 243, 205))
                elif row.get("action") == "archived":
                    action_item.setBackground(QColor(248, 215, 218))
                table.setItem(row_idx, 0, action_item)
                
                # User
                table.setItem(row_idx, 1, QTableWidgetItem(row.get("user_id", "")))
                
                # Timestamp
                timestamp = row.get("timestamp", "")
                if timestamp:
                    try:
                        # Format the timestamp to be more readable
                        from datetime import datetime
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        formatted_time = timestamp
                    table.setItem(row_idx, 2, QTableWidgetItem(formatted_time))
                else:
                    table.setItem(row_idx, 2, QTableWidgetItem(""))
                
                # Old Title
                old_title = row.get("old_title", "") or ""
                table.setItem(row_idx, 3, QTableWidgetItem(old_title))
                
                # Old Content (truncated)
                old_content = row.get("old_content", "") or ""
                if len(old_content) > 50:
                    old_content = old_content[:50] + "..."
                table.setItem(row_idx, 4, QTableWidgetItem(old_content))
                
                # Old Topic
                old_topic = row.get("old_topic", "") or ""
                table.setItem(row_idx, 5, QTableWidgetItem(old_topic))
                
                # Old Priority
                old_priority = row.get("old_priority")
                priority_text = str(old_priority) if old_priority is not None else ""
                table.setItem(row_idx, 6, QTableWidgetItem(priority_text))

            layout.addWidget(table)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #5a6268;
            }
        """)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)