from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QComboBox, QPushButton, QLineEdit, QDialog, QTextEdit, QMessageBox, QTableWidget,
    QListWidgetItem, QInputDialog, QListView, QDialogButtonBox, QMainWindow
)

from PyQt5.QtCore import Qt
import sys, os
import sqlite3 as sql



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../data')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data')))
from databaseConnect import add_company, add_board, add_note, init_db

class MainWindow(QWidget): 
    def __init__(self):
        super().__init__()
        init_db()
        self.setWindowTitle("Troubleshooting Notes")
        self.resize(600, 425)

        main_layout = QVBoxLayout()

        # Topics layout for dynamic topic buttons
        self.topics_layout = QVBoxLayout()
        main_layout.addLayout(self.topics_layout)

        # Top controls grid
        controls_grid = QGridLayout()
        controls_grid.setColumnStretch(2, 1)

        # User ID
        controls_grid.addWidget(QLabel("User ID:"), 0, 0)
        self.user_id_edit = QLineEdit()
        controls_grid.addWidget(self.user_id_edit, 0, 1, 1, 3)

        # Company row
        controls_grid.addWidget(QLabel("Company:"), 1, 0)
        self.company_search = QComboBox()
        self.company_search.currentIndexChanged.connect(self.on_company_changed)
        controls_grid.addWidget(self.company_search, 1, 1)
        self.add_company_button = QPushButton("Add")
        self.add_company_button.clicked.connect(self.add_new_company)
        controls_grid.addWidget(self.add_company_button, 1, 2)
        self.delete_company_button = QPushButton("Delete")
        self.delete_company_button.clicked.connect(self.delete_selected_company)
        controls_grid.addWidget(self.delete_company_button, 1, 3)

        # Board row
        controls_grid.addWidget(QLabel("Board:"), 2, 0)
        self.board_search = QComboBox()
        controls_grid.addWidget(self.board_search, 2, 1)
        self.add_board_button = QPushButton("Add")
        self.add_board_button.clicked.connect(self.add_new_board)
        controls_grid.addWidget(self.add_board_button, 2, 2)
        self.delete_board_button = QPushButton("Delete")
        self.delete_board_button.clicked.connect(self.delete_selected_board)
        controls_grid.addWidget(self.delete_board_button, 2, 3)

        main_layout.addLayout(controls_grid)

        # Notes label
        notes_label = QLabel("Notes")
        main_layout.addWidget(notes_label)

        # Notes table
        self.notes_table = QTableWidget()
        self.notes_table.setColumnCount(5)
        self.notes_table.setHorizontalHeaderLabels(["ID", "Topic", "Created By", "Last Modified By", "Date"])
        self.notes_table.horizontalHeader().setStretchLastSection(True)
        self.notes_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.notes_table)

        # Bottom buttons
        self.bottom_buttons = QHBoxLayout()
        self.new_note_button = QPushButton("New Note")
        self.new_note_button.clicked.connect(self.add_new_note)
        self.bottom_buttons.addWidget(self.new_note_button)
        self.edit_note_button = QPushButton("Edit Note")
        self.edit_note_button.clicked.connect(self.edit_selected_note)
        self.bottom_buttons.addWidget(self.edit_note_button)
        self.delete_note_button = QPushButton("Delete Note")
        self.delete_note_button.clicked.connect(self.delete_selected_note)
        self.bottom_buttons.addWidget(self.delete_note_button)
        self.notes_table.cellDoubleClicked.connect(self.show_selected_note)

        # Add bottom buttons to main_layout and set layout
        self.bottom_buttons.addStretch()
        main_layout.addLayout(self.bottom_buttons)
        self.setLayout(main_layout)

        # Load companies at startup
        self.load_companies()
        self.board_search.currentIndexChanged.connect(self.load_notes_table)
        
    def show_selected_note(self, row, column):
        note_id_item = self.notes_table.item(row, 0)
        topic_item = self.notes_table.item(row, 1)
        if not note_id_item or not topic_item:
            QMessageBox.warning(self, "Error", "Could not determine selected note.")
            return
        note_id = int(note_id_item.text())
        topic = topic_item.text()
        user_id = self.user_id_edit.text().strip()
        dialog = NotesWindow(self.board_search.itemData(self.board_search.currentIndex()), topic, user_id, self, note_id=note_id)
        dialog.exec_()
        self.load_notes_table()

    def delete_selected_company(self):
        index = self.company_search.currentIndex()
        if index < 0:
            QMessageBox.warning(self, "Error", "Please select a company to delete.")
            return
        company_id = self.company_search.itemData(index)
        db_path = r"P:\EMS_TR_PATH\Shared_notes"
        connection = sql.connect(os.path.join(db_path, "shard_notes.db"))
        cursor = connection.cursor()
        cursor.execute("DELETE FROM companies WHERE id = ?", (company_id,))
        connection.commit()
        connection.close()
        self.load_companies()

    def delete_selected_board(self):
        index = self.board_search.currentIndex()
        if index < 0:
            QMessageBox.warning(self, "Error", "Please select a board to delete.")
            return
        board_id = self.board_search.itemData(index)
        db_path = r"P:\EMS_TR_PATH\Shared_notes"
        connection = sql.connect(os.path.join(db_path, "shard_notes.db"))
        cursor = connection.cursor()
        cursor.execute("DELETE FROM boards WHERE id = ?", (board_id,))
        connection.commit()
        connection.close()
        self.load_boards(self.company_search.itemData(self.company_search.currentIndex()))
        self.load_notes_table()

    def delete_selected_note(self):
        selected = self.notes_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Error", "Please select a note to delete.")
            return
        note_id_item = self.notes_table.item(selected, 0)
        if not note_id_item:
            QMessageBox.warning(self, "Error", "Could not determine selected note.")
            return
        note_id = int(note_id_item.text())
        db_path = r"P:\EMS_TR_PATH\Shared_notes"
        connection = sql.connect(os.path.join(db_path, "shard_notes.db"))
        cursor = connection.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        connection.commit()
        connection.close()
        self.load_notes_table()

    def load_notes_table(self):
        self.notes_table.setRowCount(0)
        board_id = self.board_search.itemData(self.board_search.currentIndex())
        if board_id is None:
            return
        db_path = r"P:\EMS_TR_PATH\Shared_notes"
        connection = sql.connect(os.path.join(db_path, "shard_notes.db"))
        cursor = connection.cursor()
        cursor.execute("SELECT id, topic, created_by, last_modified_by, timestamp FROM notes WHERE board_id = ? ORDER BY timestamp DESC", (board_id,))
        notes = cursor.fetchall()
        connection.close()
        self.notes_table.setRowCount(len(notes))
        from PyQt5.QtWidgets import QTableWidgetItem
        for row_idx, (note_id, topic, created_by, last_modified_by, timestamp) in enumerate(notes):
            self.notes_table.setItem(row_idx, 0, QTableWidgetItem(str(note_id)))
            self.notes_table.setItem(row_idx, 1, QTableWidgetItem(topic))
            self.notes_table.setItem(row_idx, 2, QTableWidgetItem(str(created_by)))
            self.notes_table.setItem(row_idx, 3, QTableWidgetItem(str(last_modified_by)))
            self.notes_table.setItem(row_idx, 4, QTableWidgetItem(str(timestamp)))
        self.notes_table.resizeColumnsToContents()

    def edit_selected_note(self):
        selected = self.notes_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Error", "Please select a note to edit.")
            return
        note_id_item = self.notes_table.item(selected, 0)
        topic_item = self.notes_table.item(selected, 1)
        if not note_id_item or not topic_item:
            QMessageBox.warning(self, "Error", "Could not determine selected note.")
            return
        note_id = int(note_id_item.text())
        topic = topic_item.text()
        user_id = self.user_id_edit.text().strip()
        if not user_id:
            QMessageBox.warning(self, "Error", "Please enter a User ID before editing a note.")
            return
        dialog = NotesWindow(self.board_search.itemData(self.board_search.currentIndex()), topic, user_id, self, note_id=note_id)
        dialog.exec_()
        self.load_notes_table()
        # if widget: widget.setParent(None)

        # Load topics for the selected board (example: empty list or fetch from database)
        topics = []
        board_id = self.board_search.itemData(self.board_search.currentIndex())
        if board_id is not None:
            from databaseConnect import get_notes_by_topic
            try:
                topics = get_notes_by_topic(board_id)
            except Exception:
                topics = []
        for topic in topics:
            button = QPushButton(topic)
            button.clicked.connect(lambda checked, t=topic: self.open_notes_window(board_id, t))
            # Ensure self.topics_layout exists, or replace with main_layout/addWidget as needed
            # self.topics_layout.addWidget(button)

    def open_notes_window(self, board_id, topic):
        dialog = NotesWindow(self, board_id, topic, )
        dialog.exec_()

    def on_company_changed(self, index):
        if index >= 0:
            company = self.company_search.itemData(index)
            self.load_boards(company)

    def on_board_changed(self, index):
        if index >= 0:
            board_id = self.board_search.itemData(index)
            self.load_topics(board_id)

    def add_new_company(self):
        company_name, ok = QInputDialog.getText(self, "Add Company", "Enter company name:")
        if ok and company_name:
            try:
                company_id = add_company(company_name)
                self.company_search.addItem(company_name, company_id)
                QMessageBox.information(self, "Success", f"Company '{company_name}' added (ID: {company_id})")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add company: {e}")
                
    def add_new_board(self):
        board_name, ok = QInputDialog.getText(self, "Add Board", "Enter board name:")
        if ok and board_name:
            try:
                # Get the currently selected company
                company_name = self.company_search.currentText()
                if not company_name:
                    QMessageBox.warning(self, "Error", "Please select a company first.")
                    return

                # Look up company_id
                db_path = r"P:\EMS_TR_PATH\Shared_notes"
                import sqlite3 as sql, os
                connection = sql.connect(os.path.join(db_path, "shard_notes.db"))
                cursor = connection.cursor()
                cursor.execute("SELECT id FROM companies WHERE name = ?", (company_name,))
                row = cursor.fetchone()
                connection.close()

                if row is None:
                    QMessageBox.warning(self, "Error", "Selected company not found.")
                    return
                company_id = row[0]

                # Now insert board linked to company
                board_id = add_board(company_id, board_name)
                self.board_search.addItem(board_name)
                QMessageBox.information(self, "Success", f"Board '{board_name}' added (ID: {board_id})")
                self.load_boards(company_id)  # Refresh boards list
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add board: {e}")

    def add_new_note(self):
        board_id = self.board_search.itemData(self.board_search.currentIndex())
        if board_id is None:
            QMessageBox.warning(self, "Error", "Please Select a board first")
            return
        topic, ok = QInputDialog.getText(self, "Add Topic", "Enter topic name: ")
        if ok and topic:
            user_id = self.user_id_edit.text().strip()
            if not user_id:
                QMessageBox.warning(self, "Error", "Please enter a User ID before adding a note.")
                return
            dialog = NotesWindow(board_id, topic, user_id, self)
            dialog.exec_()
            self.load_topics(board_id)

    def load_companies(self):
        self.company_search.clear()
        db_path = r"P:\EMS_TR_PATH\Shared_notes"
        import sqlite3 as sql, os
        connection = sql.connect(os.path.join(db_path, "shard_notes.db"))
        cursor = connection.cursor()
        cursor.execute("SELECT id, name FROM companies ORDER BY name")
        companies = cursor.fetchall()
        connection.close()
        for company_id, name in companies:
            self.company_search.addItem(name, company_id)
        # Optionally, load boards for the first company
        if self.company_search.count() > 0:
            self.load_boards(self.company_search.itemData(self.company_search.currentIndex()))
        else:
            self.board_search.clear()

    def load_boards(self, company_id):
        self.board_search.clear()
        db_path = r"P:\EMS_TR_PATH\Shared_notes"
        connection = sql.connect(os.path.join(db_path, "shard_notes.db"))
        query = connection.cursor()
        query.execute("SELECT id, name FROM boards WHERE company_id = ? ORDER BY name", (company_id,))
        boards = query.fetchall()
        connection.close()
        for board_id, name in boards:
            self.board_search.addItem(name, board_id)

    def load_topics(self, board_id):
        from databaseConnect import get_topics
        topics = get_topics(board_id)

        for i in reversed(range(self.topics_layout.count())):
            widget = self.topics_layout.itemAt(i).widget
            if widget:
                widget.setParent(None)



