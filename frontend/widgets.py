# frontend/widgets.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime

class ModernCard(QFrame):
    note_selected = pyqtSignal(int)
    note_double_clicked = pyqtSignal(dict)

    def __init__(self, note_data, parent=None):
        super().__init__(parent)
        self.note_data = note_data
        self.is_selected = False
        self.setup_ui()

    def setup_ui(self):
        """Set up the card UI"""
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
        
        # Topic label - Fixed sizing
        topic_label = QLabel(f"📋 {self.note_data['topic']}")
        topic_label.setStyleSheet("""
            QLabel {
                background: #e3f2fd;
                color: #1976d2;
                padding: 6px 10px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
                min-height: 16px;
            }
        """)
        
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
        if event.button() == Qt.LeftButton:
            # Emit selection and toggle visual selection state
            self.note_selected.emit(self.note_data['id'])
            self.toggle_selection()
        super().mousePressEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        """Double click -> open view dialog"""
        if event.button() == Qt.LeftButton:
            # Emit both the id-selected event and the full note data for a double-click
            self.note_selected.emit(self.note_data['id'])
            # Emit the full note data so dialogs can receive all fields
            try:
                self.note_double_clicked.emit(self.note_data)
            except Exception:
                # Fallback: emit only id wrapped in dict form
                self.note_double_clicked.emit({'id': self.note_data.get('id')})

        # Call the proper super double-click handler
        super().mouseDoubleClickEvent(event)

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

    def toggle_selection(self):
        """Toggle selection state and update style (helper)."""
        self.set_selected(not self.is_selected)

class TopicButton(QPushButton):
    """Custom topic button with emoji and styling"""
    
    def __init__(self, topic_name, color="#6c757d", parent=None):
        super().__init__(parent)
        self.topic_name = topic_name
        self.color = color
        self.setup_button()
        
    def setup_button(self):
        """Set up the topic button"""
        # Add emoji based on topic
        topic_emojis = {
            'Network': '🌐',
            'Software': '💻', 
            'Hardware': '🔧',
            'Security': '🔒',
            'General': '📋',
            'All Topics': '📋'
        }
        
        emoji = topic_emojis.get(self.topic_name, '📝')
        self.setText(f"{emoji} {self.topic_name}")
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: {self.color};
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 500;
                text-align: left;
            }}
            QPushButton:hover {{
                background: {self.adjust_color_brightness(self.color, -20)};
            }}
            QPushButton:pressed {{
                background: {self.adjust_color_brightness(self.color, -40)};
            }}
        """)
        
    def adjust_color_brightness(self, hex_color, amount):
        """Adjust the brightness of a hex color"""
        # Simple brightness adjustment - you could use a more sophisticated method
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        
        # Convert to RGB
        try:
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except (ValueError, IndexError):
            # Fallback for invalid hex colors
            return "#6c757d"
        
        # Adjust brightness
        rgb = tuple(max(0, min(255, c + amount)) for c in rgb)
        
        # Convert back to hex
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"