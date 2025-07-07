import sqlite3

def init_db():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    # Create books table
    cursor.execute('''CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY,
        title TEXT,
        author TEXT,
        available INTEGER DEFAULT 1
    )''')

    # Create issue log table
    cursor.execute('''CREATE TABLE IF NOT EXISTS issues (
        id INTEGER PRIMARY KEY,
        book_id INTEGER,
        user TEXT,
        issue_date TEXT,
        return_date TEXT,
        FOREIGN KEY(book_id) REFERENCES books(id)
    )''')

    conn.commit()
    conn.close()

def connect():
    return sqlite3.connect("library.db")
