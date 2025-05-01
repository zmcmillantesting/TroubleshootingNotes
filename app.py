import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
import json
import os

class BaseDialog(tk.Toplevel):
    def __init__(self, parent, title, size="400x200"):
        super().__init__(parent)
        self.title(title)
        self.geometry(size)
        self.grab_set()
        
        # Configure grid weights for better resizing
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

class NoteDialog(BaseDialog):
    def __init__(self, parent, title, app, note=None, is_readonly=True, on_edit=None, on_save=None):
        super().__init__(parent, title, "600x400")
        self.note = note
        self.app = app  # Store reference to NotesApp instance
        
        # If we're editing, try to acquire the lock
        if not is_readonly and note:
            can_edit, editor = self.app.db.set_note_editing_status(note[0], self.app.user_id.get())
            if not can_edit:
                messagebox.showwarning(
                    "Note Locked", 
                    f"This note is currently being edited by {editor}. Please try again later."
                )
                self.destroy()
                return
        
        # Title
        ttk.Label(self, text="Title:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.title_entry = ttk.Entry(self, width=50)
        self.title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Content
        ttk.Label(self, text="Content:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.content_text = tk.Text(self, wrap=tk.WORD, width=50, height=15)
        self.content_text.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Load note data if provided
        if note:
            self.title_entry.insert(0, note[3])  # title
            self.content_text.insert(1.0, note[4] or "")  # content
            
        # Set readonly state if needed
        if is_readonly:
            self.title_entry.configure(state='readonly')
            self.content_text.configure(state='disabled')
        
        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        if is_readonly:
            if on_edit:
                ttk.Button(button_frame, text="Edit", command=on_edit).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Close", command=self.destroy).pack(side=tk.LEFT, padx=5)
        else:
            ttk.Button(button_frame, text="Save", command=on_save).pack(side=tk.LEFT, padx=5)
            
        # Bind the window close event
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def on_close(self):
        # Clear editing status if we were editing
        if self.note and not self.title_entry.cget('state') == 'readonly':
            self.app.db.clear_note_editing_status(self.note[0], self.app.user_id.get())
        self.destroy()

class NotesApp:
    def __init__(self, root, settings_file="test_settings.json"):
        self.root = root
        self.root.title("Troubleshooting Notes")
        
        # Initialize database and settings
        self.db = Database()
        self.settings_file = settings_file
        self.load_user_settings()
        
        self.setup_gui()
        self.refresh_companies()

    def load_user_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                self.settings = json.load(f)
        else:
            self.settings = {"last_user": ""}
            self.save_user_settings()

    def save_user_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f)

    def setup_gui(self):
        # Configure root window to be resizable
        self.root.resizable(True, True)
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # User section
        ttk.Label(main_frame, text="User ID:").grid(row=0, column=0, sticky=tk.W)
        self.user_id = ttk.Entry(main_frame)
        self.user_id.grid(row=0, column=1, sticky=(tk.W, tk.E))
        self.user_id.insert(0, self.settings.get("last_user", ""))
        
        # Company section
        ttk.Label(main_frame, text="Company:").grid(row=1, column=0, sticky=tk.W)
        company_frame = ttk.Frame(main_frame)
        company_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E))
        company_frame.columnconfigure(0, weight=1)
        
        self.company_var = tk.StringVar()
        self.company_combo = ttk.Combobox(company_frame, textvariable=self.company_var)
        self.company_combo.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        company_buttons_frame = ttk.Frame(company_frame)
        company_buttons_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))
        ttk.Button(company_buttons_frame, text="Add", command=self.add_company_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(company_buttons_frame, text="Delete", command=self.delete_company_dialog).pack(side=tk.LEFT, padx=2)
        
        # Board section
        ttk.Label(main_frame, text="Board:").grid(row=2, column=0, sticky=tk.W)
        board_frame = ttk.Frame(main_frame)
        board_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E))
        board_frame.columnconfigure(0, weight=1)
        
        self.board_var = tk.StringVar()
        self.board_combo = ttk.Combobox(board_frame, textvariable=self.board_var)
        self.board_combo.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        board_buttons_frame = ttk.Frame(board_frame)
        board_buttons_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))
        ttk.Button(board_buttons_frame, text="Add", command=self.add_board_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(board_buttons_frame, text="Delete", command=self.delete_board_dialog).pack(side=tk.LEFT, padx=2)
        
        # Notes section
        notes_frame = ttk.LabelFrame(main_frame, text="Notes", padding="5")
        notes_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        notes_frame.columnconfigure(0, weight=1)
        notes_frame.rowconfigure(0, weight=1)
        
        # Notes list with scrollbar
        self.notes_tree = ttk.Treeview(notes_frame, columns=("Title", "Created By", "Last Modified By", "Date"), show="headings")
        for col in ("Title", "Created By", "Last Modified By", "Date"):
            self.notes_tree.heading(col, text=col)
        self.notes_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure column widths
        self.notes_tree.column("Title", width=200, minwidth=100)
        self.notes_tree.column("Created By", width=100, minwidth=80)
        self.notes_tree.column("Last Modified By", width=100, minwidth=80)
        self.notes_tree.column("Date", width=150, minwidth=100)
        
        scrollbar = ttk.Scrollbar(notes_frame, orient=tk.VERTICAL, command=self.notes_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.notes_tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        button_frame = ttk.Frame(notes_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        for (text, command) in [
            ("New Note", self.new_note_dialog),
            ("Edit Note", lambda: self.edit_note_dialog(is_new=False)),
            ("Delete Note", self.delete_note)
        ]:
            ttk.Button(button_frame, text=text, command=command).pack(side=tk.LEFT, padx=5)
        
        # Configure weights for resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Configure main_frame columns
        main_frame.grid_columnconfigure(1, weight=1)  # Middle column expands
        main_frame.grid_columnconfigure(0, weight=0)  # Label column stays fixed
        main_frame.grid_columnconfigure(2, weight=0)  # Button column stays fixed
        main_frame.grid_rowconfigure(3, weight=1)     # Notes section expands vertically
        
        # Bind events
        self.company_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_boards())
        self.company_combo.bind('<KeyRelease>', self.on_company_change)  # Handle manual clearing
        self.board_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_notes())
        self.notes_tree.bind('<Double-1>', lambda e: self.view_note())
        self.user_id.bind('<FocusOut>', self.save_user_id)
        
        # Set minimum window size
        self.root.minsize(600, 400)

    def on_company_change(self, event=None):
        """Handle when company selection changes, including manual clearing"""
        if not self.company_var.get():
            self.refresh_boards()  # This will clear and disable the board combo

    def save_user_id(self, event=None):
        self.settings["last_user"] = self.user_id.get()
        self.save_user_settings()

    def refresh_companies(self):
        companies = self.db.get_companies()
        self.companies_dict = {name: id_ for id_, name in companies}
        self.company_combo['values'] = list(self.companies_dict.keys())

    def refresh_boards(self):
        # Clear existing board selection
        self.board_var.set("")
        self.board_combo['values'] = []
        self.boards_dict = {}
        
        company_name = self.company_var.get()
        if company_name and company_name in self.companies_dict:
            # Enable board combo and get boards for selected company
            self.board_combo['state'] = 'normal'
            boards = self.db.get_boards(self.companies_dict[company_name])
            self.boards_dict = {identifier: id_ for id_, identifier in boards}
            self.board_combo['values'] = list(self.boards_dict.keys())
        else:
            # Disable board combo when no company is selected
            self.board_combo['state'] = 'disabled'
        
        # Always refresh notes (will clear them if no board is selected)
        self.refresh_notes()

    def refresh_notes(self):
        self.notes_tree.delete(*self.notes_tree.get_children())
        board_id = self.boards_dict.get(self.board_var.get())
        if board_id:
            notes = self.db.get_notes(board_id)
            for note in notes:
                # note indices: id[0], user_id[1], title[2], content[3], created_at[4], updated_at[5], last_modified_by[6]
                last_modified = note[6] if note[6] else note[1]  # Use creator if no modifier
                self.notes_tree.insert('', 'end', values=(
                    note[2],        # title
                    note[1],        # created by (user_id)
                    last_modified,  # last modified by
                    note[5][:19]    # updated_at
                ), iid=note[0])

    def add_company_dialog(self):
        dialog = BaseDialog(self.root, "Add Company")
        
        ttk.Label(dialog, text="Company Name:").grid(row=0, column=0, padx=5, pady=5)
        company_entry = ttk.Entry(dialog)
        company_entry.grid(row=0, column=1, padx=5, pady=5)
        
        def save():
            company_name = company_entry.get().strip()
            if company_name:
                self.db.add_company(company_name)
                self.refresh_companies()
                dialog.destroy()
        
        ttk.Button(dialog, text="Save", command=save).grid(row=1, column=0, columnspan=2, pady=10)

    def delete_company_dialog(self):
        company_name = self.company_var.get()
        if not company_name:
            messagebox.showwarning("Warning", "Please select a company to delete")
            return
            
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete the company '{company_name}'?\n\n" +
                              "This will also delete all boards and notes associated with this company."):
            company_id = self.companies_dict[company_name]
            self.db.delete_company(company_id)
            self.company_var.set("")  # Clear selection
            self.board_var.set("")    # Clear board selection
            self.refresh_companies()
            self.refresh_boards()      # Clear boards list
            self.refresh_notes()       # Clear notes list

    def delete_board_dialog(self):
        board_identifier = self.board_var.get()
        if not board_identifier:
            messagebox.showwarning("Warning", "Please select a board to delete")
            return
            
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete the board '{board_identifier}'?\n\n" +
                              "This will also delete all notes on this board."):
            board_id = self.boards_dict[board_identifier]
            self.db.delete_board(board_id)
            self.board_var.set("")    # Clear board selection
            self.refresh_boards()
            self.refresh_notes()       # Clear notes list

    def add_board_dialog(self):
        if not self.company_var.get():
            messagebox.showwarning("Warning", "Please select a company first")
            return
            
        dialog = BaseDialog(self.root, "Add Board")
        
        ttk.Label(dialog, text="Board Identifier:").grid(row=0, column=0, padx=5, pady=5)
        board_entry = ttk.Entry(dialog)
        board_entry.grid(row=0, column=1, padx=5, pady=5)
        
        def save():
            board_id = board_entry.get().strip()
            if board_id:
                company_id = self.companies_dict[self.company_var.get()]
                self.db.add_board(company_id, board_id)
                self.refresh_boards()
                dialog.destroy()
        
        ttk.Button(dialog, text="Save", command=save).grid(row=1, column=0, columnspan=2, pady=10)

    def new_note_dialog(self):
        if not self.user_id.get():
            messagebox.showwarning("Warning", "Please enter a User ID")
            return
            
        if not self.company_var.get():
            messagebox.showwarning("Warning", "Please select a Company")
            return
            
        board_identifier = self.board_var.get()
        if not board_identifier or board_identifier not in self.boards_dict:
            messagebox.showwarning("Warning", "Please select a valid Board")
            return
            
        self.edit_note_dialog(is_new=True)

    def edit_note_dialog(self, is_new=False):
        if not is_new and not self.notes_tree.selection():
            messagebox.showwarning("Warning", "Please select a note to edit")
            return
        
        note = None if is_new else self.db.get_note(self.notes_tree.selection()[0])
        
        def save():
            title = dialog.title_entry.get().strip()
            content = dialog.content_text.get(1.0, tk.END).strip()
            
            if not title:
                messagebox.showwarning("Warning", "Please enter a title")
                return
                
            if is_new:
                board_id = self.boards_dict[self.board_var.get()]
                self.db.add_note(board_id, self.user_id.get(), title, content)
            else:
                self.db.update_note(note[0], title, content, self.user_id.get())
                
            self.refresh_notes()
            dialog.destroy()
        
        dialog = NoteDialog(
            parent=self.root,
            title="New Note" if is_new else "Edit Note",
            app=self,
            note=note,
            is_readonly=False,
            on_save=save
        )

    def view_note(self):
        selected = self.notes_tree.selection()
        if not selected:
            return
            
        note = self.db.get_note(selected[0])
        if note:
            dialog = NoteDialog(
                self.root,  # Changed from self to self.root
                "View Note",
                app=self,  # Pass the NotesApp instance
                note=note,
                is_readonly=True,
                on_edit=lambda: (dialog.destroy(), self.edit_note_dialog(is_new=False))
            )

    def delete_note(self):
        selected = self.notes_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a note to delete")
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this note?"):
            note_id = selected[0]
            self.db.delete_note(note_id)
            self.refresh_notes()

if __name__ == "__main__": 
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()