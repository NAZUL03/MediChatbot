import streamlit as st
from datetime import datetime
import logging

from openai import OpenAI
from config import Config

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI Client
client = OpenAI(api_key=Config.OPENAI_API_KEY)

# System prompt for healthcare chatbot
SYSTEM_PROMPT = """
You are MediMate, an AI healthcare assistant.

Rules:
🩺 Provide general health guidance only
⚠️ Do NOT diagnose diseases
🚑 Recommend seeing a doctor for serious symptoms
💊 Provide safe wellness & lifestyle suggestions
😊 Be friendly, supportive, and clear

Keep responses short, helpful, and easy to read.
"""

# Healthcare Chatbot Class
class OpenAIHealthcareChatbot:
    def __init__(self):
        self.conversation_history = []

    def initialize_conversation(self):
        self.conversation_history = [
            {
                "role": "assistant",
                "content": "Hello! I'm MediMate, your AI healthcare assistant 🤖🩺 How can I help you today?"
            }
        ]

    def add_message(self, role, content):
        self.conversation_history.append({"role": role, "content": content})

    def get_chat_response(self, user_message):
        try:
            self.add_message("user", user_message)

            # Build OpenAI messages
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.conversation_history

            # Request to OpenAI
            response = client.chat.completions.create(
                model="gpt-4o-mini",        # Change model here if needed
                messages=messages
            )

            bot_reply = response.choices[0].message["content"]

            self.add_message("assistant", bot_reply)

            # Limit history size
            if len(self.conversation_history) > 14:
                self.conversation_history = (
                    [self.conversation_history[0]] +
                    self.conversation_history[-12:]
                )

            return bot_reply

        except Exception as e:
            print(f"❌ OpenAI Error: {e}")
            return "I'm having trouble connecting to OpenAI. Please try again."

# Create chatbot instance
chatbot = OpenAIHealthcareChatbot()

# Streamlit Interface
def chat_interface():
    # Session state to remember conversation history
    if 'chat_initialized' not in st.session_state:
        chatbot.initialize_conversation()
        st.session_state.chat_initialized = True
        st.session_state.conversation_start = datetime.now().isoformat()

    st.title("MediMate Healthcare Chatbot 🩺🤖")

    # Display the conversation history
    for message in chatbot.conversation_history:
        if message["role"] == "assistant":
            st.markdown(f"**Assistant:** {message['content']}")
        else:
            st.markdown(f"**You:** {message['content']}")

    # Input text box for user message
    user_message = st.text_input("Your message:", "")

    if user_message:
        # Get chatbot's reply
        bot_reply = chatbot.get_chat_response(user_message)
        st.markdown(f"**Assistant:** {bot_reply}")

# Start new chat
def new_chat():
    chatbot.initialize_conversation()
    st.session_state.conversation_start = datetime.now().isoformat()
    st.success("New conversation started! 👋")

# Streamlit App main
def main():
    st.sidebar.title("Options")
    option = st.sidebar.radio("Select an action", ("Chat", "New Chat"))

    if option == "Chat":
        chat_interface()
    elif option == "New Chat":
        new_chat()

if __name__ == "__main__":
    print("🚀 Starting MediMate Healthcare Chatbot (OpenAI Version)...")
    print("🤖 Using OpenAI GPT-4o-mini")
    print(f"🔑 OPENAI KEY LOADED: {Config.OPENAI_API_KEY[:6]}********")
    print("🌍 https://medichatbot-hu35xsasjg4ejgw9bt2qpq.streamlit.app/")
    st.set_page_config(page_title="MediMate Healthcare Chatbot", layout="wide")
    main()
