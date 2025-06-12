from flask import Flask, request, render_template
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
import database
import utils

load_dotenv()

app = Flask(__name__)

# Initialize the database if it doesn't exist
# database.init_db()

# In app.py, replace the old function with this one
@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    """Responds to incoming WhatsApp messages."""
    incoming_msg = request.values.get('Body', '').strip()
    response = MessagingResponse()
    msg = response.message()

    command, data = utils.parse_message(incoming_msg)

    if command == 'add_expense':
        database.add_expense(data['description'], data['amount'], data['category'])
        # Changed the currency symbol in the reply message below
        reply = f"Expense added: {data['description'].capitalize()} for ₹{data['amount']:.2f} in {data['category'].capitalize()}."
        msg.body(reply)
    elif command == 'set_budget':
        database.set_budget(data['category'], data['amount'])
        reply = f"Budget for {data['category'].capitalize()} set to ₹{data['amount']:.2f}."
        msg.body(reply)
    elif command == 'get_report':
        report = database.get_monthly_report()
        msg.body(report)
    else:
        reply = "Sorry, I didn't understand that. You can use commands like:\n" \
                "- add <description> <amount> [in <category>]\n" \
                "- budget <category> <amount>\n" \
                "- report"
        msg.body(reply)

    return str(response)

@app.route('/expenses')
def show_expenses():
    """Renders a web page with a table of all expenses."""
    all_expenses = database.get_all_expenses()
    return render_template('expenses.html', expenses=all_expenses)
# ^^^ ADD THIS NEW CODE BLOCK ^^^


if __name__ == '__main__':
    # Use 0.0.0.0 to make it accessible on your network for homelab setup
    app.run(host='0.0.0.0', port=5000, debug=True)
