from PyQt5.QtWidgets import(
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, 
    QLabel, QFileDialog, QMessageBox, QTextEdit, QLineEdit,
    QHBoxLayout, QComboBox, QListWidgetItem, QInputDialog, QListView
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
        self.setWindowTitle("EMS Testing & Repair Shared Notes")
        self.resize(400, 300)

        layout = QVBoxLayout()
        self.setLayout(layout)

        search_layout = QVBoxLayout()

        # Company dropdown
        self.Company_label = QLabel("Select Company")
        self.company_search = QComboBox()
        self.company_search.currentIndexChanged.connect(self.on_company_changed)
        self.company_search.setMinimumWidth(200)
        search_layout.addWidget(self.Company_label)
        search_layout.addWidget(self.company_search)

        # Board dropdown
        self.board_label = QLabel("Select Board")
        self.board_search = QComboBox()
        self.board_search.setMinimumWidth(200)
        search_layout.addWidget(self.board_label)
        search_layout.addWidget(self.board_search)

        # Add company and board buttons
        button_layout = QHBoxLayout()
        self.add_company_button = QPushButton("Add Company")
        self.add_company_button.setMinimumWidth(200)
        self.add_company_button.clicked.connect(self.add_company)
        button_layout.addWidget(self.add_company_button)

        self.add_board_button = QPushButton("Add Board")
        self.add_board_button.setMinimumWidth(200)
        self.add_board_button.clicked.connect(self.add_board)
        button_layout.addWidget(self.add_board_button)

        search_layout.addLayout(button_layout)
        layout.addLayout(search_layout)

        # Notes dropdown
        self.notes_options = QComboBox()
        self.notes_options.setMinimumWidth(200)
        layout.addWidget(QLabel("Select Note Title"))
        layout.addWidget(self.notes_options)

        # Add notes button
        self.add_note_button = QPushButton("Add Notes")
        self.add_note_button.setMinimumWidth(200)
        self.add_note_button.clicked.connect(self.add_note)
        layout.addWidget(self.add_note_button)

        # Load companies at startup
        self.load_companies()

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

        if companies:
            # Automatically load boards for the first company
            first_company_id = companies[0][0]
            self.load_boards(first_company_id)


    def load_boards(self, company):
        self.board_search.clear()
        db_path = r"P:\EMS_TR_PATH\Shared_notes"
        connection = sql.connect(os.path.join(db_path, "shard_notes.db"))
        curser = connection.cursor()
        curser.execute("SELECT id, name FROM boards WHERE company_id = ? ORDER BY name", (company,))
        boards = curser.fetchall()
        connection.close()

        for board_id, name in boards:
            print("DEBUG:", board_id, "name:", name)
            self.board_search.addItem(name, board_id)

    def on_company_changed(self, index):
        if index >= 0:
            company = self.company_search.itemData(index)
            self.load_boards(company)


    def add_company(self):
        company_name, ok = QInputDialog.getText(self, "Add Company", "Enter company name:")
        if ok and company_name:
            try:
                company_id = add_company(company_name)
                self.company_search.addItem(company_name, company_id)
                QMessageBox.information(self, "Success", f"Company '{company_name}' added (ID: {company_id})")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add company: {e}")
                

    def add_board(self):
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


    def add_note(self):
        pass
            
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
