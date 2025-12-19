import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from ttkbootstrap import ttk
from openpyxl import Workbook
import sqlite3
from cryptography.fernet import Fernet
from pathlib import Path
import shutil
import datetime
import platform

# ----------------------------
# Paths & Directories
# ----------------------------
home_dir = Path.home()
backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
key_file = home_dir / ".myfinance_secret.key"  # hidden key in user's home

# ----------------------------
# Encryption Key Setup
# ----------------------------
def generate_key():
    key = Fernet.generate_key()
    with open(key_file, "wb") as f:
        f.write(key)
    return key

def load_key():
    return open(key_file, "rb").read()

if not key_file.exists():
    key = generate_key()
else:
    key = load_key()

cipher = Fernet(key)

# ----------------------------
# Backup Function
# ----------------------------
def backup_db(db_name):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    db_path = Path(db_name)
    backup_file = backup_dir / f"{db_name}_{timestamp}.db"
    shutil.copy(db_path, backup_file)
    messagebox.showinfo("Backup", f"Backup created: {backup_file}")

# ----------------------------
# Center Window Function
# ----------------------------
def center_window(win, width, height):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

# ----------------------------
# Fonts (Cross-Platform)
# ----------------------------
font_name = "Segoe UI" if platform.system() == "Windows" else "Arial"

# ----------------------------
# PIN WINDOW (Starting Screen)
# ----------------------------
pin_window = tk.Tk()
pin_window.title("Secure Access")
pin_window.geometry("350x300")
pin_window.resizable(False, False)

style = Style("sandstone")
pin_window.configure(bg=style.colors.bg)
center_window(pin_window, 350, 300)

frame = ttk.Frame(pin_window, padding=30)
frame.pack(expand=True)

ttk.Label(frame, text="Welcome to your", font=(font_name, 11)).pack(pady=(0, 2))
ttk.Label(frame, text="Personal Financial Tracker", font=(font_name, 16, "bold")).pack(pady=(0, 15))
ttk.Label(frame, text="Enter your 4-digit PIN", font=(font_name, 10)).pack(pady=(0, 8))

pin_entry = ttk.Entry(frame, show="•", font=(font_name, 12), justify="center", width=15)
pin_entry.pack(ipady=5, pady=(0, 15))

# ----------------------------
# MAIN WINDOW
# ----------------------------
def main_window():
    global main_win
    pin_window.withdraw()

    main_win = tk.Toplevel()
    main_win.title("Expense Tracker")
    center_window(main_win, 600, 250)
    main_win.configure(padx=20, pady=20, bg=style.colors.bg)

    header = ttk.Label(main_win, text="Expense Tracker", font=(font_name, 20, "bold"))
    header.pack(anchor="center", pady=(0, 15))

    btn_frame = ttk.Frame(main_win)
    btn_frame.pack(pady=10)

    ttk.Button(btn_frame, text="Daily Expenses", bootstyle=PRIMARY, width=20, command=expenses_window).grid(row=0, column=0, padx=15)
    ttk.Button(btn_frame, text="Bills", bootstyle=WARNING, width=20, command=bills_window).grid(row=0, column=1, padx=15)
    ttk.Button(btn_frame, text="Debts", bootstyle=DANGER, width=20, command=debts_window).grid(row=0, column=2, padx=15)
    ttk.Button(btn_frame, text="Lock App", bootstyle=OUTLINE + SECONDARY, width=20, command=lock_app).grid(row=1, column=1, padx=15, pady=30)

