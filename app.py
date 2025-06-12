from flask import Flask, request, render_template
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
import re # Make sure 're' is imported
import database

load_dotenv()

app = Flask(__name__)

# The message parser is now inside app.py
def parse_message(message):
    """
    Parses an incoming message to extract command, description, amount, and category.
    """
    message = message.lower().strip()

    # For adding an expense
    match = re.match(r'add\s+(.+?)\s+([\d\.]+)(\s+in\s+(.+))?$', message)
    if match:
        description = match.group(1).strip()
        amount = float(match.group(2))
        category = match.group(4).strip() if match.group(4) else 'general'
        return 'add_expense', {'description': description, 'amount': amount, 'category': category}

    # For setting a budget
    match = re.match(r'budget\s+(.+?)\s+([\d\.]+)', message)
    if match:
        category = match.group(1).strip()
        amount = float(match.group(2))
        return 'set_budget', {'category': category, 'amount': amount}

    # For getting a report
    if message == 'report':
        return 'get_report', {}

    # For getting help (New)
    if message == 'help':
        return 'show_help', {}

    return None, {}


@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    """Responds to incoming WhatsApp messages."""
    incoming_msg = request.values.get('Body', '').strip()
    response = MessagingResponse()
    msg = response.message()

    command, data = parse_message(incoming_msg)

    if command == 'add_expense':
        database.add_expense(data['description'], data['amount'], data['category'])
        reply = f"Expense added: {data['description'].capitalize()} for ₹{data['amount']:.2f} in {data['category'].capitalize()}."
        msg.body(reply)
        
    elif command == 'set_budget':
        database.set_budget(data['category'], data['amount'])
        reply = f"Budget for {data['category'].capitalize()} set to ₹{data['amount']:.2f}."
        msg.body(reply)
        
    elif command == 'get_report':
        report = database.get_monthly_report()
        msg.body(report)

    elif command == 'show_help':
        help_text = (
            "Welcome to your Spending Tracker Bot!\n\n"
            "*Available Commands:*\n\n"
            "1️⃣ *Add an expense:*\n"
            "`add <description> <amount> in <category>`\n"
            "_Example:_ `add Coffee 250 in food`\n"
            "_(The 'in <category>' part is optional and will default to 'general')_\n\n"
            "2️⃣ *Set a category budget:*\n"
            "`budget <category> <amount>`\n"
            "_Example:_ `budget food 10000`\n\n"
            "3️⃣ *Get a monthly report:*\n"
            "`report`\n\n"
            "4️⃣ *Get this help message:*\n"
            "`help`\n\n"
            "You can also view your full expense history on your web dashboard!"
        )
        msg.body(help_text)

    else:
        # This is the default reply for any unrecognized command
        reply = "Sorry, I didn't understand that. Send 'help' to see a list of all available commands."
        msg.body(reply)

    return str(response)

@app.route('/expenses')
def show_expenses():
    """Renders a web page with a table of all expenses."""
    all_expenses = database.get_all_expenses()
    return render_template('expenses.html', expenses=all_expenses)


if __name__ == '__main__':
    # Use 0.0.0.0 to make it accessible on your network for homelab setup
    app.run(host='0.0.0.0', port=5000, debug=True)