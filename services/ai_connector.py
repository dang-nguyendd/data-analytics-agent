from google import genai
from google.genai import types
import os
import pandas as pd
import json

from services.prompt import get_agent_prompt
from services.data_summary import data_summary

class AIConnector:
    def __init__(self):
        self.model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
        # Automatically picks up the GEMINI_API_KEY environment variable
        self.client = genai.Client()
        self.chat_session = None

    # ========================================================
    # 1. Single-Turn Generation (No Memory)
    # ========================================================
    def generate(self, message: str) -> str:
        """Sends a single message without remembering previous context."""
        response = self.client.models.generate_content(
            model=self.model,
            contents=message
        )
        return response.text

    # ========================================================
    # 2. Multi-Turn Chat (Remembers Context)
    # ========================================================
    def start_chat(self):
        """Initializes a new chat session with memory."""
        self.chat_session = self.client.chats.create(
            model=self.model
        )

    def start_data_chat(self):
            # 1. Get the prompt (no summary passed here anymore)
            system_instruction = get_agent_prompt()

            # 2. Configure and start the chat
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1,
            )

            self.chat_session = self.client.chats.create(
                model=self.model,
                config=config
            )

    def send_chat_message(self, message: str, df: pd.DataFrame) -> str:
        """Sends a message injected with the latest data state."""
        if self.chat_session is None:
            self.start_data_chat()

        # Get data summary
        df_summary = json.dumps(data_summary(df=df))

        # Wrap the user's message with the latest context
        augmented_message = f"""
        ### CURRENT DATA STATE
        {df_summary}

        ### USER REQUEST
        {message}
        """
        # Send the combined message to the AI
        response = self.chat_session.send_message(augmented_message)
        return response.text