# frontend/clean_main_window.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from datetime import datetime

from backend.database_manager import DatabaseManager
from frontend.dialogs import CompanyDialog, BoardDialog, NoteDialog, NoteHistoryDialog
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

        self.topics_widget = QWidget()
        self.topics_layout = QVBoxLayout(self.topics_widget)
        self.topics_layout.setSpacing(8)

        all_topics_btn = QPushButton("📋 All Topics")
        all_topics_btn.setStyleSheet(topic_button_style("#6c757d"))
        all_topics_btn.clicked.connect(self.refresh_notes)
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
        self.show_archived_checkbox.stateChanged.connect(self.toggle_archived_notes)

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

        self.history_note_btn.setEnabled(False)

        toolbar_layout.addWidget(self.search_input, 2)
        toolbar_layout.addWidget(view_container)
        toolbar_layout.addWidget(self.new_note_btn)
        toolbar_layout.addWidget(self.edit_note_btn)
        toolbar_layout.addWidget(self.archive_note_btn)
        toolbar_layout.addWidget(self.show_archived_checkbox)
        toolbar_layout.addWidget(self.history_note_btn)

        return toolbar

<<<<<<< HEAD
    def refresh_notes(self, topic_filter=None):
        """Fixed refresh_notes method that updates topics sidebar"""
        if not self.current_board_id:
            raise TypeError 
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

        # Add stretch to push content to tops
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

        # IMPORTANT: Refresh topics sidebar after loading notes
        self.refresh_topics()

=======
>>>>>>> V2
    def on_note_selected(self, note_id):
        """Handle note selection and enable edit button"""
        self.selected_note_id = note_id

        for card in getattr(self, "cards", []):
            card.set_selected(card.note_data["id"] == note_id)
        
        if hasattr(self, 'edit_note_btn'):
            self.edit_note_btn.setEnabled(True)
        if hasattr(self, 'archive_note_btn'):
            self.archive_note_btn.setEnabled(True)
        if hasattr(self, 'history_note_btn'):
            self.history_note_btn.setEnabled(True)
    
    def set_selected(self, selected: bool):
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
        """Fixed create_new_note method that populates topics"""
        if not self.current_board_id:
            QMessageBox.warning(self, "Warning", "Please select a board first")
            return

        # Get existing topics for dropdown
        try:
            existing_topics = self.db.get_topics(self.current_board_id)
            print(f"Existing topics for dropdown: {existing_topics}")  # Debug
        except Exception as e:
            print(f"Error getting topics: {e}")
            existing_topics = []

        dialog = NoteDialog(self, topics=existing_topics)
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
                print(f"Added note with topic: {topic}")  # Debug
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add note: {str(e)}")

    def edit_selected_note(self):
        """Edit the selected note"""
        if not self.selected_note_id:
            QMessageBox.warning(self, "Warning", "Please select a note first")
            return

        # get all notes for the current board, including archived
        notes = self.db.get_notes(self.current_board_id, include_archived=True)
        note = next((n for n in notes if n["id"] == self.selected_note_id), None)

        if not note:
            QMessageBox.critical(self, "Error", "Selected note could not be found")
            return

        dialog = NoteDialog(self, note)
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
<<<<<<< HEAD
            self.db.archive_note(self.selected_note_id, user_id=self.current_user)
            self.selected_note_id = None
            self.refresh_notes()
=======
            try:
                # Pass both note ID and user ID
                self.db.archive_note(self.selected_note_id, self.current_user)
                self.selected_note_id = None
                self.refresh_notes()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to archive note: {str(e)}")

    def toggle_archived_notes(self, state):
        self.show_archived = (state == Qt.Checked)
        self.refresh_notes
>>>>>>> V2

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
                self.refresh_topics()
            else:
                self.current_board_id = None
                self.refresh_notes()  # Clear notes display
                self.refresh_topics()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load boards: {str(e)}")
            self.current_board_id = None
            self.refresh_notes()
            self.refresh_topics()

    def refresh_topics(self):
        """Refresh the topics list in the sidebar"""
        # Clear existing topic button (except "All Topics")
        for i in reversed(range(self.topics_layout.count())):
            widget = self.topics_layout.itemAt(i).widget()
            if widget and widget.text() != "📋 All Topics":
                widget.deleteLater()
        
        if not self.current_board_id:
            return
        
        try:
            topics = self.db.get_topics(self.current_board_id)

            for topic in topics:
                if topic:
                    topic_btn = QPushButton(f"📁 {topic}")
                    topic_btn.setStyleSheet(topic_button_style(self.generate_topic_color(topic)))
                    topic_btn.clicked.connect(lambda checked, t=topic: self.filter_by_topic(t))
                    self.topics_layout.addWidget(topic_btn)

        except Exception as e:
            print(f"Error Loading topics: {e}")

    def generate_topic_color(self, topic_name):
        color1 = hash(topic_name) % 360
        color2 = color1 + 30
        hsl_string_for_color_1 = f"hsl({color1}, 70%, 65%)"
        hsl_string_for_color_2 = f"hsl({color2}, 70%, 65%)"
        return str(hsl_string_for_color_1), str(hsl_string_for_color_2)
    
    def filter_by_topic(self, topic):
        self.refresh_notes(topic)
        
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
        notes = self.db.get_notes(self.current_board_id, include_archived= self.toggle_archived_notes(self.show_archived_checkbox))

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

                self.cards = []
                for note in notes:
                    card = ModernCard(note)
                    card.note_selected.connect(self.on_note_selected)
                    self.cards.append(card)
                    cards_layout.addWidget(card)

                self.notes_layout.addWidget(cards_container)
            else:
                #TODO: Create table view (you'll need to implement this)
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
        self.refresh_topics()

    def refresh_topics(self):
        if not self.current_board_id:
            return
        
        for i in reversed(range(self.topics_layout.count())):
            child = self.topics_layout.itemAt(i).widget()
            if child and child.text() != "📋 All Topics":
                child.deleteLater()
        
        try:
            topics = self.db.get_topics(self.current_board_id)
            print(f"Found topics: {topics} ")

            topic_colors = {
                'Troubleshooting': '#3498db',
                'Testing': '#e74c3c',
                'Labeling': '#f39c12',
                'General': '#9b59b6',
                'Miscellaneous': '#95a5a6'
            }

            for topic in topics:
                color = topic_colors.get(topic, "#6c757d")
                topic_button = QPushButton(f"📝 {topic}")
                topic_button.setStyleSheet("""
                    QPushButton {{
                        background: {color};
                        color: white;
                        border: none;
                        padding: 8px 12px;
                        border-radius: 20px;
                        font-size: 12px;
                        font-weight: 500;
                        text-align: left;
                        min-height: 24px;
                    }}
                    QPushButton:hover {{
                        background: {color};
                        opacity: 0.8;
                    }}
                """)
                topic_button.clicked.connect(lambda checked, t=topic: self.refresh_notes(t))
                self.topics_layout.addWidget(topic_button)
        except Exception as e:
            print(f"Error Refreshing topics: {e}")

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
            self.refresh_topics()

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