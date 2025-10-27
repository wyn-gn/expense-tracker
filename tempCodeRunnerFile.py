# Tkinter setup
root = Tk()
root.title("Expense Tracker")
root.geometry("650x450")

# Labels
Label(root, text="Category").grid(row=0, column=0, padx=10, pady=5)
Label(root, text="Amount").grid(row=1, column=0, padx=10, pady=5)
Label(root, text="Date").grid(row=2, column=0, padx=10, pady=5)
Label(root, text="Description").grid(row=3, column=0, padx=10, pady=5)

# Input fields
category_entry = Entry(root)
amount_entry = Entry(root)
date_entry = Entry(root)
desc_entry = Entry(root)

category_entry.grid(row=0, column=1, padx=10, pady=5)
amount_entry.grid(row=1, column=1, padx=10, pady=5)
date_entry.grid(row=2, column=1, padx=10, pady=5)
desc_entry.grid(row=3, column=1, padx=10, pady=5)

# Function to add expenses
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

# Function to load data
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

# Export to Excel
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
Button(root, text="Add Expense", command=add_expense, bg="#4CAF50", fg="white").grid(row=4, column=0, columnspan=2, pady=10)
Button(root, text="Export to Excel", command=export_to_excel, bg="#2196F3", fg="white").grid(row=5, column=0, columnspan=2, pady=5)

# Table setup
columns = ("ID", "Category", "Amount", "Date", "Description")
tree = ttk.Treeview(root, columns=columns, show="headings", height=10)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120)

tree.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

load_expenses()
root.mainloop()

# Start the app with the PIN window
pin_window.mainloop()
