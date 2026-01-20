"""
SendGrid Inbound Email Webhook with AI Response
Converted from NestJS POC to Python/Flask
"""

import os
import re
from dotenv import load_dotenv
from flask import Flask, request

# Load environment variables from .env file
load_dotenv()

from services.openai_service import OpenAIService
from services.sendgrid_service import SendGridService

app = Flask(__name__)

# Initialize services
openai_service = OpenAIService()
sendgrid_service = SendGridService()


@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return "Hello World!"


@app.route("/inbound-email", methods=["POST"])
def receive_email():
    """
    Receives inbound emails from SendGrid Inbound Parse.
    Processes the email with AI and sends a reply.
    """
    print("📩 New Email Received")

    # Parse form data from SendGrid
    from_email = request.form.get("from", "")
    to_email = request.form.get("to", "")
    subject = request.form.get("subject", "")
    text = request.form.get("text", "")

    print(f"From: {from_email}")
    print(f"Subject: {subject}")

    # Extract email from "Name <email>" format
    email_match = re.search(r"<(.+)>", from_email)
    sender_email = email_match.group(1) if email_match else from_email

    # Get the question from email body or subject
    question = text or subject

    print(f"🧠 Asking AI: {question}")

    # Get AI response
    ai_reply = openai_service.ask(question)

    print(f"🤖 AI reply: {ai_reply}")

    # Send acknowledgement reply
    sendgrid_service.send_acknowledgement(sender_email, ai_reply)

    return "OK"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3005))
    app.run(host="0.0.0.0", port=port, debug=True)
