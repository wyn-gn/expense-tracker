import sqlite3
from tkinter import *
from tkinter import messagebox
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from ttkbootstrap import ttk
from openpyxl import Workbook

# ---------------- PIN WINDOW ----------------
def open_main_window():
    pin = pin_entry.get()
    if pin == "1234":
        pin_window.destroy()
        main_window()
    else:
        messagebox.showerror("Error", "Incorrect PIN. Try again.")

# Initialize modern theme
style = Style(theme="superhero")  # Try also "flatly", "cyborg", or "darkly"

pin_window = style.master
pin_window.title("Security Check")
pin_window.geometry("320x200")
pin_window.resizable(False, False)

Label(pin_window, text="🔒 Expense Tracker", font=("Segoe UI Semibold", 16)).pack(pady=(20, 10))
Label(pin_window, text="Enter your 4-digit PIN", font=("Segoe UI", 11)).pack()

pin_entry = ttk.Entry(pin_window, show="*", width=25, font=("Segoe UI", 12))
pin_entry.pack(pady=10)

ttk.Button(pin_window, text="Unlock", bootstyle=SUCCESS, width=15, command=open_main_window).pack(pady=10)

# ---------------- MAIN WINDOW ----------------
def main_window():
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

    root = Tk()
    root.title("💰 Expense Tracker Dashboard")
    root.geometry("900x600")
    root.configure(padx=20, pady=20)

    # Header Section
    header = ttk.Label(root, text="Expense Tracker", font=("Segoe UI Semibold", 20))
    header.pack(anchor="center", pady=(0, 15))

    # ---- Input Frame ----
    input_frame = ttk.LabelFrame(root, text="Add New Expense", padding=20, bootstyle="primary")
    input_frame.pack(fill=X, padx=10, pady=10)

    # Input Fields
    ttk.Label(input_frame, text="Category:").grid(row=0, column=0, padx=10, pady=5, sticky=W)
    ttk.Label(input_frame, text="Amount:").grid(row=0, column=2, padx=10, pady=5, sticky=W)
    ttk.Label(input_frame, text="Date:").grid(row=1, column=0, padx=10, pady=5, sticky=W)
    ttk.Label(input_frame, text="Description:").grid(row=1, column=2, padx=10, pady=5, sticky=W)

    category_entry = ttk.Entry(input_frame, width=25)
    amount_entry = ttk.Entry(input_frame, width=25)
    date_entry = ttk.Entry(input_frame, width=25)
    desc_entry = ttk.Entry(input_frame, width=25)

    category_entry.grid(row=0, column=1, padx=10, pady=5)
    amount_entry.grid(row=0, column=3, padx=10, pady=5)
    date_entry.grid(row=1, column=1, padx=10, pady=5)
    desc_entry.grid(row=1, column=3, padx=10, pady=5)

    # ---- Functions ----
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
            category_entry.delete(0, END)
            amount_entry.delete(0, END)
            date_entry.delete(0, END)
            desc_entry.delete(0, END)
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
            tree.insert("", END, values=row)

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

    # ---- Buttons ----
    btn_frame = ttk.Frame(root)
    btn_frame.pack(pady=10)

    ttk.Button(btn_frame, text="Add Expense", bootstyle=SUCCESS, width=20, command=add_expense).grid(row=0, column=0, padx=10)
    ttk.Button(btn_frame, text="Export to Excel", bootstyle=INFO, width=20, command=export_to_excel).grid(row=0, column=1, padx=10)

    # ---- Table Frame ----
    table_frame = ttk.LabelFrame(root, text="Expense Records", padding=15, bootstyle="info")
    table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    columns = ("ID", "Category", "Amount", "Date", "Description")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12, bootstyle=PRIMARY)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor=CENTER, width=150)
    tree.pack(fill=BOTH, expand=True)

    load_expenses()
    root.mainloop()


pin_window.mainloop()
