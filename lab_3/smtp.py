# simple_smtp_client.py
import smtplib
from dotenv import load_dotenv
import os
load_dotenv()

sender_email = os.getenv('EMAIL')
password = os.getenv('PASSWORD')

class SimpleSmtpClient:
    def __init__(self, smtp_server, smtp_port):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = None
        self.password = None
        self.smtp_connection = None

    def login(self, sender_email, password):
        self.sender_email = sender_email
        self.password = password

    def connect(self):
        try:
            self.smtp_connection = smtplib.SMTP(self.smtp_server, self.smtp_port)
            self.smtp_connection.starttls()
            self.smtp_connection.login(self.sender_email, self.password)
            print("Successfully connected to SMTP server")
        except Exception as e:
            print(f"Connection failed: {str(e)}")
            raise

    def send_email(self, recipient_email, subject, message):
        if not self.smtp_connection:
            raise Exception("Not connected to SMTP server")

        email_text = f"Subject: {subject}\n\n{message}"

        try:
            self.smtp_connection.sendmail(
                self.sender_email,
                recipient_email,
                email_text.encode('utf-8')
            )
            print(f"Email sent successfully to {recipient_email}")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            raise

    def disconnect(self):
        if self.smtp_connection:
            self.smtp_connection.quit()
            print("Disconnected from SMTP server")

def main():
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    client = SimpleSmtpClient(SMTP_SERVER, SMTP_PORT)

    try:
        client.login(sender_email, password)
        client.connect()

        MOCK_RECIPIENT = "linkolnmax24@gmail.com"
        MOCK_SUBJECT = "Test Email from Python SMTP Client"
        MOCK_MESSAGE = """
           Hello!

           This is a test email sent from our Python SMTP client.

           Features demonstrated:
           - SMTP connection
           - TLS encryption
           - Basic email sending

           Best regards,
           Python SMTP Client
           """

        client.send_email(MOCK_RECIPIENT,  MOCK_SUBJECT, MOCK_MESSAGE)

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()