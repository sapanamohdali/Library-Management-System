import tkinter as tk
from database import init_db
from ui import LibraryUI

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = LibraryUI(root)
    root.mainloop()
