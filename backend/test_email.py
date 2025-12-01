import os
from flask import Flask
from flask_mail import Mail, Message
from config import Config

def test_email():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    mail = Mail(app)
    
    with app.app_context():
        try:
            msg = Message(
                subject="Test Email from HMS",
                recipients=["sangalkartik4@gmail.com"],  # Replace with your email for testing
                body="This is a test email from the Hospital Management System."
            )
            mail.send(msg)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_email()