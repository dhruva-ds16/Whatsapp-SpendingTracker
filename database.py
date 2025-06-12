import os
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    DATABASE_URL = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id SERIAL PRIMARY KEY,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT,
                date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS budget (
                id SERIAL PRIMARY KEY,
                category TEXT UNIQUE NOT NULL,
                amount REAL NOT NULL
            )
        ''')
    conn.commit()
    conn.close()
    print("Database tables created or already exist.")

def add_expense(description, amount, category='general'):
    """Adds a new expense to the database."""
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO expenses (description, amount, category) VALUES (%s, %s, %s)",
                (description, amount, category)
            )
    conn.close()

def set_budget(category, amount):
    """Sets or updates a budget for a specific category."""
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            # Use ON CONFLICT to perform an "upsert" (insert or update)
            cur.execute(
                """
                INSERT INTO budget (category, amount) VALUES (%s, %s)
                ON CONFLICT (category) DO UPDATE SET amount = EXCLUDED.amount
                """,
                (category.lower(), amount)
            )
    conn.close()

def get_monthly_report():
    """Generates a report of expenses for the current month."""
    conn = get_db_connection()
    report_data = {}
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT SUM(amount) as total FROM expenses WHERE date_trunc('month', date) = date_trunc('month', current_date)")
        report_data['total_spent'] = cur.fetchone()['total'] or 0
        
        cur.execute("SELECT category, SUM(amount) as amount FROM expenses WHERE date_trunc('month', date) = date_trunc('month', current_date) GROUP BY category")
        report_data['category_expenses'] = cur.fetchall()
        
        cur.execute("SELECT category, amount FROM budget")
        report_data['budgets'] = cur.fetchall()
    conn.close()

    # Formatting the report string
    report = f"Total spent this month: ₹{report_data['total_spent']:.2f}\n\n"
    report += "Spending by category:\n"
    for row in report_data['category_expenses']:
        report += f"- {row['category'].capitalize() if row['category'] else 'General'}: ₹{row['amount']:.2f}\n"

    report += "\nBudget status:\n"
    budgets_dict = {row['category']: row['amount'] for row in report_data['budgets']}
    category_expenses_dict = {row['category']: row['amount'] for row in report_data['category_expenses']}

    for category, budget_amount in budgets_dict.items():
        spent_in_category = category_expenses_dict.get(category, 0)
        remaining = budget_amount - spent_in_category
        status = "Under budget" if remaining >= 0 else "Over budget"
        report += f"- {category.capitalize()}: ₹{spent_in_category:.2f} / ₹{budget_amount:.2f} (Remaining: ₹{remaining:.2f}) - {status}\n"
    
    return report

def get_all_expenses():
    """Retrieves all expenses from the database, ordered by date."""
    conn = get_db_connection()
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT * FROM expenses ORDER BY date DESC")
        all_expenses = cur.fetchall()
    conn.close()
    return all_expenses