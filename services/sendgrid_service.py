"""
SendGrid Email Service
"""

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class SendGridService:
    """Service for sending emails via SendGrid"""

    def __init__(self):
        api_key = os.environ.get("SENDGRID_KEY")
        if not api_key:
            print("❌ SENDGRID_KEY not set")
        self.client = SendGridAPIClient(api_key)
        self.from_email = os.environ.get("FROM_EMAIL")

    def send_acknowledgement(self, to: str, ai_reply: str) -> None:
        """
        Send an acknowledgement email with the AI's reply.

        Args:
            to: Recipient email address
            ai_reply: The AI-generated reply to include in the email
        """
        html_content = f"<p>{ai_reply.replace(chr(10), '<br/>')}</p>"

        message = Mail(
            from_email=self.from_email,
            to_emails=to,
            subject="Re: Your support request",
            plain_text_content=ai_reply,
            html_content=html_content,
        )

        try:
            response = self.client.send(message)
            print(f"✅ SendGrid response: {response.status_code}")
        except Exception as e:
            print(f"❌ SendGrid error: {e}")
