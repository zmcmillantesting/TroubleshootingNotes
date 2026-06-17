# frontend/widgets.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime

class ModernCard(QFrame):
    note_selected = pyqtSignal(int)
    
    def __init__(self, note_data, parent=None):
        super().__init__(parent)
        self.note_data = note_data
        self.is_selected = False

    def init_card(self):

        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #e9ecef;
                border-radius: 12px;
                margin: 5px;
            }
            QFrame:hover {
                border-color: #3498db;
            }
        """)
        
        self.setFixedHeight(200)
        self.setMinimumWidth(320)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header with topic and priority
        header_layout = QHBoxLayout()
        
        # Topic label - FIXED: Better sizing and no max width constraint
        topic_label = QLabel(f"📋 {self.note_data['topic']}")
        topic_label.setStyleSheet("""
            QLabel {
                background: #e3f2fd;
                color: #1976d2;
                padding: 6px 6px 6px 6px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
                max-width: none;
                min-width: 80px;
                text-align: center;
            }
        """)
        # Remove max width constraint that was causing cut-off
        
        # Priority label
        priority_colors = {1: "#27ae60", 2: "#f39c12", 3: "#e67e22", 4: "#e74c3c", 5: "#8e44ad"}
        priority_color = priority_colors.get(self.note_data['priority'], "#6c757d")
        
        priority_label = QLabel(f"P{self.note_data['priority']}")
        priority_label.setStyleSheet(f"""
            QLabel {{
                background: {priority_color};
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: bold;
                min-width: 20px;
                text-align: center;
            }}
        """)
        priority_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(topic_label)
        header_layout.addStretch()
        header_layout.addWidget(priority_label)
        
        # Title
        title_label = QLabel(self.note_data['title'])
        title_label.setStyleSheet(""" 
            QLabel {
                font-weight: bold;
                font-size: 16px;
                color: #2c3e50;
                margin: 5px 0;
            }
        """)
        title_label.setWordWrap(True)
        title_label.setMaximumHeight(40)

        # Content preview
        content_preview = self.note_data['content'][:120]
        if len(self.note_data['content']) > 120:
            content_preview += "..."
            
        content_label = QLabel(content_preview)
        content_label.setStyleSheet(""" 
            QLabel {
                color: #6c757d;
                font-size: 12px;
                line-height: 1.4;
            }
        """)
        content_label.setWordWrap(True)
        content_label.setMaximumHeight(60)
        
        # Footer with metadata
        footer_layout = QHBoxLayout()
        
        created_by_label = QLabel(f"👤 {self.note_data['created_by']}")
        created_by_label.setStyleSheet("QLabel { color: #6c757d; font-size: 10px; }")
        
        # Handle date formatting safely
        try:
            if isinstance(self.note_data['created_at'], str):
                date_obj = datetime.fromisoformat(self.note_data['created_at'].replace('Z', '+00:00'))
            else:
                date_obj = self.note_data['created_at']
            created_date = date_obj.strftime('%m/%d/%Y')
        except:
            created_date = "Recent"
            
        date_label = QLabel(f"📅 {created_date}")
        date_label.setStyleSheet("QLabel { color: #6c757d; font-size: 10px; }")
        
        footer_layout.addWidget(created_by_label)
        footer_layout.addStretch()
        footer_layout.addWidget(date_label)

        # Add all to layout
        layout.addLayout(header_layout)
        layout.addWidget(title_label)
        layout.addWidget(content_label)
        layout.addLayout(footer_layout)

    def mousePressEvent(self, event):
        """Handle clicks on the card"""
        self.is_selected = True
        self.note_selected.emit(self.note_data['id'])  # emit the note ID
        super().mousePressEvent(event)
        
    def set_selected(self, selected: bool):
        """Update card selection state and style"""
        self.is_selected = selected
        if selected:
            self.setStyleSheet("""
                QFrame {
                    background: #f0f8ff;
                    border: 2px solid #3498db;
                    border-radius: 12px;
                    margin: 5px;
                }
                QFrame:hover {
                    border-color: #3498db;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background: white;
                    border: 2px solid #e9ecef;
                    border-radius: 12px;
                    margin: 5px;
                }
                QFrame:hover {
                    border-color: #3498db;
                }
            """)

