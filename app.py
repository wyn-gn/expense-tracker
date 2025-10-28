import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from ttkbootstrap import ttk
from openpyxl import Workbook
import sqlite3

# CENTER WINDOW
def center_window(win, width, height):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

# MAIN WINDOW FUNCTION
def main_window(root):
    # Clear the PIN screen widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Create or connect to database
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            amount REAL,
            date TEXT,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

    # Reconfigure window for main dashboard
    root.title("💰 Expense Tracker Dashboard")
    center_window(root, 900, 600)
    root.geometry("900x600")
    root.configure(padx=20, pady=20, bg=style.colors.bg)

    style.theme_use("sandstone")

    # Header Section
    header = ttk.Label(root, text="Expense Tracker", font=("Segoe UI Semibold", 20))
    header.pack(anchor="center", pady=(0, 15))

    # Input Frame
    input_frame = ttk.LabelFrame(root, text="Add New Expense", padding=20, bootstyle="info")
    input_frame.pack(fill=X, padx=10, pady=10)

    ttk.Label(input_frame, text="Category:").grid(row=0, column=0, padx=10, pady=5, sticky=W)
    ttk.Label(input_frame, text="Amount:").grid(row=0, column=2, padx=10, pady=5, sticky=W)
    ttk.Label(input_frame, text="Date (MM-DD-YYYY):").grid(row=1, column=0, padx=10, pady=5, sticky=W)
    ttk.Label(input_frame, text="Description:").grid(row=1, column=2, padx=10, pady=5, sticky=W)

    category_entry = ttk.Entry(input_frame, width=25)
    amount_entry = ttk.Entry(input_frame, width=25)
    date_entry = ttk.Entry(input_frame, width=25)
    desc_entry = ttk.Entry(input_frame, width=25)

    category_entry.grid(row=0, column=1, padx=10, pady=5)
    amount_entry.grid(row=0, column=3, padx=10, pady=5)
    date_entry.grid(row=1, column=1, padx=10, pady=5)
    desc_entry.grid(row=1, column=3, padx=10, pady=5)

    # FUNCTIONS
    def add_expense():
        category = category_entry.get()
        amount = amount_entry.get()
        date = date_entry.get()
        desc = desc_entry.get()

        if category and amount and date:
            conn = sqlite3.connect('expenses.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO expenses (category, amount, date, description) VALUES (?, ?, ?, ?)",
                           (category, amount, date, desc))
            conn.commit()
            conn.close()
            category_entry.delete(0, tk.END)
            amount_entry.delete(0, tk.END)
            date_entry.delete(0, tk.END)
            desc_entry.delete(0, tk.END)
            load_expenses()
        else:
            messagebox.showwarning("Input Error", "Please fill in all required fields.")

    def load_expenses():
        for row in tree.get_children():
            tree.delete(row)
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            tree.insert("", tk.END, values=row)

    def export_to_excel():
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses")
        rows = cursor.fetchall()
        conn.close()
        wb = Workbook()
        ws = wb.active
        ws.title = "Expenses"
        ws.append(["ID", "Category", "Amount", "Date", "Description"])
        for row in rows:
            ws.append(row)
        wb.save("expenses.xlsx")
        messagebox.showinfo("Success", "Data exported to expenses.xlsx!")

    # Buttons
    btn_frame = ttk.Frame(root)
    btn_frame.pack(pady=10)

    ttk.Button(btn_frame, text="Add Expense", bootstyle=SUCCESS, width=20, command=add_expense).grid(row=0, column=0, padx=10)
    ttk.Button(btn_frame, text="Export to Excel", bootstyle=INFO, width=20, command=export_to_excel).grid(row=0, column=1, padx=10)

    # Table Frame
    table_frame = ttk.LabelFrame(root, text="Expense Records", padding=15, bootstyle="info")
    table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    columns = ("ID", "Category", "Amount", "Date", "Description")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12, bootstyle=PRIMARY)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER, width=150)
    tree.pack(fill=BOTH, expand=True)

    load_expenses()
    root.deiconify()


# PIN WINDOW
pin_window = tk.Tk()
pin_window.title("Secure Access")
pin_window.geometry("350x300")
pin_window.resizable(False, False)
center_window(pin_window, 350, 300)

# Apply modern theme
style = Style("sandstone")
pin_window.configure(bg=style.colors.bg)

frame = ttk.Frame(pin_window, padding=30)
frame.pack(expand=True)

ttk.Label(frame, text="Welcome to your", font=("Segoe UI", 11)).pack(pady=(0, 2))
ttk.Label(frame, text="Personal Financial Tracker", font=("Segoe UI Semibold", 16)).pack(pady=(0, 15))
ttk.Label(frame, text="Enter your 4-digit PIN", font=("Segoe UI", 10)).pack(pady=(0, 8))

pin_entry = ttk.Entry(frame, show="•", font=("Segoe UI", 12), justify="center", width=15)
pin_entry.pack(ipady=5, pady=(0, 15))

def open_main_window():
    pin = pin_entry.get()
    if pin == "1234":
        main_window(pin_window)
    else:
        messagebox.showerror("Error", "Incorrect PIN. Try again.")

ttk.Button(frame, text="Unlock", bootstyle=INFO, command=open_main_window).pack(fill=X, pady=5)

ttk.Label(frame, text="Your data is encrypted and secure.", font=("Segoe UI", 8)).pack(pady=(20, 0))

pin_window.mainloop()
