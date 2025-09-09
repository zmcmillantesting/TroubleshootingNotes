from PyQt5.QtWidgets import(
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, 
    QLabel, QFileDialog, QMessageBox, QTextEdit, QLineEdit,
    QHBoxLayout, QComboBox, QListWidgetItem, QInputDialog, QListView
)

from PyQt5.QtCore import Qt
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../data')))
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data')))
from databaseConnect import add_company, add_board, add_note, init_db

class MainWindow(QWidget):
    def add_note(self):
        # TODO: Implement note adding logic
        pass
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


    def add_company(self):
        name, ok = QInputDialog.getText(self, "Add Company", "Enter company name:")
        if ok and name:
            try:
                company_id = add_company(name)
                self.company_search.addItem(name)
                QMessageBox.information(self, "Success", f"Company '{name}' added (ID: {company_id})")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add company: {e}")

    def add_board(self):
        board_name, ok = QInputDialog.getText(self, "Add Board", "Enter board name:")
        if ok and board_name:
            try:
                board_id = add_board(board_name)
                self.board_search.addItem(board_name)
                QMessageBox.information(self, "Success", f"Board '{board_name}' added (ID: {board_id})")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add board: {e}")
            
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
