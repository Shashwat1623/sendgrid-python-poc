"""
OpenAI Service using OpenRouter API
"""

import os
from openai import OpenAI


class OpenAIService:
    """Service for interacting with OpenAI/OpenRouter API"""

    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_KEY"),
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://sendgrid-python-poc.onrender.com",
                "X-Title": "SendGrid AI Support POC",
            },
        )

    def ask(self, question: str) -> str:
        """
        Ask the AI a question and get a response.

        Args:
            question: The question to ask the AI

        Returns:
            The AI's response as a string
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # cheap + fast for POC
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful customer support agent.",
                    },
                    {"role": "user", "content": question},
                ],
            )
            return response.choices[0].message.content or "No response"
        except Exception as e:
            print(f"❌ OpenAI error: {e}")
            return "Sorry, I couldn't process your request at this time."
