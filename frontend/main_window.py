# frontend/clean_main_window.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from datetime import datetime

from backend.database_manager import DatabaseManager
from frontend.dialogs import CompanyDialog, BoardDialog, NoteDialog
from frontend.widgets import ModernCard
from frontend.styles import *

class LearningWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize database
        self.db = DatabaseManager()
        
        # Current selections
        self.current_company_id = None
        self.current_board_id = None
        self.current_user = "Anonymous"
        self.selected_note_id = None
        self.current_view_mode = "cards"
        
        self.init_ui()
        self.setup_connections()
        self.refresh_companies()

    def setup_connections(self):
        """Connect signals and slots"""
        self.company_combo.currentIndexChanged.connect(self.on_company_changed)
        self.board_combo.currentIndexChanged.connect(self.on_board_changed)
        self.add_company_btn.clicked.connect(self.add_company)
        self.delete_company_btn.clicked.connect(self.delete_company)
        self.add_board_btn.clicked.connect(self.add_board)
        self.delete_board_btn.clicked.connect(self.delete_board)
        self.cards_view_btn.clicked.connect(self.show_cards_view)
        self.table_view_btn.clicked.connect(self.show_table_view)
        self.search_input.textChanged.connect(self.on_search_changed)
        self.new_note_btn.clicked.connect(self.create_new_note)
        self.edit_note_btn.clicked.connect(self.edit_selected_note)
        self.archive_note_btn.clicked.connect(self.archive_selected_note)
        self.user_input.textChanged.connect(self.on_user_changed)
    
    def on_user_changed(self, text):
        """Update current user when user input changes"""
        self.current_user = text.strip() if text.strip() else "Anonymous"

    def init_ui(self):
        self.setWindowTitle("🛠️ Troubleshooting Notes - Modern Interface")
        self.setMinimumSize(1400, 900)
        self.setStyleSheet(MAIN_WINDOW_STYLE)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(10, 10, 10, 10)

        sidebar = self.create_modern_sidebar()
        main_layout.addWidget(sidebar)

        content_area = self.create_content_area()
        main_layout.addWidget(content_area, 3)

    def create_content_area(self):
        """Create the modern content area with toolbar"""
        content_area = QWidget()
        content_area.setStyleSheet(CONTENT_AREA_STYLE)

        self.content_layout = QVBoxLayout(content_area)
        self.content_layout.setSpacing(15)
        self.content_layout.setContentsMargins(20, 20, 20, 20)

        toolbar = self.create_modern_toolbar()
        self.content_layout.addWidget(toolbar)

        self.content_display = QLabel("Select a company and board to view notes")
        self.content_display.setAlignment(Qt.AlignCenter)
        self.content_display.setStyleSheet("color: #6c757d; font-size: 16px; padding: 40px;")
        self.content_layout.addWidget(self.content_display)

        return content_area

    def create_modern_sidebar(self):
        """Create the sidebar"""
        sidebar = QWidget()
        sidebar.setMaximumWidth(320)
        sidebar.setMinimumWidth(300)
        sidebar.setStyleSheet(SIDEBAR_STYLE)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(25)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)

        self.add_user_section(sidebar_layout)
        self.add_company_section(sidebar_layout)
        self.add_board_section(sidebar_layout)
        self.add_topics_section(sidebar_layout)

        sidebar_layout.addStretch()
        return sidebar

    def add_user_section(self, layout):
        """Add the user ID section"""
        section = QVBoxLayout()

        header = QLabel("USER INFORMATION")
        header.setStyleSheet(SECTION_HEADER_STYLE)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Enter your User ID")
        self.user_input.setStyleSheet(USER_INPUT_STYLE)

        section.addWidget(header)
        section.addWidget(self.user_input)
        layout.addLayout(section)

    def add_company_section(self, layout):
        """Add company dropdown with buttons"""
        section = QVBoxLayout()

        header = QLabel("COMPANY")
        header.setStyleSheet(SECTION_HEADER_STYLE)

        dropdown_container = QHBoxLayout()

        self.company_combo = QComboBox()
        self.company_combo.setStyleSheet(COMBO_BOX_STYLE)

        self.add_company_btn = QPushButton("➕")
        self.delete_company_btn = QPushButton("🗑️")

        self.add_company_btn.setStyleSheet(CIRCULAR_BUTTON_STYLE)
        self.delete_company_btn.setStyleSheet(DELETE_BUTTON_STYLE)

        self.add_company_btn.setMaximumSize(35, 35)
        self.delete_company_btn.setMaximumSize(35, 35)

        dropdown_container.addWidget(self.company_combo)
        dropdown_container.addWidget(self.add_company_btn)
        dropdown_container.addWidget(self.delete_company_btn)

        section.addWidget(header)
        section.addLayout(dropdown_container)
        layout.addLayout(section)

    def add_board_section(self, layout):
        """Create the board section"""
        section = QVBoxLayout()

        header = QLabel("BOARD")
        header.setStyleSheet(SECTION_HEADER_STYLE)

        dropdown_container = QHBoxLayout()

        self.board_combo = QComboBox()
        self.board_combo.setStyleSheet(COMBO_BOX_STYLE)

        self.add_board_btn = QPushButton("➕")
        self.delete_board_btn = QPushButton("🗑️")

        self.add_board_btn.setStyleSheet(CIRCULAR_BUTTON_STYLE)
        self.delete_board_btn.setStyleSheet(DELETE_BUTTON_STYLE)

        self.add_board_btn.setMaximumSize(35, 35)
        self.delete_board_btn.setMaximumSize(35, 35)

        dropdown_container.addWidget(self.board_combo)
        dropdown_container.addWidget(self.add_board_btn)
        dropdown_container.addWidget(self.delete_board_btn)

        section.addWidget(header)
        section.addLayout(dropdown_container)
        layout.addLayout(section)

    def add_topics_section(self, layout):
        """Add the colorful topic tags"""
        section = QVBoxLayout()

        header = QLabel("TOPICS")
        header.setStyleSheet(SECTION_HEADER_STYLE)

        topics_widget = QWidget()
        self.topics_layout = QVBoxLayout(topics_widget)
        self.topics_layout.setSpacing(8)

        all_topics_btn = QPushButton("📋 All Topics")
        all_topics_btn.setStyleSheet(topic_button_style("#6c757d"))
        all_topics_btn.clicked.connect(self.refresh_notes)
        self.topics_layout.addWidget(all_topics_btn)

        scroll = QScrollArea()
        scroll.setWidget(topics_widget)
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(200)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        section.addWidget(header)
        section.addWidget(scroll)
        layout.addLayout(section)

    def create_modern_toolbar(self):
        """Create the top toolbar"""
        toolbar = QWidget()
        toolbar.setStyleSheet(TOOLBAR_STYLE)

        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setSpacing(15)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search notes...")
        self.search_input.setStyleSheet(SEARCH_INPUT_STYLE)

        view_container = QWidget()
        view_layout = QHBoxLayout(view_container)
        view_layout.setSpacing(0)
        view_layout.setContentsMargins(0, 0, 0, 0)

        self.cards_view_btn = QPushButton("📋 Cards")
        self.table_view_btn = QPushButton("📊 Table")

        self.cards_view_btn.setStyleSheet(VIEW_BUTTON_STYLE + "QPushButton { border-top-left-radius: 6px; border-bottom-left-radius: 6px; }")
        self.table_view_btn.setStyleSheet(VIEW_BUTTON_STYLE + "QPushButton { border-top-right-radius: 6px; border-bottom-right-radius: 6px; }")

        self.cards_view_btn.setCheckable(True)
        self.table_view_btn.setCheckable(True)
        self.cards_view_btn.setChecked(True)

        view_layout.addWidget(self.cards_view_btn)
        view_layout.addWidget(self.table_view_btn)

        self.new_note_btn = QPushButton("✏️ New Note")
        self.edit_note_btn = QPushButton("📝 Edit")
        self.archive_note_btn = QPushButton("📦 Archive")

        self.new_note_btn.setStyleSheet(NEW_NOTE_BUTTON_STYLE)
        self.edit_note_btn.setStyleSheet(EDIT_NOTE_BUTTON_STYLE)
        self.archive_note_btn.setStyleSheet(ARCHIVE_NOTE_BUTTON_STYLE)

        toolbar_layout.addWidget(self.search_input, 2)
        toolbar_layout.addWidget(view_container)
        toolbar_layout.addWidget(self.new_note_btn)
        toolbar_layout.addWidget(self.edit_note_btn)
        toolbar_layout.addWidget(self.archive_note_btn)

        return toolbar

    def refresh_notes(self, topic_filter=None):
        if not self.current_board_id:
            self.content_display.setText("Select a board to view notes")
            return

        # Clear current content
        if hasattr(self, 'notes_container'):
            self.notes_container.deleteLater()

        # Create scroll area for notes
        self.notes_container = QScrollArea()
        self.notes_container.setWidgetResizable(True)
        self.notes_container.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        # Create container widget for notes
        notes_widget = QWidget()
        self.notes_layout = QVBoxLayout(notes_widget)
        self.notes_layout.setSpacing(15)
        self.notes_layout.setContentsMargins(10, 10, 10, 10)
        self.notes_layout.setAlignment(Qt.AlignTop)

        # Get notes from database
        notes = self.db.get_notes(self.current_board_id)

        if not notes:
            no_notes_label = QLabel("No notes found for this board")
            no_notes_label.setAlignment(Qt.AlignCenter)
            no_notes_label.setStyleSheet("color: #6c757d; font-size: 16px; padding: 40px;")
            self.notes_layout.addWidget(no_notes_label)
        else:
            # Filter by topic if specified
            if topic_filter and topic_filter != "All Topics":
                notes = [note for note in notes if note['topic'] == topic_filter]

            # Filter by search text if any
            search_text = self.search_input.text().lower()
            if search_text:
                notes = [note for note in notes 
                        if search_text in note['title'].lower() 
                        or search_text in note['content'].lower()]

            if self.current_view_mode == "cards":
                # Create cards view
                cards_container = QWidget()
                cards_layout = QVBoxLayout(cards_container)
                cards_layout.setSpacing(15)

                for note in notes:
                    card = ModernCard(note)
                    card.note_selected.connect(self.on_note_selected)
                    cards_layout.addWidget(card)

                self.notes_layout.addWidget(cards_container)
            else:
                # Create table view (you'll need to implement this)
                self.notes_layout.addWidget(QLabel("Table view not implemented yet"))

        # Add stretch to push content to top
        self.notes_layout.addStretch()

        # Set the widget and add to layout
        self.notes_container.setWidget(notes_widget)

        # Replace current content display
        if hasattr(self, 'content_display'):
            self.content_layout.replaceWidget(self.content_display, self.notes_container)
            self.content_display.deleteLater()
            self.content_display = self.notes_container
        else:
            self.content_layout.addWidget(self.notes_container)
        # ... (keep all the other functional methods like refresh_companies, refresh_boards, etc.)

    def on_note_selected(self, note_id):
        """Handle note selection"""
        self.selected_note_id = note_id
        # You can add visual feedback for selected notes here

    def show_cards_view(self):
        """Switch to cards view"""
        self.current_view_mode = "cards"
        self.cards_view_btn.setChecked(True)
        self.table_view_btn.setChecked(False)
        self.refresh_notes()

    def show_table_view(self):
        """Switch to table view"""
        self.current_view_mode = "table"
        self.cards_view_btn.setChecked(False)
        self.table_view_btn.setChecked(True)
        self.refresh_notes()

    def on_search_changed(self, text):
        """Handle search text changes"""
        self.refresh_notes()

    def create_new_note(self):
        if not self.current_board_id:
            QMessageBox.warning(self, "Warning", "Please select a board first")
            return

        dialog = NoteDialog(self)
        if dialog.exec_():
            note_data = dialog.get_note_data()

            # Extract individual parameters for the database call
            title = note_data['title']
            content = note_data['content']
            topic = note_data['topic']
            priority = note_data['priority']
            user_id = self.current_user

            try:
                # Call the database method with individual parameters
                self.db.add_note(
                    board_id=self.current_board_id,
                    topic=topic,
                    title=title,
                    content=content,
                    user_id=user_id,
                    priority=priority
                )
                self.refresh_notes()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add note: {str(e)}")
                
    def edit_selected_note(self):
        """Edit the selected note"""
        if not self.selected_note_id:
            QMessageBox.warning(self, "Warning", "Please select a note first")
            return

        note = self.db.get_note(self.selected_note_id)
        if note:
            dialog = NoteDialog(self, note)
            if dialog.exec_():
                updated_data = dialog.get_note_data()
                self.db.update_note(self.selected_note_id, updated_data)
                self.refresh_notes()

    def archive_selected_note(self): 
        """Archive the selected note"""
        if not self.selected_note_id:
            QMessageBox.warning(self, "Warning", "Please select a note first")
            return

        reply = QMessageBox.question(self, "Archive Note", 
                                   "Are you sure you want to archive this note?",
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.db.archive_note(self.selected_note_id)
            self.selected_note_id = None
            self.refresh_notes()

    def refresh_companies(self):
        """Refresh the company dropdown"""
        self.company_combo.clear()
        companies = self.db.get_companies()
        for company_id, name in companies:
            self.company_combo.addItem(name, company_id)

        if companies:
            self.current_company_id = companies[0][0]
            self.refresh_boards()

    def refresh_boards(self):
        """Refresh the board dropdown"""
        self.board_combo.clear()
        if not self.current_company_id:
            return
        
        try:
            boards = self.db.get_boards(self.current_company_id)
            for board in boards:
                # Handle both (id, name) and (id, name, description) formats
                board_id = board[0]
                board_name = board[1]
                self.board_combo.addItem(board_name, board_id)
            
            if boards:
                self.current_board_id = boards[0][0]
                self.refresh_notes()
            else:
                self.current_board_id = None
                self.refresh_notes()  # Clear notes display
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load boards: {str(e)}")
            self.current_board_id = None
            self.refresh_notes()

    def on_company_changed(self, index):
        """Handle company selection change"""
        if index >= 0:
            self.current_company_id = self.company_combo.currentData()
            self.refresh_boards()

    def on_board_changed(self, index):
        """Handle board selection change"""
        if index >= 0:
            self.current_board_id = self.board_combo.currentData()
            self.refresh_notes()

    def add_company(self):
        """Add a new company"""
        dialog = CompanyDialog(self)
        if dialog.exec_():
            company_name = dialog.get_company_name()
            if company_name:
                self.db.add_company(company_name)
                self.refresh_companies()

    def delete_company(self):
        """Delete the selected company"""
        if not self.current_company_id:
            QMessageBox.warning(self, "Warning", "Please select a company first")
            return

        company_name = self.company_combo.currentText()

        reply = QMessageBox.question(self, "Delete Company", 
                                   f"Are you sure you want to delete '{company_name}' and all its boards and notes?",
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.db.delete_company(self.current_company_id)
                self.current_company_id = None
                self.current_board_id = None
                self.refresh_companies()
                self.refresh_notes()  # Clear any displayed notes
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete company: {str(e)}")

    def add_board(self):
        """Add a new board"""
        if not self.current_company_id:
            QMessageBox.warning(self, "Warning", "Please select a company first")
            return

        dialog = BoardDialog(self)
        if dialog.exec_():
            board_name, description = dialog.get_board_data()

            # Validate board name
            if not board_name.strip():
                QMessageBox.warning(self, "Warning", "Board name cannot be empty")
                return

            try:
                self.db.add_board(board_name, description, self.current_company_id)
                self.refresh_boards()
            except ValueError as e:
                QMessageBox.warning(self, "Warning", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add board: {str(e)}")

    def delete_board(self):
        """Delete the selected board"""
        if not self.current_board_id:
            QMessageBox.warning(self, "Warning", "Please select a board first")
            return

        reply = QMessageBox.question(self, "Delete Board", 
                                   "Are you sure you want to delete this board and all its notes?",
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.db.delete_board(self.current_board_id)
            self.current_board_id = None
            self.refresh_boards()