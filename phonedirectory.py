import sqlite3
from tkinter import *
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime
import re

class PhoneDirectoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Phone Directory")
        self.root.geometry("800x600")
        
        # Database setup
        self.conn = sqlite3.connect("phone_directory.db")
        self.cursor = self.conn.cursor()
        self.setup_database()
        
        # Main container
        main_container = Frame(root, padx=10, pady=10)
        main_container.pack(fill=BOTH, expand=True)
        
        # Contact details frame
        self.create_contact_frame(main_container)
        
        # Search frame
        self.create_search_frame(main_container)
        
        # Contacts list
        self.create_list_frame(main_container)
        
        # Buttons frame
        self.create_buttons_frame(main_container)
        
        # Load contacts
        self.load_contacts()

    def setup_database(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            email TEXT,
            category TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        self.conn.commit()

    def create_contact_frame(self, container):
        contact_frame = LabelFrame(container, text="Contact Details", padx=5, pady=5)
        contact_frame.pack(fill=X, pady=5)
        
        # Contact fields
        self.entries = {}
        fields = [('Name:', 0), ('Phone:', 1), ('Email:', 2), 
                 ('Category:', 3), ('Notes:', 4)]
        
        for (label, row) in fields:
            Label(contact_frame, text=label).grid(row=row, column=0, sticky=W, padx=5, pady=2)
            if label == 'Notes:':
                self.entries[label] = Text(contact_frame, height=3, width=50)
            elif label == 'Category:':
                self.entries[label] = ttk.Combobox(contact_frame, 
                    values=['Family', 'Friend', 'Work', 'Other'])
            else:
                self.entries[label] = Entry(contact_frame, width=50)
            self.entries[label].grid(row=row, column=1, columnspan=3, sticky=W+E, padx=5, pady=2)

    def create_search_frame(self, container):
        search_frame = Frame(container)
        search_frame.pack(fill=X, pady=5)
        
        Label(search_frame, text="Search:").pack(side=LEFT, padx=5)
        self.search_entry = Entry(search_frame, width=30)
        self.search_entry.pack(side=LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_contacts())
        
        Label(search_frame, text="Category:").pack(side=LEFT, padx=5)
        self.category_filter = ttk.Combobox(search_frame, values=['All', 'Family', 'Friend', 'Work', 'Other'])
        self.category_filter.set('All')
        self.category_filter.pack(side=LEFT, padx=5)
        self.category_filter.bind('<<ComboboxSelected>>', lambda e: self.load_contacts())

    def create_list_frame(self, container):
        list_frame = Frame(container)
        list_frame.pack(fill=BOTH, expand=True, pady=5)
        
        columns = ('Name', 'Phone', 'Email', 'Category')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        scrolly = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.tree.yview)
        scrollx = ttk.Scrollbar(list_frame, orient=HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
        
        self.tree.grid(row=0, column=0, sticky=NSEW)
        scrolly.grid(row=0, column=1, sticky=NS)
        scrollx.grid(row=1, column=0, sticky=EW)
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

    def create_buttons_frame(self, container):
        button_frame = Frame(container)
        button_frame.pack(fill=X, pady=5)
        
        buttons = [
            ("Add", self.add_contact),
            ("Update", self.update_contact),
            ("Delete", self.delete_contact),
            ("Export CSV", self.export_to_csv),
            ("Import CSV", self.import_from_csv),
            ("Clear", self.clear_fields)
        ]
        
        for text, command in buttons:
            Button(button_frame, text=text, command=command, width=10).pack(side=LEFT, padx=5)

    def validate_input(self, values):
        if not values['Name:'].strip() or not values['Phone:'].strip():
            raise ValueError("Name and Phone are required")
            
        phone_pattern = r'^\+?1?\d{9,15}$'
        if not re.match(phone_pattern, values['Phone:'].strip()):
            raise ValueError("Invalid phone number format")
            
        if values['Email:'].strip():
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, values['Email:'].strip()):
                raise ValueError("Invalid email format")
        
        return True

    def add_contact(self):
        try:
            values = {k: v.get() if not isinstance(v, Text) else v.get('1.0', END).strip()
                     for k, v in self.entries.items()}
            
            if self.validate_input(values):
                self.cursor.execute("""
                    INSERT INTO contacts (name, phone, email, category, notes)
                    VALUES (?, ?, ?, ?, ?)
                """, (values['Name:'], values['Phone:'], values['Email:'],
                      values['Category:'], values['Notes:']))
                self.conn.commit()
                self.load_contacts()
                self.clear_fields()
                messagebox.showinfo("Success", "Contact added successfully!")
                
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Phone number already exists")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def update_contact(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a contact to update")
            return
            
        try:
            values = {k: v.get() if not isinstance(v, Text) else v.get('1.0', END).strip()
                     for k, v in self.entries.items()}
            
            if self.validate_input(values):
                contact_id = self.get_contact_id(selected[0])
                self.cursor.execute("""
                    UPDATE contacts 
                    SET name=?, phone=?, email=?, category=?, notes=?
                    WHERE id=?
                """, (values['Name:'], values['Phone:'], values['Email:'],
                      values['Category:'], values['Notes:'], contact_id))
                self.conn.commit()
                self.load_contacts()
                messagebox.showinfo("Success", "Contact updated successfully!")
                
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Phone number already exists")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def delete_contact(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a contact to delete")
            return
            
        if messagebox.askyesno("Confirm", "Delete this contact?"):
            contact_id = self.get_contact_id(selected[0])
            self.cursor.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
            self.conn.commit()
            self.load_contacts()
            self.clear_fields()

    def load_contacts(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        category = self.category_filter.get()
        if category == 'All':
            self.cursor.execute("SELECT * FROM contacts ORDER BY name")
        else:
            self.cursor.execute("SELECT * FROM contacts WHERE category=? ORDER BY name", (category,))
            
        for contact in self.cursor.fetchall():
            self.tree.insert('', END, values=contact[1:5])

    def search_contacts(self):
        search = self.search_entry.get().strip().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.cursor.execute("""
            SELECT * FROM contacts 
            WHERE lower(name) LIKE ? OR lower(phone) LIKE ? OR lower(email) LIKE ?
            ORDER BY name
        """, (f"%{search}%", f"%{search}%", f"%{search}%"))
        
        for contact in self.cursor.fetchall():
            self.tree.insert('', END, values=contact[1:5])

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
            
        contact_id = self.get_contact_id(selected[0])
        self.cursor.execute("SELECT name, phone, email, category, notes FROM contacts WHERE id=?", 
                          (contact_id,))
        contact = self.cursor.fetchone()
        
        self.clear_fields()
        fields = ['Name:', 'Phone:', 'Email:', 'Category:', 'Notes:']
        for field, value in zip(fields, contact):
            if field == 'Notes:':
                self.entries[field].insert('1.0', value or '')
            else:
                self.entries[field].insert(0, value or '')

    def clear_fields(self):
        for entry in self.entries.values():
            if isinstance(entry, Text):
                entry.delete('1.0', END)
            else:
                entry.delete(0, END)

    def export_to_csv(self):
        filename = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"contacts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        if filename:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Name', 'Phone', 'Email', 'Category', 'Notes'])
                self.cursor.execute("SELECT name, phone, email, category, notes FROM contacts")
                writer.writerows(self.cursor.fetchall())
            messagebox.showinfo("Success", f"Exported to {filename}")

    def import_from_csv(self):
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    try:
                        if len(row) >= 5:
                            self.cursor.execute("""
                                INSERT INTO contacts (name, phone, email, category, notes)
                                VALUES (?, ?, ?, ?, ?)
                            """, row)
                    except sqlite3.IntegrityError:
                        continue
            self.conn.commit()
            self.load_contacts()
            messagebox.showinfo("Success", "Contacts imported successfully")

    def get_contact_id(self, item):
        values = self.tree.item(item)['values']
        self.cursor.execute("SELECT id FROM contacts WHERE phone=?", (values[1],))
        return self.cursor.fetchone()[0]

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = Tk()
    app = PhoneDirectoryApp(root)
    root.mainloop()