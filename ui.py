import tkinter as tk
from tkinter import messagebox
from database import connect
from datetime import datetime
from utils import calculate_late_fee

class LibraryUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")

        # --- Add Book Section ---
        tk.Label(root, text="Title").grid(row=0, column=0)
        tk.Label(root, text="Author").grid(row=1, column=0)

        self.title = tk.Entry(root)
        self.author = tk.Entry(root)
        self.title.grid(row=0, column=1)
        self.author.grid(row=1, column=1)

        tk.Button(root, text="Add Book", command=self.add_book).grid(row=2, column=1)

        # --- Inventory Section ---
        tk.Button(root, text="Show Inventory", command=self.show_books).grid(row=3, column=1)
        tk.Button(root, text="Show Issued Books", command=self.show_issued_books).grid(row=3, column=0)

        self.book_listbox = tk.Listbox(root, width=80)
        self.book_listbox.grid(row=4, column=0, columnspan=2)

        # --- Issue Book Section ---
        tk.Label(root, text="Book ID to Issue").grid(row=5, column=0)
        tk.Label(root, text="Issued To (User)").grid(row=6, column=0)

        self.issue_book_id = tk.Entry(root)
        self.issue_user = tk.Entry(root)

        self.issue_book_id.grid(row=5, column=1)
        self.issue_user.grid(row=6, column=1)

        tk.Button(root, text="Issue Book", command=self.issue_book).grid(row=7, column=1)

        # --- Return Book Section ---
        tk.Label(root, text="Issue ID to Return").grid(row=8, column=0)
        tk.Label(root, text="Return Date (YYYY-MM-DD)").grid(row=9, column=0)

        self.return_issue_id = tk.Entry(root)
        self.return_date = tk.Entry(root)

        self.return_issue_id.grid(row=8, column=1)
        self.return_date.grid(row=9, column=1)

        # Auto-fill return date with today
        self.return_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Button(root, text="Return Book", command=self.return_book).grid(row=10, column=1)

        # --- Delete Book Section ---
        tk.Label(root, text="Book ID to Delete").grid(row=11, column=0)

        self.delete_book_id = tk.Entry(root)
        self.delete_book_id.grid(row=11, column=1)

        tk.Button(root, text="Delete Book", command=self.delete_book).grid(row=12, column=1)

        # --- Search Book Section ---
        tk.Label(root, text="Search Title").grid(row=13, column=0)

        self.search_title = tk.Entry(root)
        self.search_title.grid(row=13, column=1)

        tk.Button(root, text="Search Book", command=self.search_book).grid(row=14, column=1)

    # --- Method to Add Book ---
    def add_book(self):
        title = self.title.get()
        author = self.author.get()
        if title == "" or author == "":
            messagebox.showwarning("Input Error", "Please enter both Title and Author")
            return
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO books (title, author) VALUES (?, ?)", (title, author))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Book Added")

    # --- Method to Show Inventory ---
    def show_books(self):
        self.book_listbox.delete(0, tk.END)
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, author, available FROM books")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            status = "Available" if row[3] == 1 else "Issued"
            display_text = f"ID: {row[0]} | {row[1]} by {row[2]} [{status}]"
            self.book_listbox.insert(tk.END, display_text)

    # --- Method to Show Issued Books ---
    def show_issued_books(self):
        self.book_listbox.delete(0, tk.END)
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT issues.id, books.title, books.author, issues.user, issues.issue_date, issues.return_date
            FROM issues
            JOIN books ON issues.book_id = books.id
        """)
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            return_info = f"Returned on {row[5]}" if row[5] else "Not Returned"
            display_text = (f"Issue ID: {row[0]} | {row[1]} by {row[2]} | "
                            f"Issued to: {row[3]} on {row[4]} | {return_info}")
            self.book_listbox.insert(tk.END, display_text)

    # --- Method to Issue Book ---
    def issue_book(self):
        book_id = self.issue_book_id.get()
        user = self.issue_user.get()
        if book_id == "" or user == "":
            messagebox.showwarning("Input Error", "Please enter both Book ID and User")
            return
        issue_date = datetime.now().strftime("%Y-%m-%d")

        conn = connect()
        cursor = conn.cursor()

        cursor.execute("SELECT available FROM books WHERE id=?", (book_id,))
        book = cursor.fetchone()
        if not book:
            messagebox.showerror("Error", "Book not found!")
            conn.close()
            return
        if book[0] == 0:
            messagebox.showwarning("Warning", "Book is already issued!")
            conn.close()
            return

        cursor.execute("UPDATE books SET available=0 WHERE id=?", (book_id,))
        cursor.execute("INSERT INTO issues (book_id, user, issue_date) VALUES (?, ?, ?)",
                       (book_id, user, issue_date))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Book issued!")

    # --- Method to Return Book ---
    def return_book(self):
        issue_id = self.return_issue_id.get()
        return_date = self.return_date.get()

        if issue_id == "" or return_date == "":
            messagebox.showwarning("Input Error", "Please enter both Issue ID and Return Date")
            return

        conn = connect()
        cursor = conn.cursor()

        cursor.execute("SELECT book_id, issue_date FROM issues WHERE id=?", (issue_id,))
        issue = cursor.fetchone()
        if not issue:
            messagebox.showerror("Error", "Issue ID not found!")
            conn.close()
            return

        book_id, issue_date = issue

        try:
            fee = calculate_late_fee(issue_date, return_date)
        except ValueError:
            messagebox.showerror("Date Error", "Please enter Return Date in format YYYY-MM-DD (example: 2025-06-21)")
            conn.close()
            return

        cursor.execute("UPDATE issues SET return_date=? WHERE id=?", (return_date, issue_id))
        cursor.execute("UPDATE books SET available=1 WHERE id=?", (book_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Returned", f"Book returned!\nLate fee: Rs {fee}")

    # --- Method to Delete Book ---
    def delete_book(self):
        book_id = self.delete_book_id.get()
        if book_id == "":
            messagebox.showwarning("Input Error", "Please enter Book ID to delete")
            return

        conn = connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM books WHERE id=?", (book_id,))
        book = cursor.fetchone()
        if not book:
            messagebox.showerror("Error", "Book ID not found!")
            conn.close()
            return

        if book[3] == 0:
            messagebox.showwarning("Warning", "Book is currently issued. Cannot delete.")
            conn.close()
            return

        cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Deleted", f"Book ID {book_id} deleted.")

    # --- Method to Search Book ---
    def search_book(self):
        keyword = self.search_title.get()
        if keyword == "":
            messagebox.showwarning("Input Error", "Please enter Title to search")
            return

        self.book_listbox.delete(0, tk.END)
        conn = connect()
        cursor = conn.cursor()

        cursor.execute("SELECT id, title, author, available FROM books WHERE title LIKE ?", ('%' + keyword + '%',))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            self.book_listbox.insert(tk.END, "No matching books found.")
        else:
            for row in rows:
                status = "Available" if row[3] == 1 else "Issued"
                display_text = f"ID: {row[0]} | {row[1]} by {row[2]} [{status}]"
                self.book_listbox.insert(tk.END, display_text)
