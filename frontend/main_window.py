# frontend/main_window.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from datetime import datetime
import os

from backend.database_manager import DatabaseManager
from frontend.dialogs import CompanyDialog, BoardDialog, NoteDialog, NoteHistoryDialog, NoteViewerDialog
from frontend.widgets import ModernCard
from frontend.styles import *

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


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
        self.show_archived = False
        self.current_topic_filter = None
        
        # Initialize UI components
        self.notes_scroll_area = None
        self.cards = []
        
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
        self.history_note_btn.clicked.connect(self.show_note_history)
        self.user_input.textChanged.connect(self.on_user_changed)
        self.show_archived_checkbox.stateChanged.connect(self.toggle_archived_notes)
    
    def on_user_changed(self, text):
        """Update current user when user input changes"""
        self.current_user = text.strip() if text.strip() else "Anonymous"

    def init_ui(self):
        self.setWindowTitle("🛠️ Troubleshooting Notes")
        self.setMinimumSize(1400, 900)
        self.setStyleSheet(MAIN_WINDOW_STYLE)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Create sidebar
        sidebar = self.create_modern_sidebar()
        main_layout.addWidget(sidebar)

        # Create content area
        content_area = self.create_content_area()
        main_layout.addWidget(content_area, 3)

    def create_content_area(self):
        """Create the modern content area with toolbar and notes display"""
        content_area = QWidget()
        content_area.setStyleSheet(CONTENT_AREA_STYLE)

        self.content_layout = QVBoxLayout(content_area)
        self.content_layout.setSpacing(15)
        self.content_layout.setContentsMargins(20, 20, 20, 20)

        # Create toolbar
        toolbar = self.create_modern_toolbar()
        self.content_layout.addWidget(toolbar)

        # Create notes display area
        self.create_notes_display_area()

        return content_area

    def create_notes_display_area(self):
        """Create the scrollable notes display area"""
        # Create scroll area for notes
        self.notes_scroll_area = QScrollArea()
        self.notes_scroll_area.setWidgetResizable(True)
        self.notes_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f3f4;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #c1c8cd;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a8b2b8;
            }
        """)

        # Create the content widget that will hold all notes
        self.notes_content_widget = QWidget()
        self.notes_content_layout = QVBoxLayout(self.notes_content_widget)
        self.notes_content_layout.setSpacing(15)
        self.notes_content_layout.setContentsMargins(10, 10, 10, 10)
        self.notes_content_layout.setAlignment(Qt.AlignTop)

        # Set initial empty state
        self.show_empty_state("Select a company and board to view notes")

        # Set the content widget to the scroll area
        self.notes_scroll_area.setWidget(self.notes_content_widget)
        
        # Add scroll area to main layout
        self.content_layout.addWidget(self.notes_scroll_area)

    def show_empty_state(self, message):
        """Show empty state message in the notes area"""
        # Clear existing content
        self.clear_notes_display()
        
        # Create empty state label
        empty_label = QLabel(message)
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 18px;
                padding: 60px;
                background: rgba(108, 117, 125, 0.1);
                border-radius: 12px;
                border: 2px dashed #dee2e6;
            }
        """)
        
        self.notes_content_layout.addWidget(empty_label)
        self.notes_content_layout.addStretch()

    def clear_notes_display(self):
        """Clear all widgets from the notes display area"""
        while self.notes_content_layout.count():
            child = self.notes_content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.cards = []

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

        self.topics_widget = QWidget()
        self.topics_layout = QVBoxLayout(self.topics_widget)
        self.topics_layout.setSpacing(8)

        # "All Topics" button
        all_topics_btn = QPushButton("📋 All Topics")
        all_topics_btn.setStyleSheet(topic_button_style("#6c757d"))
        all_topics_btn.clicked.connect(lambda: self.filter_by_topic(None))
        self.topics_layout.addWidget(all_topics_btn)

        scroll = QScrollArea()
        scroll.setWidget(self.topics_widget)
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

        self.show_archived_checkbox = QCheckBox("Show Archived")
        self.show_archived_checkbox.setStyleSheet("QCheckBox {color: #6c757d; font-size: 12px; }")

        view_layout.addWidget(self.cards_view_btn)
        view_layout.addWidget(self.table_view_btn)

        self.new_note_btn = QPushButton("✏️ New Note")
        self.edit_note_btn = QPushButton("📝 Edit")
        self.archive_note_btn = QPushButton("📦 Archive")
        self.history_note_btn = QPushButton("📜 History")

        self.new_note_btn.setStyleSheet(NEW_NOTE_BUTTON_STYLE)
        self.edit_note_btn.setStyleSheet(EDIT_NOTE_BUTTON_STYLE)
        self.archive_note_btn.setStyleSheet(ARCHIVE_NOTE_BUTTON_STYLE)
        self.history_note_btn.setStyleSheet(EDIT_NOTE_BUTTON_STYLE)

        self.edit_note_btn.setEnabled(False)
        self.archive_note_btn.setEnabled(False)
        self.history_note_btn.setEnabled(False)

        toolbar_layout.addWidget(self.search_input, 2)
        toolbar_layout.addWidget(view_container)
        toolbar_layout.addWidget(self.new_note_btn)
        toolbar_layout.addWidget(self.edit_note_btn)
        toolbar_layout.addWidget(self.archive_note_btn)
        toolbar_layout.addWidget(self.show_archived_checkbox)
        toolbar_layout.addWidget(self.history_note_btn)

        return toolbar

    def on_note_selected(self, note_id):
        """Handle note selection and enable edit button"""
        self.selected_note_id = note_id

        # Update card selection states
        for card in self.cards:
            card.set_selected(card.note_data["id"] == note_id)
        
        # Enable buttons
        self.edit_note_btn.setEnabled(True)
        self.archive_note_btn.setEnabled(True)
        self.history_note_btn.setEnabled(True)

    def on_note_double_clicked(self, note_data):
        # ✅ Correct argument order
        dialog = NoteViewerDialog(note_data, self)
        result = dialog.exec_()

        if result == 2:
            self.selected_note_id = note_data['id']
            self.edit_selected_note()

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

    def show_note_history(self):
        """Show history of the selected note"""
        if not self.selected_note_id:
            QMessageBox.warning(self, "Warning", "Please select a note first")
            return

        try:
            history = self.db.get_note_history(self.selected_note_id)
            dialog = NoteHistoryDialog(history, self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch history: {str(e)}")

    def on_search_changed(self, text):
        """Handle search text changes"""
        self.refresh_notes()

    def create_new_note(self):
        """Create a new note"""
        if not self.current_board_id:
            QMessageBox.warning(self, "Warning", "Please select a board first")
            return

        try:
            topics = self.db.get_topics(self.current_board_id)
        except:
            topics = []

        dialog = NoteDialog(self, topics=topics)
        if dialog.exec_():
            note_data = dialog.get_note_data()

            title = note_data['title']
            content = note_data['content']
            topic = note_data['topic']
            priority = note_data['priority']
            user_id = self.current_user

            try:
                self.db.add_note(
                    board_id=self.current_board_id,
                    topic=topic,
                    title=title,
                    content=content,
                    user_id=user_id,
                    priority=priority
                )
                self.refresh_notes()
                self.refresh_topics()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add note: {str(e)}")
                
    def edit_selected_note(self):
        """Edit the selected note"""
        if not self.selected_note_id:
            QMessageBox.warning(self, "Warning", "Please select a note first")
            return

        notes = self.db.get_notes(self.current_board_id, include_archived=True)
        note = next((n for n in notes if n["id"] == self.selected_note_id), None)

        if not note:
            QMessageBox.critical(self, "Error", "Selected note could not be found")
            return

        try:
            topics = self.db.get_topics(self.current_board_id)
        except:
            topics = []

        dialog = NoteDialog(self, note, topics)
        if dialog.exec_():
            updated_data = dialog.get_note_data()
            title = updated_data.get('title', '').strip()
            content = updated_data.get('content', '')
            topic = updated_data.get('topic')
            priority = updated_data.get('priority')
            user_id = self.current_user

            try:
                self.db.update_note(
                    self.selected_note_id,
                    title,
                    content,
                    user_id,
                    topic=topic,
                    priority=priority
                )
                self.refresh_notes()
                self.refresh_topics()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update note: {str(e)}")

    def archive_selected_note(self): 
        """Archive the selected note"""
        if not self.selected_note_id:
            QMessageBox.warning(self, "Warning", "Please select a note first")
            return

        reply = QMessageBox.question(
            self,
            "Archive Note", 
            "Are you sure you want to archive this note?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.db.archive_note(self.selected_note_id, self.current_user)
                self.selected_note_id = None
                self.edit_note_btn.setEnabled(False)
                self.archive_note_btn.setEnabled(False)
                self.history_note_btn.setEnabled(False)
                self.refresh_notes()
                self.refresh_topics()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to archive note: {str(e)}")

    def toggle_archived_notes(self, state):
        """Toggle showing archived notes"""
        self.show_archived = (state == Qt.Checked)
        self.refresh_notes()

    def refresh_companies(self):
        """Refresh the company dropdown"""
        self.company_combo.clear()
        try:
            companies = self.db.get_companies()
            for company_id, name in companies:
                self.company_combo.addItem(name, company_id)

            if companies:
                self.current_company_id = companies[0][0]
                self.refresh_boards()
            else:
                self.current_company_id = None
                self.show_empty_state("No companies found. Please add a company first.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load companies: {str(e)}")

    def refresh_boards(self):
        """Refresh the board dropdown"""
        self.board_combo.clear()
        if not self.current_company_id:
            self.show_empty_state("Please select a company first")
            return
        
        try:
            boards = self.db.get_boards(self.current_company_id)
            for board in boards:
                board_id = board[0]
                board_name = board[1]
                self.board_combo.addItem(board_name, board_id)
            
            if boards:
                self.current_board_id = boards[0][0]
                self.refresh_notes()
                self.refresh_topics()
            else:
                self.current_board_id = None
                self.show_empty_state("No boards found. Please add a board first.")
                self.refresh_topics()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load boards: {str(e)}")
            self.current_board_id = None
            self.show_empty_state("Error loading boards")
            self.refresh_topics()

    def refresh_topics(self):
        """Refresh the topics list in the sidebar"""
        # Clear existing topic buttons (except "All Topics")
        for i in reversed(range(self.topics_layout.count())):
            widget = self.topics_layout.itemAt(i).widget()
            if widget and not widget.text().startswith("📋 All Topics"):
                widget.deleteLater()
        
        if not self.current_board_id:
            return
        
        try:
            topics = self.db.get_topics(self.current_board_id)

            for topic in topics:
                if topic:
                    topic_btn = QPushButton(f"📁 {topic}")
                    color_tuple = self.generate_topic_color(topic)
                    topic_btn.setStyleSheet(topic_button_style(color_tuple))
                    topic_btn.clicked.connect(lambda checked, t=topic: self.filter_by_topic(t))
                    self.topics_layout.addWidget(topic_btn)

        except Exception as e:
            print(f"Error loading topics: {e}")

    def generate_topic_color(self, topic_name):
        """Generate consistent colors for topics"""
        color1 = hash(topic_name) % 360
        color2 = (color1 + 60) % 360
        hsl_string_for_color_1 = f"hsl({color1}, 70%, 65%)"
        hsl_string_for_color_2 = f"hsl({color2}, 70%, 65%)"
        return (hsl_string_for_color_1, hsl_string_for_color_2)
    
    def filter_by_topic(self, topic):
        """Filter notes by topic"""
        self.current_topic_filter = topic
        self.refresh_notes()
        
    def refresh_notes(self):
        """Refresh the notes display in the main window"""
        if not self.current_board_id:
            self.show_empty_state("Select a company and board to view notes")
            return

        try:
            # Get notes from database
            notes = self.db.get_notes(self.current_board_id, include_archived=self.show_archived)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load notes: {str(e)}")
            self.show_empty_state("Error loading notes")
            return

        # Apply filters
        filtered_notes = notes

        # Filter by topic if specified
        if self.current_topic_filter:
            filtered_notes = [note for note in filtered_notes if note['topic'] == self.current_topic_filter]

        # Filter by search text if any
        search_text = self.search_input.text().lower().strip()
        if search_text:
            filtered_notes = [note for note in filtered_notes 
                            if search_text in note['title'].lower() 
                            or search_text in note['content'].lower()
                            or search_text in note['topic'].lower()]

        # Clear existing display
        self.clear_notes_display()

        # Show appropriate content
        if not filtered_notes:
            if search_text or self.current_topic_filter:
                self.show_empty_state("No notes match your search criteria")
            else:
                self.show_empty_state("No notes found. Click 'New Note' to create one!")
        else:
            if self.current_view_mode == "cards":
                self.display_notes_as_cards(filtered_notes)
            else:
                self.display_notes_as_table(filtered_notes)

    def display_notes_as_cards(self, notes):
        """Display notes as cards in the scroll area"""
        for note in notes:
            card = ModernCard(note)
            card.note_selected.connect(self.on_note_selected)
            card.note_double_clicked.connect(self.on_note_double_clicked)
            self.cards.append(card)
            self.notes_content_layout.addWidget(card)
        
        # Add stretch to push cards to top
        self.notes_content_layout.addStretch()

    def display_notes_as_table(self, notes):
        """Display notes as table (placeholder implementation)"""
        table_label = QLabel("📊 Table view coming soon!")
        table_label.setAlignment(Qt.AlignCenter)
        table_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 16px;
                padding: 40px;
                background: rgba(108, 117, 125, 0.1);
                border-radius: 12px;
            }
        """)
        self.notes_content_layout.addWidget(table_label)
        self.notes_content_layout.addStretch()

    def on_company_changed(self, index):
        """Handle company selection change"""
        if index >= 0:
            self.current_company_id = self.company_combo.currentData()
            self.current_topic_filter = None  # Reset topic filter
            self.refresh_boards()

    def on_board_changed(self, index):
        """Handle board selection change"""
        if index >= 0:
            self.current_board_id = self.board_combo.currentData()
            self.current_topic_filter = None  # Reset topic filter
            self.selected_note_id = None  # Reset selected note
            # Disable action buttons
            self.edit_note_btn.setEnabled(False)
            self.archive_note_btn.setEnabled(False)
            self.history_note_btn.setEnabled(False)
            self.refresh_notes()
            self.refresh_topics()

    def add_company(self):
        """Add a new company"""
        dialog = CompanyDialog(self)
        if dialog.exec_():
            company_name = dialog.get_company_name()
            if company_name:
                try:
                    self.db.add_company(company_name)
                    self.refresh_companies()
                except ValueError as e:
                    QMessageBox.warning(self, "Warning", str(e))
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to add company: {str(e)}")

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
                self.selected_note_id = None
                self.current_topic_filter = None
                self.edit_note_btn.setEnabled(False)
                self.archive_note_btn.setEnabled(False)
                self.history_note_btn.setEnabled(False)
                self.refresh_companies()
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

        board_name = self.board_combo.currentText()
        reply = QMessageBox.question(self, "Delete Board", 
                                   f"Are you sure you want to delete '{board_name}' and all its notes?",
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.db.delete_board(self.current_board_id)
                self.current_board_id = None
                self.selected_note_id = None
                self.current_topic_filter = None
                self.edit_note_btn.setEnabled(False)
                self.archive_note_btn.setEnabled(False)
                self.history_note_btn.setEnabled(False)
                self.refresh_boards()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete board: {str(e)}")