# ----------------------------
# EXPENSES WINDOW
# ----------------------------
def expenses_window():
    main_win.withdraw()
    global expenses_win

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            amount REAL,
            date TEXT,
            description BLOB
        )
    ''')
    conn.commit()
    conn.close()

    expenses_win = tk.Toplevel()
    expenses_win.title("Daily Expenses")
    center_window(expenses_win, 900, 600)
    style.theme_use("sandstone")

    header_frame = ttk.Frame(expenses_win)
    header_frame.pack(fill="x", pady=10, padx=10)
    header_frame.columnconfigure(0, weight=1)

    ttk.Label(header_frame, text="Daily Expenses", font=(font_name, 16, "bold")).grid(row=0, column=0, sticky="nsew")
    ttk.Button(header_frame, text="Back", bootstyle=SECONDARY, command=go_back_to_main_from_expenses).grid(row=0, column=1, sticky="e")

    input_frame = ttk.LabelFrame(expenses_win, text="Add New Expense", padding=20, bootstyle="info")
    input_frame.pack(fill=X, padx=10, pady=10)

    ttk.Label(input_frame, text="Category:", font=(font_name, 10)).grid(row=0, column=0, padx=10, pady=5, sticky=W)
    ttk.Label(input_frame, text="Amount:", font=(font_name, 10)).grid(row=0, column=2, padx=10, pady=5, sticky=W)
    ttk.Label(input_frame, text="Date (MM-DD-YYYY):", font=(font_name, 10)).grid(row=1, column=0, padx=10, pady=5, sticky=W)
    ttk.Label(input_frame, text="Description:", font=(font_name, 10)).grid(row=1, column=2, padx=10, pady=5, sticky=W)

    category_entry = ttk.Entry(input_frame, width=25)
    amount_entry = ttk.Entry(input_frame, width=25)
    date_entry = ttk.Entry(input_frame, width=25)
    desc_entry = ttk.Entry(input_frame, width=25)

    category_entry.grid(row=0, column=1, padx=10, pady=5)
    amount_entry.grid(row=0, column=3, padx=10, pady=5)
    date_entry.grid(row=1, column=1, padx=10, pady=5)
    desc_entry.grid(row=1, column=3, padx=10, pady=5)

    def add_expense():
        category = category_entry.get()
        amount = amount_entry.get()
        date = date_entry.get()
        desc = desc_entry.get()
        encrypted_desc = cipher.encrypt(desc.encode())

        if category and amount and date:
            conn = sqlite3.connect('expenses.db')
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO expenses (category, amount, date, description) VALUES (?, ?, ?, ?)",
                (category, amount, date, encrypted_desc)
            )
            conn.commit()
            conn.close()

            backup_db("expenses.db")

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
        cursor.execute("SELECT * FROM expenses ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            encrypted = row[4]
            if isinstance(encrypted, memoryview):
                encrypted = encrypted.tobytes()
            try:
                decrypted_desc = cipher.decrypt(encrypted).decode()
            except Exception:
                decrypted_desc = encrypted
            tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3], decrypted_desc))

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
            encrypted_desc = row[4]
            if isinstance(encrypted_desc, memoryview):
                encrypted_desc = encrypted_desc.tobytes()
            try:
                decrypted_desc = cipher.decrypt(encrypted_desc).decode()
            except Exception:
                decrypted_desc = encrypted_desc
            ws.append([row[0], row[1], row[2], row[3], decrypted_desc])

        excel_file = Path("expenses.xlsx")
        wb.save(excel_file)
        messagebox.showinfo("Success", f"Data exported to {excel_file}!")

    btn_frame = ttk.Frame(expenses_win)
    btn_frame.pack(pady=10)
    ttk.Button(btn_frame, text="Add Expense", bootstyle=SUCCESS, width=20, command=add_expense).grid(row=0, column=0, padx=10)
    ttk.Button(btn_frame, text="Export to Excel", bootstyle=INFO, width=20, command=export_to_excel).grid(row=0, column=1, padx=10)

    table_frame = ttk.LabelFrame(expenses_win, text="Expense Records", padding=15, bootstyle="info")
    table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    columns = ("ID", "Category", "Amount", "Date", "Description")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12, bootstyle=PRIMARY)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER, width=150)
    tree.pack(fill=BOTH, expand=True)

    load_expenses()

# ----------------------------
# BILLS WINDOW
# ----------------------------
def bills_window():
    main_win.withdraw()
    global bills_win

    conn = sqlite3.connect('bills.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            amount REAL,
            duedate TEXT,
            description BLOB,
            status TEXT DEFAULT 'Unpaid'
        )
    ''')
    conn.commit()
    conn.close()

    bills_win = tk.Toplevel()
    bills_win.title("Bills")
    center_window(bills_win, 900, 600)
    style.theme_use("sandstone")

    header_frame = ttk.Frame(bills_win)
    header_frame.pack(fill="x", pady=10, padx=10)
    header_frame.columnconfigure(0, weight=1)

    ttk.Label(header_frame, text="Bills", font=(font_name, 16, "bold")).grid(row=0, column=0, sticky="nsew")
    ttk.Button(header_frame, text="Back", bootstyle=SECONDARY, command=go_back_to_main_from_bills).grid(row=0, column=1, sticky="e")

    input_frame = ttk.LabelFrame(bills_win, text="Add New Bill", padding=20, bootstyle="info")
    input_frame.pack(fill=X, padx=10, pady=10)

    ttk.Label(input_frame, text="Category:", font=(font_name, 10)).grid(row=0, column=0, padx=10, pady=5, sticky=W)
    ttk.Label(input_frame, text="Amount:", font=(font_name, 10)).grid(row=0, column=2, padx=10, pady=5, sticky=W)
    ttk.Label(input_frame, text="Due Date (MM-DD-YYYY):", font=(font_name, 10)).grid(row=1, column=0, padx=10, pady=5, sticky=W)
    ttk.Label(input_frame, text="Description:", font=(font_name, 10)).grid(row=1, column=2, padx=10, pady=5, sticky=W)

    category_entry = ttk.Entry(input_frame, width=25)
    amount_entry = ttk.Entry(input_frame, width=25)
    date_entry = ttk.Entry(input_frame, width=25)
    desc_entry = ttk.Entry(input_frame, width=25)

    category_entry.grid(row=0, column=1, padx=10, pady=5)
    amount_entry.grid(row=0, column=3, padx=10, pady=5)
    date_entry.grid(row=1, column=1, padx=10, pady=5)
    desc_entry.grid(row=1, column=3, padx=10, pady=5)

    def add_bills():
        category = category_entry.get()
        amount = amount_entry.get()
        duedate = date_entry.get()
        desc = cipher.encrypt(desc_entry.get().encode())

        if category and amount and duedate:
            conn = sqlite3.connect('bills.db')
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO bills (category, amount, duedate, description) VALUES (?, ?, ?, ?)",
                (category, amount, duedate, desc)
            )
            conn.commit()
            conn.close()

            backup_db("bills.db")

            category_entry.delete(0, tk.END)
            amount_entry.delete(0, tk.END)
            date_entry.delete(0, tk.END)
            desc_entry.delete(0, tk.END)

            load_bills()
        else:
            messagebox.showwarning("Input Error", "Please fill in all required fields.")

    def load_bills():
        for row in tree.get_children():
            tree.delete(row)
        conn = sqlite3.connect('bills.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bills ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            encrypted = row[4]
            if isinstance(encrypted, memoryview):
                encrypted = encrypted.tobytes()
            try:
                decrypted_desc = cipher.decrypt(encrypted).decode()
            except Exception:
                decrypted_desc = encrypted
            tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3], decrypted_desc, row[5]))

    def export_to_excel():
        conn = sqlite3.connect('bills.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bills")
        rows = cursor.fetchall()
        conn.close()

        wb = Workbook()
        ws = wb.active
        ws.title = "Bills"
        ws.append(["ID", "Category", "Amount", "Due Date", "Description", "Status"])

        for row in rows:
            encrypted_desc = row[4]
            if isinstance(encrypted_desc, memoryview):
                encrypted_desc = encrypted_desc.tobytes()
            try:
                decrypted_desc = cipher.decrypt(encrypted_desc).decode()
            except Exception:
                decrypted_desc = encrypted_desc
            ws.append([row[0], row[1], row[2], row[3], decrypted_desc, row[5]])

        excel_file = Path("bills.xlsx")
        wb.save(excel_file)
        messagebox.showinfo("Success", f"Data exported to {excel_file}!")

    def resolve_bill():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Error", "Please select a bill to mark as Paid.")
            return
        bill_id = tree.item(selected)['values'][0]

        conn = sqlite3.connect('bills.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE bills SET status='Paid' WHERE id=?", (bill_id,))
        conn.commit()
        conn.close()

        load_bills()
        messagebox.showinfo("Success", "Bill marked as Paid!")

    btn_frame = ttk.Frame(bills_win)
    btn_frame.pack(pady=10)
    ttk.Button(btn_frame, text="Add Bill", bootstyle=SUCCESS, width=20, command=add_bills).grid(row=0, column=0, padx=10)
    ttk.Button(btn_frame, text="Export to Excel", bootstyle=INFO, width=20, command=export_to_excel).grid(row=0, column=1, padx=10)
    ttk.Button(btn_frame, text="Resolve Selected", bootstyle=SUCCESS, width=20, command=resolve_bill).grid(row=0, column=2, padx=10)

    table_frame = ttk.LabelFrame(bills_win, text="Bills Records", padding=15, bootstyle="info")
    table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    columns = ("ID", "Category", "Amount", "Due Date", "Description", "Status")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12, bootstyle=PRIMARY)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER, width=150)
    tree.pack(fill=BOTH, expand=True)

    load_bills()

