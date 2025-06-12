from dotenv import load_dotenv
from twilio.rest import Client
import os
import database

def send_whatsapp_report():
    """
    Generates the monthly report and sends it via WhatsApp.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Get credentials from environment variables
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_number = os.getenv('TWILIO_PHONE_NUMBER')
    recipient_number = os.getenv('RECIPIENT_PHONE_NUMBER')

    # Check if all required variables are present
    if not all([account_sid, auth_token, twilio_number, recipient_number]):
        print("Error: Missing one or more required environment variables.")
        print("Please check your .env file.")
        return

    print("Generating monthly report...")
    # Get the report string from our database module
    report_body = database.get_monthly_report()

    print(f"Sending report to {recipient_number}...")
    try:
        # Initialize the Twilio client
        client = Client(account_sid, auth_token)

        # Create and send the message
        message = client.messages.create(
            from_=twilio_number,
            body=report_body,
            to=recipient_number
        )
        print(f"Message sent successfully! SID: {message.sid}")
    except Exception as e:
        print(f"An error occurred while sending the message: {e}")

# This block allows us to run the script directly from the command line
if __name__ == '__main__':
    send_whatsapp_report()