class NotesWindow(QDialog):
    def __init__(self, board_id, topic, user_id, parent=None, note_id=None):
        super().__init__(parent)
        self.board_id = board_id
        self.topic = topic
        self.user_id = user_id
        self.note_id = note_id
        self.setWindowTitle(f"Notes for Board ID: {board_id} - Topic: {topic}")
        self.resize(400, 300)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        if note_id:
            db_path = r"P:\EMS_TR_PATH\Shared_notes"
            connection = sql.connect(os.path.join(db_path, "shard_notes.db"))
            cursor = connection.cursor()
            cursor.execute("SELECT content FROM notes WHERE id = ?", (note_id,))
            row = cursor.fetchone()
            connection.close()
            if row:
                self.text_edit.setPlainText(row[0])
        else:
            from databaseConnect import get_notes_by_topic
            notes = get_notes_by_topic(board_id, topic)
            self.text_edit.setPlainText("\n\n".join(notes))

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_notes)
        layout.addWidget(save_button)

    def save_notes(self):
        content = self.text_edit.toPlainText()
        try:
            if self.note_id:
                from databaseConnect import edit_note
                edit_note(self.note_id, content, self.user_id)
                QMessageBox.information(self, "Success", "Note updated successfully.")
            else:
                from databaseConnect import add_note
                add_note(self.board_id, self.topic, content, self.user_id)
                QMessageBox.information(self, "Success", "Notes saved successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save notes: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = QMainWindow()
    window.setWindowTitle("Troubleshooting Notes")
    window.resize(400, 300)
    main_widget = MainWindow()
    window.setCentralWidget(main_widget)
    window.show()
    sys.exit(app.exec_())
