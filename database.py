import sqlite3
from datetime import datetime

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = sqlite3.connect('spending.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT UNIQUE NOT NULL,
            amount REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_expense(description, amount, category='general'):
    """Adds a new expense to the database."""
    conn = sqlite3.connect('spending.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (description, amount, category) VALUES (?, ?, ?)",
        (description, amount, category)
    )
    conn.commit()
    conn.close()

def set_budget(category, amount):
    """Sets or updates a budget for a specific category."""
    conn = sqlite3.connect('spending.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO budget (category, amount) VALUES (?, ?)",
        (category.lower(), amount)
    )
    conn.commit()
    conn.close()

# Add this new function to the end of database.py
def get_all_expenses():
    """Retrieves all expenses from the database, ordered by date."""
    conn = sqlite3.connect('spending.db')
    # This makes the results act like dictionaries, which is easier to use
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
    all_expenses = cursor.fetchall()
    conn.close()
    return all_expenses

# In database.py, replace the old function with this one
def get_monthly_report():
    """Generates a report of expenses for the current month."""
    conn = sqlite3.connect('spending.db')
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')")
    total_spent = cursor.fetchone()[0] or 0
    cursor.execute("SELECT category, SUM(amount) FROM expenses WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now') GROUP BY category")
    category_expenses = cursor.fetchall()
    cursor.execute("SELECT category, amount FROM budget")
    budgets = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()

    report = f"Total spent this month: ₹{total_spent:.2f}\n\n"
    report += "Spending by category:\n"
    for cat, amt in category_expenses:
        report += f"- {cat.capitalize() if cat else 'General'}: ₹{amt:.2f}\n"

    report += "\nBudget status:\n"
    for category, budget_amount in budgets.items():
        spent_in_category = next((amt for cat, amt in category_expenses if cat and cat.lower() == category), 0)
        remaining = budget_amount - spent_in_category
        status = "Under budget" if remaining >= 0 else "Over budget"
        report += f"- {category.capitalize()}: ₹{spent_in_category:.2f} / ₹{budget_amount:.2f} (Remaining: ₹{remaining:.2f}) - {status}\n"
    
    return report