# Troubleshooting Notes Application

A multi-user desktop application for creating, saving, and editing notes organized by company and board identifiers. Built with Python, Tkinter, and SQLite.

## Features

- Multi-user support with user identification
- Notes organized by company and board structure
- Simple and intuitive GUI interface
- Offline-first architecture with SQLite database
- Supports multiple devices accessing the same database

## Setup

1. Ensure you have Python 3.x installed on your system
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `.\venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Run the application:
   ```bash
   python app.py
   ```

## Usage

1. Enter your User ID in the top field
2. Select or add a company using the dropdown or "Add Company" button
3. Select or add a board for the selected company
4. Use the "New Note" button to create notes
5. Double-click a note or use the "Edit Note" button to modify existing notes

## Multi-device Usage

To use the application across multiple devices:
1. Copy the `notes.db` file to the same location on other devices
2. Run the application on each device
3. All devices will access the same database file

Note: For concurrent access across devices, place the database file in a shared network location accessible to all devices.

## Data Structure

- Companies can have multiple boards
- Each board can contain multiple notes
- Notes are associated with:
  - User ID
  - Title
  - Content
  - Creation and update timestamps