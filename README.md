# Phone Directory Application

A simple phone directory application built using Python, SQLite, and Tkinter. This application provides CRUD (Create, Read, Update, Delete) functionality for managing contacts and supports exporting contacts to a CSV file.

## Features

- **Add Contacts**: Add new contacts with name and phone number.
- **Update Contacts**: Modify existing contact details.
- **Delete Contacts**: Remove unwanted contacts from the directory.
- **Search Contacts**: Search for contacts by name or phone number.
- **Export Contacts**: Export all contacts to a CSV file.
- **User-Friendly Interface**: Built using Tkinter for a graphical user interface.

## Requirements

- Python 3.x
- Required Libraries:
  - `tkinter` (for GUI)
  - `sqlite3` (for database management)
  - `csv` (for exporting data to CSV)

## Installation

1. Clone this repository or download the code files.
   ```bash
   git clone https://github.com/leefarhadaman/phonedirectory.git
   cd phonedirectory
   ```

2. Ensure you have Python 3.x installed on your system.

3. Install any necessary dependencies (though no external libraries are required).

## Usage

1. Run the `phonedirectory.py` script.
   ```bash
   python phonedirectory.py
   ```

2. The application window will open. Use the buttons and input fields to:
   - Add new contacts
   - Update or delete existing contacts
   - Search contacts
   - Export all contacts to a CSV file

## Application Screenshots

Include screenshots of the application (e.g., Add Contact screen, Search Contact screen).

## Database Structure

The application uses an SQLite database (`contacts.db`) with the following table structure:

| Column Name | Data Type    | Constraint       |
|-------------|--------------|------------------|
| `id`        | INTEGER      | PRIMARY KEY      |
| `name`      | TEXT         | NOT NULL         |
| `phone`     | TEXT         | UNIQUE, NOT NULL |

## Handling Errors

- **Duplicate Phone Numbers**:
  The application prevents duplicate phone numbers by enforcing a `UNIQUE` constraint on the `phone` column.
  - If a duplicate phone number is entered, an error message will appear.
  - You can modify this behavior in the code if duplicates are allowed.

## Export to CSV

- The exported CSV file contains all contacts in the database.
- File is saved in the current working directory with the name `contacts.csv`.

## Code Highlights

### Adding a New Contact
```python
def add_contact(self):
    name = self.name_entry.get().strip()
    phone = self.phone_entry.get().strip()

    if not name or not phone:
        messagebox.showerror("Input Error", "Both fields are required!")
        return

    try:
        self.cursor.execute("INSERT INTO contacts (name, phone) VALUES (?, ?)", (name, phone))
        self.conn.commit()
        messagebox.showinfo("Success", "Contact added successfully!")
        self.display_contacts()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Phone number already exists!")
```

### Updating a Contact
```python
def update_contact(self):
    contact_id = self.contact_id_entry.get().strip()
    name = self.name_entry.get().strip()
    phone = self.phone_entry.get().strip()

    if not contact_id or not name or not phone:
        messagebox.showerror("Input Error", "All fields are required!")
        return

    self.cursor.execute("SELECT id FROM contacts WHERE phone = ? AND id != ?", (phone, contact_id))
    duplicate = self.cursor.fetchone()

    if duplicate:
        messagebox.showerror("Update Error", "This phone number is already assigned to another contact!")
        return

    try:
        self.cursor.execute("UPDATE contacts SET name = ?, phone = ? WHERE id = ?", (name, phone, contact_id))
        self.conn.commit()
        messagebox.showinfo("Success", "Contact updated successfully!")
        self.display_contacts()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", str(e))
```

## Future Improvements

- Implement advanced search with partial matches.
- Add functionality to import contacts from a CSV file.
- Use Flask or Django for a web-based version of the application.
- Add authentication for secure access.

##Portfolio

[DevFaru(Farhad) Portfolio - ](https://devfaru.netlify.app)