# ----------------------------
# DEBTS WINDOW
# ----------------------------
def debts_window():
    main_win.withdraw()
    global debts_win

    conn = sqlite3.connect('debts.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS debts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creditor TEXT,
            amount REAL,
            dateborrowed TEXT,
            description BLOB,
            status TEXT DEFAULT 'Unpaid'
        )
    ''')
    conn.commit()
    conn.close()

    debts_win = tk.Toplevel()
    debts_win.title("Debts")
    center_window(debts_win, 900, 600)
    style.theme_use("sandstone")

    header_frame = ttk.Frame(debts_win)
    header_frame.pack(fill="x", pady=10, padx=10)
    header_frame.columnconfigure(0, weight=1)

    ttk.Label(header_frame, text="Debts", font=(font_name, 16, "bold")).grid(row=0, column=0, sticky="nsew")
    ttk.Button(header_frame, text="Back", bootstyle=SECONDARY, command=go_back_to_main_from_debts).grid(row=0, column=1, sticky="e")

    input_frame = ttk.LabelFrame(debts_win, text="Add New Debt", padding=20, bootstyle="info")
    input_frame.pack(fill=X, padx=10, pady=10)

    ttk.Label(input_frame, text="Creditor:", font=(font_name, 10)).grid(row=0, column=0, padx=10, pady=5, sticky=W)
    ttk.Label(input_frame, text="Amount:", font=(font_name, 10)).grid(row=0, column=2, padx=10, pady=5, sticky=W)
    ttk.Label(input_frame, text="Date Borrowed (MM-DD-YYYY):", font=(font_name, 10)).grid(row=1, column=0, padx=10, pady=5, sticky=W)
    ttk.Label(input_frame, text="Description:", font=(font_name, 10)).grid(row=1, column=2, padx=10, pady=5, sticky=W)

    creditor_entry = ttk.Entry(input_frame, width=25)
    amount_entry = ttk.Entry(input_frame, width=25)
    date_entry = ttk.Entry(input_frame, width=25)
    desc_entry = ttk.Entry(input_frame, width=25)

    creditor_entry.grid(row=0, column=1, padx=10, pady=5)
    amount_entry.grid(row=0, column=3, padx=10, pady=5)
    date_entry.grid(row=1, column=1, padx=10, pady=5)
    desc_entry.grid(row=1, column=3, padx=10, pady=5)

    def add_debts():
        creditor = creditor_entry.get()
        amount = amount_entry.get()
        dateborrowed = date_entry.get()
        desc = cipher.encrypt(desc_entry.get().encode())

        if creditor and amount and dateborrowed:
            conn = sqlite3.connect('debts.db')
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO debts (creditor, amount, dateborrowed, description) VALUES (?, ?, ?, ?)",
                (creditor, amount, dateborrowed, desc)
            )
            conn.commit()
            conn.close()

            backup_db("debts.db")

            creditor_entry.delete(0, tk.END)
            amount_entry.delete(0, tk.END)
            date_entry.delete(0, tk.END)
            desc_entry.delete(0, tk.END)

            load_debts()
        else:
            messagebox.showwarning("Input Error", "Please fill in all required fields.")

    def load_debts():
        for row in tree.get_children():
            tree.delete(row)
        conn = sqlite3.connect('debts.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM debts ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            encrypted = row[4]
            if isinstance(encrypted, memoryview):
                encrypted = encrypted.tobytes()
            try:
                decrypted_desc = cipher.decrypt(encrypted).decode()
            except Exception:
                decrypted_desc = encrypted
            tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3], decrypted_desc, row[5]))

    def export_to_excel():
        conn = sqlite3.connect('debts.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM debts")
        rows = cursor.fetchall()
        conn.close()

        wb = Workbook()
        ws = wb.active
        ws.title = "Debts"
        ws.append(["ID", "Creditor", "Amount", "Date Borrowed", "Description", "Status"])

        for row in rows:
            encrypted_desc = row[4]
            if isinstance(encrypted_desc, memoryview):
                encrypted_desc = encrypted_desc.tobytes()
            try:
                decrypted_desc = cipher.decrypt(encrypted_desc).decode()
            except Exception:
                decrypted_desc = encrypted_desc
            ws.append([row[0], row[1], row[2], row[3], decrypted_desc, row[5]])

        excel_file = Path("debts.xlsx")
        wb.save(excel_file)
        messagebox.showinfo("Success", f"Data exported to {excel_file}!")

    def resolve_debt():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Error", "Please select a debt to mark as Paid.")
            return
        debt_id = tree.item(selected)['values'][0]

        conn = sqlite3.connect('debts.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE debts SET status='Paid' WHERE id=?", (debt_id,))
        conn.commit()
        conn.close()

        load_debts()
        messagebox.showinfo("Success", "Debt marked as Paid!")

    btn_frame = ttk.Frame(debts_win)
    btn_frame.pack(pady=10)
    ttk.Button(btn_frame, text="Add Debt", bootstyle=SUCCESS, width=20, command=add_debts).grid(row=0, column=0, padx=10)
    ttk.Button(btn_frame, text="Export to Excel", bootstyle=INFO, width=20, command=export_to_excel).grid(row=0, column=1, padx=10)
    ttk.Button(btn_frame, text="Resolve Selected", bootstyle=SUCCESS, width=20, command=resolve_debt).grid(row=0, column=2, padx=10)

    table_frame = ttk.LabelFrame(debts_win, text="Debts Records", padding=15, bootstyle="info")
    table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    columns = ("ID", "Creditor", "Amount", "Date Borrowed", "Description", "Status")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12, bootstyle=PRIMARY)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER, width=140)
    tree.pack(fill=BOTH, expand=True)

    load_debts()

# ----------------------------
# NAVIGATION & LOCK
# ----------------------------
def go_back_to_main_from_expenses():
    expenses_win.destroy()
    main_win.deiconify()

def go_back_to_main_from_bills():
    bills_win.destroy()
    main_win.deiconify()

def go_back_to_main_from_debts():
    debts_win.destroy()
    main_win.deiconify()

def lock_app():
    main_win.destroy()
    pin_window.deiconify()

# ----------------------------
# PIN VALIDATION
# ----------------------------
def open_main_window():
    pin = pin_entry.get()
    if pin == "1234":
        main_window()
    else:
        messagebox.showerror("Error", "Incorrect PIN. Try again.")

ttk.Button(frame, text="Unlock", bootstyle=INFO, command=open_main_window).pack(fill=X, pady=5)
ttk.Label(frame, text="Your data is encrypted and secure.", font=(font_name, 8)).pack(pady=(20, 0))

pin_window.bind("<Return>", lambda e: open_main_window())
pin_window.mainloop()