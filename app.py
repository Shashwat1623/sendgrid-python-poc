"""
SendGrid Inbound Email Webhook with AI Response
Converted from NestJS POC to Python/Flask
"""

import os
import re
import json
from dotenv import load_dotenv
from flask import Flask, request
import cloudinary
import cloudinary.uploader

# Load environment variables from .env file
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
)

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

    # Handle file attachments
    attachment_urls = []
    
    # Get attachment info from SendGrid (JSON string)
    attachment_info = request.form.get("attachment-info", "{}")
    try:
        attachments_meta = json.loads(attachment_info)
    except json.JSONDecodeError:
        attachments_meta = {}
    
    # Process each attachment
    for key in request.files:
        file = request.files[key]
        if file and file.filename:
            print(f"📎 Attachment: {file.filename} ({file.content_type})")
            
            try:
                # Read file content
                file_content = file.read()
                
                # Generate a clean filename (remove special chars)
                clean_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', file.filename)
                
                # Upload to Cloudinary
                result = cloudinary.uploader.upload(
                    file_content,
                    folder="sendgrid-attachments",
                    resource_type="auto",  # auto-detect file type
                    public_id=f"{os.urandom(8).hex()}_{clean_filename}",
                )
                
                url = result.get("secure_url")
                attachment_urls.append({
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "url": url,
                })
                print(f"✅ Uploaded: {url}")
                
            except Exception as e:
                print(f"❌ Failed to upload {file.filename}: {e}")
    
    # Log all attachment URLs
    if attachment_urls:
        print("📎 Attachment URLs:")
        for att in attachment_urls:
            print(f"   - {att['filename']}: {att['url']}")

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
